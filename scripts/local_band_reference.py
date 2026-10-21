"""Independent, generator-specific eight-mask oracle; no geometry/DP kernel calls.

Valid only after structural admission below: chain rooms, fixed three slots,
adjacent edges, owner local to one two-edge band. Not a general repair solver.
"""
from collections import defaultdict
from decimal import Decimal
import argparse,json
from pathlib import Path
from cfar.io import fingerprint,write_json


def solve(a):
    n=(len(a['floors'])-1)//2
    assert len(a['floors'])==2*n+1 and len(a['actions'])==8*n
    assert all(not f['access_edges'] for f in a['floors']) and not a['portals']
    assert all(len(f['rooms'])==1 and f['rooms'][0]['room_id']==f'R{i}' for i,f in enumerate(a['floors']))
    expected_room=[[0,0],[6,0],[6,4],[0,4]]
    assert all(f['boundary']==f['rooms'][0]['polygon']==expected_room and not f['obstacles']
        and f['reserved_portal_zones']==[expected_room] and not f['adjacency_edges'] for f in a['floors'])
    targets={o['profile_id']:int(o['target'][1:]) for o in a['obligations']}
    assert len(a['obligations'])==len(a['profiles'])==2
    assert {p['profile_id'] for p in a['profiles']}==set(targets)
    assert all(p['min_width_m']==p['clearance_m']==.4 and p['can_use_stairs'] is True
        and p['max_slope']==.5 for p in a['profiles'])
    assert all(f['elevation_m']==3*i for i,f in enumerate(a['floors']))
    assert all(o['source']=='R0' for o in a['obligations'])
    assert len(targets)==2 and set(targets.values())=={2*n,2*n-1}
    catalog={c['connection_id']:c for c in a['connections']};groups=defaultdict(list);owner_band={};owner_slot={}
    for x in a['actions']:
        assert not x['requires'] and not x['excludes'] and x['type']=='physical_intervention'
        assert Decimal(str(x['cost']))>=0
        assert x['geometry_certificate']==dict(geometry_model='reserved_interfaces_2d_v1',
            connection_ids=[e['connection_id'] for e in x['effects']],changed_floor_ids=[])
        j=int(x['action_id'][1:5]);groups[j].append(x)
        assert 0<=j<n
        for effect in x['effects']:
            assert effect['op']=='activate_connection' and effect['permitted_profiles'] and set(effect['permitted_profiles'])<=set(targets)
            c=catalog[effect['connection_id']];u,v=int(c['u'][1:]),int(c['v'][1:])
            assert c['kind']=='lift' and set(c['physical_profiles'])==set(targets)
            assert v==u+1 and u in (2*j,2*j+1) and not c['existing']
            g=c['geometry'];owner=g['asset_id'];owner_band.setdefault(owner,j);assert owner_band[owner]==j
            assert g['width_m']==1 and g['rise_m']==3 and g['run_m']==1
            assert len(g['footprints'])==len(g['landings'])==2
            assert {r['room_id'] for r in g['footprints']}=={c['u'],c['v']}
            assert {r['room_id'] for r in g['landings']}=={c['u'],c['v']}
            for record in g['footprints']+g['landings']:
                p=record['polygon'];xs={v[0] for v in p};ys={v[1] for v in p}
                assert ys=={.5,1.5} and len(xs)==2
                assert (min(xs),max(xs)) in ((.5,1.5),(2.5,3.5),(4.5,5.5))
                assert p==[[min(xs),.5],[max(xs),.5],[max(xs),1.5],[min(xs),1.5]]
                owner_slot.setdefault(owner,min(xs));assert owner_slot[owner]==min(xs)
    previous={0:(Decimal(0),0,())};ledger=[]
    for j in range(n):
        actions=sorted(groups[j],key=lambda x:x['action_id']);assert len(actions)==8
        patterns=[]
        for mask in range(256):
            selected=[x for k,x in enumerate(actions) if mask&(1<<k)]
            occupancy={};coverage=set();valid=True
            for x in selected:
                for effect in x['effects']:
                    c=catalog[effect['connection_id']];g=c['geometry'];owner=g['asset_id']
                    u=int(c['u'][1:]);coverage.update((pid,u) for pid in effect['permitted_profiles'])
                    for record in g['footprints']:
                        f=int(record['room_id'][1:]);slot=int((min(v[0] for v in record['polygon'])-.5)/2)
                        key=(f,slot)
                        if key in occupancy and occupancy[key]!=owner:valid=False
                        occupancy[key]=owner
            required={(pid,e) for pid,t in targets.items() for e in (2*j,2*j+1) if e<t}
            if not valid or not required<=coverage:continue
            left=sum(1<<s for s in range(3) if (2*j,s) in occupancy)
            right=sum(1<<s for s in range(3) if (2*j+2,s) in occupancy)
            label=(sum((Decimal(str(x['cost'])) for x in selected),Decimal(0)),len(selected),tuple(x['action_id'] for x in selected))
            patterns.append((left,right,label))
        current={}
        for occupied,prefix in previous.items():
            for left,right,label in patterns:
                if left&occupied:continue
                value=(prefix[0]+label[0],prefix[1]+label[1],tuple(sorted(prefix[2]+label[2])))
                if right not in current or value<current[right]:current[right]=value
        ledger.append(dict(band=j,local_subsets=256,admissible_covering_patterns=len(patterns),boundary_states=len(current)))
        previous=current
    best=min(previous.values()) if previous else None
    return dict(method='independent_three_slot_chain_oracle',scope='admitted authored local-band family only',
        input_fingerprint=fingerprint(a),status='optimal' if best else 'infeasible',
        cost=str(best[0]) if best else None,selected=list(best[2]) if best else None,ledger=ledger,
        maximum_boundary_states=max(x['boundary_states'] for x in ledger))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();write_json(a.output,solve(json.loads(a.input.read_text())))
