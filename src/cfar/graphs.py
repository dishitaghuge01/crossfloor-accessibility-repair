from __future__ import annotations

from .geometry import computed_adjacency, room_index
from .errors import require
from .schema import Instance
from .validation import baseline_active

Graph = dict[str, set[str]]


def build_adjacency_graph(floor: dict) -> Graph:
    graph = {r["room_id"]: set() for r in floor["rooms"]}
    for u, v in computed_adjacency(floor):
        graph[u].add(v)
        graph[v].add(u)
    return graph


def build_profile_graph(instance: Instance, profile_id: str, active: dict | None = None) -> Graph:
    require(profile_id in {p["profile_id"] for p in instance["profiles"]},"UNKNOWN_PROFILE",profile_id)
    graph = {rid: set() for rid in room_index(instance)}
    catalog = {c["connection_id"]: c for c in instance["connections"]}
    for cid, permitted in (baseline_active(instance) if active is None else active).items():
        if profile_id in permitted:
            u, v = catalog[cid]["u"], catalog[cid]["v"]
            graph[u].add(v)
            graph[v].add(u)
    return graph


def build_access_graph(instance: Instance, floor_id: str, profile_id: str, active: dict | None = None) -> Graph:
    require(floor_id in {f["floor_id"] for f in instance["floors"]},"UNKNOWN_FLOOR",floor_id)
    ids = {rid for rid, (f, _) in room_index(instance).items() if f["floor_id"] == floor_id}
    building = build_profile_graph(instance, profile_id, active)
    return {rid: building[rid] & ids for rid in sorted(ids)}
