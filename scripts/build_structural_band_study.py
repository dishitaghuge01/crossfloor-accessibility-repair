"""Frozen structural extension: fixed price seed, changed conflicts and demands."""
import argparse
from copy import deepcopy
from pathlib import Path
from random import Random
from build_local_band_study import instance
from cfar.io import fingerprint,write_json

VARIANTS=('identity','alternating','permuted','permuted-permissions-targets')


def structural_instance(bands,variant):
    if variant not in VARIANTS:raise ValueError(variant)
    a=instance(bands,0);rng=Random(713)
    permutations=[]
    for j in range(bands):
        slots=list(range(3))
        if variant=='alternating':slots=[(s+j%2)%3 for s in slots]
        elif variant.startswith('permuted'):rng.shuffle(slots)
        permutations.append(slots)
    for c in a['connections']:
        j=int(c['connection_id'][1:5]);g=c['geometry']
        old=int((g['footprints'][0]['polygon'][0][0]-.5)/2)
        slot=permutations[j][old];shift=2*(slot-old)
        for record in g['footprints']+g['landings']:
            record['polygon']=[[x+shift,y] for x,y in record['polygon']]
    if variant=='permuted-permissions-targets':
        pids=[p['profile_id'] for p in a['profiles']]
        for action in a['actions']:
            if int(action['action_id'][1:5])%2:
                for effect in action['effects']:
                    effect['permitted_profiles']=[pids[1-pids.index(p)] for p in effect['permitted_profiles']]
        a['obligations'][1]['target']=f'R{bands}'
    a['building_id']=f'structural-bands-{bands}-{variant}'
    a['description']+=' Structural extension: '+variant+'. Price seed fixed at zero.'
    return a


def build(output):
    output.mkdir(parents=True,exist_ok=False);cases=[]
    for bands in (8,24):
        for variant in VARIANTS:
            a=structural_instance(bands,variant);iid=a['building_id']
            write_json(output/'instances'/(iid+'.json'),a)
            cases.append(dict(instance_id=iid,family='structural-bands',level=bands,structural_variant=variant,
                structural_seed=713,price_seed=0,input_fingerprint=fingerprint(a),source_building_id='authored',
                geometry_subset_id=f'{2*bands+1}-floor-chain',catalogue_layout_id=variant,
                permission_pattern_id='alternating-Q-U' if variant.endswith('targets') else 'original',
                conflict_pattern_id=variant))
    write_json(output/'dataset.json',dict(cases=cases,classification='authored structural extension; hypothetical geometry and interventions',
        mechanism='Fixed prices and action count. Identity, alternating and seeded per-band slot permutations change inter-band conflict incidence. Final variant additionally swaps profile permissions in odd bands and shortens the second demand. No independent buildings; final variant couples mechanisms.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    build(p.parse_args().output)
