"""Full original-action objectives, including isolated vertex retirement."""
from copy import deepcopy
import pytest

from cfar.cp_sat import solve_cp_sat
from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.oracle import exact_oracle
from cfar.synthetic_shaft import make_shaft_instance


def asynchronous_instance():
    instance = make_shaft_instance(2,[(0,0,1),(0,0,2),(0,1,2)],[2,3,9],
                                  profiles=2,physical=True,asset_groups=[0,0,4])
    instance['actions'][1]['effects'][0]['permitted_profiles']=['profile1']
    # Q overlaps O only at the root-floor cell, and routes to another floor.
    # It must not create a later incident event at O's target component.
    q=next(c for c in instance['connections'] if c['connection_id']=='G4P0')
    q['v']='R2';q['geometry']['rise_m']=6
    for field in ('landings','footprints'):
        q['geometry'][field][1]['room_id']='R2'
    instance['connections']=[c for c in instance['connections'] if c['connection_id']!='G4P1']
    a=instance['actions'][2]
    a['effects']=a['effects'][:1];a['evidence_ids']=a['evidence_ids'][:1]
    a['geometry_certificate']['connection_ids']=a['geometry_certificate']['connection_ids'][:1]
    for o in instance['obligations']:o['target']='R1'
    return instance


def cases():
    result = authored_interface_scenarios()
    result['asynchronous'] = asynchronous_instance()
    same = deepcopy(result['asynchronous'])
    for obligation in same['obligations']:
        obligation['target']=obligation['source']
    result['source_is_target']=same
    impossible = deepcopy(result['asynchronous'])
    impossible['actions']=impossible['actions'][:1]
    result['unreachable_profile']=impossible
    ties = deepcopy(result['asynchronous'])
    for action in ties['actions']:
        action['cost']=0
    duplicate=deepcopy(ties['actions'][0]);duplicate['action_id']='A999'
    ties['actions'].append(duplicate)
    result['zero_cost_count_and_ids']=ties
    return result


@pytest.mark.parametrize('name',sorted(cases()))
def test_all_five_ablations_and_flow_equal_exhaustive_full_label(name):
    instance=cases()[name]
    expected=exact_oracle(instance)
    label=lambda r:(r['status'],r['cost'],r['selected'])
    for cells,vertices,compress in [(False,False,False),(True,False,False),
        (False,True,False),(True,True,False),(True,True,True)]:
        for order in ('canonical','reverse'):
            actual=solve_owned_interface(instance,compress=compress,
                release_dead_cells=cells,release_dead_vertices=vertices,event_order=order)
            assert label(actual)==label(expected)
    assert label(solve_cp_sat(instance))==label(expected)


def test_asynchronous_example_reuses_owner_and_retires_profile_vertex():
    instance=asynchronous_instance()
    result=solve_owned_interface(instance,compress=False,release_dead_cells=True,release_dead_vertices=True)
    assert result['selected']==['A000','A001']
    assert result['cost']=='5'
    assert result['statistics']['released_vertices']>=2
    from cfar.interface_recognition import recognize_physical_interface
    recognized=recognize_physical_interface(instance)
    unit=next(u for u in recognized['units'] if 'A000' in u['action_ids'])
    assert unit['action_ids']==['A000','A001']
    # Profile0's target has its final incident event at the first action,
    # strictly before this complete ownership unit closes.
    target=next(o['target'] for o in instance['obligations'] if o['profile_id']=='profile0')
    catalog={c['connection_id']:c for c in instance['connections']}
    incident=[a['action_id'] for a in instance['actions'] if any(
        'profile0' in e['permitted_profiles'] and target in (catalog[e['connection_id']]['u'],catalog[e['connection_id']]['v'])
        for e in a['effects'])]
    assert incident==['A000']
