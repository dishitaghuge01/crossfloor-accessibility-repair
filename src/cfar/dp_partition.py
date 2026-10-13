"""Exact full-component partition DP; scope/proof in docs/partition_dp.md."""
from __future__ import annotations

from decimal import Decimal

from .actions import apply_actions
from .errors import ValidationError, require
from .graphs import build_profile_graph
from .obligations import verify_obligations
from .objective import exact_sum
from .validation import validate_instance


def _components(graph: dict) -> dict[str, int]:
    result = {}
    for root in sorted(graph):
        if root in result:
            continue
        label = len(set(result.values()))
        pending = [root]
        while pending:
            node = pending.pop()
            if node not in result:
                result[node] = label
                pending.extend(graph[node] - result.keys())
    return result


def recognize_partition_catalogue(instance: dict) -> dict:
    validate_instance(instance)
    actions = sorted(instance["actions"], key=lambda a: a["action_id"])
    for action in actions:
        require(not action["requires"] and not action["excludes"],
                "PARTITION_SCOPE", "dependencies and exclusions unsupported")
        require(all(e["op"] == "activate_connection" for e in action["effects"]),
                "PARTITION_SCOPE", "activation-only actions required")
    try:
        apply_actions(instance, [a["action_id"] for a in actions], validated=True)
    except ValidationError as error:
        raise ValidationError("PARTITION_SCOPE", f"full catalogue not jointly feasible: {error}") from error
    pids = sorted({o["profile_id"] for o in instance["obligations"]})
    catalog = {c["connection_id"]: c for c in instance["connections"]}
    maps, counts, obligations = [], [], []
    for pid in pids:
        components = _components(build_profile_graph(instance, pid))
        relevant = set()
        for obligation in instance["obligations"]:
            if obligation["profile_id"] == pid:
                relevant.update((components[obligation["source"]], components[obligation["target"]]))
        for action in actions:
            for effect in action["effects"]:
                if pid in effect["permitted_profiles"]:
                    c = catalog[effect["connection_id"]]
                    relevant.update((components[c["u"]], components[c["v"]]))
        dense = {c: i for i, c in enumerate(sorted(relevant))}
        mapping = {room: dense[c] for room, c in components.items() if c in dense}
        maps.append(mapping)
        counts.append(len(dense))
        obligations.append([(mapping[o["source"]], mapping[o["target"]])
                            for o in instance["obligations"] if o["profile_id"] == pid])
    bundles = []
    for action in actions:
        edges = []
        for pi, pid in enumerate(pids):
            for effect in action["effects"]:
                if pid in effect["permitted_profiles"]:
                    c = catalog[effect["connection_id"]]
                    edges.append((pi, maps[pi][c["u"]], maps[pi][c["v"]]))
        bundles.append((action["action_id"], Decimal(str(action["cost"])), edges))
    return {"profiles": pids, "component_counts": counts,
            "obligations": obligations, "bundles": bundles}


def _join(state: tuple, edges: list) -> tuple:
    partitions = [list(p) for p in state]
    for pi, u, v in edges:
        partition = partitions[pi]
        a, b = partition[u], partition[v]
        if a != b:
            partition[:] = [a if block == b else block for block in partition]
    canonical = []
    for partition in partitions:
        names = {}
        canonical.append(tuple(names.setdefault(block, len(names)) for block in partition))
    return tuple(canonical)


def solve_partition(instance: dict, max_components: int = 16, max_states: int = 100000) -> dict:
    require(max_components >= 0 and max_states >= 1, "PARTITION_LIMIT", "invalid resource caps")
    recognized = recognize_partition_catalogue(instance)
    counts = recognized["component_counts"]
    require(sum(counts) <= max_components, "COMPONENT_LIMIT", f"{sum(counts)} > {max_components}")
    initial = tuple(tuple(range(n)) for n in counts)
    states = {initial: (Decimal(0), 0, ())}
    peak, transitions = 1, 0
    for aid, cost, edges in recognized["bundles"]:
        updated = dict(states)
        for state, key in states.items():
            transitions += 1
            nxt = _join(state, edges)
            candidate = (exact_sum([key[0], cost]), key[1] + 1, key[2] + (aid,))
            if nxt not in updated or candidate < updated[nxt]:
                updated[nxt] = candidate
                require(len(updated) <= max_states, "STATE_LIMIT", f"more than {max_states} states")
        states = updated
        peak = max(peak, len(states))
    feasible = [key for state, key in states.items()
                if all(state[pi][u] == state[pi][v]
                       for pi, pairs in enumerate(recognized["obligations"]) for u, v in pairs)]
    best = min(feasible) if feasible else None
    verification = None
    if best is not None:
        repair = apply_actions(instance, list(best[2]), validated=True)
        paths = verify_obligations(instance, repair["active"])
        require(paths["satisfied"], "DP_POSTCHECK", "reachability disagrees")
        verification = {"reachability": paths, "adjacency": repair["adjacency"], "geometry": repair["geometry"]}
    return {"status": "optimal" if best is not None else "infeasible", "variant": "SCFAR",
            "method": "full_component_partition_dp", "cost": str(best[0]) if best is not None else None,
            "selected": list(best[2]) if best is not None else None,
            "profiles": recognized["profiles"], "component_counts": counts,
            "states": len(states), "peak_states": peak, "transitions": transitions,
            "verification": verification,
            "optimality_evidence": "partition recurrence; no independent exhaustive certificate",
            "guarantee_scope": "jointly feasible independent activation catalogue; complete component partitions"}
