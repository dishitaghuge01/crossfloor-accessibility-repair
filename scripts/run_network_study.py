"""Pinned new campaign: unchanged and last-use DP, same-model CP-SAT, greedy.

Fresh workers; repeat-major rotated order; failed/capped outcomes retained.
Development probes must use --development and are never confirmatory evidence.
"""
import argparse
from fractions import Fraction
import hashlib,json,subprocess,sys,platform,importlib.metadata
from pathlib import Path
from time import perf_counter
from cfar.io import manifest,write_json,fingerprint

CONFIG={'compressed':dict(compress=True),'uncompressed':dict(compress=False),
        'cells-uncompressed':dict(compress=False,release_dead_cells=True),
        'lifetime-compressed':dict(compress=True,release_dead_cells=True,release_dead_vertices=True),
        'lifetime-uncompressed':dict(compress=False,release_dead_cells=True,release_dead_vertices=True)}


def worker(source,method,target,budget):
    from cfar.dp_owned_interface import solve_owned_interface
    from cfar.cp_sat import solve_cp_sat
    from cfar.greedy import solve_greedy
    from cfar.errors import ValidationError
    from cfar.actions import apply_actions
    from cfar.obligations import verify_obligations
    from audit_revised_evidence import paid_rectangles
    from ortools.sat.python import cp_model
    import psutil
    a=json.loads(Path(source).read_text());start=perf_counter()
    try:
        if method in CONFIG:r=solve_owned_interface(a,profile=True,max_states=100000,**CONFIG[method])
        elif method=='cp-sat':r=solve_cp_sat(a,time_limit=float(budget),seed=0)
        elif method=='oracle':
            from cfar.oracle import exact_oracle
            r=exact_oracle(a,max_actions=8)
        else:r=solve_greedy(a,improve=True,exchange_budget=100)
        status=r['status']
    except ValidationError as e:
        r=dict(error_code=e.code,error=str(e));status='limit_exceeded' if 'LIMIT' in e.code else 'unsupported'
    elapsed=perf_counter()-start
    ids=r.get('selected');ids=ids if ids is not None else r.get('incumbent',{}).get('selected')
    replay=None
    if ids is not None:
        repaired=apply_actions(a,ids)
        assert verify_obligations(repaired['instance'],repaired['active'])['satisfied']
        assert not any(x['delta'] for x in repaired['adjacency'].values())
        assert paid_rectangles(a,ids)==Fraction(r.get('cost') or r['incumbent']['cost'])
        replay=dict(satisfied=True,delta_A=0,paid_box_cost=True)
    mem=psutil.Process().memory_info()
    write_json(target,dict(status=status,result=r,function_seconds=elapsed,replay=replay,
        peak_memory_bytes=getattr(mem,'peak_wset',mem.rss)))


def run(inputs,output,repeats,timeout,methods,development=False,confirmatory=False):
    dirty=bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip())
    if dirty and not development:raise ValueError('commit before confirmatory evidence')
    output.mkdir(parents=True,exist_ok=False)
    protocol=dict(repetitions=repeats,timeout_seconds=timeout,cp_sat_seconds=timeout-3,
        methods=methods,configurations=CONFIG,max_states=100000,max_cut_columns=65536,
        order='repeat-major, methods rotated by repeat, cases lexicographic; fresh processes',
        timing='function wall time including recognition and full solve replay, excluding imports; separate parent wall time includes startup',
        development=development,git_dirty=dirty,platform=platform.platform(),
        confirmatory=confirmatory,
        repeat_policy='seed0: lifetime-uncompressed and CP-SAT three times; original uncompressed and greedy once; other seeds: lifetime-uncompressed and CP-SAT once; seed0 cell-only and compressed once' if confirmatory else 'all requested methods/repetitions',
        runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        packages={p:importlib.metadata.version(p) for p in ('ortools','numpy','shapely','psutil')})
    write_json(output/'protocol.json',protocol);records=[]
    paths=sorted(inputs.glob('*.json'))
    for path in paths:write_json(output/path.stem/'input.json',json.loads(path.read_text()))
    for repeat in range(repeats):
        order=methods[repeat%len(methods):]+methods[:repeat%len(methods)]
        for path in paths:
            a=json.loads(path.read_text());folder=output/path.stem
            for method in order:
                if confirmatory:
                    seed0=path.stem.endswith('-s0')
                    if not seed0 and (repeat or method not in ('lifetime-uncompressed','cp-sat')):continue
                    if seed0 and repeat and method not in ('lifetime-uncompressed','cp-sat'):continue
                target=folder/f'{method}-{repeat}.json';started=perf_counter()
                try:
                    p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(folder/'input.json'),method,str(target),str(timeout-3)],capture_output=True,text=True,timeout=timeout)
                    payload=json.loads(target.read_text()) if p.returncode==0 else dict(status='internal_error',result={},stderr=p.stderr)
                except subprocess.TimeoutExpired:payload=dict(status='timeout',result={})
                wall=perf_counter()-started;write_json(target,payload)
                metadata=manifest(a,dict(protocol,method=method,repeat=repeat),payload['status'],0)
                write_json(target.with_suffix('.manifest.json'),metadata)
                records.append(dict(case=path.stem,method=method,repeat=repeat,input_fingerprint=fingerprint(a),
                    code_commit=metadata['git_revision'],raw_record=target.relative_to(output).as_posix(),
                    end_to_end_seconds=wall,**payload));write_json(output/'records.json',records)
                print(path.stem,repeat,method,payload['status'],round(payload.get('function_seconds',wall),3),flush=True)
    for path in paths:
        rows=[r for r in records if r['case']==path.stem and r['status'] in ('optimal','infeasible')]
        labels=[(r['status'],r['result'].get('cost'),r['result'].get('selected')) for r in rows]
        if labels and any(x!=labels[0] for x in labels):raise RuntimeError('exact-label disagreement '+path.stem)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',nargs=4);p.add_argument('--instances',type=Path)
    p.add_argument('--output',type=Path);p.add_argument('--repeats',type=int,default=3);p.add_argument('--timeout',type=float,default=30)
    p.add_argument('--methods',nargs='+',default=list(CONFIG)+['cp-sat','greedy-improved'])
    p.add_argument('--development',action='store_true');p.add_argument('--confirmatory',action='store_true');a=p.parse_args()
    if a.worker:worker(*a.worker)
    else:run(a.instances,a.output,a.repeats,a.timeout,a.methods,a.development,a.confirmatory)
