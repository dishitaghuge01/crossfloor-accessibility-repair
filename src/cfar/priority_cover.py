"""Priority Line Cover equivalence witness; no new optimization algorithm.

See docs/shaft_priority_cover.md. Retains complete original action identities.
"""
from __future__ import annotations

from decimal import Decimal

from .dp_partition import recognize_partition_catalogue
from .errors import require
from .geometry import room_index
from .io import fingerprint
from .objective import exact_sum
from .validation import baseline_active, validate_instance


def compile_priority_cover(instance: dict, profile_order: list[str]) -> dict:
    recognized = _compile_priority_structure(instance, profile_order)
    recognize_partition_catalogue(instance)
    recognized["scope"] = "jointly feasible independent activations; common path and uniform prefix intervals"
    return recognized


def _compile_priority_structure(instance: dict, profile_order: list[str], *, validated: bool = False) -> dict:
    """Structural quotient only; callers must separately check subset admissibility."""
    if not validated:
        validate_instance(instance)
    require(len(profile_order) == len(set(profile_order)) and set(profile_order) ==
            {p["profile_id"] for p in instance["profiles"]}, "PRIORITY_SCOPE", "order must contain every profile once")
    require(all(e["op"] == "activate_connection" for a in instance["actions"] for e in a["effects"]),
            "PRIORITY_SCOPE", "activation-only actions required")
    ranks = {pid: i+1 for i, pid in enumerate(profile_order)}
    rooms = sorted(room_index(instance))
    catalog = {c["connection_id"]: c for c in instance["connections"]}
    active = baseline_active(instance)
    by_pair = {}
    for cid, permitted in active.items():
        c = catalog[cid]
        pair = tuple(sorted((c["u"], c["v"])))
        by_pair.setdefault(pair, set()).update(permitted)
    parent = {r: r for r in rooms}

    def find(r):
        while parent[r] != r:
            parent[r] = parent[parent[r]]
            r = parent[r]
        return r

    for (u, v), permitted in by_pair.items():
        if set(profile_order) <= permitted:
            parent[find(u)] = find(v)
    groups = {}
    for room in rooms:
        groups.setdefault(find(room), []).append(room)
    components = sorted(groups.values())
    component_of = {room: i for i, group in enumerate(components) for room in group}

    def quotient_pair(cid):
        c = catalog[cid]
        return tuple(sorted((component_of[c["u"]], component_of[c["v"]])))

    used = set(active) | {e["connection_id"] for a in instance["actions"] for e in a["effects"]}
    pairs = {quotient_pair(cid) for cid in used if len(set(quotient_pair(cid))) == 2}
    graph = {i: set() for i in range(len(components))}
    for u, v in pairs:
        graph[u].add(v)
        graph[v].add(u)
    if len(components) == 1:
        order = [0]
    else:
        ends = sorted(v for v in graph if len(graph[v]) == 1)
        require(len(ends) == 2 and all(1 <= len(g) <= 2 for g in graph.values()),
                "PRIORITY_SCOPE", "common quotient must be a connected path")
        order = [ends[0]]
        while True:
            options = graph[order[-1]]-set(order)
            if not options:
                break
            order.append(min(options))
        require(len(order) == len(graph), "PRIORITY_SCOPE", "disconnected common quotient")
    positions = {v: i for i, v in enumerate(order)}
    edge_index = {tuple(sorted((u, v))): i for i, (u, v) in enumerate(zip(order, order[1:]))}
    baseline_profiles = [set() for _ in edge_index]
    for cid, permitted in active.items():
        pair = quotient_pair(cid)
        if pair in edge_index:
            baseline_profiles[edge_index[pair]].update(permitted)
    priorities = [0]*len(edge_index)
    for obligation in instance["obligations"]:
        u = positions[component_of[obligation["source"]]]
        v = positions[component_of[obligation["target"]]]
        pid = obligation["profile_id"]
        for edge in range(min(u, v), max(u, v)):
            if pid not in baseline_profiles[edge]:
                priorities[edge] = max(priorities[edge], ranks[pid])
    intervals = []
    for action in sorted(instance["actions"], key=lambda a: a["action_id"]):
        affected = {}
        for effect in action["effects"]:
            pair = quotient_pair(effect["connection_id"])
            if pair in edge_index:
                affected.setdefault(edge_index[pair], set()).update(effect["permitted_profiles"])
        if affected:
            indices = sorted(affected)
            permissions = affected[indices[0]]
            height = len(permissions)
            require(permissions == set(profile_order[:height]) and
                    all(ps == permissions for ps in affected.values()),
                    "PRIORITY_SCOPE", "bundle permissions must be one uniform nonempty prefix")
            require(indices == list(range(indices[0], indices[-1]+1)),
                    "PRIORITY_SCOPE", "noncontiguous action bundle")
            left, right = indices[0], indices[-1]
        else:
            left = right = None
            height = 0
        intervals.append({"action_id": action["action_id"], "left": left, "right": right,
                          "supply": height, "cost": str(Decimal(str(action["cost"])))})
    return {"format": "priority_line_cover_witness_v1", "input_fingerprint": fingerprint(instance),
            "profile_order": profile_order[:], "path_components": [components[v] for v in order],
            "priorities": priorities, "intervals": intervals,
            "scope": "structural priority-cover quotient only; subset admissibility not checked"}


def evaluate_priority_cover(compiled: dict, selected: list[str]) -> dict:
    require(len(selected) == len(set(selected)), "DUPLICATE_SELECTION", str(selected))
    choices = set(selected)
    actions = {a["action_id"]: a for a in compiled["intervals"]}
    require(choices <= actions.keys(), "UNKNOWN_SELECTION", str(choices))
    covered = []
    for edge, priority in enumerate(compiled["priorities"]):
        covered.append(priority == 0 or any(a["left"] is not None and a["left"] <= edge <= a["right"]
                       and a["supply"] >= priority for aid, a in actions.items() if aid in choices))
    return {"satisfied": all(covered), "covered_edges": covered,
            "cost": str(exact_sum(Decimal(actions[aid]["cost"]) for aid in sorted(choices)))}
