"""Endpoint-sweep baseline adapted from prior ply-two interval machinery.

Independent transitions; scope and attribution in docs/local_conflict_interval_candidate.md.
"""
from decimal import Decimal

from .errors import require
from .objective import exact_sum


def solve_interval_sweep(edge_count, intervals, conflicts, blocked=None, *,
                         max_actions=100, max_states=100000):
    require(type(edge_count) is int and edge_count >= 0, "SWEEP_SCOPE", "invalid edge count")
    require(type(max_actions) is int and max_actions >= 0 and
            type(max_states) is int and max_states >= 1, "SWEEP_LIMIT", "invalid caps")
    require(len(intervals) <= max_actions, "SWEEP_ACTION_LIMIT", "action cap exceeded")
    catalog, costs = {}, {}
    for action in intervals:
        aid, left, right = action["action_id"], action["left"], action["right"]
        require(isinstance(aid, str) and aid and aid not in catalog,
                "SWEEP_SCOPE", "unique nonempty IDs required")
        require(type(left) is int and type(right) is int and 0 <= left <= right < edge_count,
                "SWEEP_SCOPE", "invalid interval")
        cost = Decimal(str(action["cost"]))
        require(cost.is_finite() and cost >= 0, "SWEEP_SCOPE", "invalid cost")
        catalog[aid], costs[aid] = action, cost
    unavailable = set(blocked or [])
    require(unavailable <= catalog.keys(), "SWEEP_SCOPE", "unknown blocked ID")
    forbidden = set()
    for pair in conflicts:
        require(len(pair) == 2 and pair[0] != pair[1] and set(pair) <= catalog.keys(),
                "SWEEP_SCOPE", "invalid conflict pair")
        if unavailable & set(pair):
            continue
        a, b = (catalog[aid] for aid in pair)
        require(max(a["left"], b["left"]) <= min(a["right"]+1, b["right"]+1),
                "NONLOCAL_CONFLICT", str(pair))
        forbidden.add(frozenset(pair))
    # Starts precede ends at equal floor coordinates: touching node supports
    # coexist and are checked. Required points are strictly between floors.
    events = [(2*i+1, 1, "") for i in range(edge_count)]
    for aid, action in catalog.items():
        if aid not in unavailable:
            events.extend([(2*action["left"], 0, aid), (2*(action["right"]+1), 2, aid)])
    current = {(): (Decimal(0), 0, ())}
    states, transitions, peak = 1, 0, 1
    for _, kind, aid in sorted(events):
        following = {}

        def retain(active, key):
            if active not in following or key < following[active]:
                following[active] = key

        for active, key in current.items():
            transitions += 1
            if kind == 0:
                retain(active, key)  # skip this action at its only start
                if len(active) < 2 and not any(frozenset((aid, other)) in forbidden for other in active):
                    ids = tuple(sorted((*key[2], aid)))
                    retain(tuple(sorted((*active, aid))),
                           (exact_sum([key[0], costs[aid]]), key[1]+1, ids))
            elif kind == 2:
                retain(tuple(other for other in active if other != aid), key)
            elif active:
                retain(active, key)
        states += len(following)
        peak = max(peak, len(following))
        require(states <= max_states, "SWEEP_STATE_LIMIT", "cumulative state cap exceeded")
        current = following
        if not current:
            break
    best = current.get(())
    if best is not None:
        selected = set(best[2])
        require(not selected & unavailable and not any(pair <= selected for pair in forbidden) and
                all(any(catalog[aid]["left"] <= i <= catalog[aid]["right"] for aid in selected)
                    for i in range(edge_count)), "SWEEP_POSTCHECK", "invalid cover")
    return {"method": "prior_framework_endpoint_sweep", "status": "optimal" if best is not None else "infeasible",
            "cost": str(best[0]) if best is not None else None,
            "selected": list(best[2]) if best is not None else None,
            "states": states, "peak_states": peak, "transitions": transitions,
            "optimality_evidence": "ply-two endpoint sweep adaptation; no independent scalable certificate"}
