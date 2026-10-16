from copy import deepcopy
import pytest
from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_recognition import recognize_physical_interface
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.experiment_families import integrated_example, generate_instance
from cfar.errors import ValidationError


def sig(r): return r['status'], r['cost'], r['selected']

@pytest.mark.parametrize('name', sorted(authored_interface_scenarios()))
def test_reversed_events_and_index_preserve_exact_label(name):
    a = authored_interface_scenarios()[name]
    expected = sig(solve_owned_interface(a))
    assert sig(solve_owned_interface(a, event_order='reverse')) == expected
    assert sig(solve_owned_interface(a, spatial_index=True)) == expected
    plain = recognize_physical_interface(a, profile=True)
    indexed = recognize_physical_interface(a, profile=True, spatial_index=True)
    for field in ['cells','action_cells','units','geometry_conflicts','blocked','parameters']:
        assert plain[field] == indexed[field]
    assert indexed['operation_counts']['cell_owner_coverage_tests'] <= plain['operation_counts']['cell_owner_coverage_tests']

@pytest.mark.parametrize('a', [generate_instance('catalogue', 2), generate_instance('support', 2), integrated_example()])
def test_history_mode_preserves_exact_label(a):
    assert sig(solve_owned_interface(a, compress=False, dominance=False, max_states=100000)) == sig(solve_owned_interface(a))

def test_caps_and_cache_settings_are_explicit():
    a=integrated_example()
    with pytest.raises(ValidationError, match='INTERFACE_ABLATION'):
        solve_owned_interface(a, dominance=False)
    with pytest.raises(ValidationError, match='INTERFACE_STATE_LIMIT'):
        solve_owned_interface(a, compress=False, dominance=False, max_states=1)
    cache=recognize_physical_interface(a, spatial_index=True)
    before=deepcopy(cache)
    solve_owned_interface(a, spatial_index=True, recognized_cache=cache, event_order='reverse')
    assert cache == before
    with pytest.raises(ValidationError, match='INTERFACE_CACHE'):
        solve_owned_interface(a, recognized_cache=cache)
