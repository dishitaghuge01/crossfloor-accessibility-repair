"""Pinned public IFC inventory and deterministic, hypothetical repair subsets.

No inferred door connectivity, fabricated IFC portals or construction labels.
Every selected room retains its world-coordinate XY ring and GlobalId. Cases
are aligned two-storey subsets, not whole-building accessibility evaluations.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.metadata
import json
from math import ceil, floor
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from cfar.actions import apply_actions
from cfar.errors import ValidationError
from cfar.geometry import polygon
from cfar.interface_recognition import recognize_physical_interface
from cfar.io import fingerprint, write_json
from cfar.obligations import verify_obligations
from cfar.synthetic_star import rectangle


def mesh_projection(settings, entity):
    shape = ifcopenshell.geom.create_shape(settings, entity)
    raw, indices = shape.geometry.verts, shape.geometry.faces
    vertices = [raw[i:i+3] for i in range(0, len(raw), 3)]
    triangles = [Polygon([vertices[indices[i+j]][:2] for j in range(3)]) for i in range(0, len(indices), 3)]
    projected = unary_union([p for p in triangles if p.area > 1e-10])
    return projected, vertices


def inventory(source, provenance):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != provenance["sha256"]:
        raise ValueError("source fingerprint mismatch")
    model = ifcopenshell.open(str(source))
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    spaces, background = [], []
    for space in sorted(model.by_type("IfcSpace"), key=lambda e: e.GlobalId):
        parent = ifcopenshell.util.element.get_aggregate(space)
        while parent is not None and not parent.is_a("IfcBuildingStorey"):
            parent = ifcopenshell.util.element.get_aggregate(parent)
        row = dict(global_id=space.GlobalId, name=space.Name or space.GlobalId,
                   storey_id=parent.GlobalId if parent else None)
        try:
            shape, vertices = mesh_projection(settings, space)
            row.update(area=shape.area, geometry_type=shape.geom_type,
                       z_min=min(v[2] for v in vertices), z_max=max(v[2] for v in vertices))
            if shape.geom_type != "Polygon" or shape.interiors or parent is None:
                raise ValueError("non-simple polygon, holes or missing storey")
            row["polygon"] = [list(v) for v in shape.exterior.coords]
            polygon(row["polygon"])
            row["eligible"] = True
        except (ValueError, RuntimeError, ValidationError) as e:
            row.update(eligible=False, exclusion=str(e))
        spaces.append(row)
    for kind in ("IfcStair", "IfcTransportElement"):
        for entity in sorted(model.by_type(kind), key=lambda e: e.GlobalId):
            row = dict(global_id=entity.GlobalId, kind=kind)
            try:
                parts = [entity] if entity.Representation else ifcopenshell.util.element.get_decomposition(entity)
                vertices = []
                for part in parts:
                    if part.Representation:
                        _, points = mesh_projection(settings, part)
                        vertices.extend(points)
                if not vertices:
                    raise ValueError("physical background has no mesh")
                row["bounds"] = [min(p[0] for p in vertices), min(p[1] for p in vertices),
                                 max(p[0] for p in vertices), max(p[1] for p in vertices)]
            except (ValueError, RuntimeError) as e:
                row["error"] = str(e)
            background.append(row)
    return dict(provenance=provenance, spaces=spaces, background=background,
                counts=dict(storeys=len(model.by_type("IfcBuildingStorey")), spaces=len(spaces),
                            eligible_spaces=sum(s["eligible"] for s in spaces),
                            stairs=len(model.by_type("IfcStair")), transport=len(model.by_type("IfcTransportElement"))))


def make_reference(audit, pair):
    first, second = pair
    obstacles = [rectangle(*b["bounds"]) for b in audit["background"]]
    shapes = [polygon(r["polygon"]) for r in pair]
    common = shapes[0].intersection(shapes[1]).difference(unary_union([box(*b["bounds"]) for b in audit["background"]]))
    min_x, min_y, max_x, max_y = common.bounds
    slots = []
    # Fixed 0.8m grid, independent of solver answers; retain first two legal squares.
    for ix in range(ceil(min_x/.8), floor((max_x-.7)/.8)+1):
        for iy in range(ceil(min_y/.8), floor((max_y-.7)/.8)+1):
            shape = box(.8*ix, .8*iy, .8*ix+.7, .8*iy+.7)
            if common.covers(shape):
                slots.append([list(v) for v in shape.exterior.coords])
                if len(slots) == 2:
                    break
        if len(slots) == 2:
            break
    if len(slots) != 2:
        raise ValueError("fewer than two clear fixed-grid 0.7m slots")
    bounds = unary_union(shapes + [box(*b["bounds"]) for b in audit["background"]]).bounds
    boundary = rectangle(bounds[0]-1, bounds[1]-1, bounds[2]+1, bounds[3]+1)
    pids = ["experimental0", "experimental1"]
    floors = [dict(floor_id=r["storey_id"], elevation_m=r["z_min"], boundary=boundary,
        rooms=[dict(room_id=r["global_id"], label=r["name"], polygon=r["polygon"])],
        adjacency_edges=[], access_edges=[], obstacles=obstacles, reserved_portal_zones=slots) for r in pair]
    ids = [r["global_id"] for r in pair]
    connections = []
    for i, slot in enumerate(slots):
        records = [dict(room_id=rid, polygon=slot) for rid in ids]
        connections.append(dict(connection_id=f"X{i}", evidence_id=f"hypothetical-X{i}",
            u=ids[0], v=ids[1], kind="lift", existing=False, physical_profiles=pids,
            geometry=dict(asset_id=f"hypothetical-owner{i}", width_m=.7,
                          rise_m=second["z_min"]-first["z_min"], run_m=1, landings=records, footprints=records)))
    actions = []
    for aid, cost, effects in [("A",3,[("X0",pids[:1]),("X1",pids[1:])]),
                              ("B",2,[("X0",pids[:1])]),("C",2,[("X1",pids[1:])]),("D",4,[("X0",pids)])]:
        cids = [cid for cid, _ in effects]
        actions.append(dict(action_id=aid, type="physical_intervention", cost=cost,
            effects=[dict(op="activate_connection", connection_id=cid, permitted_profiles=ps) for cid,ps in effects],
            requires=[], excludes=[], evidence_ids=["hypothetical-"+cid for cid in cids],
            geometry_certificate=dict(geometry_model="reserved_interfaces_2d_v1", connection_ids=cids, changed_floor_ids=[])))
    instance = dict(schema_version="0.1.0", building_id=audit["provenance"]["building"]+"-controlled-subset",
        description="Two-room world-coordinate IFC subset; hypothetical profile, lift reservations, prices and permissions; no whole-building or construction claim.",
        profiles=[dict(profile_id=pid, min_width_m=w, clearance_m=w, can_use_stairs=False, max_slope=.1)
                  for pid,w in zip(pids,(.4,.5))], floors=floors, connections=connections, actions=actions, portals=[],
        obligations=[dict(obligation_id=f"O{i}", source=ids[0], target=ids[1], profile_id=pid) for i,pid in enumerate(pids)],
        original_restoration_actions=[])
    recognize_physical_interface(instance)
    reference = apply_actions(instance, ["D"])
    if not verify_obligations(reference["instance"], reference["active"])["satisfied"]:
        raise ValueError("reference failed declared obligations")
    return instance


def select_reference(audit):
    if any("error" in b for b in audit["background"]):
        raise ValueError("unmapped physical background; no controlled instance admitted")
    eligible = [s for s in audit["spaces"] if s["eligible"]]
    pairs = []
    for first in eligible:
        for second in eligible:
            if first["storey_id"] == second["storey_id"] or second["z_min"]-first["z_min"] <= .1:
                continue
            common = polygon(first["polygon"]).intersection(polygon(second["polygon"]))
            if common.area > 1:
                pairs.append((-common.area, first["global_id"], second["global_id"], first, second))
    rejections = []
    for _, _, _, first, second in sorted(pairs):
        try:
            return make_reference(audit, (first,second)), rejections
        except (ValueError, ValidationError) as e:
            rejections.append(dict(rooms=[first["global_id"],second["global_id"]], reason=str(e)))
    raise ValueError("no recognized aligned subset; candidates="+str(len(pairs))+" rejected="+str(len(rejections)))


def build(source_directory, output):
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("fresh empty output required")
    summary = []
    for metadata in sorted(source_directory.glob("*.source.json")):
        provenance = json.loads(metadata.read_text())
        name = provenance["building"]
        audit = inventory(source_directory/(name+".ifc"), provenance)
        write_json(output/"audits"/(name+".json"), audit)
        row = dict(building=name, counts=audit["counts"], sha256=provenance["sha256"], seed=0)
        try:
            reference, rejections = select_reference(audit)
            materialized_reference = apply_actions(reference, ["D"])
            write_json(output/"audits"/(name+"-reference.json"), dict(selected=["D"],
                active=materialized_reference["active"], geometry=materialized_reference["geometry"],
                reachability=verify_obligations(materialized_reference["instance"], materialized_reference["active"]),
                label="hypothetical feasible reference, not original IFC portal truth or optimum"))
            write_json(output/"audits"/(name+"-selection.json"), dict(rejections=rejections,
                selected_rooms=[f["rooms"][0]["room_id"] for f in reference["floors"]],
                reference_fingerprint=fingerprint(reference), reference_selected=["D"],
                corrupted_reference="D's profile-valid links removed; rooms and background unchanged"))
            variants = {"bundle": reference, "separate": deepcopy(reference),
                        "infeasible": deepcopy(reference), "single": deepcopy(reference)}
            variants["separate"]["actions"][0]["cost"] = 5
            variants["separate"]["actions"] = variants["separate"]["actions"][:3]
            variants["infeasible"]["actions"] = [variants["infeasible"]["actions"][1]]
            variants["single"]["actions"] = [variants["single"]["actions"][3]]
            for kind, instance in variants.items():
                recognize_physical_interface(instance)
                write_json(output/"instances"/f"{name}-{kind}.json", instance)
            row.update(status="controlled-subset-admitted", variants=4,
                       omitted_spaces=audit["counts"]["spaces"]-2,
                       contract="one original room per floor; empty per-floor adjacency; experimental profiles/reservations/costs")
        except (ValueError, ValidationError) as e:
            row.update(status="unsupported-source", reason=str(e))
        summary.append(row)
        write_json(output/"summary.json", summary)
        print(name, row["status"], audit["counts"], flush=True)
    write_json(output/"provenance.json", dict(runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        ifcopenshell=importlib.metadata.version("ifcopenshell"), seed=0, sources=[r["sha256"] for r in summary],
        changes="world-coordinate XY mesh projection; deterministic eligibility and subsets; conservative stair/lift XY obstacles on both floors; declared hypothetical reference and action catalogues"))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    build(args.sources, args.output)
