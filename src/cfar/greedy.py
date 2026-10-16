"""Whole-action greedy comparator; a failed heuristic is never infeasibility."""
from fractions import Fraction
from itertools import combinations

from .actions import apply_actions
from .graphs import build_profile_graph
from .interface_recognition import recognize_physical_interface
from .objective import action_cost
from .obligations import verify_obligations
from .errors import ValidationError


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


def improve_greedy(instance, selected, *, exchange_budget=100):
    """Prune, then first-improve by deleting <=2 actions and adding <=1.

    The deterministic budget counts fully replayed exchange proposals, including
    incompatible proposals. Pruning is separate and bounded by the catalogue.
    This improves feasible repairs only; it is not a completeness procedure.
    """
    if not isinstance(exchange_budget, int) or isinstance(exchange_budget, bool) or exchange_budget < 0:
        raise ValueError("exchange_budget must be a nonnegative integer")
    selected = sorted(selected)
    stats = dict(prune_trials=0, removed_actions=0, exchange_trials=0, accepted_exchanges=0,
                 exchange_budget=exchange_budget)

    def label(ids):
        return action_cost(instance, ids), len(ids), tuple(ids)

    def feasible(ids):
        try:
            repair = apply_actions(instance, ids)
        except ValidationError:
            return False
        return verify_obligations(repair["instance"], repair["active"])["satisfied"]

    if not feasible(selected):
        raise ValueError("improvement requires a replay-valid feasible repair")
    catalog = sorted(a["action_id"] for a in instance["actions"])
    while True:
        # Deletions cannot restore reachability lost by another deletion.
        for aid in list(reversed(selected)):
            trial = [a for a in selected if a != aid]
            stats["prune_trials"] += 1
            if feasible(trial):
                selected = trial
                stats["removed_actions"] += 1
        improved = False
        for size in (1, 2):
            for removed in combinations(selected, size):
                for added in catalog:
                    if added in selected:
                        continue
                    trial = sorted((set(selected) - set(removed)) | {added})
                    if label(trial) >= label(selected):
                        continue
                    if stats["exchange_trials"] >= exchange_budget:
                        return selected, stats
                    stats["exchange_trials"] += 1
                    if feasible(trial):
                        selected = trial
                        stats["accepted_exchanges"] += 1
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break
        if not improved:
            return selected, stats


def solve_greedy(instance, *, improve=False, exchange_budget=100):
    recognized = recognize_physical_interface(instance)
    actions = {a["action_id"]: a for a in instance["actions"]}
    selected, occupancy = [], {}
    while True:
        repair = apply_actions(instance, selected)
        verification = verify_obligations(repair["instance"], repair["active"])
        if verification["satisfied"]:
            statistics = None
            if improve:
                selected, statistics = improve_greedy(instance, selected, exchange_budget=exchange_budget)
                repair = apply_actions(instance, selected)
                verification = verify_obligations(repair["instance"], repair["active"])
            return dict(method="whole_action_greedy_improved_v1" if improve else "whole_action_greedy_v1",
                        statistics=statistics, status="feasible", selected=selected,
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
            return dict(method="whole_action_greedy_improved_v1" if improve else "whole_action_greedy_v1",
                        status="heuristic_failed", selected=None, cost=None,
                        partial_selected=selected, input_fingerprint=recognized["input_fingerprint"])
        aid = min(candidates)[1]
        selected = sorted(selected + [aid])
        occupancy.update(recognized["action_cells"][aid])
