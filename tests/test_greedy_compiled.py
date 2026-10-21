from itertools import combinations
import pytest

from cfar.actions import apply_actions
from cfar.errors import ValidationError
from cfar.greedy import _compiled_selection, solve_greedy
from cfar.interface_recognition import recognize_physical_interface
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.obligations import verify_obligations


@pytest.mark.parametrize('name', sorted(authored_interface_scenarios()))
def test_compiled_proposals_equal_full_replay_for_every_selection(name):
    instance = authored_interface_scenarios()[name]
    recognized = recognize_physical_interface(instance)
    ids = sorted(a['action_id'] for a in instance['actions'])
    for size in range(len(ids)+1):
        for selection in combinations(ids,size):
            active = _compiled_selection(instance,recognized,selection)
            try:
                repair = apply_actions(instance,list(selection))
            except ValidationError:
                assert active is None
            else:
                assert active is not None
                assert {k:set(v) for k,v in active.items()} == {k:set(v) for k,v in repair['active'].items()}
                assert verify_obligations(instance,active)['satisfied'] == verify_obligations(repair['instance'],repair['active'])['satisfied']


def test_expired_improvement_keeps_verified_initial_repair():
    instance = authored_interface_scenarios()['atomic_bundle']
    seed = solve_greedy(instance)['selected']
    trace = []
    result = solve_greedy(instance,improve=True,time_limit=1e-12,initial_selected=seed,progress=trace.append)
    assert result['status']=='feasible'
    assert result['termination']=='deadline'
    assert result['selected']==seed
    assert trace[0]['replay_verified']
