import importlib.util
from pathlib import Path
import pytest
from cfar.dp_owned_interface import solve_owned_interface
from cfar.oracle import exact_oracle


def script(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).resolve().parents[1]/'scripts'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


generate=script('build_local_band_study').instance
reference=script('local_band_reference').solve


def test_reference_full_label_matches_independent_subset_oracle():
    a=generate(1);x=reference(a);y=exact_oracle(a)
    assert (x['cost'],x['selected'])==(y['cost'],y['selected'])


@pytest.mark.parametrize('seed',[0,1,2])
def test_reference_and_physical_dp_agree_on_coupled_bands(seed):
    a=generate(3,seed);x=reference(a)
    y=solve_owned_interface(a,compress=False,release_dead_cells=True,release_dead_vertices=True)
    assert (x['cost'],x['selected'])==(y['cost'],y['selected'])
    assert x['maximum_boundary_states']<=8


def test_reference_rejects_geometry_outside_admitted_class():
    a=generate(2);a['connections'][0]['geometry']['footprints'][0]['polygon'][0][0]+=.1
    with pytest.raises(AssertionError):reference(a)
