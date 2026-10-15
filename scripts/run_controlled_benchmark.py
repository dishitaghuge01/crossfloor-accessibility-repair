"""Frozen controlled benchmark; each measurement runs in a bounded subprocess."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
from time import perf_counter

from cfar.certificates import make_certificate, verify_certificate
from cfar.dp_owned_interface import solve_owned_interface
from cfar.errors import ValidationError
from cfar.interface_recognition import recognize_physical_interface
from cfar.interface_scenarios import (authored_interface_scenarios, branching_interface_probe,
    branching_rooms_probe, coupled_owner_probe, dense_alternative_probe)
from cfar.io import manifest, write_json
from cfar.oracle import exact_oracle
from cfar.synthetic_shaft import make_shaft_instance


def cases():
    for name, instance in authored_interface_scenarios().items():
        yield name, 0, 'correctness-small', instance
    yield 'cyclic', 0, 'correctness-small', branching_interface_probe()
    yield 'rooms', 0, 'correctness-small', branching_rooms_probe()
    for h in (2, 3, 4, 8, 16):
        yield f'owners-{h}', 0, 'correctness-small' if h <= 4 else 'scaling-large', coupled_owner_probe(h)
    for n in (8, 32, 64, 128):
        yield f'dense-{n}', 0, 'analytical', dense_alternative_probe(n)
    for seed in (0, 1, 2, 3, 4, 5):
        rng = random.Random(seed)
        for edges, profiles in ((2, 1), (4, 2), (6, 3)):
            intervals = [(rng.randrange(edges), edges-1, rng.randint(1, profiles)) for _ in range(6)]
            instance = make_shaft_instance(edges, intervals, [rng.randint(0, 8)/4 for _ in intervals],
                profiles=profiles, physical=True, asset_groups=[rng.randrange(4) for _ in intervals])
            yield f'shaft-{edges}-{profiles}-{seed}', seed, 'correctness-small', instance
    rejected = branching_rooms_probe()
    rejected['actions'][0]['requires'] = ['B']
    yield 'unsupported-dependency', 0, 'scope-control', rejected
    yield 'state-limit', 0, 'limit-control', branching_interface_probe()
    tiny = authored_interface_scenarios()['shared_asset']
    from cfar.synthetic_star import rectangle
    for connection in tiny['connections']:
        if connection['geometry']['asset_id'] == 'asset-group-1':
            for field in ('landings', 'footprints'):
                for record in connection['geometry'][field]:
                    record['polygon'] = rectangle(.500000001, .5, 1.500000001, 1.5)
    yield 'tiny-arrangement', 0, 'scope-control', tiny


def worker(input_path, method, output, max_states):
    instance = json.loads(Path(input_path).read_text(encoding='utf-8'))
    started = perf_counter()
    try:
        if method == 'recognition':
            result = recognize_physical_interface(instance)
            result['status'] = 'recognized'
        elif method == 'oracle':
            result = exact_oracle(instance, max_actions=8)
        elif method == 'cp-sat':
            from cfar.cp_sat import solve_cp_sat
            result = solve_cp_sat(instance, time_limit=55, seed=0)
        elif method == 'greedy':
            from cfar.greedy import solve_greedy
            result = solve_greedy(instance)
        else:
            result = solve_owned_interface(instance, compress=method == 'compressed', max_states=max_states)
        elapsed = perf_counter()-started
        payload = dict(status=result['status'], elapsed_seconds=elapsed, result=result)
        if method == 'oracle':
            certificate = make_certificate(instance, result)
            verification = verify_certificate(instance, certificate)
            if not verification['valid']:
                raise RuntimeError('certificate replay failed')
            payload.update(certificate=certificate, verification=verification)
    except ValidationError as error:
        status = 'limit-exceeded' if 'LIMIT' in error.code else 'unsupported'
        payload = dict(status=status, elapsed_seconds=perf_counter()-started, error_code=error.code, error=str(error))
    write_json(output, payload)


def run(output, repetitions=3, timeout=60, audit_path=None, optimizers=False):
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('choose a new empty output directory')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    if subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip():
        raise ValueError('commit benchmark source before collecting clean-revision evidence')
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    protocol = dict(version=3, repetitions=repetitions, timeout_seconds=timeout,
        oracle_max_actions=8, max_states=100000, max_cut_columns=65536,
        git_revision=revision, runner_sha256=script_hash, timing='worker function wall time; DP includes recognition')
    protocol['script_fingerprints'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}
    protocol['optimizers'] = optimizers
    if optimizers:
        import importlib.metadata
        protocol.update(ortools=importlib.metadata.version('ortools'), cp_sat_workers=1,
                        cp_sat_total_budget_seconds=55, cp_sat_seed=0)
    if audit_path:
        from duplex_controlled import building_cases
        protocol['building_provenance'] = json.loads((audit_path/'provenance.json').read_text())
        recipes = building_cases(audit_path)
    else:
        recipes = cases()
    write_json(output/'protocol.json', protocol)
    for name, seed, category, instance in recipes:
        folder = output/name
        write_json(folder/'input.json', instance)
        methods = ['recognition', 'compressed', 'uncompressed']
        if optimizers:
            methods += ['cp-sat', 'greedy']
        if len(instance['actions']) <= 8 and category not in ('scope-control', 'limit-control'):
            methods.append('oracle')
        signatures = []
        for method in methods:
            for repetition in range(repetitions if method in ('compressed', 'uncompressed', 'recognition', 'cp-sat') else 1):
                target = folder/f'{method}-{repetition}.json'
                cap = 1 if category == 'limit-control' else 100000
                command = [sys.executable, str(Path(__file__).resolve()), '--worker',
                    str(folder/'input.json'), method, str(target), str(cap)]
                try:
                    completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
                    if completed.returncode:
                        payload = dict(status='error', stderr=completed.stderr)
                        write_json(target, payload)
                    else:
                        payload = json.loads(target.read_text(encoding='utf-8'))
                except subprocess.TimeoutExpired:
                    payload = dict(status='timeout', timeout_seconds=timeout)
                    write_json(target, payload)
                settings = dict(protocol, method=method, max_states=cap, category=category, repetition=repetition)
                write_json(target.with_suffix('.manifest.json'), manifest(instance, settings, payload['status'], seed))
                if method != 'recognition' and payload['status'] in ('optimal', 'infeasible'):
                    result = payload['result']
                    signature = (result['status'], result['cost'], result['selected'])
                    signatures.append(signature)
                    if category == 'analytical' and signature != ('optimal', '1', ['A0000']):
                        raise RuntimeError(f'analytical mismatch: {name}')
                if payload['status'] == 'error':
                    raise RuntimeError(f'worker failure saved: {target}')
        if signatures and any(signature != signatures[0] for signature in signatures):
            raise RuntimeError(f'cost/original-action agreement failure saved: {name}')
        print(name, flush=True)
    from summarize_controlled_benchmark import summarize
    summarize(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--repetitions', type=int, default=3, choices=(1, 3))
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--worker', nargs=4)
    parser.add_argument('--building-audit', type=Path)
    parser.add_argument('--optimizers', action='store_true')
    args = parser.parse_args()
    if args.worker:
        worker(*args.worker[:3], int(args.worker[3]))
    elif args.output and args.timeout > 0:
        run(args.output, args.repetitions, args.timeout, args.building_audit, args.optimizers)
    else:
        parser.error('output and positive timeout required')
