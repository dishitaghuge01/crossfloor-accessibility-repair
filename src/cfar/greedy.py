"""Whole-action greedy comparator; a failed heuristic is never infeasibility."""
from fractions import Fraction

from .actions import apply_actions
from .graphs import build_profile_graph
from .interface_recognition import recognize_physical_interface
from .objective import action_cost
from .obligations import verify_obligations


def _reach(instance, active, anchors):
    reached = set()
    for pid, root in sorted(anchors.items()):
        graph = build_profile_graph(instance, pid, active)
        stack, seen = [root], {root}
        while stack:
            for other in graph[stack.pop()] - seen:
                seen.add(other)
                stack.append(other)
        reached.update((pid, room) for room in seen)
    return reached


def solve_greedy(instance):
    recognized = recognize_physical_interface(instance)
    actions = {a["action_id"]: a for a in instance["actions"]}
    selected, occupancy = [], {}
    while True:
        repair = apply_actions(instance, selected)
        verification = verify_obligations(repair["instance"], repair["active"])
        if verification["satisfied"]:
            return dict(method="whole_action_greedy_v1", status="feasible", selected=selected,
                        cost=str(action_cost(instance, selected)), input_fingerprint=recognized["input_fingerprint"],
                        reachability=verification, geometry=repair["geometry"], adjacency=repair["adjacency"])
        before = _reach(instance, repair["active"], recognized["anchors"])
        candidates = []
        for aid, cells in recognized["action_cells"].items():
            if aid in selected or any(c in occupancy and occupancy[c] != owner for c, owner in cells.items()):
                continue
            trial = apply_actions(instance, sorted(selected + [aid]))
            gain = len(_reach(instance, trial["active"], recognized["anchors"]) - before)
            if gain:
                candidates.append((Fraction(str(actions[aid]["cost"])) / gain, aid))
        if not candidates:
            return dict(method="whole_action_greedy_v1", status="heuristic_failed", selected=None, cost=None,
                        partial_selected=selected, input_fingerprint=recognized["input_fingerprint"])
        aid = min(candidates)[1]
        selected = sorted(selected + [aid])
        occupancy.update(recognized["action_cells"][aid])
