"""Executable witnesses for audited priority-cover boundaries, not novel solvers."""
from .synthetic_shaft import make_shaft_instance


def singleton_priority_shaft(groups: list[int], conflicts: list[tuple[int, int]], levels: int) -> dict:
    """Encode indexed duplicate singleton sets as suffix spans with nested supply.

    Conflicts are declared exclusions, never claimed to arise from footprints.
    Each group is present; indices distinguish equal-coverage alternatives.
    """
    if type(levels) is not int or levels < 1 or set(groups) != set(range(1, levels+1)):
        raise ValueError("positive levels with every singleton group represented required")
    if any(type(g) is not int for g in groups):
        raise ValueError("integer groups required")
    if any(type(i) is not int or type(j) is not int or not 0 <= i < j < len(groups) for i,j in conflicts):
        raise ValueError("conflicts must be ordered distinct valid action indices")
    instance = make_shaft_instance(levels, [(g-1, levels-1, g) for g in groups], [1]*len(groups), profiles=levels)
    instance["building_id"] = "singleton-priority-transfer"
    instance["obligations"] = [dict(obligation_id=f"O{i}", source=f"R{i}", target=f"R{i+1}",
                                    profile_id=f"profile{i}") for i in range(levels)]
    for i,j in conflicts:
        instance["actions"][i]["excludes"].append(instance["actions"][j]["action_id"])
    return instance


def closed_support_tight_witness(levels: int) -> dict:
    """Every one of 2p intervals is essential; all supports contain floor p."""
    if type(levels) is not int or levels < 1:
        raise ValueError("positive integer levels required")
    priorities = list(range(1,levels+1))+list(range(levels,0,-1))
    intervals = []
    for q in range(1,levels+1):
        intervals.extend([dict(action_id=f"L{q}", left=q-1, right=levels-1, supply=q, cost=1),
                          dict(action_id=f"R{q}", left=levels, right=2*levels-q, supply=q, cost=1)])
    return dict(priorities=priorities, intervals=intervals)
