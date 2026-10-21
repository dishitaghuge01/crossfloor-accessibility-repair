"""Two-condition permission-only control; reuse the frozen pipeline runner."""
import argparse
from copy import deepcopy
import json
from pathlib import Path

from cfar.io import fingerprint, write_json
import run_joint_network_study as driver


def build(source, output):
    base=json.loads(source.read_text())
    output.mkdir(parents=True,exist_ok=False)
    cases=[]
    for mode in ('restricted','shared'):
        instance=deepcopy(base)
        if mode=='shared':
            profiles=[p['profile_id'] for p in instance['profiles']]
            for action in instance['actions']:
                if action['action_id'].startswith('Q'):
                    for effect in action['effects']:effect['permitted_profiles']=profiles
        # Reversing the single experimental change must recover the source exactly.
        restored=deepcopy(instance)
        originals={a['action_id']:a for a in base['actions']}
        for action in restored['actions']:
            for effect,old in zip(action['effects'],originals[action['action_id']]['effects']):
                effect['permitted_profiles']=old['permitted_profiles']
        assert restored==base
        iid='clinic16-permissions-'+mode
        write_json(output/'instances'/(iid+'.json'),instance)
        cases.append(dict(instance_id=iid,input_fingerprint=fingerprint(instance),
            source_building_id='clinic',geometry_subset_id='clinic-frozen-network-rooms',
            catalogue_layout_id='clinic-network-16',permission_pattern_id=mode,
            conflict_pattern_id='overlap-every-second-column',price_seed=0))
    write_json(output/'dataset.json',dict(cases=cases,
        classification='building-derived controlled permission-only experiment; hypothetical permissions and abstract costs',
        fixed='Geometry, actions/effects/owners, costs, reservations/conflicts, baseline and complementary demands; only Q permitted_profiles changes'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path)
    p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.source:build(a.source,a.dataset)
    else:
        driver.METHODS=['both','cp-sat']
        ids=[c['instance_id'] for c in json.loads((a.dataset/'dataset.json').read_text())['cases']]
        driver.run(a.dataset.resolve(),a.output.resolve(),ids,60)
