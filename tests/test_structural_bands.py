import importlib.util
from pathlib import Path
import sys
import pytest
from cfar.dp_owned_interface import solve_owned_interface
from cfar.actions import apply_actions
from cfar.obligations import verify_obligations

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_structural_band_study import structural_instance,VARIANTS
from local_band_reference import solve


@pytest.mark.parametrize('variant',VARIANTS)
def test_structural_variants_match_full_label_and_replay(variant):
    a=structural_instance(3,variant);x=solve(a)
    y=solve_owned_interface(a,compress=False,release_dead_cells=True,release_dead_vertices=True)
    assert (x['cost'],x['selected'])==(y['cost'],y['selected'])
    repaired=apply_actions(a,x['selected'])
    assert verify_obligations(repaired['instance'],repaired['active'])['satisfied']


def test_prices_frozen_while_boundary_conflicts_change():
    from cfar.interface_recognition import recognize_physical_interface
    cases=[structural_instance(3,v) for v in VARIANTS]
    assert all([x['cost'] for x in a['actions']]==[x['cost'] for x in cases[0]['actions']] for a in cases)
    conflicts=[recognize_physical_interface(a)['geometry_conflicts'] for a in cases]
    assert conflicts[0]!=conflicts[1] and conflicts[0]!=conflicts[2]
