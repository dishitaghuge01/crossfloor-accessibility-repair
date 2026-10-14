"""Audit an IFC without fabricating accessibility permissions or reservations."""
import argparse
import hashlib
import importlib.metadata
from pathlib import Path
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
from shapely.geometry import Polygon
from shapely.ops import unary_union
from cfar.io import write_json

EXPECTED_SHA256 = 'b347a2c8aa8fff6db896a4417a9c50c22ac0ccd7c5cfc22b99b8d29336c606ed'
SOURCE = 'https://github.com/buildingsmart-community/Community-Sample-Test-Files/tree/main/IFC%202.3.0.1%20(IFC%202x3)/Duplex%20Apartment'


def audit(source, output):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError('source bytes differ from audited Duplex architectural release')
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('choose a new empty output directory')
    model = ifcopenshell.open(str(source))
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    spaces = []
    geometries = {}
    for space in model.by_type('IfcSpace'):
        parent = ifcopenshell.util.element.get_aggregate(space)
        row = dict(global_id=space.GlobalId, step_id=space.id(), name=space.Name,
            long_name=space.LongName, storey_id=parent.GlobalId if parent else None)
        try:
            shape = ifcopenshell.geom.create_shape(settings, space)
            v, f = shape.geometry.verts, shape.geometry.faces
            vertices = [v[i:i+3] for i in range(0, len(v), 3)]
            triangles = [Polygon([vertices[f[i+j]][:2] for j in range(3)]) for i in range(0, len(f), 3)]
            polygon = unary_union([p for p in triangles if p.area > 1e-10])
            row.update(projected_area=polygon.area, projected_type=polygon.geom_type)
            if polygon.geom_type == 'Polygon':
                row['projected_exterior'] = list(polygon.exterior.coords)
                row['projected_holes'] = [list(r.coords) for r in polygon.interiors]
                geometries[space.GlobalId] = polygon
        except Exception as error:
            row['geometry_error'] = str(error)
        spaces.append(row)
    overlaps = []
    for i, a in enumerate(spaces):
        for b in spaces[i+1:]:
            if a['storey_id'] != b['storey_id'] or a['global_id'] not in geometries or b['global_id'] not in geometries:
                continue
            area = geometries[a['global_id']].intersection(geometries[b['global_id']]).area
            if area > 1e-8:
                overlaps.append(dict(a=a['global_id'], b=b['global_id'], area=area))
    background = [dict(global_id=e.GlobalId, step_id=e.id(), type=e.is_a(), name=e.Name)
        for kind in ('IfcStair', 'IfcTransportElement') for e in model.by_type(kind)]
    for record in background:
        entity = model.by_id(record['step_id'])
        parts = [entity] if entity.Representation else list(ifcopenshell.util.element.get_decomposition(entity))
        vertices = []
        for part in parts:
            if not part.Representation:
                continue
            shape = ifcopenshell.geom.create_shape(settings, part)
            raw = shape.geometry.verts
            vertices.extend(raw[i:i+3] for i in range(0, len(raw), 3))
        if not vertices:
            raise ValueError('unmapped physical background: ' + entity.GlobalId)
        record['conservative_xy_bounds'] = [min(v[0] for v in vertices), min(v[1] for v in vertices),
            max(v[0] for v in vertices), max(v[1] for v in vertices)]
        record['z_bounds'] = [min(v[2] for v in vertices), max(v[2] for v in vertices)]
    boundaries = [dict(step_id=e.id(), space=e.RelatingSpace.GlobalId,
        element=e.RelatedBuildingElement.GlobalId if e.RelatedBuildingElement else None,
        physical_or_virtual=e.PhysicalOrVirtualBoundary, internal_or_external=e.InternalOrExternalBoundary)
        for e in model.by_type('IfcRelSpaceBoundary')]
    provenance = dict(source_url=SOURCE, sha256=digest, license='CC BY 4.0',
        attribution='BSI (2020) "Duplex Apartment Test Files," buildingSMART International',
        changes='Read-only IFC inventory and mesh XY projections; no source changes, no solver input adaptation.',
        ifcopenshell=importlib.metadata.version('ifcopenshell'), runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    result = dict(status='evidence-incomplete', spaces=len(spaces), same_storey_projected_overlaps=len(overlaps),
        stairs=len(model.by_type('IfcStair')), transport_elements=len(model.by_type('IfcTransportElement')),
        missing=['authenticated profile permissions', 'candidate reserved vertical envelopes', 'candidate fixed physical templates and costs',
            'physical-background-to-kernel mapping', 'reviewed nonoverlapping room subset and floor boundaries'],
        conclusion='No main-solver repair instance is asserted from this source. Presence and geometric boundary relations do not establish traversal or reservation.')
    for name, value in [('provenance', provenance), ('spaces', spaces), ('background', background),
        ('space-boundaries', boundaries), ('overlaps', overlaps), ('assessment', result)]:
        write_json(output/f'{name}.json', value)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(audit(args.source, args.output))
