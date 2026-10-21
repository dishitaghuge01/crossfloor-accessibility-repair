"""Larger IFC-derived controlled networks; never inferred construction options.

Uses frozen original orthogonal room rings, consecutive original storeys and
all conservative background envelopes. Every door, permission, reservation,
candidate and price is an experimental assumption. No source is downloaded.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from math import ceil, floor
from pathlib import Path
from random import Random

from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from cfar.geometry import computed_adjacency
from cfar.io import fingerprint, write_json
from cfar.synthetic_star import rectangle
from build_multiroom_experiments import door, PIDS, components
from source_room_selection import maximum_nonoverlap


def prepare(audit):
    if any('error' in b for b in audit['background']):
        raise ValueError('unmapped physical background')
    obstacles = [rectangle(*b['bounds']) for b in audit['background']]
    retained = []
    exclusions = []
    for storey in audit['storeys']:
        rooms, omitted, _ = maximum_nonoverlap([r for r in audit['spaces']
            if r['eligible'] and r['storey_id'] == storey['global_id']])
        retained.append((storey, rooms)); exclusions.extend(omitted)
    # Largest consecutive run of occupied original storeys; no cloned floors.
    runs, current = [], []
    for s, rooms in retained:
        if rooms: current.append((s, rooms))
        elif current: runs.append(current); current = []
    if current: runs.append(current)
    selected = max(runs, key=lambda run: (len(run), sum(len(r) for _, r in run)))
    bounds = unary_union([Polygon(r['polygon']) for _, rooms in selected for r in rooms]
                         + [Polygon(o) for o in obstacles]).bounds
    a = dict(schema_version='0.1.0', building_id=audit['provenance']['building']+'-network-study',
        description='IFC-derived controlled network. Original room rings, IDs and consecutive storeys; hypothetical baseline doors, profiles, permissions, grid reservations, complete purchases and abstract prices. Not validated building repairs.',
        profiles=[dict(profile_id=p,min_width_m=w,clearance_m=w,can_use_stairs=False,max_slope=.1)
                  for p,w in zip(PIDS,[.4,.5])],
        floors=[],connections=[],actions=[],portals=[],obligations=[],original_restoration_actions=[])
    for storey, rooms in selected:
        f=dict(floor_id=storey['global_id'],elevation_m=storey['elevation_m'],
            boundary=rectangle(bounds[0]-1,bounds[1]-1,bounds[2]+1,bounds[3]+1),
            rooms=[dict(room_id=r['global_id'],label=r['name'],polygon=r['polygon']) for r in rooms],
            adjacency_edges=[],access_edges=[],obstacles=deepcopy(obstacles),reserved_portal_zones=[])
        f['adjacency_edges']=[list(e) for e in sorted(computed_adjacency(f))]
        a['floors'].append(f)
    for f in a['floors']:
        by={r['room_id']:r for r in f['rooms']}
        for u,v in f['adjacency_edges']:
            c=door(a,by[u],by[v],len(a['connections']))
            if c:
                a['connections'].append(c)
                f['access_edges'].append(dict(edge_id=c['connection_id'],connection_id=c['connection_id'],permitted_profiles=PIDS[:]))
    blocked=unary_union([Polygon(o) for o in obstacles])
    # Two positions per endpoint pair before taking another pair. Grid and
    # selection are independent of optimization outcomes and costs.
    columns={}
    pairs=[]
    for i,(low,high) in enumerate(zip(a['floors'],a['floors'][1:])):
        for u in low['rooms']:
            for v in high['rooms']:
                common=Polygon(u['polygon']).intersection(Polygon(v['polygon'])).difference(blocked)
                if common.is_empty:continue
                x1,y1,x2,y2=common.bounds
                found=[]
                for ix in range(ceil(x1/1.6),floor((x2-.7)/1.6)+1):
                    for iy in range(ceil(y1/1.6),floor((y2-.7)/1.6)+1):
                        shape=box(ix*1.6,iy*1.6,ix*1.6+.7,iy*1.6+.7)
                        if common.covers(shape):
                            key=(ix,iy)
                            columns.setdefault(key,[]).append((i,u['room_id'],v['room_id']))
                            found.append(key)
                            if len(found)==2:break
                    if len(found)==2:break
                if found:pairs.append((i,u['room_id'],v['room_id'],found))
    ordered=[]
    for slot_index in range(2):
        for _,_,_,keys in sorted(pairs):
            if slot_index<len(keys) and keys[slot_index] not in ordered:ordered.append(keys[slot_index])
    return a,columns,ordered,exclusions


def catalogue(base,columns,ordered,count,seed):
    a=deepcopy(base);rng=Random(seed)
    for k,key in enumerate(ordered[:count]):
        ix,iy=key;slot=rectangle(ix*1.6,iy*1.6,ix*1.6+.7,iy*1.6+.7)
        cids=[]
        for i,u,v in sorted(set(columns[key])):
            cid=f'X{k:03d}-{i:02d}';cids.append(cid)
            records=[dict(room_id=r,polygon=deepcopy(slot)) for r in (u,v)]
            a['connections'].append(dict(connection_id=cid,evidence_id='hypothetical-'+cid,
                u=u,v=v,kind='lift',existing=False,physical_profiles=PIDS[:],
                geometry=dict(asset_id=f'column{k:03d}',width_m=.7,
                    rise_m=a['floors'][i+1]['elevation_m']-a['floors'][i]['elevation_m'],
                    run_m=1,landings=records,footprints=deepcopy(records))))
            for f in a['floors'][i:i+2]:
                if slot not in f['reserved_portal_zones']:f['reserved_portal_zones'].append(deepcopy(slot))
        def purchase(aid,ids,cost):
            return dict(action_id=aid,type='physical_intervention',cost=cost,
                effects=[dict(op='activate_connection',connection_id=c,permitted_profiles=PIDS[:]) for c in ids],
                requires=[],excludes=[],evidence_ids=['hypothetical-'+c for c in ids],
                geometry_certificate=dict(geometry_model='reserved_interfaces_2d_v1',connection_ids=ids,changed_floor_ids=[]))
        prices=[rng.randint(2,9) for _ in cids]
        for j,(cid,cost) in enumerate(zip(cids,prices)):
            a['actions'].append(purchase(f'S{k:03d}-{j:02d}',[cid],cost))
        if len(cids)>1:
            a['actions'].append(purchase(f'B{k:03d}',cids,max(1,sum(prices)-rng.randint(1,len(prices)))))
    ids=[r['room_id'] for f in a['floors'] for r in f['rooms']]
    groups=components(ids,[(c['u'],c['v']) for c in a['connections']])
    # Root in the lowest represented storey of the largest potential network;
    # demand every room in that network, not only two convenient endpoints.
    group=min(groups,key=lambda g:(-len(g),sorted(g)))
    root=next(r['room_id'] for f in a['floors'] for r in sorted(f['rooms'],key=lambda r:r['room_id']) if r['room_id'] in group)
    a['obligations']=[dict(obligation_id=f'O{q}-{j:03d}',profile_id=p,source=root,target=t)
                      for q,p in enumerate(PIDS) for j,t in enumerate(sorted(group-{root}))]
    if not a['obligations']:raise ValueError('no nontrivial obligation')
    a['building_id']+=f'-columns{count}-seed{seed}'
    return a,dict(columns=min(count,len(ordered)),available_columns=len(ordered),
        rooms=len(ids),potentially_reachable_rooms=len(group),excluded_from_obligations=sorted(set(ids)-group),
        obligations=len(a['obligations']),candidate_connections=sum(not c['existing'] for c in a['connections']),
        actions=len(a['actions']),source_root=root)


def build(audits,output,counts=(16,48,96),seeds=(0,1,2)):
    output.mkdir(parents=True,exist_ok=False);rows=[]
    for name in ('clinic','molio'):
        path=audits/(name+'.json');audit=json.loads(path.read_text())
        base,cols,order,excluded=prepare(audit)
        actual_counts=sorted({min(count,len(order)) for count in counts})
        for count in actual_counts:
            for seed in seeds:
                a,stats=catalogue(base,cols,order,count,seed)
                namecase=f'{name}-network-{count}-s{seed}'
                write_json(output/'instances'/(namecase+'.json'),a)
                rows.append(dict(case=namecase,seed=seed,source=audit['provenance'],
                    inventory_sha256=sha256(path.read_bytes()).hexdigest(),input_fingerprint=fingerprint(a),
                    excluded_overlapping_rooms=excluded,**stats))
                print(namecase,stats['rooms'],stats['actions'],stats['potentially_reachable_rooms'],flush=True)
    write_json(output/'dataset.json',dict(classification='building-derived controlled; hypothetical interventions, access and prices',
        grid_step_m=1.6,footprint_side_m=.7,columns_per_endpoint_pair=2,seed_list=list(seeds),cases=rows))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audits',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build(a.audits,a.output)
