"""Full original-action objectives, including isolated vertex retirement."""
from copy import deepcopy
import pytest

from cfar.cp_sat import solve_cp_sat
from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.oracle import exact_oracle
from cfar.synthetic_shaft import make_shaft_instance


def asynchronous_instance():
    instance = make_shaft_instance(1,[(0,0,1),(0,0,2),(0,0,2)],[2,3,9],
                                  profiles=2,physical=True,asset_groups=[0,0,4])
    instance['actions'][1]['effects'][0]['permitted_profiles']=['profile1']
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
