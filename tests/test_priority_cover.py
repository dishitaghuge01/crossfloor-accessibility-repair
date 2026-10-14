from copy import deepcopy
from itertools import combinations
import random

import pytest

from cfar.actions import apply_actions
from cfar.conflict_compilation import compile_activation_constraints
from cfar.errors import ValidationError
from cfar.objective import action_cost
from cfar.obligations import verify_obligations
from cfar.oracle import exact_oracle
from cfar.priority_cover import compile_priority_cover, evaluate_priority_cover
from cfar.schema import ROOT, load_instance
from cfar.synthetic_shaft import make_shaft_instance
from cfar.synthetic_star import make_star_instance


def check_subsets(instance, order):
    before = deepcopy(instance)
    compiled = compile_priority_cover(instance, order)
    aids = sorted(a["action_id"] for a in instance["actions"])
    for size in range(len(aids)+1):
        for selected in combinations(aids, size):
            repair = apply_actions(instance, list(selected), validated=True)
            expected = verify_obligations(instance, repair["active"])
            actual = evaluate_priority_cover(compiled, list(selected))
            assert actual["satisfied"] == expected["satisfied"]
            assert actual["cost"] == str(action_cost(instance, list(selected)))
    assert instance == before
    return compiled


@pytest.mark.parametrize("seed", range(16))
def test_local_shaft_intervals_with_baselines_and_arbitrary_pairs(seed):
    rng = random.Random(seed)
    n = rng.randint(2, 5)
    intervals = [(0, n-1, 2)]
    for _ in range(4):
        left = rng.randrange(n)
        intervals.append((left, rng.randrange(left, n), rng.randint(1, 2)))
    instance = make_shaft_instance(n, intervals, [rng.randint(0, 9) for _ in intervals])
    transitions = []
    for edge in range(n):
        permitted = [pid for pid in ("profile0", "profile1") if rng.random() < .4]
        if permitted:
            transitions.append({"connection_id": f"P{edge}", "permitted_profiles": permitted})
    instance["portals"] = [{"portal_id": "baseline", "kind": "lift", "transitions": transitions}] if transitions else []
    for obligation in instance["obligations"]:
        obligation["source"] = f"R{rng.randrange(n+1)}"
        obligation["target"] = f"R{rng.randrange(n+1)}"
    check_subsets(instance, ["profile0", "profile1"])


def test_physical_bundles_and_priorities():
    instance = make_shaft_instance(3, [(0,1,2),(1,2,1),(0,2,2)], [1,1,10], physical=True)
    instance["obligations"][1]["target"] = "R1"
    compiled = check_subsets(instance, ["profile0", "profile1"])
    assert compiled["priorities"] == [2,1,1]
    assert exact_oracle(instance)["selected"] == ["A000", "A001"]


def test_geometric_conflicts_break_plain_priority_cover():
    instance = make_shaft_instance(3, [(0,1,2),(1,2,1),(0,2,2)], [1,1,10],
                                   physical=True, conflict_witness=True)
    constraints = compile_activation_constraints(instance)
    assert not constraints["blocked"]
    assert [c["actions"] for c in constraints["geometry_conflicts"]] == [["A000", "A001"]]
    with pytest.raises(ValidationError, match="PORTAL_COLLISION"):
        apply_actions(instance, ["A000", "A001"])
    with pytest.raises(ValidationError, match="PARTITION_SCOPE"):
        compile_priority_cover(instance, ["profile0", "profile1"])
    oracle = exact_oracle(instance)
    assert oracle["cost"] == "10" and oracle["selected"] == ["A002"]


def test_baseline_contraction_coupled_microcase():
    instance = load_instance(ROOT/"examples/micro/06_coupled_portal_actions.json")
    compiled = check_subsets(instance, ["ambulant", "wheelchair"])
    assert len(compiled["path_components"]) == 3


def test_scope_guards():
    instance = make_shaft_instance(3, [(0,2,2),(0,2,2)], [1,2])
    instance["actions"][0]["effects"].pop(1)
    instance["actions"][0]["evidence_ids"].pop(1)
    with pytest.raises(ValidationError, match="PRIORITY_SCOPE.*noncontiguous"):
        compile_priority_cover(instance, ["profile0", "profile1"])
    instance = make_shaft_instance(2, [(0,1,2)], [1])
    instance["actions"][0]["effects"][0]["permitted_profiles"] = ["profile0"]
    with pytest.raises(ValidationError, match="PRIORITY_SCOPE.*uniform"):
        compile_priority_cover(instance, ["profile0", "profile1"])
    with pytest.raises(ValidationError, match="PRIORITY_SCOPE.*order"):
        compile_priority_cover(instance, ["profile0", "profile0"])
    with pytest.raises(ValidationError, match="PRIORITY_SCOPE.*path"):
        compile_priority_cover(make_star_instance(3, [[0,1,2]], [1]), ["controlled"])


def test_all_baseline_and_empty_obligations():
    instance = make_shaft_instance(2, [(0,1,2)], [0])
    instance["portals"] = [{"portal_id": "baseline", "kind": "lift", "transitions": [
        {"connection_id": f"P{i}", "permitted_profiles": ["profile0", "profile1"]} for i in range(2)]}]
    compiled = check_subsets(instance, ["profile0", "profile1"])
    assert compiled["priorities"] == [] and compiled["intervals"][0]["left"] is None
    instance["obligations"] = []
    check_subsets(instance, ["profile0", "profile1"])


def test_invalid_selection_and_exact_cost():
    instance = make_shaft_instance(1, [(0,0,2)], [10**30+1])
    compiled = check_subsets(instance, ["profile0", "profile1"])
    assert evaluate_priority_cover(compiled, ["A000"])["cost"] == str(10**30+1)
    with pytest.raises(ValidationError, match="UNKNOWN_SELECTION"):
        evaluate_priority_cover(compiled, ["bad"])
    with pytest.raises(ValidationError, match="DUPLICATE_SELECTION"):
        evaluate_priority_cover(compiled, ["A000", "A000"])
