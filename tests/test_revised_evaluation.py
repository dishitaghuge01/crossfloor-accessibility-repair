from copy import deepcopy
from decimal import Decimal

import pytest
from cfar.dp_owned_interface import solve_owned_interface
from cfar.experiment_families import generate_instance
from cfar.interface_recognition import recognize_physical_interface
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.io import fingerprint


def signature(instance, **settings):
    r=solve_owned_interface(instance, **settings)
    return r['status'],r['cost'],r['selected']


@pytest.mark.parametrize('name',sorted(authored_interface_scenarios()))
def test_translation_permutation_and_cost_scale(name):
    original=authored_interface_scenarios()[name]
    changed=deepcopy(original)
    def move(points):return [[x+16,y-8] for x,y in points]
    for f in changed['floors']:
        f['boundary']=move(f['boundary'])
        for r in f['rooms']:r['polygon']=move(r['polygon'])
        for key in ['obstacles','reserved_portal_zones']:f[key]=[move(p) for p in f[key]]
        f['rooms'].reverse();f['access_edges'].reverse()
    moved=set()
    for c in changed['connections']:
        for key in ['landings','footprints']:
            for r in c['geometry'].get(key,[]):
                if id(r) not in moved:
                    moved.add(id(r));r['polygon']=move(r['polygon'])
        if 'opening' in c['geometry']:c['geometry']['opening']=move(c['geometry']['opening'])
    changed['actions'].reverse();changed['connections'].reverse();changed['floors'].reverse()
    expected=signature(original)
    assert signature(changed)==expected
    for a in changed['actions']:a['cost']=float(Decimal(str(a['cost']))*Decimal('7.5'))
    actual=signature(changed)
    assert actual[0]==expected[0] and Decimal(actual[1])==Decimal(expected[1])*Decimal('7.5') and actual[2]==expected[2]


def test_duplicate_dominated_candidate_cannot_improve_and_cache_is_checked():
    instance=authored_interface_scenarios()['atomic_bundle']
    expected=signature(instance)
    extra=deepcopy(instance['actions'][0]);extra['action_id']='ZZ-dominated';extra['cost']=100
    instance['actions'].append(extra)
    assert signature(instance)==expected
    recognized=recognize_physical_interface(instance,profile=True)
    assert signature(instance,recognized_cache=recognized)==expected
    instance['actions'][-1]['cost']=101
    with pytest.raises(ValueError,match='INTERFACE_CACHE'):signature(instance,recognized_cache=recognized)


@pytest.mark.parametrize('family,size',[('catalogue',8),('ownership',3),('profiles',2),('support',5),('connectivity',5),('rooms',4)])
def test_seeded_structural_generators_and_valid_ablations(family,size):
    a=generate_instance(family,size,0)
    assert fingerprint(a)==fingerprint(generate_instance(family,size,0))
    old=signature(a,compress=False)
    assert signature(a,compress=True)==old
    assert signature(a,prune_irrelevant=True)==old
    result=solve_owned_interface(a,profile=True)
    assert all(v>=0 for v in result['phase_seconds'].values())
    assert result['recognition_operation_counts']['generated_cells']>=1


def test_integrated_example_paid_unused_collision_and_owner_reuse():
    from cfar.actions import apply_actions
    from cfar.experiment_families import integrated_example
    from cfar.oracle import exact_oracle
    a=integrated_example()
    expected=('optimal','5',['A000','A001'])
    assert signature(a)==expected
    o=exact_oracle(a)
    assert (o['status'],o['cost'],o['selected'])==expected
    # Graph-cheap reuse competitor and paid-but-unused competitor both fail physically.
    for selected in [['A000','E']]:
        with pytest.raises(ValueError,match='PORTAL_COLLISION'):apply_actions(a,selected)
    from cfar.obligations import verify_obligations
    active={e['connection_id']:e['permitted_profiles'] for action in a['actions']
            if action['action_id'] in ['A000','E'] for e in action['effects']}
    assert verify_obligations(a,active)['satisfied']
    repair=apply_actions(a,expected[2])
    assert 'SPARE' in repair['active']


def test_identifier_renaming_and_unit_rescaling():
    import json
    original=authored_interface_scenarios()['shared_asset']
    # JSON roundtrip removes Python constructor aliases before coordinate edits.
    a=json.loads(json.dumps(original))
    for f in a['floors']:
        f['elevation_m']*=2
        for key in ['boundary']:
            f[key]=[[2*x,2*y] for x,y in f[key]]
        for r in f['rooms']:r['polygon']=[[2*x,2*y] for x,y in r['polygon']]
        for key in ['obstacles','reserved_portal_zones']:
            f[key]=[[[2*x,2*y] for x,y in p] for p in f[key]]
    for p in a['profiles']:
        for key in ['min_width_m','clearance_m']:p[key]*=2
    for c in a['connections']:
        for key in ['width_m','rise_m','run_m']:
            if key in c['geometry']:c['geometry'][key]*=2
        for key in ['landings','footprints']:
            for r in c['geometry'].get(key,[]):r['polygon']=[[2*x,2*y] for x,y in r['polygon']]
        if 'opening' in c['geometry']:c['geometry']['opening']=[[2*x,2*y] for x,y in c['geometry']['opening']]
    assert signature(a)==signature(original)
    identifiers=set()
    def collect(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key.endswith('_id') and isinstance(item,str):identifiers.add(item)
                collect(item)
        elif isinstance(value,list):
            for item in value:collect(item)
    collect(a)
    mapping={i:'renamed-'+i for i in identifiers}
    def rename(value):
        if isinstance(value,str):return mapping.get(value,value)
        if isinstance(value,list):return [rename(v) for v in value]
        if isinstance(value,dict):return {k:rename(v) for k,v in value.items()}
        return value
    result=signature(rename(a));expected=signature(original)
    assert result[:2]==expected[:2]
    assert result[2]==[mapping[i] for i in expected[2]]


def test_feasible_candidate_addition_and_empty_trivial_demand_contract():
    a=authored_interface_scenarios()['atomic_bundle']
    old=solve_owned_interface(a)
    extra=deepcopy(a['actions'][0]);extra.update(action_id='ZZ-new',cost=.5)
    a['actions'].append(extra)
    new=solve_owned_interface(a)
    assert Decimal(new['cost'])<=Decimal(old['cost'])
    for o in a['obligations']:o['target']=o['source']
    r=solve_owned_interface(a)
    assert r['selected']==[] and Decimal(r['cost'])==0
    a['obligations']=[]
    with pytest.raises(ValueError,match='SCHEMA|INTERFACE_ROOTED'):solve_owned_interface(a)


def test_independent_paid_rectangle_checker_finds_annex_collision():
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
    from audit_revised_evidence import paid_rectangles
    from cfar.experiment_families import integrated_example
    a=integrated_example()
    assert paid_rectangles(a,['A000','A001'])==5
    with pytest.raises(ValueError,match='paid-owner overlap'):paid_rectangles(a,['A000','E'])


def test_independent_owner_signature_check():
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
    from audit_revised_evidence import paid_rectangles
    from cfar.experiment_families import integrated_example
    a=integrated_example()
    # Different per-edge capabilities for the same physical owner are invalid.
    c=next(c for c in a['connections'] if c['connection_id']=='G0P2')
    c['physical_profiles']=['profile0']
    with pytest.raises(ValueError,match='owner consistency'):paid_rectangles(a,['A000','A001'])


@pytest.mark.parametrize('count',[2,3,4])
def test_untimed_geometry_operation_count_matches_private_pairs(count):
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
    from profile_recognition_operations import count_recognition
    from cfar.interface_scenarios import dense_alternative_probe
    result=count_recognition(dense_alternative_probe(count))
    assert result['physical_footprint_pair_intersection_tests']==count*(count-1)//2
    assert result['generated_cells']==2
