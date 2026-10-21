"""Three-floor K(2,n) witness: constant transient frontier, growing floor bound."""
import argparse
from copy import deepcopy
from pathlib import Path
from cfar.geometry import computed_adjacency
from cfar.io import fingerprint,write_json
from cfar.synthetic_shaft import make_shaft_instance
from cfar.synthetic_star import rectangle


def instance(bays):
    if bays<1:raise ValueError('positive bays required')
    a=make_shaft_instance(2,[],[],profiles=1,physical=True)
    a['connections']=[];a['actions']=[]
    for f in a['floors']:
        f['boundary']=rectangle(0,0,2*bays,4);f['reserved_portal_zones']=[deepcopy(f['boundary'])]
        if f['floor_id']=='F1':
            f['rooms']=[dict(room_id=f'V{i}',label=f'bay{i}',polygon=rectangle(2*i,0,2*i+2,4)) for i in range(bays)]
        else:f['rooms'][0]['polygon']=deepcopy(f['boundary'])
        f['adjacency_edges']=[list(x) for x in sorted(computed_adjacency(f))]
    for i in range(bays):
        prefix=f'P{i:04d}';shape=rectangle(2*i+.5,.5,2*i+1.5,1.5)
        for j,(u,v) in enumerate((('R0',f'V{i}'),(f'V{i}','R2'))):
            cid=prefix+str(j);records=[dict(room_id=r,polygon=deepcopy(shape)) for r in (u,v)]
            a['connections'].append(dict(connection_id=cid,evidence_id='e'+cid,u=u,v=v,kind='lift',existing=False,
                physical_profiles=['profile0'],geometry=dict(asset_id=prefix,width_m=1,rise_m=3,run_m=1,landings=records,footprints=deepcopy(records))))
        for suffix,cids,cost in [('A',[prefix+'0'],2),('B',[prefix+'1'],2),('C',[prefix+'0',prefix+'1'],3+i%3)]:
            a['actions'].append(dict(action_id=prefix+suffix,type='physical_intervention',cost=cost,
                effects=[dict(op='activate_connection',connection_id=c,permitted_profiles=['profile0']) for c in cids],
                evidence_ids=['e'+c for c in cids],requires=[],excludes=[],
                geometry_certificate=dict(geometry_model='reserved_interfaces_2d_v1',connection_ids=cids,changed_floor_ids=[])))
    a['building_id']=f'private-bays-{bays}';a['description']='Authored three-floor separating family, private complete owner units; hypothetical geometry and abstract costs.'
    return a


def build(output,sizes=(2,4,8,16,32)):
    output.mkdir(parents=True,exist_ok=False);cases=[]
    for n in sizes:
        a=instance(n);iid=a['building_id'];write_json(output/'instances'/(iid+'.json'),a)
        cases.append(dict(instance_id=iid,family='private-bays',level=n,input_fingerprint=fingerprint(a),price_seed=0,
            source_building_id='authored',geometry_subset_id=f'three-floors-{n}-bays',catalogue_layout_id=iid,
            permission_pattern_id='one-profile',conflict_pattern_id='private-disjoint-units'))
    write_json(output/'dataset.json',dict(cases=cases,classification='authored separating family; not domain validation',
        purpose='Constant transient potential interface with complete paid units; coarse floor r=z=n. Distinction is from the coarse bound, not general pathwidth algorithms.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--sizes',nargs='+',type=int,default=[2,4,8,16,32])
    a=p.parse_args();build(a.output,a.sizes)
