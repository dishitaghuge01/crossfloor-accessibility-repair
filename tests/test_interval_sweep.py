from copy import deepcopy
from itertools import combinations
import random

import pytest

from cfar.dp_interval_sweep import solve_interval_sweep
from cfar.dp_local_intervals import solve_local_interval_cover, solve_local_shaft
from cfar.errors import ValidationError
from cfar.oracle import exact_oracle
from cfar.priority_cover import _compile_priority_structure
from cfar.synthetic_shaft import make_shaft_instance
from test_local_interval_dp import brute_intervals


@pytest.mark.parametrize("seed", range(100))
def test_three_way_abstract_comparison(seed):
    rng = random.Random(seed)
    n, k = rng.randint(1, 8), rng.randint(0, 10)
    intervals = []
    for i in range(k):
        left = rng.randrange(n)
        intervals.append(dict(action_id=f"A{i}", left=left, right=rng.randrange(left, n), cost=rng.randrange(9)))
    conflicts = [[a["action_id"], b["action_id"]] for a, b in combinations(intervals, 2)
                 if max(a["left"], b["left"]) <= min(a["right"]+1, b["right"]+1) and rng.random() < .4]
    blocked = [a["action_id"] for a in intervals if rng.random() < .1]
    original = deepcopy((intervals, conflicts, blocked))
    expected = brute_intervals(n, intervals, conflicts, blocked)
    for solver in (solve_interval_sweep, solve_local_interval_cover):
        result = solver(n, intervals, conflicts, blocked)
        assert tuple(result[key] for key in ("status", "cost", "selected")) == expected
    assert (intervals, conflicts, blocked) == original


@pytest.mark.parametrize("seed", range(6))
def test_physical_compilation_three_way(seed):
    rng = random.Random(seed)
    spans = [(0,3,1)]
    for _ in range(6):
        left = rng.randrange(4)
        spans.append((left, rng.randrange(left,4),1))
    instance = make_shaft_instance(4, spans, [10]+[rng.randint(1,5) for _ in range(6)],
                                   profiles=1, physical=True, asset_groups=[0]+[rng.randrange(8) for _ in range(6)])
    local = solve_local_shaft(instance)
    constraints = local["compiled_constraints"]
    structure = _compile_priority_structure(instance, ["profile0"], validated=True)
    sweep = solve_interval_sweep(4, structure["intervals"],
                               [c["actions"] for c in constraints["geometry_conflicts"]]+constraints["excludes"],
                               list(constraints["blocked"]))
    oracle = exact_oracle(instance)
    assert all(tuple(r[key] for key in ("status", "cost", "selected")) ==
               tuple(oracle[key] for key in ("status", "cost", "selected")) for r in (local, sweep))


def test_contacts_empty_ties_limits_and_nonlocal_rejection():
    intervals = [dict(action_id=f"A{i}", left=i, right=i, cost=10**30+1) for i in range(3)]
    assert solve_interval_sweep(3, intervals, [])["cost"] == str(3*(10**30+1))
    assert solve_interval_sweep(3, intervals, [["A0","A1"]])["status"] == "infeasible"
    with pytest.raises(ValidationError, match="NONLOCAL_CONFLICT"):
        solve_interval_sweep(3, intervals, [["A0","A2"]])
    with pytest.raises(ValidationError, match="SWEEP_STATE_LIMIT"):
        solve_interval_sweep(3, intervals, [], max_states=1)
    with pytest.raises(ValidationError, match="SWEEP_ACTION_LIMIT"):
        solve_interval_sweep(3, intervals, [], max_actions=1)
    assert solve_interval_sweep(0, [], [])["selected"] == []
    ties = [dict(action_id=aid, left=0, right=2, cost=0) for aid in ("z","a")]+intervals
    assert solve_interval_sweep(3, ties, [])["selected"] == ["a"]
