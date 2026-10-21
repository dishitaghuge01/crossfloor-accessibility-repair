"""Controlled interaction tiers on frozen building-derived geometry.

No permissions, reservations or prices are inferred from the IFC. Original
segment purchases remain a constructive feasible control in every tier.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import json

from cfar.io import fingerprint, write_json


def transform(base, tier, stride=2):
    instance = deepcopy(base)
    if tier == 'connectivity':
        return instance
    originals = {c['connection_id']:c for c in instance['connections']}
    columns = sorted({c['geometry']['asset_id'] for c in instance['connections'] if not c['existing']})
    duplicated = set(columns[::stride])
    mapping = {}
    for cid,c in sorted(originals.items()):
        if c['existing'] or c['geometry']['asset_id'] not in duplicated:
            continue
        alternative = deepcopy(c)
        alternative['connection_id']='Q'+cid
        alternative['evidence_id']='hypothetical-Q'+cid
        alternative['geometry']['asset_id']='competing-'+c['geometry']['asset_id']
        mapping[cid]=alternative['connection_id']
        instance['connections'].append(alternative)
    for action in list(instance['actions']):
        if not action['action_id'].startswith('S'):
            continue
        cid = action['effects'][0]['connection_id']
        if cid not in mapping:
            continue
        alternative=deepcopy(action)
        alternative['action_id']='Q'+action['action_id']
        alternative['cost']=1
        alternative['effects'][0]['connection_id']=mapping[cid]
        if tier=='full':
            alternative['effects'][0]['permitted_profiles']=[instance['profiles'][0]['profile_id']]
        alternative['evidence_ids']=['hypothetical-'+mapping[cid]]
        alternative['geometry_certificate']['connection_ids']=[mapping[cid]]
        instance['actions'].append(alternative)
    if tier=='full':
        pid=instance['profiles'][0]['profile_id']
        targets=sorted({o['target'] for o in instance['obligations'] if o['profile_id']==pid})
        if len(targets)<2:
            raise ValueError('Complementary profile demands need at least two destinations')
        retained=set(targets[::2])
        instance['obligations']=[o for o in instance['obligations']
            if (o['target'] in retained)==(o['profile_id']==pid)]
    instance['building_id']+='-joint-'+tier
    instance['description']+=' Hypothetical overlapping alternative owners and experimental permissions; abstract costs.'
    return instance


def build(source, output):
    dataset=json.loads((source/'dataset.json').read_text())
    output.mkdir(parents=True,exist_ok=False)
    rows=[]
    for entry in dataset['cases']:
        if entry['seed']!=0:
            continue
        base=json.loads((source/'instances'/(entry['case']+'.json')).read_text())
        for tier in ('connectivity','resource','full'):
            instance=transform(base,tier)
            iid=entry['case']+'-'+tier
            write_json(output/'instances'/(iid+'.json'),instance)
            rows.append(dict(instance_id=iid,tier=tier,
                source_building_id=entry['source']['building'],
                geometry_subset_id=entry['source']['building']+'-frozen-network-rooms',
                catalogue_layout_id=entry['case'].rsplit('-s',1)[0],
                permission_pattern_id='asymmetric-alternatives-and-demands' if tier=='full' else 'identical',
                conflict_pattern_id='overlap-every-second-column' if tier!='connectivity' else 'disjoint',
                price_seed=0,input_fingerprint=fingerprint(instance),
                base_input_fingerprint=fingerprint(base),actions=len(instance['actions']),
                obligations=len(instance['obligations']),source=entry['source']))
    write_json(output/'dataset.json',dict(cases=rows,
        classification='building-derived controlled experiments; hypothetical interventions, reservations, permissions and abstract costs',
        design='Five layouts from two buildings, three constraint tiers; fixed price seed. Tier changes are coupled, not isolated parameter estimates.',
        constructive_control='Original S segment actions; no competing Q purchases'))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    build(a.source,a.output)
