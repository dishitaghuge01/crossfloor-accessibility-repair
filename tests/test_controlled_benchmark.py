import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from run_controlled_benchmark import cases, worker
from summarize_controlled_benchmark import summarize
from cfar.io import write_json
import json


def test_worker_oracle_and_modes(tmp_path):
    from cfar.interface_scenarios import branching_rooms_probe
    input_path = tmp_path/'input.json'
    write_json(input_path, branching_rooms_probe())
    signatures = []
    for method in ('compressed', 'uncompressed', 'oracle'):
        target = tmp_path/f'{method}.json'
        worker(input_path, method, target, 100000)
        payload = json.loads(target.read_text())
        r = payload['result']
        signatures.append((r['status'], r['cost'], r['selected']))
        assert payload['elapsed_seconds'] >= 0
        if method == 'oracle':
            assert payload['verification']['valid']
    assert signatures == [('optimal', '3', ['A'])]*3


def test_limit_and_unsupported_are_not_infeasible(tmp_path):
    inputs = {name: instance for name, _, _, instance in cases()}
    for name, cap, status in [('state-limit', 1, 'limit-exceeded'), ('unsupported-dependency', 100000, 'unsupported')]:
        source = tmp_path/f'{name}.json'
        target = tmp_path/f'{name}-result.json'
        write_json(source, inputs[name])
        worker(source, 'compressed', target, cap)
        assert json.loads(target.read_text())['status'] == status


def test_summary_preserves_censoring(tmp_path):
    folder = tmp_path/'probe'
    for i, value in enumerate([dict(status='optimal', elapsed_seconds=1, result=dict(cost='1', selected=['A'])), dict(status='timeout')]):
        target = folder/f'compressed-{i}.json'
        write_json(target, value)
        write_json(target.with_suffix('.manifest.json'), dict(git_dirty=False, git_revision='abc', settings=dict(category='analytical')))
    row = summarize(tmp_path)[0]
    assert row['statuses'] == 'optimal,timeout'
    assert row['median_seconds'] == ''
