"""Controlled frozen-floor shaft bundles; dimensions are experimental, not codes."""
from __future__ import annotations

from .synthetic_star import rectangle


def make_shaft_instance(edges: int, intervals: list[tuple[int, int, int]], costs: list[int | float],
                        profiles: int = 2, *, physical: bool = False, conflict_witness: bool = False,
                        asset_groups: list[int] | None = None) -> dict:
    if edges < 1 or profiles < 1 or len(intervals) != len(costs):
        raise ValueError("positive sizes and matching interval costs required")
    if any(not (0 <= l <= r < edges and 1 <= h <= profiles) for l, r, h in intervals):
        raise ValueError("invalid interval or profile height")
    if conflict_witness and (edges != 3 or profiles != 2 or intervals != [(0,1,2),(1,2,1),(0,2,2)]):
        raise ValueError("fixed four-floor witness requires its declared intervals")
    if conflict_witness and not physical:
        raise ValueError("overlapping alternatives must be proposed physical interventions")
    if asset_groups is not None and (conflict_witness or not physical or len(asset_groups) != len(intervals)
                                    or any(type(g) is not int or not 0 <= g < 8 for g in asset_groups)):
        raise ValueError("asset groups require matching physical alternatives in groups 0 through 7")
    pids = [f"profile{i}" for i in range(profiles)]
    floors = [{"floor_id": f"F{i}", "elevation_m": 3*i, "boundary": rectangle(0,0,4,4),
               "rooms": [{"room_id": f"R{i}", "label": f"R{i}", "polygon": rectangle(0,0,4,4)}],
               "adjacency_edges": [], "access_edges": [], "obstacles": [],
               "reserved_portal_zones": [rectangle(0,0,4,4)]} for i in range(edges+1)]
    connections, actions = [], []
    # Ordinary runs reuse one fixed asset; the conflict witness gives each action its own proposed asset.
    def connection(cid, edge, asset, footprint):
        landings = [{"room_id": f"R{i}", "polygon": footprint} for i in (edge, edge+1)]
        return {"connection_id": cid, "evidence_id": "e"+cid, "u": f"R{edge}", "v": f"R{edge+1}",
                "kind": "lift", "existing": not physical, "physical_profiles": pids[:],
                "geometry": {"asset_id": asset, "width_m": 1, "rise_m": 3, "run_m": 1,
                             "landings": landings, "footprints": landings}}
    if asset_groups is not None:
        pairs = {(group, edge) for group, (left, right, _) in zip(asset_groups, intervals)
                 for edge in range(left, right+1)}
        for group, edge in sorted(pairs):
            slot = group % 4
            x, y = .5+2*(slot % 2), .5+2*(slot // 2)
            connections.append(connection(f"G{group}P{edge}", edge, f"asset-group-{group}", rectangle(x,y,x+1,y+1)))
    elif not conflict_witness:
        connections = [connection(f"P{i}", i, "shaft", rectangle(.5,.5,1.5,1.5)) for i in range(edges)]
    for i, ((left, right, height), cost) in enumerate(zip(intervals, costs)):
        if asset_groups is not None:
            cids = [f"G{asset_groups[i]}P{edge}" for edge in range(left, right+1)]
        elif conflict_witness:
            footprint = rectangle(2.5,2.5,3.5,3.5) if i == 2 else rectangle(.5,.5,1.5,1.5)
            cids = [f"A{i}P{edge}" for edge in range(left, right+1)]
            connections.extend(connection(cid, edge, f"asset{i}", footprint)
                               for cid, edge in zip(cids, range(left, right+1)))
        else:
            cids = [f"P{edge}" for edge in range(left, right+1)]
        action = {"action_id": f"A{i:03d}", "type": "physical_intervention" if physical else "representation_correction",
                  "cost": cost, "effects": [{"op": "activate_connection", "connection_id": cid,
                                             "permitted_profiles": pids[:height]} for cid in cids],
                  "requires": [], "excludes": [], "evidence_ids": ["e"+cid for cid in cids]}
        if physical:
            action["geometry_certificate"] = {"geometry_model": "reserved_interfaces_2d_v1",
                                               "connection_ids": cids, "changed_floor_ids": []}
        actions.append(action)
    obligations = [{"obligation_id": f"O{i}", "source": "R0", "target": f"R{edges}", "profile_id": pid}
                   for i, pid in enumerate(pids)]
    if conflict_witness:
        obligations[1]["target"] = "R1"
    return {"schema_version": "0.1.0", "building_id": f"controlled-shaft-{edges}-{len(intervals)}",
            "description": "Controlled shaft-span evidence; experimental geometry and profiles, no construction-safety claim.",
            "profiles": [{"profile_id": pid, "min_width_m": .4, "clearance_m": .4,
                          "can_use_stairs": True, "max_slope": .5} for pid in pids],
            "floors": floors, "connections": connections, "portals": [], "obligations": obligations,
            "actions": actions, "original_restoration_actions": []}
