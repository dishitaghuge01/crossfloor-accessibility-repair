"""Controlled cross-floor chain family with shared-cost multi-profile bundles."""
from __future__ import annotations

from copy import deepcopy

from .synthetic_star import make_star_instance, rectangle


def make_chain_instance(elements: int, bundles: list[list[tuple[int, str]]],
                        costs: list[int | float], profiles: int = 2) -> dict:
    if profiles < 1 or len(bundles) != len(costs):
        raise ValueError("positive profile count and one cost per bundle required")
    pids = [f"profile{i}" for i in range(profiles)]
    if any(edge < 0 or edge >= elements or pid not in pids for b in bundles for edge, pid in b):
        raise ValueError("unknown chain edge or profile")
    instance = make_star_instance(elements, [], [])
    template = instance["profiles"][0]
    instance["profiles"] = [dict(template, profile_id=pid) for pid in pids]
    instance["building_id"] = f"controlled-chain-{elements}-{profiles}-{len(bundles)}"
    instance["description"] = "Controlled cross-floor chain with profile-specific activation bundles; no building-standard claim."
    instance["portals"][0]["transitions"][0]["permitted_profiles"] = pids[:]
    for connection in instance["connections"]:
        connection["physical_profiles"] = pids[:]
    for i in range(1, elements):
        c = instance["connections"][i+1]
        x = 2*i
        c["u"], c["v"] = f"T{i-1}", f"T{i}"
        c["geometry"] = {"width_m": 1, "opening": [[x, 2.5], [x, 3.5]],
                         "landings": [{"room_id": c["u"], "polygon": rectangle(x-1, 2.5, x, 3.5)},
                                      {"room_id": c["v"], "polygon": rectangle(x, 2.5, x+1, 3.5)}]}
    instance["obligations"] = [{"obligation_id": f"O{pi}", "source": "S", "target": f"T{elements-1}",
                                "profile_id": pid} for pi, pid in enumerate(pids)]
    actions = []
    for i, (bundle, cost) in enumerate(zip(bundles, costs)):
        by_edge = {}
        for edge, pid in bundle:
            by_edge.setdefault(edge, set()).add(pid)
        effects = [{"op": "activate_connection", "connection_id": f"D{edge}",
                    "permitted_profiles": sorted(permitted)} for edge, permitted in sorted(by_edge.items())]
        if not effects:
            effects = [{"op": "activate_connection", "connection_id": "P", "permitted_profiles": pids[:]}]
        actions.append({"action_id": f"A{i:03d}", "type": "representation_correction", "cost": cost,
                        "effects": effects, "evidence_ids": ["e"+e["connection_id"] for e in effects],
                        "requires": [], "excludes": []})
    instance["actions"] = actions
    return deepcopy(instance)
