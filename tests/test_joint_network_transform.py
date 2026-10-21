import importlib.util
from pathlib import Path

from cfar.actions import apply_actions
from cfar.interface_recognition import recognize_physical_interface
from cfar.obligations import verify_obligations
from cfar.synthetic_shaft import make_shaft_instance

spec=importlib.util.spec_from_file_location('joint_generator',Path(__file__).resolve().parents[1]/'scripts/build_joint_network_study.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_interaction_tiers_keep_original_geometry_and_feasible_segment_control():
    base=make_shaft_instance(2,[(0,0,2),(1,1,2)],[3,4],profiles=2,physical=True,asset_groups=[0,0])
    for i,a in enumerate(base['actions']):a['action_id']=f'S{i:03d}'
    for tier in ('connectivity','resource','full'):
        result=module.transform(base,tier,stride=1)
        assert result['floors']==base['floors']
        control=[a['action_id'] for a in result['actions'] if a['action_id'].startswith('S')]
        repaired=apply_actions(result,control)
        assert verify_obligations(repaired['instance'],repaired['active'])['satisfied']
        recognized=recognize_physical_interface(result)
        assert bool(recognized['geometry_conflicts'])==(tier!='connectivity')
        if tier=='full':
            assert all(len(a['effects'][0]['permitted_profiles'])==1 for a in result['actions'] if a['action_id'].startswith('Q'))


def test_profile_metrics_do_not_change_complete_objective():
    from cfar.dp_owned_interface import solve_owned_interface
    from cfar.interface_scenarios import authored_interface_scenarios
    instance=authored_interface_scenarios()['shared_asset']
    result=solve_owned_interface(instance,compress=False,profile=True,release_dead_vertices=True,release_dead_cells=True)
    expected=solve_owned_interface(instance,compress=False,release_dead_vertices=True,release_dead_cells=True)
    assert (result['cost'],result['selected'])==(expected['cost'],expected['selected'])
    stats=result['statistics']
    for key in ('state_generation_seconds','state_merge_seconds','objective_label_seconds'):
        assert stats[key]>=0
    assert stats['peak_live_vertex_union']>=stats['peak_live_selected_vertices']
    assert stats['peak_owner_domain_size']>=2
