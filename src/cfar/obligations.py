from __future__ import annotations

from collections import deque

from .graphs import Graph, build_profile_graph
from .schema import Instance


def shortest_profile_path(graph: Graph, source: str, target: str) -> list[str] | None:
    parents: dict[str, str | None] = {source: None}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        if u == target:
            path = [u]
            while parents[path[-1]] is not None:
                path.append(parents[path[-1]])
            return path[::-1]
        for v in sorted(graph[u]):
            if v not in parents:
                parents[v] = u
                queue.append(v)
    return None


def verify_obligations(instance: Instance, active: dict | None = None) -> dict:
    graphs = {p["profile_id"]: build_profile_graph(instance, p["profile_id"], active) for p in instance["profiles"]}
    paths = {o["obligation_id"]: shortest_profile_path(graphs[o["profile_id"]], o["source"], o["target"])
             for o in instance["obligations"]}
    return {"satisfied": all(path is not None for path in paths.values()), "paths": paths}
