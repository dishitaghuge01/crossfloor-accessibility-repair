"""Separate instrumented rerun; never modifies historical campaign records.

JSONL events are flushed individually so external termination retains stage and
candidate evidence. Candidates from callbacks are NOT verified repairs. Parent
replay is timed separately and cannot count as completion within the deadline.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from time import perf_counter

from cfar.io import fingerprint, manifest, write_json


def worker(source, target, budget):
    from cfar.cp_sat import solve_cp_sat
    instance = json.loads(Path(source).read_text())
    with Path(target).with_suffix('.events.jsonl').open('w', encoding='utf-8', buffering=1) as stream:
        def progress(event):
            stream.write(json.dumps(event, allow_nan=False)+'\n')
            stream.flush()
        result = solve_cp_sat(instance, time_limit=budget, seed=0, progress=progress)
    write_json(target, result)


def run(source, output, timeout, repeats):
    from cfar.actions import apply_actions
    from cfar.obligations import verify_obligations
    if subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip():
        raise ValueError('Commit instrumented revision before diagnostic campaign')
    output.mkdir(parents=True, exist_ok=False)
    instance = json.loads(source.read_text())
    write_json(output/'input.json', instance)
    protocol = dict(campaign='cp-stage-diagnostic', role='posthoc_diagnostic',
        timeout_seconds=timeout, cp_sat_seconds=timeout-3, repetitions=repeats,
        solver_seed=0, enforced_ram_cap=None,
        timing='External deadline includes worker imports, recognition, model, all stages and solver replay; parent audit outside deadline',
        input_fingerprint=fingerprint(instance))
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    protocol['code_revision'] = revision
    write_json(output/'protocol.json', protocol)
    rows = []
    for repeat in range(repeats):
        if (subprocess.check_output(['git','status','--porcelain'],text=True).strip() or
            subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=revision):
            write_json(output/'INVALIDATED.json', dict(reason='Code changed during campaign'))
            raise RuntimeError('Code changed during campaign')
        target = output/f'cp-sat-{repeat}.json'
        started = perf_counter()
        try:
            p = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker',
                str(output/'input.json'), str(target), str(timeout-3)],
                capture_output=True, text=True, timeout=timeout)
            result = json.loads(target.read_text()) if p.returncode == 0 else dict(status='internal_error', stderr=p.stderr)
        except subprocess.TimeoutExpired:
            result = dict(status='timeout')
        elapsed = perf_counter()-started
        if (subprocess.check_output(['git','status','--porcelain'],text=True).strip() or
            subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=revision):
            write_json(output/'INVALIDATED.json', dict(reason='Code changed during campaign'))
            raise RuntimeError('Code changed during campaign')
        trace_path = target.with_suffix('.events.jsonl')
        trace = [json.loads(line) for line in trace_path.read_text().splitlines()] if trace_path.exists() else []
        last_stage = next((e for e in reversed(trace) if e['event']=='stage_started'), None)
        candidate = next((e for e in reversed(trace) if e['event']=='incumbent'), None)
        audit = None
        if candidate:
            audit_start = perf_counter()
            repair = apply_actions(instance, candidate['selected'])
            audit = dict(satisfied=verify_obligations(repair['instance'],repair['active'])['satisfied'],
                         seconds=perf_counter()-audit_start, outside_deadline=True,
                         selected=candidate['selected'], cost=candidate['cost'])
            assert audit['satisfied']
        row = dict(repeat_index=repeat, status=result['status'], end_to_end_seconds=elapsed,
                   last_started_stage=last_stage, parent_audit=audit, result=result)
        write_json(target.with_suffix('.manifest.json'), manifest(instance,protocol,row['status'],0))
        rows.append(row)
        write_json(output/'records.json', rows)
        print(repeat, row['status'], last_stage, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--worker', nargs=3)
    p.add_argument('--instance', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--timeout', type=float, default=30)
    p.add_argument('--repeats', type=int, default=3)
    a = p.parse_args()
    if a.worker:
        worker(a.worker[0], a.worker[1], float(a.worker[2]))
    else:
        run(a.instance.resolve(), a.output.resolve(), a.timeout, a.repeats)
