"""Trace contract distinguishes cost proof, full ties and replay verification."""
import pytest

pytest.importorskip('ortools')
from cfar.cp_sat import solve_cp_sat
from cfar.interface_scenarios import branching_interface_probe
from cfar.oracle import exact_oracle


def test_trace_orders_stages_and_preserves_exact_objective():
    instance = branching_interface_probe()
    trace = []
    result = solve_cp_sat(instance, progress=trace.append)
    expected = exact_oracle(instance)
    assert (result['cost'], result['selected']) == (expected['cost'], expected['selected'])
    stages = [e['stage'] for e in trace if e['event'] == 'stage_started']
    assert stages[:2] == ['cost', 'count']
    assert set(stages[2:]) == {'identifier'}
    assert all(not e['replay_verified'] for e in trace if e['event'] == 'incumbent')
    verified = [e for e in trace if e['event'] == 'replay_finished']
    assert verified[0]['replay_verified']
    task = result['task_status']
    assert task['cost_stage_status'] == task['count_stage_status'] == task['id_stage_status'] == 'OPTIMAL'
    assert task['first_feasible_seconds'] <= task['cost_proof_seconds']
    assert task['best_cost_seconds'] <= task['cost_proof_seconds']
    assert trace[-1]['event'] == 'finished'


def test_presearch_deadline_has_no_fictitious_cost_proof():
    trace = []
    result = solve_cp_sat(branching_interface_probe(), time_limit=1e-12, progress=trace.append)
    assert result['status'] == 'limit_exceeded'
    assert result['task_status']['cost_stage_status'] == 'NOT_STARTED'
    assert result['task_status']['cost_proof_seconds'] is None
    assert result['task_status']['first_feasible_seconds'] is None
