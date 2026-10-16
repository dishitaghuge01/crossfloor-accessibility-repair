"""Multi-room IFC experiment; all access/permissions/reservations/costs hypothetical.

Source rings/IDs are frozen. Exact shared boundaries support hypothetical door
placements, never inferred source doors. Every exclusion is saved.
"""
import argparse
from copy import deepcopy
from itertools import combinations
import json
from math import ceil,floor
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from cfar.geometry import computed_adjacency, connection_feasible
from cfar.interface_recognition import recognize_physical_interface
from cfar.io import fingerprint,write_json
from cfar.synthetic_star import rectangle
from cfar.validation import validate_instance

PIDS=['experimental0','experimental1']


def components(ids,edges):
    groups=[{i} for i in ids]
    for u,v in edges:
        selected=[g for g in groups if u in g or v in g]
        groups=[g for g in groups if g not in selected]+[set().union(*selected)]
    return groups


def door(instance,first,second,index):
    shared=Polygon(first['polygon']).boundary.intersection(Polygon(second['polygon']).boundary)
    segments=list(shared.geoms) if hasattr(shared,'geoms') else [shared]
    for segment in sorted(segments,key=lambda s:(-s.length,s.wkt)):
        if segment.length<.8 or segment.geom_type!='LineString':continue
        x,y=segment.interpolate(.5,normalized=True).coords[0]
        coords=list(segment.coords)
        vertical=abs(coords[0][0]-coords[-1][0])<1e-8
        opening=[[x,y-.3],[x,y+.3]] if vertical else [[x-.3,y],[x+.3,y]]
        landings=[]
        for room in (first,second):
            candidates=([rectangle(x-.6,y-.3,x,y+.3),rectangle(x,y-.3,x+.6,y+.3)] if vertical else
                        [rectangle(x-.3,y-.6,x+.3,y),rectangle(x-.3,y,x+.3,y+.6)])
            fits=[shape for shape in candidates if Polygon(room['polygon']).buffer(1e-8).covers(Polygon(shape))]
            if not fits:break
            landings.append(dict(room_id=room['room_id'],polygon=fits[0]))
        if len(landings)!=2:continue
        c=dict(connection_id=f'H{index}',evidence_id=f'hypothetical-H{index}',u=first['room_id'],v=second['room_id'],
            kind='door',existing=True,physical_profiles=PIDS,geometry=dict(width_m=.6,opening=opening,landings=landings))
        try:connection_feasible(instance,c,PIDS)
        except ValueError:continue
        return c
    return None


def build_one(audit):
    if any('error' in b for b in audit['background']):raise ValueError('unmapped background')
    obstacles=[rectangle(*b['bounds']) for b in audit['background']]
    rooms_by={};exclusions=[]
    for storey in audit['storeys']:
        retained=[]
        eligible=[s for s in audit['spaces'] if s['eligible'] and s['storey_id']==storey['global_id']]
        for s in sorted(eligible,key=lambda r:(-r['area'],r['global_id'])):
            if any(Polygon(s['polygon']).intersection(Polygon(t['polygon'])).area>1e-8 for t in retained):
                exclusions.append(dict(room=s['global_id'],reason='overlap with earlier larger-area retained room'))
            else:retained.append(s)
        rooms_by[storey['global_id']]=retained
    attempts=[]
    for low,high in zip(audit['storeys'],audit['storeys'][1:]):
        if high['elevation_m']-low['elevation_m']<.1:continue
        chosen=rooms_by[low['global_id']]+rooms_by[high['global_id']]
        if not chosen:continue
        extent=unary_union([Polygon(s['polygon']) for s in chosen]+[Polygon(o) for o in obstacles]).bounds
        boundary=rectangle(extent[0]-1,extent[1]-1,extent[2]+1,extent[3]+1)
        instance=dict(schema_version='0.1.0',building_id=audit['provenance']['building']+'-multiroom',
            description='Building-derived controlled experiment. Frozen original room projections; ALL doors, profile permissions, reservations, lift candidates and abstract costs are hypothetical experimental assumptions, not IFC facts or prices.',
            profiles=[dict(profile_id=p,min_width_m=w,clearance_m=w,can_use_stairs=False,max_slope=.1) for p,w in zip(PIDS,[.4,.5])],
            floors=[],connections=[],actions=[],portals=[],obligations=[],original_restoration_actions=[])
        for storey in (low,high):
            f=dict(floor_id=storey['global_id'],elevation_m=storey['elevation_m'],boundary=boundary,
                rooms=[dict(room_id=s['global_id'],label=s['name'],polygon=s['polygon']) for s in rooms_by[storey['global_id']]],
                adjacency_edges=[],access_edges=[],obstacles=obstacles,reserved_portal_zones=[])
            f['adjacency_edges']=[list(e) for e in sorted(computed_adjacency(f))]
            instance['floors'].append(f)
        for f in instance['floors']:
            rooms={r['room_id']:r for r in f['rooms']}
            for u,v in f['adjacency_edges']:
                c=door(instance,rooms[u],rooms[v],len(instance['connections']))
                if c:
                    instance['connections'].append(c)
                    f['access_edges'].append(dict(edge_id=c['connection_id'],connection_id=c['connection_id'],permitted_profiles=PIDS))
        floor0,floor1=instance['floors']
        lower=components([r['room_id'] for r in floor0['rooms']],[(c['u'],c['v']) for c in instance['connections'] if c['u'] in {r['room_id'] for r in floor0['rooms']}])
        upper=components([r['room_id'] for r in floor1['rooms']],[(c['u'],c['v']) for c in instance['connections'] if c['u'] in {r['room_id'] for r in floor1['rooms']}])
        slots=[]
        blocked=unary_union([Polygon(o) for o in obstacles])
        for a in floor0['rooms']:
            for b in floor1['rooms']:
                common=Polygon(a['polygon']).intersection(Polygon(b['polygon'])).difference(blocked)
                if common.is_empty:continue
                x1,y1,x2,y2=common.bounds
                found=None
                for ix in range(ceil(x1/.8),floor((x2-.7)/.8)+1):
                    for iy in range(ceil(y1/.8),floor((y2-.7)/.8)+1):
                        slot=box(ix*.8,iy*.8,ix*.8+.7,iy*.8+.7)
                        if common.covers(slot):found=[list(p) for p in slot.exterior.coords];break
                    if found:break
                if found:slots.append((a['room_id'],b['room_id'],found))
        options=[]
        for a,b in combinations(slots,2):
            if a[1]==b[1]:continue
            if not any({a[0],b[0]}<=g for g in lower) or not any({a[1],b[1]}<=g for g in upper):continue
            options.append((a,b))
        for pair in options:
            trial=deepcopy(instance)
            for i,(u,v,slot) in enumerate(pair):
                cid=f'X{i}';records=[dict(room_id=r,polygon=slot) for r in (u,v)]
                trial['connections'].append(dict(connection_id=cid,evidence_id='hypothetical-'+cid,u=u,v=v,kind='lift',existing=False,
                    physical_profiles=PIDS,geometry=dict(asset_id='hypothetical-'+cid,width_m=.7,rise_m=high['elevation_m']-low['elevation_m'],run_m=1,landings=records,footprints=records)))
                for f in trial['floors']:f['reserved_portal_zones'].append(slot)
                trial['actions'].append(dict(action_id=f'A{i}',type='physical_intervention',cost=[1,3][i],
                    effects=[dict(op='activate_connection',connection_id=cid,permitted_profiles=PIDS)],requires=[],excludes=[],evidence_ids=['hypothetical-'+cid],
                    geometry_certificate=dict(geometry_model='reserved_interfaces_2d_v1',connection_ids=[cid],changed_floor_ids=[])))
            trial['obligations']=[dict(obligation_id=f'O{q}{j}',profile_id=p,source=pair[0][0],target=t) for q,p in enumerate(PIDS) for j,t in enumerate([pair[0][1],pair[1][1]])]
            try:recognize_physical_interface(trial)
            except ValueError as e:attempts.append(str(e));continue
            restricted=deepcopy(trial)
            for edge in restricted['floors'][1]['access_edges']:edge['permitted_profiles']=PIDS[:1]
            recognize_physical_interface(restricted)
            return {'horizontal':trial,'restricted-horizontal':restricted},dict(exclusions=exclusions,attempts=attempts,
                retained_rooms=sum(len(f['rooms']) for f in trial['floors']),source_rooms=audit['counts']['spaces'],
                omitted_rooms=audit['counts']['spaces']-sum(len(f['rooms']) for f in trial['floors']),
                adjacency_edges_per_floor=[len(f['adjacency_edges']) for f in trial['floors']],
                hypothetical_doors_per_floor=[len(f['access_edges']) for f in trial['floors']],
                selected_storeys=[low['global_id'],high['global_id']],candidate_pairs=pair)
    raise ValueError('no two aligned candidate pairs joining the same hypothetical horizontal components on consecutive storeys; '+str(len(attempts))+' recognition exclusions')


def build(audits,output):
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('fresh output required')
    summary=[]
    for path in sorted(audits.glob('*.json')):
        if path.name.endswith(('-reference.json','-selection.json')):continue
        audit=json.loads(path.read_text());name=audit['provenance']['building']
        row=dict(source_building_id=name,source_sha256=audit['provenance']['sha256'],source_counts=audit['counts'])
        try:
            variants,selection=build_one(audit)
            for key,instance in variants.items():write_json(output/'instances'/f'{name}-{key}.json',instance)
            row.update(status='admitted',variants=len(variants),selection=selection)
        except ValueError as e:row.update(status='unsupported',reason=str(e))
        summary.append(row);write_json(output/'summary.json',summary);print(name,row['status'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audits',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.audits,a.output)
