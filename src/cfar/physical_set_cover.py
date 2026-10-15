"""Executable two-floor physical witness for the Set Cover hardness boundary.

Each incidence owns a separate reserved lift footprint. This standard reduction
clarifies scope; it is not a new hardness technique or realistic renovation.
"""
from .synthetic_star import rectangle


def make_physical_set_cover(elements, subsets):
    if elements < 1 or any(not s or len(s) != len(set(s)) or
                           any(type(e) is not int or not 0 <= e < elements for e in s) for s in subsets):
        raise ValueError("nonempty duplicate-free subsets of the positive universe required")
    incidence = {e: [i for i, s in enumerate(subsets) if e in s] for e in range(elements)}
    width = 2 * (sum(len(v) for v in incidence.values()) + elements)
    floors = [dict(floor_id=f"F{i}", elevation_m=3*i, boundary=rectangle(0, 0, width, 3),
                   rooms=[], adjacency_edges=[], access_edges=[], obstacles=[], reserved_portal_zones=[])
              for i in range(2)]
    floors[0]["rooms"] = [dict(room_id="S", label="S", polygon=rectangle(0, 0, width, 3))]
    connections, effects = [], {i: [] for i in range(len(subsets))}
    cursor = 0
    for e in range(elements):
        end = cursor + 2*(len(incidence[e])+1)
        floors[1]["rooms"].append(dict(room_id=f"T{e}", label=f"T{e}", polygon=rectangle(cursor, 0, end-1, 3)))
        for offset, i in enumerate(incidence[e]):
            footprint = rectangle(cursor+2*offset+.5, .5, cursor+2*offset+1.5, 1.5)
            cid = f"P{i}-{e}"
            records = [dict(room_id=rid, polygon=footprint) for rid in ("S", f"T{e}")]
            connections.append(dict(connection_id=cid, evidence_id="e"+cid, u="S", v=f"T{e}",
                kind="lift", existing=False, physical_profiles=["controlled"],
                geometry=dict(asset_id="asset-"+cid, width_m=1, rise_m=3, run_m=1,
                              landings=records, footprints=records)))
            for floor in floors:
                floor["reserved_portal_zones"].append(footprint)
            effects[i].append(dict(op="activate_connection", connection_id=cid, permitted_profiles=["controlled"]))
        cursor = end
    actions = []
    for i in range(len(subsets)):
        cids = [e["connection_id"] for e in effects[i]]
        actions.append(dict(action_id=f"A{i:03d}", type="physical_intervention", cost=1,
            effects=effects[i], requires=[], excludes=[], evidence_ids=["e"+cid for cid in cids],
            geometry_certificate=dict(geometry_model="reserved_interfaces_2d_v1", connection_ids=cids, changed_floor_ids=[])))
    return dict(schema_version="0.1.0", building_id="physical-set-cover-witness",
        description="Standard Set Cover reduction using physical portal bundles; no construction claim.",
        floors=floors, profiles=[dict(profile_id="controlled", min_width_m=.4, clearance_m=.4,
                                    can_use_stairs=False, max_slope=.1)],
        connections=connections, portals=[], actions=actions,
        obligations=[dict(obligation_id=f"O{e}", source="S", target=f"T{e}", profile_id="controlled")
                     for e in range(elements)], original_restoration_actions=[])
