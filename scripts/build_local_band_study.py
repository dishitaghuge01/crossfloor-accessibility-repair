"""Authored bounded-band physical catalogues; no construction validation."""
import argparse
from copy import deepcopy
from pathlib import Path
from random import Random

from cfar.io import fingerprint,write_json
from cfar.synthetic_shaft import make_shaft_instance
from cfar.synthetic_star import rectangle


def instance(bands, seed=0):
    if bands<1:raise ValueError('positive bands required')
    a=make_shaft_instance(2*bands,[],[],profiles=2,physical=True)
    a['connections']=[];a['actions']=[];rng=Random(seed)
    for floor in a['floors']:
        floor['boundary']=rectangle(0,0,6,4)
        floor['rooms'][0]['polygon']=deepcopy(floor['boundary'])
        floor['reserved_portal_zones']=[deepcopy(floor['boundary'])]
    pids=[p['profile_id'] for p in a['profiles']]
    def connection(cid,edge,owner,slot):
        shape=rectangle(.5+2*slot,.5,1.5+2*slot,1.5)
        records=[dict(room_id=f'R{i}',polygon=deepcopy(shape)) for i in (edge,edge+1)]
        a['connections'].append(dict(connection_id=cid,evidence_id='e'+cid,u=f'R{edge}',v=f'R{edge+1}',
            kind='lift',existing=False,physical_profiles=pids[:],
            geometry=dict(asset_id=owner,width_m=1,rise_m=3,run_m=1,landings=records,footprints=deepcopy(records))))
    def action(aid,cids,permissions,cost):
        a['actions'].append(dict(action_id=aid,type='physical_intervention',cost=cost,
            effects=[dict(op='activate_connection',connection_id=c,permitted_profiles=permissions) for c in cids],
            evidence_ids=['e'+c for c in cids],requires=[],excludes=[],
            geometry_certificate=dict(geometry_model='reserved_interfaces_2d_v1',connection_ids=cids,changed_floor_ids=[])))
    for j in range(bands):
        prefix=f'M{j:04d}'
        for offset in (0,1):
            edge=2*j+offset
            for kind,slot in (('S',0),('Q',0),('U',1),('T',2)):
                connection(prefix+kind+str(offset),edge,prefix+kind,slot)
            action(prefix+'A'+str(offset),[prefix+'S'+str(offset)],pids[:],rng.randint(2,6))
            action(prefix+'C'+str(offset),[prefix+'Q'+str(offset)],[pids[0]],1)
        action(prefix+'B',[prefix+'S0',prefix+'S1'],pids[:],rng.randint(3,8))
        action(prefix+'E',[prefix+'Q0',prefix+'Q1'],[pids[0]],rng.randint(1,3))
        action(prefix+'F',[prefix+'U0',prefix+'U1'],[pids[1]],rng.randint(1,3))
        action(prefix+'D',[prefix+'T0',prefix+'T1'],pids[:],rng.randint(5,10))
    a['building_id']=f'local-bands-{bands}-s{seed}'
    a['description']='Authored bounded-band catalogue: shared two-edge bundles, competing owners, two profile-restricted shafts, alternate shared shaft. Adjacent bands conflict at their shared landing floor. Abstract costs; not an actual building.'
    # Distinct endpoint demands; profile1 stops one segment earlier.
    a['obligations'][1]['target']=f'R{2*bands-1}'
    return a


def build(output,sizes=(4,8,16,32),seeds=(0,1,2)):
    output.mkdir(parents=True,exist_ok=False);cases=[]
    for n in sizes:
        for seed in seeds:
            a=instance(n,seed);iid=a['building_id'];write_json(output/'instances'/(iid+'.json'),a)
            cases.append(dict(instance_id=iid,family='local-bands',level=n,price_seed=seed,input_fingerprint=fingerprint(a),
                source_building_id='authored',geometry_subset_id=f'{2*n+1}-floor-chain',catalogue_layout_id=f'local-bands-{n}',
                permission_pattern_id='Q-profile0-U-profile1-S-T-shared',conflict_pattern_id='S-Q-overlap-and-adjacent-band-landing-conflicts'))
    write_json(output/'dataset.json',dict(cases=cases,classification='authored bounded-band structural benchmark; not building validation',
        mechanism='Two profiles, whole two-edge bundles, same-owner reuse, competing-owner overlap and alternate shafts. Three price seeds are repetitions of catalogue topology, not independent geometries.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--sizes',nargs='+',type=int,default=[4,8,16,32]);p.add_argument('--seeds',nargs='+',type=int,default=[0,1,2])
    a=p.parse_args();build(a.output,a.sizes,a.seeds)
