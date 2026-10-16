"""Attempt a consecutive third source storey without changing existing rooms."""
from copy import deepcopy
from pathlib import Path
import sys,json
from math import ceil,floor as floor_integer
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_multiroom_experiments import door,PIDS
from source_room_selection import maximum_nonoverlap
from cfar.geometry import computed_adjacency
from cfar.interface_recognition import recognize_physical_interface
from cfar.io import write_json
from cfar.synthetic_star import rectangle
from shapely.geometry import Polygon,box
from shapely.ops import unary_union


def extend(audit,instance):
    index=next(i for i,s in enumerate(audit['storeys']) if s['global_id']==instance['floors'][-1]['floor_id'])
    if index+1>=len(audit['storeys']):raise ValueError('no next original storey')
    storey=audit['storeys'][index+1]
    eligible=[r for r in audit['spaces'] if r['eligible'] and r['storey_id']==storey['global_id']]
    rooms,exclusions,selection_stats=maximum_nonoverlap(eligible)
    if not rooms:raise ValueError('next original storey has no admissible rooms')
    a=deepcopy(instance)
    floor=dict(floor_id=storey['global_id'],elevation_m=storey['elevation_m'],boundary=deepcopy(a['floors'][-1]['boundary']),
        rooms=[dict(room_id=r['global_id'],label=r['name'],polygon=r['polygon']) for r in rooms],
        adjacency_edges=[],access_edges=[],reserved_portal_zones=[],obstacles=deepcopy(a['floors'][-1]['obstacles']))
    a['floors'].append(floor)
    all_polygons=[Polygon(r['polygon']) for f in a['floors'] for r in f['rooms']]+[Polygon(o) for o in floor['obstacles']]
    x1,y1,x2,y2=unary_union(all_polygons).bounds
    for f in a['floors']:f['boundary']=rectangle(x1-1,y1-1,x2+1,y2+1)
    floor['adjacency_edges']=[list(e) for e in sorted(computed_adjacency(floor))]
    by={r['room_id']:r for r in floor['rooms']}
    for u,v in floor['adjacency_edges']:
        c=door(a,by[u],by[v],len(a['connections']))
        if c:
            a['connections'].append(c);floor['access_edges'].append(dict(edge_id=c['connection_id'],connection_id=c['connection_id'],permitted_profiles=PIDS))
    targets=sorted({o['target'] for o in a['obligations']})
    upper={r['room_id']:r for r in a['floors'][-2]['rooms']}
    blocked=unary_union([Polygon(o) for o in floor['obstacles']]+[Polygon(c['geometry']['footprints'][0]['polygon']) for c in a['connections'] if c['kind']!='door'])
    attempts=[]
    for u in targets:
        for v in sorted(by):
            common=Polygon(upper[u]['polygon']).intersection(Polygon(by[v]['polygon'])).difference(blocked)
            if common.is_empty:continue
            minx,miny,maxx,maxy=common.bounds
            for ix in range(ceil(minx/.8),floor_integer((maxx-.7)/.8)+1):
                for iy in range(ceil(miny/.8),floor_integer((maxy-.7)/.8)+1):
                    shape=box(ix*.8,iy*.8,ix*.8+.7,iy*.8+.7)
                    if not common.covers(shape):continue
                    trial=deepcopy(a);slot=[list(p) for p in shape.exterior.coords]
                    records=[dict(room_id=r,polygon=slot) for r in (u,v)];cid='X2'
                    trial['connections'].append(dict(connection_id=cid,evidence_id='hypothetical-'+cid,u=u,v=v,kind='lift',existing=False,physical_profiles=PIDS,
                        geometry=dict(asset_id='hypothetical-'+cid,width_m=.7,rise_m=floor['elevation_m']-a['floors'][-2]['elevation_m'],run_m=1,landings=records,footprints=records)))
                    for f in trial['floors'][-2:]:f['reserved_portal_zones'].append(slot)
                    trial['actions'].append(dict(action_id='A2',type='physical_intervention',cost=2,
                        effects=[dict(op='activate_connection',connection_id=cid,permitted_profiles=PIDS)],requires=[],excludes=[],evidence_ids=['hypothetical-'+cid],
                        geometry_certificate=dict(geometry_model='reserved_interfaces_2d_v1',connection_ids=[cid],changed_floor_ids=[])))
                    trial['obligations'] += [dict(obligation_id=f'Othird{q}',profile_id=p,source=trial['obligations'][0]['source'],target=v) for q,p in enumerate(PIDS)]
                    try:recognize_physical_interface(trial)
                    except ValueError as e:attempts.append(str(e));continue
                    return trial,dict(added_storey=storey,retained_rooms=len(rooms),selection_statistics=selection_stats,exclusions=exclusions,attempts=attempts,
                        added_adjacency_edges=len(floor['adjacency_edges']),added_hypothetical_doors=len(floor['access_edges']))
    raise ValueError('no third-storey candidate passes full recognition; '+str(len(attempts))+' failed recognitions')


def build(audits,base,output):
    output.mkdir(parents=True,exist_ok=True)
    summary=[]
    for name in ['clinic','molio']:
        audit=json.loads((audits/(name+'.json')).read_text())
        row=dict(source_building_id=name)
        try:
            original=json.loads((base/'instances'/(name+'-horizontal.json')).read_text())
            three,selection=extend(audit,original)
            restricted=deepcopy(three)
            for edge in restricted['floors'][1]['access_edges']:edge['permitted_profiles']=PIDS[:1]
            for key,instance in [('three-storey',three),('three-storey-restricted',restricted)]:
                write_json(output/'instances'/(name+'-'+key+'.json'),instance)
            row.update(status='admitted',selection=selection)
        except ValueError as e:row.update(status='unsupported',reason=str(e))
        summary.append(row);write_json(output/'summary.json',summary);print(name,row['status'],flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    for key in ['audits','base','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();build(a.audits,a.base,a.output)
