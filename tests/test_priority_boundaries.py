from itertools import combinations
import random

import pytest

from cfar.conflict_compilation import compile_activation_constraints, selection_admissibility
from cfar.oracle import exact_oracle
from cfar.priority_boundaries import closed_support_tight_witness, singleton_priority_shaft
from cfar.priority_cover import _compile_priority_structure, evaluate_priority_cover


def covers(priorities, selected):
    return all(d == 0 or any(a["left"] <= i <= a["right"] and a["supply"] >= d for a in selected)
               for i,d in enumerate(priorities))


@pytest.mark.parametrize("seed", range(64))
def test_every_irredundant_cover_has_witness_class_ply_two(seed):
    rng = random.Random(seed)
    n,p,k = rng.randint(1,7),rng.randint(1,4),rng.randint(0,8)
    demands = [rng.randint(0,p) for _ in range(n)]
    intervals = []
    for i in range(k):
        left = rng.randrange(n)
        intervals.append(dict(action_id=str(i), left=left, right=rng.randrange(left,n), supply=rng.randint(1,p)))
    for size in range(k+1):
        for chosen in combinations(intervals,size):
            if not covers(demands,chosen):
                continue
            witnesses = []
            for action in chosen:
                rest = [a for a in chosen if a is not action]
                essential = [i for i,d in enumerate(demands) if d and
                             action["left"] <= i <= action["right"] and action["supply"] >= d and
                             not any(a["left"] <= i <= a["right"] and a["supply"] >= d for a in rest)]
                if not essential:
                    break
                witnesses.append(demands[essential[0]])
            else:
                for floor in range(n+1):
                    active = [(a,q) for a,q in zip(chosen,witnesses) if a["left"] <= floor <= a["right"]+1]
                    assert len(active) <= 2*len(set(d for d in demands if d))
                    assert all(sum(q == rank for _,q in active) <= 2 for rank in set(witnesses))


@pytest.mark.parametrize("levels", range(1,7))
def test_closed_floor_support_bound_is_tight(levels):
    witness = closed_support_tight_witness(levels)
    intervals, priorities = witness["intervals"],witness["priorities"]
    assert covers(priorities,intervals)
    assert all(not covers(priorities,[b for b in intervals if b is not a]) for a in intervals)
    assert all(a["left"] <= levels <= a["right"]+1 for a in intervals)
    assert len(intervals) == 2*levels


@pytest.mark.parametrize("seed", range(12))
def test_singleton_transfer_every_subset_and_oracle(seed):
    rng = random.Random(seed)
    groups = [1,1,2,2,3,3]
    # Bipartite declared conflicts, matching the relevant prior hardness class.
    conflicts = [(i,j) for i in range(2) for j in range(2,6) if rng.random() < .5]
    instance = singleton_priority_shaft(groups,conflicts,3)
    structure = _compile_priority_structure(instance,[f"profile{i}" for i in range(3)])
    constraints = compile_activation_constraints(instance)
    assert structure["priorities"] == [1,2,3]
    assert not constraints["blocked"] and not constraints["geometry_conflicts"]
    expected = None
    for size in range(7):
        for indices in combinations(range(6),size):
            choices = set(indices)
            ids = [instance["actions"][i]["action_id"] for i in indices]
            source_feasible = set(groups[i] for i in indices)=={1,2,3} and not any(i in choices and j in choices for i,j in conflicts)
            compiled_feasible = evaluate_priority_cover(structure,ids)["satisfied"] and selection_admissibility(constraints,ids)["admissible"]
            assert source_feasible == compiled_feasible
            if source_feasible:
                key = (size,tuple(ids))
                if expected is None or key < expected:
                    expected = key
    result = exact_oracle(instance)
    assert (result["status"],result["cost"],result["selected"]) == (
        ("infeasible",None,None) if expected is None else ("optimal",str(expected[0]),list(expected[1])))


def test_invalid_witness_inputs():
    with pytest.raises(ValueError):
        singleton_priority_shaft([1],[],2)
    with pytest.raises(ValueError):
        singleton_priority_shaft([1,2],[(1,0)],2)
    with pytest.raises(ValueError):
        closed_support_tight_witness(0)
