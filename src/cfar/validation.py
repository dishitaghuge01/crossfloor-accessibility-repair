"""Semantic checks. Bad candidates may be well-formed but geometrically infeasible."""
from __future__ import annotations

from collections.abc import Iterable

from .errors import require
from .geometry import computed_adjacency, joint_geometry, polygon, room_index, validate_floor_geometry
from .schema import Instance, validate_schema


def unique(values: Iterable[str], name: str) -> None:
    values = list(values)
    require(len(values) == len(set(values)), "DUPLICATE_ID", name)


def baseline_active(instance: Instance) -> dict[str, list[str]]:
    records = [edge for f in instance["floors"] for edge in f["access_edges"]]
    records += [t for p in instance["portals"] for t in p["transitions"]]
    unique((x["connection_id"] for x in records), "active connections")
    return {r["connection_id"]: r["permitted_profiles"] for r in records}


def validate_action_evidence(instance: Instance, action: dict) -> None:
    catalog = {c["connection_id"]: c for c in instance["connections"]}
    activate = [e for e in action["effects"] if e["op"] == "activate_connection"]
    reshapes = [e for e in action["effects"] if e["op"] == "replace_floor_rooms"]
    aid = action["action_id"]
    unique((e["connection_id"] for e in activate), f"effects/{aid}")
    unique((e["floor_id"] for e in reshapes), f"reshapes/{aid}")
    require(set(action["evidence_ids"]) == {catalog[e["connection_id"]]["evidence_id"] for e in activate},
            "ACTION_EVIDENCE", aid)
    if action["type"] == "representation_correction":
        require(not reshapes and all(catalog[e["connection_id"]]["existing"] for e in activate),
                "CORRECTION_INVENTS_ROUTE", aid)
    else:
        require(all(not catalog[e["connection_id"]]["existing"] for e in activate),
                "INTERVENTION_EXISTING_EVIDENCE", aid)
        cert = action["geometry_certificate"]
        require(set(cert["connection_ids"]) == {e["connection_id"] for e in activate}
                and set(cert["changed_floor_ids"]) == {e["floor_id"] for e in reshapes},
                "CERTIFICATE_SCOPE", aid)


def validate_instance(instance: Instance) -> None:
    validate_schema(instance)
    for key, id_key in (("floors","floor_id"),("profiles","profile_id"),("connections","connection_id"),
                        ("actions","action_id"),("obligations","obligation_id"),("portals","portal_id")):
        unique((x[id_key] for x in instance[key]), key)
    unique((r["room_id"] for f in instance["floors"] for r in f["rooms"]), "rooms")
    unique((c["evidence_id"] for c in instance["connections"]), "evidence")
    unique((e["edge_id"] for f in instance["floors"] for e in f["access_edges"]), "edges")
    rooms = room_index(instance)
    floors = {f["floor_id"]: f for f in instance["floors"]}
    profiles = {p["profile_id"] for p in instance["profiles"]}
    catalog = {c["connection_id"]: c for c in instance["connections"]}
    actions = {a["action_id"] for a in instance["actions"]}
    for f in instance["floors"]:
        validate_floor_geometry(f)
        declared = {tuple(sorted(pair)) for pair in f["adjacency_edges"]}
        require(len(declared) == len(f["adjacency_edges"]) and declared == computed_adjacency(f),
                "ADJACENCY_GEOMETRY", f["floor_id"])
    for c in instance["connections"]:
        require(c["u"] in rooms and c["v"] in rooms and c["u"] != c["v"], "CONNECTION_ENDPOINT", c["connection_id"])
        require(set(c["physical_profiles"]) <= profiles, "UNKNOWN_PROFILE", c["connection_id"])
        for landing in c["geometry"]["landings"]:
            require(landing["room_id"] in rooms, "LANDING_ROOM", c["connection_id"])
            polygon(landing["polygon"])
        for footprint in c["geometry"].get("footprints", []):
            require(footprint["room_id"] in rooms, "FOOTPRINT_ROOM", c["connection_id"])
            polygon(footprint["polygon"])
    assets = {}
    for c in instance["connections"]:
        if c["kind"] == "door":
            continue
        geom = c["geometry"]
        shape = polygon(geom["footprints"][0]["polygon"])
        asset = geom["asset_id"]
        signature = (c["kind"],geom["width_m"],set(c["physical_profiles"]))
        if asset in assets:
            old_signature, old_shape = assets[asset]
            require(signature == old_signature and shape.equals(old_shape), "ASSET_CONSISTENCY", asset)
        else:
            assets[asset] = (signature,shape)
    for f in instance["floors"]:
        for edge in f["access_edges"]:
            require(edge["connection_id"] in catalog, "UNKNOWN_CONNECTION", edge["edge_id"])
            c = catalog[edge["connection_id"]]
            require(c["kind"] == "door" and all(rooms[x][0]["floor_id"] == f["floor_id"] for x in (c["u"],c["v"])),
                    "ACCESS_EDGE_FLOOR", edge["edge_id"])
    for p in instance["portals"]:
        for transition in p["transitions"]:
            require(transition["connection_id"] in catalog, "UNKNOWN_CONNECTION", p["portal_id"])
            require(catalog[transition["connection_id"]]["kind"] == p["kind"], "PORTAL_KIND", p["portal_id"])
    active = baseline_active(instance)
    for cid, ps in active.items():
        require(catalog[cid]["existing"], "BASELINE_INVENTS_ROUTE", cid)
        require(set(ps) <= profiles, "UNKNOWN_PROFILE", cid)
    for obligation in instance["obligations"]:
        require(obligation["source"] in rooms and obligation["target"] in rooms, "OBLIGATION_ENDPOINT", obligation["obligation_id"])
        require(obligation["profile_id"] in profiles, "UNKNOWN_PROFILE", obligation["obligation_id"])
    joint_geometry(instance, active)
    require(set(instance["original_restoration_actions"]) <= actions, "UNKNOWN_RESTORATION_ACTION", "restoration")
    for action in instance["actions"]:
        aid = action["action_id"]
        require(set(action["requires"]+action["excludes"]) <= actions, "UNKNOWN_ACTION_REFERENCE", aid)
        require(aid not in action["requires"]+action["excludes"], "SELF_ACTION_REFERENCE", aid)
        require(not set(action["requires"]) & set(action["excludes"]), "ACTION_CONTRADICTION", aid)
        for effect in action["effects"]:
            if effect["op"] == "activate_connection":
                require(effect["connection_id"] in catalog, "UNKNOWN_CONNECTION", aid)
                require(set(effect["permitted_profiles"]) <= profiles, "UNKNOWN_PROFILE", aid)
                require(set(effect["permitted_profiles"]) <= set(catalog[effect["connection_id"]]["physical_profiles"]),
                        "PHYSICAL_PROFILE", aid)
            else:
                require(effect["floor_id"] in floors, "UNKNOWN_FLOOR", aid)
                unique((r["room_id"] for r in effect["rooms"]), f"new rooms/{aid}")
                require({r["room_id"] for r in effect["rooms"]} == {r["room_id"] for r in floors[effect["floor_id"]]["rooms"]},
                        "ROOM_IDENTITY", aid)
                for r in effect["rooms"]:
                    polygon(r["polygon"])
        validate_action_evidence(instance, action)
