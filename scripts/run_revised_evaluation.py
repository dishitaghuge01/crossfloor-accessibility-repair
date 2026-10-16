"""Fresh-process, nullable evidence for the revised-paper evaluation."""
import argparse
from decimal import Decimal
from fractions import Fraction
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

from cfar.io import fingerprint, manifest, write_json

METHODS = ['compressed', 'uncompressed', 'cp-sat', 'greedy', 'greedy-improved']


def worker(source, method, target, budget):
    from cfar.actions import apply_actions
    from cfar.certificates import make_certificate, verify_certificate
    from cfar.cp_sat import solve_cp_sat
    from ortools.sat.python import cp_model  # exclude optional solver imports from function timing
    from cfar.dp_owned_interface import solve_owned_interface
    from cfar.errors import ValidationError
    from cfar.greedy import solve_greedy
    from cfar.interface_recognition import recognize_physical_interface
    from cfar.obligations import verify_obligations
    from cfar.oracle import exact_oracle
    import psutil
    instance = json.loads(Path(source).read_text())
    cache = recognize_physical_interface(instance, profile=True) if method == 'cached' else None
    started = perf_counter()
    result = {}
    try:
        if method == 'cp-sat':
            result = solve_cp_sat(instance, time_limit=float(budget), seed=0)
        elif method.startswith('greedy'):
            result = solve_greedy(instance, improve=method == 'greedy-improved', exchange_budget=100)
        elif method == 'oracle':
            result = exact_oracle(instance, max_actions=8)
        else:
            result = solve_owned_interface(instance, compress=method != 'uncompressed',
                max_states=1 if Path(source).parent.name == 'state-limit' else 100000,
                prune_irrelevant=method == 'pruned', profile=True, recognized_cache=cache)
        status = result['status']
    except ValidationError as e:
        status = 'limit_exceeded' if 'LIMIT' in e.code else 'unsupported'
        result = dict(error_code=e.code, error=str(e))
    function_seconds = perf_counter()-started
    replay_started = perf_counter()
    replay = None
    selected = result.get('selected')
    if selected is None:
        selected = result.get('incumbent', {}).get('selected')
    if selected is not None:
        repaired = apply_actions(instance, selected)
        replay = dict(satisfied=verify_obligations(repaired['instance'], repaired['active'])['satisfied'],
            delta_A=sum(v['delta'] for v in repaired['adjacency'].values()))
        if not replay['satisfied'] or replay['delta_A']:
            raise RuntimeError('full repair replay failed')
    certificate_path = None
    if method == 'oracle':
        certificate = make_certificate(instance, result)
        checked = verify_certificate(instance, certificate, max_actions=8)
        if not checked['valid']:
            raise RuntimeError('independent certificate replay failed')
        certificate_path = str(Path(target).with_suffix('.certificate.json'))
        write_json(certificate_path, certificate)
    replay_seconds = perf_counter()-replay_started
    memory = psutil.Process().memory_info()
    peak = getattr(memory, 'peak_wset', None)
    if peak is None:
        import resource
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024)
    write_json(target, dict(status=status, result=result, function_seconds=function_seconds,
        independent_replay_seconds=replay_seconds, peak_memory_bytes=peak, replay=replay,
        certificate_path=certificate_path))


def recipes(smoke=False):
    from cfar.experiment_families import generate_instance, integrated_example
    if not smoke:
        from run_controlled_benchmark import cases
        for name,seed,category,instance in cases():
            yield name,category,seed,instance
    yield 'integrated-example','worked-example',0,integrated_example()
    settings = {'catalogue':[8,32,128], 'ownership':[2,4,8], 'profiles':[1,2,3,4],
                'connectivity':[3,4,5,6,7], 'support':[2,3,5,8], 'rooms':[0,4,12]}
    for family, sizes in settings.items():
        for size in sizes[:1] if smoke else sizes:
            for seed in ([0] if smoke or family != 'connectivity' else [0,1,2]):
                yield f'{family}-{size}-s{seed}', family, seed, generate_instance(family,size,seed)


def run(output, instances=None, smoke=False, repetitions=5):
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip():
        raise ValueError('commit source before measuring')
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('fresh empty output required')
    import psutil
    settings = dict(version=1, repetitions=repetitions, expensive_repetitions=3, timeout_seconds=60,
        solver_budget_seconds=55, seeds=[0,1,2], exchange_budget=100,
        startup='excluded from function_seconds; included in end_to_end_seconds',
        memory='whole fresh worker process peak RSS including imports; no enforced memory cap',
        cpu=platform.processor(), logical_cpus=psutil.cpu_count(), physical_cpus=psutil.cpu_count(logical=False),
        ram_bytes=psutil.virtual_memory().total,
        packages={p:importlib.metadata.version(p) for p in ['ortools','psutil','shapely','numpy']})
    write_json(output/'protocol.json', settings)
    items = [(p.stem,'building-derived-controlled',0,json.loads(p.read_text())) for p in sorted(instances.glob('*.json'))] if instances else list(recipes(smoke))
    records=[]
    for name,family,seed,instance in items:
        folder=output/name
        write_json(folder/'input.json',instance)
        from cfar.interface_recognition import recognize_physical_interface
        try:
            recognition=recognize_physical_interface(instance)
            measured_parameters=recognition['parameters']
            write_json(folder/'recognition.json',recognition)
        except ValueError:
            measured_parameters=None
        methods=METHODS+(['pruned','cached'] if family in {'rooms','connectivity'} else [])
        if len(instance['actions'])<=8 and family not in {'scope-control','limit-control'}:
            methods+=['oracle']
        exact=[]
        for method in methods:
            count=1 if method=='oracle' else (3 if len(instance['actions'])>=100 or (family=='connectivity' and len(instance['floors'])>=7) else repetitions)
            for repeat in range(count):
                target=folder/f'{method}-{repeat}.json'
                command=[sys.executable,str(Path(__file__).resolve()),'--worker',str(folder/'input.json'),method,str(target),'55']
                start=perf_counter()
                try:
                    process=subprocess.run(command,capture_output=True,text=True,timeout=60)
                    if process.returncode:
                        payload=dict(status='internal_error',result={},stderr=process.stderr)
                        write_json(target,payload)
                    else:
                        payload=json.loads(target.read_text())
                except subprocess.TimeoutExpired:
                    payload=dict(status='timeout',result={})
                    write_json(target,payload)
                wall=perf_counter()-start
                result=payload['result']; stats=result.get('statistics') or {}; phases=result.get('phase_seconds') or {}
                cost=result.get('cost') or result.get('incumbent',{}).get('cost')
                selected=result.get('selected')
                if selected is None: selected=result.get('incumbent',{}).get('selected')
                bound=result.get('best_cost_bound')
                if result.get('status')=='optimal': bound=cost
                gap=None
                if cost is not None and bound is not None:
                    c,b=Fraction(str(cost)),Fraction(str(bound))
                    gap=float(max(Fraction(0),c-b)/abs(c)) if c else (0.0 if b==0 else None)
                row=dict(experiment_id=output.name,instance_id=name,source_building_id=instance.get('source_building_id'),
                    instance_sha256=fingerprint(instance),generator_family=family,seed=seed,solver=method,
                    solver_configuration=dict(timeout_seconds=60,internal_seconds=55,exchange_budget=100),
                    repeat_index=repeat,status=payload['status'],objective_cost=cost,
                    objective_action_count=len(selected) if selected is not None else None,selected_action_ids=selected,
                    best_bound=bound,relative_cost_gap=gap,end_to_end_seconds=wall,
                    function_seconds=payload.get('function_seconds'),recognition_seconds=phases.get('recognition'),
                    optimization_seconds=phases.get('optimization'),replay_seconds=payload.get('independent_replay_seconds'),
                    peak_memory_bytes=payload.get('peak_memory_bytes'),peak_raw_states=stats.get('peak_raw_states'),
                    peak_retained_states=stats.get('peak_retained_states'),certificate_path=payload.get('certificate_path'),
                    parameters=result.get('parameters',measured_parameters),phase_seconds=result.get('phase_seconds'),statistics=stats,
                    replay=payload.get('replay'),raw_record=str(target.relative_to(output)))
                metadata=manifest(instance,dict(settings,method=method,repeat_index=repeat),row['status'],seed)
                row['code_commit']=metadata['git_revision']
                write_json(target.with_suffix('.manifest.json'),metadata)
                if method not in {'greedy','greedy-improved'} and row['status'] in {'optimal','infeasible'}:
                    exact.append((row['status'],cost,selected))
                records.append(row)
                write_json(output/'records.json',records)
        if any(label!=exact[0] for label in exact):
            raise RuntimeError('exact-label disagreement: '+name)
        print(name, 'records',len(records),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path); p.add_argument('--instances',type=Path)
    p.add_argument('--smoke',action='store_true'); p.add_argument('--repetitions',type=int,choices=[1,3,5],default=5)
    p.add_argument('--worker',nargs=4)
    a=p.parse_args()
    if a.worker: worker(*a.worker)
    elif a.output: run(a.output,a.instances,a.smoke,a.repetitions)
    else: p.error('--output required')
