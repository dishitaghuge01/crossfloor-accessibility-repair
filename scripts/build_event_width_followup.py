"""Same K(2,4) graph/geometry/prices, paired versus batched edge events.

Optional intermediate vertices expire inside one still-live owner unit. Eager
root/target introduction is identical; no asymptotic full-interface claim.
"""
import argparse
from pathlib import Path
from cfar.experiment_families import generate_instance
from cfar.io import fingerprint,write_json


def build(output):
    output.mkdir(parents=True,exist_ok=False);cases=[]
    for order in ('paired','batched'):
        a=generate_instance('connectivity',6,0)
        catalog={c['connection_id']:c for c in a['connections']}
        edge_actions={(int(catalog[x['effects'][0]['connection_id']]['u'][1:]),int(catalog[x['effects'][0]['connection_id']]['v'][1:])):x for x in a['actions']}
        pairs=([(0,i) for i in range(1,5)]+[(i,5) for i in range(1,5)] if order=='batched' else
               [e for i in range(1,5) for e in ((0,i),(i,5))])
        chosen=[];cids=set()
        for j,pair in enumerate(pairs):
            action=edge_actions[pair];action['action_id']=f'A{j:03d}';chosen.append(action)
            cids.update(e['connection_id'] for e in action['effects'])
        a['actions']=chosen;a['connections']=[c for c in a['connections'] if c['connection_id'] in cids]
        iid='event-width-'+order;a['building_id']=iid
        a['description']='Authored event-frontier control; K(2,4), one shared owner, six floors, same edge costs; original action IDs order events. Hypothetical geometry and costs.'
        write_json(output/'instances'/(iid+'.json'),a)
        cases.append(dict(instance_id=iid,family='event-width-followup',level=order,input_fingerprint=fingerprint(a),
            source_building_id='authored',geometry_subset_id='fixed-K2-4',catalogue_layout_id='fixed-eight-edges',
            permission_pattern_id='one-profile',conflict_pattern_id='one-compatible-owner',price_seed=0,
            varies='Only action IDs/event ordering; ID tie objective can change',
            fixed='Graph, physical footprint ownership, edge costs, one source/target, six floors, eight actions',
            purpose='Paired retires an intermediate vertex before the next path; batched keeps all four live while ownership persists'))
    write_json(output/'dataset.json',dict(cases=cases,classification='posthoc authored event-frontier followup, separate from23-input structural campaign'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);build(p.parse_args().output)
