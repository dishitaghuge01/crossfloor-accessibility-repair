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
    for selected in [['A002','A001'],['A000','E']]:
        with pytest.raises(ValueError,match='PORTAL_COLLISION'):apply_actions(a,selected)
    repair=apply_actions(a,expected[2])
    assert 'SPARE' in repair['active']
