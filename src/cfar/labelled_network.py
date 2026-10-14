"""Executable formulation-equivalence witness, not a new repair algorithm.

See docs/network_design_equivalence.md. Geometry scope is checked at compilation;
label evaluation independently checks quotient-graph connectivity and exact cost.
"""
from __future__ import annotations

from decimal import Decimal

from .dp_partition import recognize_partition_catalogue
from .errors import require
from .geometry import room_index
from .io import fingerprint
from .objective import exact_sum
from .validation import baseline_active


def compile_labelled_forest(instance: dict) -> dict:
    recognize_partition_catalogue(instance)
    rooms = sorted(room_index(instance))
    catalog = {c["connection_id"]: c for c in instance["connections"]}
    active = baseline_active(instance)
    vertices, mapping = [], {}
    for profile in sorted(instance["profiles"], key=lambda p: p["profile_id"]):
        pid = profile["profile_id"]
        parent = {room: room for room in rooms}

        def find(room):
            while parent[room] != room:
                parent[room] = parent[parent[room]]
                room = parent[room]
            return room

        for cid, permitted in active.items():
            if pid in permitted:
                c = catalog[cid]
                parent[find(c["u"])] = find(c["v"])
        groups = {}
        for room in rooms:
            groups.setdefault(find(room), []).append(room)
        for members in sorted(groups.values()):
            vid = len(vertices)
            vertices.append({"vertex_id": vid, "profile_id": pid, "rooms": members})
            mapping.update({(pid, room): vid for room in members})
    edges, labels = [], {}
    for action in sorted(instance["actions"], key=lambda a: a["action_id"]):
        aid = action["action_id"]
        labels[aid] = str(Decimal(str(action["cost"])))
        added = False
        for effect in action["effects"]:
            c = catalog[effect["connection_id"]]
            for pid in sorted(effect["permitted_profiles"]):
                u, v = mapping[pid, c["u"]], mapping[pid, c["v"]]
                if u != v:
                    edges.append({"u": u, "v": v, "label": aid, "connection_id": c["connection_id"]})
                    added = True
        if not added:
            # Preserve charges for redundant labels without changing any demanded path.
            u = len(vertices)
            vertices.extend({"vertex_id": vid, "profile_id": None, "rooms": []} for vid in (u, u+1))
            edges.append({"u": u, "v": u+1, "label": aid, "connection_id": None})
    demands = [{"obligation_id": o["obligation_id"], "u": mapping[o["profile_id"], o["source"]],
                "v": mapping[o["profile_id"], o["target"]]} for o in sorted(instance["obligations"], key=lambda o: o["obligation_id"])]
    return {"format": "weighted_labelled_forest_witness_v1", "input_fingerprint": fingerprint(instance),
            "vertices": vertices, "edges": edges, "label_costs": labels, "demands": demands,
            "scope": "jointly feasible independent strict activations; provenance is not a physical certificate"}


def evaluate_labels(network: dict, selected: list[str]) -> dict:
    require(len(selected) == len(set(selected)), "DUPLICATE_SELECTION", str(selected))
    choices = set(selected)
    require(choices <= network["label_costs"].keys(), "UNKNOWN_SELECTION", str(choices))
    parent = {v["vertex_id"]: v["vertex_id"] for v in network["vertices"]}

    def find(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for edge in network["edges"]:
        if edge["label"] in choices:
            parent[find(edge["u"])] = find(edge["v"])
    satisfied = {d["obligation_id"]: find(d["u"]) == find(d["v"]) for d in network["demands"]}
    return {"satisfied": all(satisfied.values()), "obligations": satisfied,
            "cost": str(exact_sum(Decimal(network["label_costs"][aid]) for aid in sorted(choices))),
            "selected": sorted(choices)}
