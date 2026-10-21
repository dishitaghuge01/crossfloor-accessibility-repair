"""Eight declared structural families; coupled changes are explicit metadata."""
from copy import deepcopy
from pathlib import Path
import argparse
from cfar.io import write_json, fingerprint
from cfar.experiment_families import generate_instance
from cfar.synthetic_shaft import make_shaft_instance


def bundle_instance(size):
    a=make_shaft_instance(4,[(i,i,1) for i in range(4)],[2]*4,profiles=1,physical=True,asset_groups=[0]*4)
    b=deepcopy(a['actions'][0]);b['action_id']='B';b['cost']=5
    b['effects']=[deepcopy(x['effects'][0]) for x in a['actions'][:size]]
    b['evidence_ids']=[x['evidence_ids'][0] for x in a['actions'][:size]]
    b['geometry_certificate']['connection_ids']=[x['effects'][0]['connection_id'] for x in a['actions'][:size]]
    a['actions'].append(b)
    return a


def build(output):
    output.mkdir(parents=True,exist_ok=False);rows=[]
    def add(family,size,a,varies,fixed,couplings):
        iid=f'{family}-{size}'
        a['building_id']='parameter-'+iid
        a['description']='Authored parameter experiment; hypothetical geometry and abstract costs. '+couplings
        write_json(output/'instances'/(iid+'.json'),a)
        rows.append(dict(instance_id=iid,family=family,level=size,input_fingerprint=fingerprint(a),
            varies=varies,fixed=fixed,couplings=couplings,price_seed=0,
            source_building_id='authored',geometry_subset_id='authored-'+family,
            catalogue_layout_id=iid,permission_pattern_id=family if family=='profile-heterogeneity' else 'fixed-within-family',
            conflict_pattern_id=family if family=='conflict-density' else 'see-instance'))
    for n in (3,4,5):
        add('active-connectivity',n,generate_instance('connectivity',n,0),
            'complete potential graph order','one profile, same owner, price seed',
            'Action count, span and connectivity width co-vary; no isolated width causal claim.')
    for n in (8,32,128):
        add('action-count',n,generate_instance('catalogue',n,0),'parallel purchase alternatives',
            'route endpoints, demands, physical graph topology','Polynomial input size and action count vary; no width-only claim.')
    for n in (2,4,8):
        add('owner-competition',n,generate_instance('ownership',n,0),'owners competing within one unit',
            'p=1,r=1,z=2,L=4','h,g and action count co-vary; distinguishes within-unit identity from inter-unit conflicts.')
    for n in (1,2,4):
        add('bundle-size',n,bundle_instance(n),'effects included in one cost-five bundle',
            'four segment edges, five purchases, one profile, one owner, all prices','Unit support fixed by individual segment actions; bundle coverage changes.')
    for groups in ([0,1,2,3],[0,0,1,1],[0,0,0,0]):
        span=max(groups.count(g) for g in set(groups))+1
        a=make_shaft_instance(4,[(i,i,1) for i in range(4)],[2]*4,profiles=1,physical=True,asset_groups=groups)
        add('unit-span',span,a,'asset sharing across consecutive segments',
            'five floors, four graph edges, four purchases, one profile, costs','Unit span, owner incidence and footprint locations co-vary; no pure-span effect claim.')
    # Same six-edge graph, same cost order; IDs select different action-event schedules.
    for order in ('grouped','interleaved'):
        a=generate_instance('connectivity',4,0)
        connections={c['connection_id']:c for c in a['connections']}
        def endpoints(action):
            c=connections[action['effects'][0]['connection_id']]
            return c['u'],c['v']
        ordered=sorted(a['actions'],key=lambda x:endpoints(x) if order=='grouped' else tuple(reversed(endpoints(x))))
        for i,action in enumerate(ordered):action['action_id']=f'A{i:03d}'
        add('event-lifetime',order,a,'action ID/event ordering',
            'graph, physical effects, costs and demands','ID names change and can affect ties; structural schedule comparison, not a new parameter theorem.')
    for pattern in ('both','split','one-restricted'):
        a=make_shaft_instance(2,[(0,0,2),(1,1,2),(0,1,2)],[2,2,5],profiles=2,physical=True,asset_groups=[0,0,0])
        if pattern=='split':
            a['actions'][0]['effects'][0]['permitted_profiles']=['profile0']
            a['actions'][1]['effects'][0]['permitted_profiles']=['profile1']
        if pattern=='one-restricted':a['actions'][0]['effects'][0]['permitted_profiles']=['profile0']
        a['obligations'][0]['target']='R1'
        add('profile-heterogeneity',pattern,a,'action permissions','geometry, three purchases, costs, two distinct target demands',
            'Permissions vary on fixed physical capabilities; no inference from geometry.')
    for overlap in (0,1,2):
        a=make_shaft_instance(2,[(0,0,1),(1,1,1),(0,1,1)],[1,1,3],profiles=1,physical=True,asset_groups=[0,1,2])
        # Move the bundle owner's consistent fixed template; positions x=1.5,1,.5.
        x=1.5-.5*overlap
        from cfar.synthetic_star import rectangle
        shape=rectangle(x,.5,3.5 if overlap==2 else x+1,1.5)
        for c in a['connections']:
            if c['geometry']['asset_id']=='asset-group-2':
                for field in ('landings','footprints'):
                    for record in c['geometry'][field]:record['polygon']=deepcopy(shape)
        add('conflict-density',overlap,a,'bundle-owner footprint position/overlap',
            'graph, action/effect counts, demands, costs','Position and, at level2, footprint extent/cell arrangement change to vary conflicts; measured conflict count required.')
    write_json(output/'dataset.json',dict(cases=rows,classification='authored structural controlled inputs',
        protocol='One seed; descriptive family levels, not independent building samples. Couplings are explicit per family.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    build(p.parse_args().output)
