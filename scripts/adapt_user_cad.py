"""Pinned, manually annotated DWG subset; never infer intervention permission.

Input is the local source DWG plus its LibreDWG 0.14 JSON decoding. The DWG
and decoding stay outside Git. Source wall coordinates are preserved under
one rigid plan registration; door/window gap closure is documented annotation.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, box
from cfar.io import fingerprint, manifest, write_json
from cfar.synthetic_star import rectangle
from cfar.interface_recognition import recognize_physical_interface

SOURCE_SHA = '0399309c5d19218bad44329471745354098b28431548ccf9a1bff5bd8a779acc'


def flatten(document):
    objects = {o['handle'][-1]: o for o in document['OBJECTS'] if 'handle' in o}
    model = next(o for o in objects.values() if o.get('object') == 'BLOCK_HEADER'
                 and o.get('name') == '*Model_Space')
    result = []

    def visit(o, transform, path=(), instances=()):
        if o.get('invisible', 0):
            return
        kind = o.get('entity')
        handle = o.get('handle', [0])[-1]

        def point(value):
            return (transform @ np.array([value[0], value[1], 1.0]))[:2].tolist()

        if kind == 'INSERT':
            block_id = o['block_header'][-1]
            if block_id in path:
                raise ValueError('cyclic block reference')
            block = objects[block_id]
            if block.get('blkisxref'):
                raise ValueError('external block reference needs separate source')
            angle = o.get('rotation', 0)
            sx, sy = o.get('scale', [1, 1, 1])[:2]
            x, y = o['ins_pt'][:2]
            base = np.array(block.get('base_pt', [0, 0])[:2])
            matrix = np.array([[sx*math.cos(angle), -sy*math.sin(angle), x],
                               [sx*math.sin(angle), sy*math.cos(angle), y],
                               [0., 0., 1.]])
            matrix[:2, 2] -= matrix[:2, :2] @ base
            for ref in block.get('entities', []):
                visit(objects[ref[-1]], transform @ matrix, path+(block_id,), instances+(handle,))
            return
        row = dict(type=kind, handle=handle, block_path=list(path), insert_path=list(instances),
                   layer=objects.get(o.get('layer', [0])[-1], {}).get('name', '?'))
        if kind == 'LINE':
            row['points'] = [point(o['start']), point(o['end'])]
        elif kind == 'LWPOLYLINE':
            row.update(points=[point(p) for p in o['points']],
                       closed=bool(o.get('flag', 0) & 512), bulges=o.get('bulges', []))
        elif kind in {'TEXT', 'MTEXT'}:
            pos = o.get('ins_pt', o.get('insertion_pt'))
            if not pos:
                return
            row.update(point=point(pos), text=o.get('text', o.get('text_value', '')))
        else:
            return
        result.append(row)

    for ref in model['entities']:
        visit(objects[ref[-1]], np.eye(3))
    return result


def annotated_pair(flat):
    def one(handle):
        def in_group(r):
            points = r.get('points', [r.get('point', [])])
            return points and all(len(p) >= 2 and -125 < p[0] < -86 and 47 < p[1] < 165 for p in points)
        rows = [r for r in flat if r['handle'] == handle and in_group(r)]
        if len(rows) != 1:
            raise ValueError(f'ambiguous source anchor {handle}')
        return rows[0]

    # Inner faces and window-sill endpoints, selected by visual review, not
    # a generic room detector. Retain exact x/y; close source door/window gaps.
    top_upper = one(11222668)['points']
    top_lower = one(11222983)['points']
    translation = np.array(top_upper[0])-np.array(top_lower[0])
    if not np.allclose(np.array(top_lower)+translation, top_upper, atol=1e-7, rtol=0):
        raise ValueError('registration anchor endpoints disagree')
    # Endpoint x of the right-hand top-wall segment and inner bottom-wall y.
    rooms = []
    for floor, top_id, right_id, bottom_id, label_id in [
            ('lower', 11222983, 11222984, 11222929, 11250431),
            ('upper', 11222668, 11222669, 11222560, 11249846)]:
        left = one(top_id)['points'][0][0]
        right = one(right_id)['points'][1][0]
        top = one(top_id)['points'][0][1]
        bottom = one(bottom_id)['points'][0][1]
        ring = rectangle(left, bottom, right, top)
        if not (abs(right-left-5.7) < 1e-6 and abs(top-bottom-4.8) < 1e-6):
            raise ValueError('source inner faces disagree with dimensioned 5.700x4.800 label')
        label = one(label_id)['text']
        if '5.700 x 4.800' not in label:
            raise ValueError('dimension-label anchor changed')
        registered = [[x+(translation[0] if floor == 'lower' else 0),
                       y+(translation[1] if floor == 'lower' else 0)] for x, y in ring]
        rooms.append(dict(floor=floor, room_id=f'cad-{label_id}', source_label_handle=label_id,
                          boundary_handles=[top_id, right_id, bottom_id],
                          boundary_insert_paths=[one(h)['insert_path'] for h in [top_id,right_id,bottom_id]],
                          raw_ring=ring, registered_ring=registered,
                          manual_annotation='rectangular inner-face room; close door/window gaps; no wall-center dilation'))
    if not Polygon(rooms[0]['registered_ring']).equals_exact(Polygon(rooms[1]['registered_ring']), 1e-6):
        raise ValueError('registered room rings disagree')
    return rooms, translation.tolist()


def build(source, decoded, output):
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('wrong DWG source fingerprint')
    output.mkdir(parents=True, exist_ok=False)
    doc = json.loads(decoded.read_text(encoding='utf-8'))
    flat = flatten(doc)
    rooms, shift = annotated_pair(flat)
    # The plotted working group is explicitly separated from unrelated plans.
    selected = [r for r in flat if (r.get('point') and
                -125 < r['point'][0] < -86 and 47 < r['point'][1] < 165) or
                (r.get('points') and all(-125 < x < -86 and 47 < y < 165
                                         for x, y in r['points']))]
    write_json(output/'private-selected-source.json', selected)
    # Conservative background encloses the lift/stair cluster outside the
    # retained bedroom. It is carried on both floors, not treated as a new lift.
    background = rectangle(-118.5, 65.5, -110.5, 76.0)
    poly = Polygon(rooms[1]['registered_ring'])
    if poly.intersects(Polygon(background)):
        raise ValueError('background unexpectedly intersects selected room')
    minx, miny, maxx, maxy = poly.bounds
    slots = [rectangle(minx+.5, miny+.5, minx+1.7, miny+1.7),
             rectangle(minx+2.4, miny+.5, minx+3.6, miny+1.7)]
    if not all(poly.covers(Polygon(r)) for r in slots):
        raise ValueError('experimental slots leave source-derived room')
    pids = ['experimental-narrow', 'experimental-wide']
    column_records = []
    floors = []
    for i,r in enumerate(rooms):
        column_shapes = []
        yrange = (119,165) if r['floor']=='lower' else (47,96)
        for row in selected:
            if row['type']!='LWPOLYLINE' or not row.get('closed') or row.get('bulges') or 'column' not in row.get('layer','').lower():
                continue
            if not all(yrange[0]<y<yrange[1] for x,y in row['points']):
                continue
            points = [[x+(shift[0] if i==0 else 0),y+(shift[1] if i==0 else 0)] for x,y in row['points']]
            shape = Polygon(points)
            if not shape.is_valid or shape.area<=0:
                raise ValueError('invalid source column')
            column_shapes.append(rectangle(*shape.bounds))
            column_records.append(dict(floor=r['floor'],handle=row['handle'],insert_path=row['insert_path'],
                                       source_polygon=row['points'],registered_envelope=column_shapes[-1]))
        if not all(not Polygon(slot).intersects(Polygon(ob)) for slot in slots for ob in column_shapes):
            raise ValueError('slot intersects source column envelope')
        floors.append(dict(floor_id=r['floor'], elevation_m=i*3.6,
                   boundary=rectangle(-126,46,-85,98),
                   rooms=[dict(room_id=r['room_id'], label=f'anonymized {r["floor"]} room',
                               polygon=r['registered_ring'])],
                   adjacency_edges=[], access_edges=[], obstacles=[background]+column_shapes,
                   reserved_portal_zones=slots))
    connections = [dict(connection_id=f'X{i}', evidence_id=f'experimental-slot-{i}',
        u=rooms[0]['room_id'], v=rooms[1]['room_id'], kind='lift', existing=False,
        physical_profiles=pids, geometry=dict(asset_id=f'experimental-owner-{i}',
        width_m=1.0, rise_m=3.6, run_m=1,
        landings=[dict(room_id=r['room_id'], polygon=slot) for r in rooms],
        footprints=[dict(room_id=r['room_id'], polygon=slot) for r in rooms]))
        for i, slot in enumerate(slots)]
    actions = []
    for aid, cost, effects in [('A',3,[('X0',pids[:1]),('X1',pids[1:])]),
                               ('B',2,[('X0',pids[:1])]),('C',2,[('X1',pids[1:])]),
                               ('D',4,[('X0',pids)])]:
        ids = [cid for cid, _ in effects]
        actions.append(dict(action_id=aid, type='physical_intervention', cost=cost,
            effects=[dict(op='activate_connection', connection_id=cid, permitted_profiles=ps)
                     for cid, ps in effects], requires=[], excludes=[],
            evidence_ids=[f'experimental-slot-{cid[1:]}' for cid in ids], geometry_certificate=dict(
                geometry_model='reserved_interfaces_2d_v1', connection_ids=ids, changed_floor_ids=[])))
    instance = dict(schema_version='0.1.0', building_id='user-cad-working-pair',
        description='Manually reconstructed, dimension-checked CAD room pair; experimental profiles, floor rise, slots and abstract costs. Not an as-built/approved repair.',
        profiles=[dict(profile_id=p, min_width_m=w, clearance_m=w,
                       can_use_stairs=False, max_slope=.1) for p,w in zip(pids,[.8,1.0])],
        floors=floors, connections=connections, actions=actions, portals=[],
        obligations=[dict(obligation_id=f'O{i}', source=rooms[0]['room_id'],
                         target=rooms[1]['room_id'], profile_id=p) for i,p in enumerate(pids)],
        original_restoration_actions=[])
    variants = {name:deepcopy(instance) for name in ['bundle','separate','infeasible','single']}
    variants['separate']['actions'][0]['cost'] = 5
    variants['separate']['actions'] = variants['separate']['actions'][:3]
    variants['infeasible']['actions'] = [actions[1]]
    variants['single']['actions'] = [actions[3]]
    for name, a in variants.items():
        recognition = recognize_physical_interface(a)
        write_json(output/'instances'/f'{name}.json', a)
        write_json(output/'recognition'/f'{name}.json', recognition)
    evidence = dict(source_sha256=SOURCE_SHA, source_bytes=source.stat().st_size,
        decoder='GNU LibreDWG0.14 dwgread -O JSON; reported SUCCESS',
        source_header=doc['FILEHEADER'], source_INSUNITS=doc['HEADER'].get('INSUNITS'),
        units='local1unit=1metre from two independent5.700x4.800 inner-face/label checks; globalINSUNITS not trusted',
        permission='User explicitly authorized thesis research use2026-10-21; raw source redistribution not inferred',
        registration=dict(lower_to_upper_translation=shift, rotation=0, scale=1,
                          anchors=[11222668,11222983], method='align corresponding top-wall endpoints'),
        rooms=rooms, columns=column_records, background=dict(polygon=background, role='conservative lift/stair background envelope; outside retained bedroom; not measured shaft geometry'),
        assumptions=['manual door/window aperture closure defines room boundary',
                     'only two retained rooms; all other rooms/external circulation omitted; no whole-building reachability claim',
                     'experimental floor elevations0/3.6m; source lower-level sign not verified',
                     'experimental slots/profile permissions/costs; no candidate approval or construction feasibility',
                     'movable furniture not a structural obstacle in this controlled abstraction; no source clearance certification'],
        decoded_sha256=hashlib.sha256(decoded.read_bytes()).hexdigest(),
        adapter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        counts=dict(decoded_objects=len(doc['OBJECTS']), flattened_rows=len(flat), retained_rooms=2,
                    distinct_drawn_levels=2, controlled_variants=4),
        classification='permission-backed CAD-derived controlled experiment; not validated real-building repair')
    write_json(output/'source-audit.json', evidence)
    write_json(output/'dataset-manifest.json', manifest(instance, dict(
        source_sha256=SOURCE_SHA, adapter_sha256=evidence['adapter_sha256'],
        decoded_sha256=evidence['decoded_sha256'], seed_reason='deterministic pinned manual annotation'),
        'four_controlled_variants_recognized',0))
    print(json.dumps(evidence['counts']))


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    for name in ['source','decoded','output']:
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();build(a.source,a.decoded,a.output)
