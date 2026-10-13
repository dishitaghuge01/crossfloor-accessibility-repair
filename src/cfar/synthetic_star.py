"""Controlled two-floor rational-coordinate witness family for the complexity memo."""
from __future__ import annotations

from .geometry import computed_adjacency


def rectangle(x1: float, y1: float, x2: float, y2: float) -> list[list[float]]:
    return [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]


def make_star_instance(elements: int, subsets: list[list[int]], costs: list[int | float]) -> dict:
    if elements < 1 or len(subsets) != len(costs):
        raise ValueError("positive element count and one cost per subset required")
    if any(i < 0 or i >= elements for subset in subsets for i in subset):
        raise ValueError("subset element outside universe")
    width=2*elements
    def room(rid: str, shape: list) -> dict:
        return {"room_id":rid,"label":rid,"polygon":shape}
    def landing(rid: str, shape: list) -> dict:
        return {"room_id":rid,"polygon":shape}
    floor0={"floor_id":"F0","elevation_m":0,"boundary":rectangle(0,0,width,4),
            "rooms":[room("S",rectangle(0,0,width,4))],"adjacency_edges":[],"access_edges":[],
            "obstacles":[],"reserved_portal_zones":[rectangle(0,0,2,2)]}
    floor1={"floor_id":"F1","elevation_m":3,"boundary":rectangle(0,0,width,4),
            "rooms":[room("C",rectangle(0,0,width,2))]+[room(f"T{i}",rectangle(2*i,2,2*i+2,4)) for i in range(elements)],
            "adjacency_edges":[],"access_edges":[],"obstacles":[],"reserved_portal_zones":[rectangle(0,0,2,2)]}
    floor1["adjacency_edges"]=[list(edge) for edge in sorted(computed_adjacency(floor1))]
    footprint=rectangle(0.25,0.25,1.25,1.25)
    connections=[{"connection_id":"P","evidence_id":"eP","u":"S","v":"C","kind":"lift",
                  "existing":True,"physical_profiles":["controlled"],
                  "geometry":{"asset_id":"shaft","width_m":1,"rise_m":3,"run_m":1,
                              "landings":[landing("S",footprint),landing("C",footprint)],
                              "footprints":[landing("S",footprint),landing("C",footprint)]}}]
    for i in range(elements):
        x=2*i+0.5
        connections.append({"connection_id":f"D{i}","evidence_id":f"eD{i}","u":"C","v":f"T{i}","kind":"door",
                            "existing":True,"physical_profiles":["controlled"],
                            "geometry":{"width_m":1,"opening":[[x,2],[x+1,2]],
                                        "landings":[landing("C",rectangle(x,1,x+1,2)),landing(f"T{i}",rectangle(x,2,x+1,3))]}})
    actions=[]
    for j,(subset,cost) in enumerate(zip(subsets,costs)):
        # Empty coverage gets an idempotent activation inside the already connected root component.
        cids=[f"D{i}" for i in sorted(set(subset))] or ["P"]
        actions.append({"action_id":f"A{j:03d}","type":"representation_correction","cost":cost,
                        "effects":[{"op":"activate_connection","connection_id":cid,"permitted_profiles":["controlled"]} for cid in cids],
                        "evidence_ids":["e"+cid for cid in cids],"requires":[],"excludes":[]})
    return {"schema_version":"0.1.0","building_id":f"controlled-star-{elements}-{len(subsets)}",
            "description":"Controlled coverage witness; profile dimensions are experimental parameters, not building standards.",
            "profiles":[{"profile_id":"controlled","min_width_m":0.4,"clearance_m":0.4,"can_use_stairs":True,"max_slope":0.5}],
            "floors":[floor0,floor1],"connections":connections,
            "portals":[{"portal_id":"P","kind":"lift","transitions":[{"connection_id":"P","permitted_profiles":["controlled"]}]}],
            "obligations":[{"obligation_id":f"O{i}","source":"S","target":f"T{i}","profile_id":"controlled"} for i in range(elements)],
            "actions":actions,"original_restoration_actions":[]}
