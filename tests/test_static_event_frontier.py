import importlib.util
from pathlib import Path
import pytest
from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.interface_recognition import recognize_physical_interface


def script(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).resolve().parents[1]/'scripts'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


certify=script('event_frontier_certificate').certificate
bay=script('build_private_bay_study').instance
band=script('build_local_band_study').instance


@pytest.mark.parametrize('n',[1,2,4])
def test_private_bay_static_width_and_exact_analytic_objective(n):
    a=bay(n);rec=recognize_physical_interface(a);c=certify(a,rec)
    assert rec['parameters']['r']==rec['parameters']['z']==n
    assert c['b']==4 and c['max_potential_cells']==3
    assert c['max_resource_domain_product']==27
    r=solve_owned_interface(a,compress=False,profile=True,release_dead_cells=True,release_dead_vertices=True)
    assert r['cost']=='3' and r['selected']==['P0000C']
    assert r['statistics']['peak_live_vertex_union']<=c['max_potential_vertices']
    assert r['statistics']['peak_live_occupancy_cells']<=c['max_potential_cells']


@pytest.mark.parametrize('n',[2,4])
def test_local_band_frontier_is_independent_of_band_count(n):
    a=band(n);c=certify(a)
    assert c['b']==8 and c['max_resource_domain_product']==108
    assert c['max_potential_cells']==5


def test_local_band_cost_and_full_identifier_label_match_small_exhaustive_oracle():
    from cfar.oracle import exact_oracle
    a=band(1);oracle=exact_oracle(a)
    result=solve_owned_interface(a,compress=False,release_dead_cells=True,release_dead_vertices=True)
    assert (result['cost'],result['selected'])==(oracle['cost'],oracle['selected'])
    rec=recognize_physical_interface(band(2))
    assert any(x['actions'][0][:5]!=x['actions'][1][:5] for x in rec['geometry_conflicts'])


@pytest.mark.parametrize('order',['canonical','reverse'])
def test_static_frontier_dominates_observed_transient_unions(order):
    for a in authored_interface_scenarios().values():
        c=certify(a,order=order)
        r=solve_owned_interface(a,compress=False,profile=True,event_order=order,
            release_dead_cells=True,release_dead_vertices=True)
        assert r['statistics']['peak_live_vertex_union']<=c['max_potential_vertices']
        assert r['statistics']['peak_live_occupancy_cells']<=c['max_potential_cells']
