from copy import deepcopy
from decimal import Decimal
from itertools import combinations
import random

import pytest

from cfar.dp_local_intervals import solve_local_interval_cover, solve_local_shaft
from cfar.errors import ValidationError
from cfar.objective import exact_sum
from cfar.oracle import exact_oracle
from cfar.synthetic_shaft import make_shaft_instance


def brute_intervals(n, intervals, conflicts, blocked=()):
    best = None
    for size in range(len(intervals)+1):
        for subset in combinations(intervals, size):
            choices = {a["action_id"] for a in subset}
            if choices & set(blocked) or any(set(pair) <= choices for pair in conflicts):
                continue
            if not all(any(a["left"] <= edge <= a["right"] for a in subset) for edge in range(n)):
                continue
            key = (exact_sum(Decimal(str(a["cost"])) for a in subset), size, tuple(sorted(choices)))
            if best is None or key < best:
                best = key
    return ("optimal", str(best[0]), list(best[2])) if best is not None else ("infeasible", None, None)


@pytest.mark.parametrize("seed", range(64))
def test_abstract_local_conflicts_against_all_subsets(seed):
    rng = random.Random(seed)
    n, k = rng.randint(1, 8), rng.randint(0, 9)
    intervals = []
    for i in range(k):
        left = rng.randrange(n)
        intervals.append({"action_id": f"A{rng.randrange(1000):03d}-{i}", "left": left,
                          "right": rng.randrange(left, n), "cost": rng.randint(0, 8)})
    conflicts = [[a["action_id"], b["action_id"]] for a, b in combinations(intervals, 2)
                 if max(a["left"], b["left"]) <= min(a["right"]+1, b["right"]+1) and rng.random() < .4]
    blocked = [a["action_id"] for a in intervals if rng.random() < .1]
    original = deepcopy((intervals, conflicts, blocked))
    result = solve_local_interval_cover(n, intervals, conflicts, blocked)
    assert (result["status"], result["cost"], result["selected"]) == brute_intervals(n, intervals, conflicts, blocked)
    assert (intervals, conflicts, blocked) == original
    assert result["states"] <= k*k+k


def test_three_action_chain_and_node_boundary_conflict():
    intervals = [{"action_id": f"A{i}", "left": i, "right": i, "cost": 1} for i in range(3)]
    assert solve_local_interval_cover(3, intervals, [])["selected"] == ["A0", "A1", "A2"]
    # Edge intervals are disjoint, but node supports share an endpoint: still a local conflict.
    assert solve_local_interval_cover(3, intervals, [["A0", "A1"]])["status"] == "infeasible"
    with pytest.raises(ValidationError, match="NONLOCAL_CONFLICT"):
        solve_local_interval_cover(3, intervals, [["A0", "A2"]])


def test_zero_cost_ties_lexical_order_and_large_costs():
    intervals = [{"action_id": "z", "left": 0, "right": 1, "cost": 0},
                 {"action_id": "a", "left": 0, "right": 1, "cost": 0},
                 {"action_id": "b", "left": 0, "right": 0, "cost": 0},
                 {"action_id": "c", "left": 1, "right": 1, "cost": 0}]
    assert solve_local_interval_cover(2, intervals, [])["selected"] == ["a"]
    for a in intervals:
        a["cost"] = 10**30+1
    result = solve_local_interval_cover(2, intervals, [])
    assert result["selected"] == ["a"] and result["cost"] == str(10**30+1)


def test_caps_and_invalid_abstract_scope():
    intervals = [{"action_id": "a", "left": 0, "right": 0, "cost": 1},
                 {"action_id": "b", "left": 0, "right": 0, "cost": 1}]
    with pytest.raises(ValidationError, match="LOCAL_ACTION_LIMIT"):
        solve_local_interval_cover(1, intervals, [], max_actions=1)
    with pytest.raises(ValidationError, match="LOCAL_STATE_LIMIT"):
        solve_local_interval_cover(1, intervals, [], max_states=1)
    with pytest.raises(ValidationError, match="LOCAL_INTERVAL_SCOPE"):
        solve_local_interval_cover(1, intervals, [["a", "unknown"]])
    assert solve_local_interval_cover(0, [], [])["selected"] == []


@pytest.mark.parametrize("seed", range(12))
def test_declared_local_exclusions_in_strict_shaft(seed):
    rng = random.Random(seed)
    n = rng.randint(2, 5)
    spans = [(0,n-1,1)]
    for _ in range(5):
        left = rng.randrange(n)
        spans.append((left,rng.randrange(left,n),1))
    instance = make_shaft_instance(n, spans, [rng.randint(0,8) for _ in spans], profiles=1)
    for i, j in combinations(range(len(spans)), 2):
        if max(spans[i][0], spans[j][0]) <= min(spans[i][1]+1,spans[j][1]+1) and rng.random() < .3:
            instance["actions"][i]["excludes"].append(instance["actions"][j]["action_id"])
    original = deepcopy(instance)
    expected, result = exact_oracle(instance), solve_local_shaft(instance)
    assert tuple(result[key] for key in ("status","cost","selected")) == tuple(expected[key] for key in ("status","cost","selected"))
    assert instance == original


def physical_local_witness():
    instance = make_shaft_instance(3,[(0,1,2),(1,2,1),(0,2,2)],[1,1,10],physical=True,conflict_witness=True)
    instance["profiles"] = instance["profiles"][:1]
    instance["obligations"] = instance["obligations"][:1]
    for c in instance["connections"]:
        c["physical_profiles"] = ["profile0"]
    for a in instance["actions"]:
        for e in a["effects"]:
            e["permitted_profiles"] = ["profile0"]
    return instance


def test_physical_collision_is_solved_and_replayed():
    instance = physical_local_witness()
    expected, result = exact_oracle(instance), solve_local_shaft(instance)
    assert expected["selected"] == result["selected"] == ["A002"]
    assert expected["cost"] == result["cost"] == "10"
    assert result["verification"]["reachability"]["satisfied"]
    assert len(result["compiled_constraints"]["geometry_conflicts"]) == 1


def test_unavailable_geometry_is_excluded_before_optimization():
    instance = make_shaft_instance(1,[(0,0,1)],[1],profiles=1,physical=True)
    instance["connections"][0]["geometry"]["width_m"] = .1
    expected, result = exact_oracle(instance), solve_local_shaft(instance)
    assert expected["status"] == result["status"] == "infeasible"
    assert result["compiled_constraints"]["blocked"]["A000"]["code"] == "PROFILE_WIDTH"


def test_reject_dependencies_multiple_profiles_and_unrequired_edges():
    instance = make_shaft_instance(2,[(0,0,1),(1,1,1)],[1,1],profiles=1)
    instance["actions"][0]["requires"] = ["A001"]
    with pytest.raises(ValidationError, match="LOCAL_SHAFT_SCOPE.*dependencies"):
        solve_local_shaft(instance)
    with pytest.raises(ValidationError, match="LOCAL_SHAFT_SCOPE.*profile"):
        solve_local_shaft(make_shaft_instance(2,[(0,1,2)],[1]))
    instance["actions"][0]["requires"] = []
    instance["obligations"][0]["target"] = "R1"
    with pytest.raises(ValidationError, match="LOCAL_SHAFT_SCOPE.*required"):
        solve_local_shaft(instance)


def test_many_actions_without_oracle(monkeypatch):
    monkeypatch.setattr("cfar.oracle.exact_oracle", lambda *args,**kwargs: pytest.fail("DP must not enumerate"))
    instance = make_shaft_instance(3,[(0,2,1)]*100,[2]*100,profiles=1,physical=True)
    result = solve_local_shaft(instance)
    assert result["selected"] == ["A000"] and result["cost"] == "2"
    assert result["states"] == 100
    assert result["compiled_constraints"]["geometry_calls_after_validation"] == 1
    assert result["compiled_constraints"]["geometry_cache_hits"] == 5049


@pytest.mark.parametrize("seed", range(6))
def test_generated_reserved_asset_alternatives(seed):
    rng = random.Random(seed)
    spans = [(0,3,1)]
    for _ in range(6):
        left = rng.randrange(4)
        spans.append((left,rng.randrange(left,4),1))
    groups = [0]+[rng.randrange(8) for _ in range(6)]
    instance = make_shaft_instance(4,spans,[10]+[rng.randint(1,5) for _ in range(6)],
                                   profiles=1,physical=True,asset_groups=groups)
    expected, result = exact_oracle(instance), solve_local_shaft(instance)
    assert tuple(result[key] for key in ("status","cost","selected")) == tuple(expected[key] for key in ("status","cost","selected"))
    assert result["verification"]["reachability"]["satisfied"]
