"""Untimed feasibility controls restricted to the demanded potential network.

These complement, rather than replace, the timed all-segment observations.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path

from cfar.actions import apply_actions
from cfar.io import fingerprint,manifest,write_json
from cfar.objective import action_cost
from cfar.obligations import verify_obligations
from audit_revised_evidence import paid_rectangles


def check(campaign,output):
    protocol=json.loads((campaign/'protocol.json').read_text())
    output.mkdir(parents=True,exist_ok=False);rows=[]
    for case in protocol['cases']:
        iid=case['instance_id'];instance=json.loads((campaign/iid/'input.json').read_text())
        retained={o[k] for o in instance['obligations'] for k in ('source','target')}
        catalog={c['connection_id']:c for c in instance['connections']}
        selected=sorted(a['action_id'] for a in instance['actions'] if a['action_id'].startswith('S')
            and all({catalog[e['connection_id']]['u'],catalog[e['connection_id']]['v']}<=retained for e in a['effects']))
        repair=apply_actions(instance,selected)
        assert verify_obligations(repair['instance'],repair['active'])['satisfied']
        assert all(a['delta']==0 for a in repair['adjacency'].values())
        cost=str(action_cost(instance,selected))
        assert paid_rectangles(instance,selected)==Fraction(cost)
        settings=dict(role='untimed_constructive_feasibility_control',selection='S actions with all endpoints inside roots plus union of demanded rooms',
                      not_a_timed_observation=True,not_an_optimality_certificate=True)
        metadata=manifest(instance,settings,'feasible',0)
        assert not metadata['git_dirty'],'Freeze checker before verification'
        write_json(output/(iid+'.manifest.json'),metadata)
        row=dict(instance_id=iid,selected=selected,cost=cost,input_fingerprint=fingerprint(instance),
                 satisfied=True,delta_A=0,independent_box_cost_checked=True,role=settings['role'])
        write_json(output/(iid+'.json'),row);rows.append(row)
        print(iid,cost,flush=True)
    write_json(output/'controls.json',dict(cases=rows,timed_observations=0,classification='Constructive controls only; no optimum or real-building construction validation'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--campaign',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();check(a.campaign,a.output)
