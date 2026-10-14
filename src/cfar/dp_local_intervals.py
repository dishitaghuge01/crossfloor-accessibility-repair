"""Exact original-interval DP for local conflicts; novelty is unestablished.

Scope/correctness: docs/local_conflict_interval_candidate.md.
"""
from __future__ import annotations

from bisect import insort
from decimal import Decimal

from .actions import apply_actions
from .conflict_compilation import compile_activation_constraints
from .errors import require
from .obligations import verify_obligations
from .objective import exact_sum
from .priority_cover import _compile_priority_structure


def solve_local_interval_cover(edge_count: int, intervals: list[dict], conflicts: list[list[str]],
                               blocked: list[str] | None = None, *, max_actions: int = 100,
                               max_states: int = 100000) -> dict:
    require(type(edge_count) is int and edge_count >= 0, "LOCAL_INTERVAL_SCOPE", "invalid edge count")
    require(max_actions >= 0 and max_states >= 1, "LOCAL_INTERVAL_LIMIT", "invalid resource caps")
    require(len(intervals) <= max_actions, "LOCAL_ACTION_LIMIT", f"{len(intervals)} > {max_actions}")
    aids = [a["action_id"] for a in intervals]
    require(all(isinstance(aid, str) and aid for aid in aids) and len(aids) == len(set(aids)),
            "LOCAL_INTERVAL_SCOPE", "unique nonempty action IDs required")
    catalog = {a["action_id"]: a for a in intervals}
    costs = {}
    for aid, action in catalog.items():
        l, r = action["left"], action["right"]
        require(type(l) is int and type(r) is int and 0 <= l <= r < edge_count,
                "LOCAL_INTERVAL_SCOPE", "invalid nonempty interval")
        cost = Decimal(str(action["cost"]))
        require(cost.is_finite() and cost >= 0, "LOCAL_INTERVAL_SCOPE", "nonnegative finite cost required")
        costs[aid] = cost
    unavailable = set(blocked or [])
    require(unavailable <= catalog.keys(), "LOCAL_INTERVAL_SCOPE", "unknown blocked action")
    incompatible = set()
    for pair in conflicts:
        require(len(pair) == 2 and pair[0] != pair[1] and set(pair) <= catalog.keys(),
                "LOCAL_INTERVAL_SCOPE", "invalid conflict pair")
        if unavailable & set(pair):
            continue
        a, b = (catalog[aid] for aid in pair)
        require(max(a["left"], b["left"]) <= min(a["right"]+1, b["right"]+1),
                "NONLOCAL_CONFLICT", str(pair))
        incompatible.add(frozenset(pair))
    candidates = sorted((a for a in intervals if a["action_id"] not in unavailable),
                        key=lambda a: (a["right"], a["left"], a["action_id"]))
    ending = {a["action_id"]: {} for a in candidates}
    state_count, transitions = 0, 0
    for b in candidates:
        bid = b["action_id"]
        if b["left"] == 0:
            ending[bid][None] = (costs[bid], 1, (bid,))
            state_count += 1
            require(state_count <= max_states, "LOCAL_STATE_LIMIT", f"more than {max_states} states")
    for b in candidates:
        bid = b["action_id"]
        for previous, key in list(ending[bid].items()):
            for c in candidates:
                transitions += 1
                cid = c["action_id"]
                if not (b["left"] < c["left"] <= b["right"]+1 and b["right"] < c["right"]):
                    continue
                if frozenset((bid, cid)) in incompatible:
                    continue
                if previous is not None and c["left"] <= catalog[previous]["right"]+1:
                    continue
                ids = list(key[2])
                insort(ids, cid)
                nxt = (exact_sum([key[0], costs[cid]]), key[1]+1, tuple(ids))
                if bid not in ending[cid] or nxt < ending[cid][bid]:
                    if bid not in ending[cid]:
                        state_count += 1
                        require(state_count <= max_states, "LOCAL_STATE_LIMIT", f"more than {max_states} states")
                    ending[cid][bid] = nxt
    finals = [key for a in candidates if a["right"] == edge_count-1 for key in ending[a["action_id"]].values()]
    best = (Decimal(0), 0, ()) if edge_count == 0 else min(finals, default=None)
    if best is not None:
        selected = set(best[2])
        require(all(any(a["left"] <= edge <= a["right"] for aid, a in catalog.items() if aid in selected)
                    for edge in range(edge_count)) and not (selected & unavailable) and
                not any(pair <= selected for pair in incompatible), "LOCAL_DP_POSTCHECK", "invalid interval cover")
    return {"status": "optimal" if best is not None else "infeasible", "method": "local_conflict_last_two_dp",
            "cost": str(best[0]) if best is not None else None,
            "selected": list(best[2]) if best is not None else None,
            "states": state_count, "transitions": transitions, "edge_count": edge_count,
            "optimality_evidence": "original-interval recurrence; no independent scalable certificate"}


def solve_local_shaft(instance: dict, max_actions: int = 100, max_states: int = 100000) -> dict:
    require(len(instance["profiles"]) == 1, "LOCAL_SHAFT_SCOPE", "exactly one profile required")
    require(all(not a["requires"] for a in instance["actions"]), "LOCAL_SHAFT_SCOPE", "dependencies unsupported")
    constraints = compile_activation_constraints(instance, max_actions)
    pid = instance["profiles"][0]["profile_id"]
    structure = _compile_priority_structure(instance, [pid], validated=True)
    require(all(p == 1 for p in structure["priorities"]), "LOCAL_SHAFT_SCOPE", "every path edge must be required")
    intervals = [a for a in structure["intervals"] if a["left"] is not None]
    relevant = {a["action_id"] for a in intervals}
    conflicts = [c["actions"] for c in constraints["geometry_conflicts"]]+constraints["excludes"]
    conflicts = [pair for pair in conflicts if set(pair) <= relevant]
    result = solve_local_interval_cover(len(structure["priorities"]), intervals, conflicts,
                                        sorted(set(constraints["blocked"]) & relevant),
                                        max_actions=max_actions, max_states=max_states)
    result.update({"variant": "SCFAR", "profile_id": pid, "compiled_constraints": constraints,
                   "path_components": structure["path_components"],
                   "guarantee_scope": "one-profile full common-path cover with local node-span conflicts; no dependencies"})
    if result["selected"] is not None:
        repair = apply_actions(instance, result["selected"], validated=True)
        paths = verify_obligations(instance, repair["active"])
        require(paths["satisfied"], "LOCAL_DP_POSTCHECK", "repair reachability disagrees")
        result["verification"] = {"reachability": paths, "adjacency": repair["adjacency"], "geometry": repair["geometry"]}
    return result
