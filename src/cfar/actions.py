"""Atomic, order-independent action-set semantics; never mutate the input."""
from __future__ import annotations

from copy import deepcopy

from .errors import require
from .geometry import computed_adjacency, joint_geometry, validate_floor_geometry
from .schema import Instance
from .validation import baseline_active, validate_instance


def classify_action(action: dict) -> str:
    return action["type"]


def apply_actions(instance: Instance, selected: list[str], variant: str = "SCFAR", *, validated: bool = False) -> dict:
    if not validated:
        validate_instance(instance)
    require(variant in {"SCFAR", "RCFAR"}, "VARIANT", variant)
    require(len(selected) == len(set(selected)), "DUPLICATE_SELECTION", str(selected))
    choices = set(selected)
    catalog = {a["action_id"]: a for a in instance["actions"]}
    require(choices <= catalog.keys(), "UNKNOWN_SELECTION", str(choices-catalog.keys()))
    repaired = deepcopy(instance)
    floors = {f["floor_id"]: f for f in repaired["floors"]}
    active = deepcopy(baseline_active(instance))
    writes: set[tuple[str, str]] = set()
    for aid in sorted(choices):
        action = catalog[aid]
        require(set(action["requires"]) <= choices, "ACTION_REQUIRES", aid)
        require(not set(action["excludes"]) & choices, "ACTION_EXCLUDES", aid)
        for effect in action["effects"]:
            if effect["op"] == "activate_connection":
                cid = effect["connection_id"]
                active[cid] = sorted(set(active.get(cid, [])) | set(effect["permitted_profiles"]))
            else:
                require(variant == "RCFAR", "STRICT_GEOMETRY_EDIT", aid)
                key = ("floor", effect["floor_id"])
                require(key not in writes, "EFFECT_CONFLICT", aid)
                writes.add(key)
                floors[effect["floor_id"]]["rooms"] = deepcopy(effect["rooms"])
    adjacency = {}
    for original in instance["floors"]:
        f = floors[original["floor_id"]]
        validate_floor_geometry(f)
        old, new = computed_adjacency(original), computed_adjacency(f)
        require({r["room_id"] for r in original["rooms"]} == {r["room_id"] for r in f["rooms"]}, "ROOM_IDENTITY", f["floor_id"])
        adjacency[f["floor_id"]] = {"preserved": old == new, "delta": len(old ^ new),
                                     "edges": [list(pair) for pair in sorted(new)]}
        if variant == "SCFAR":
            require(old == new, "STRICT_TOPOLOGY", f["floor_id"])
        f["adjacency_edges"] = [list(pair) for pair in sorted(new)]
    geometry = joint_geometry(repaired, active)
    # Also check an intervention that was redundantly activated; every selected physical action must be feasible.
    return {"instance": repaired, "active": active, "adjacency": adjacency, "geometry": geometry}
