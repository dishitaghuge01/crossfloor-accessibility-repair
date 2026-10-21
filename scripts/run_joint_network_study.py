"""Frozen, counterbalanced five-ablation comparison on joint interaction inputs."""
import argparse
import json
import subprocess
import sys
import platform
from pathlib import Path
from time import perf_counter

from cfar.io import fingerprint, manifest, write_json

CONFIG = {
    'floor':dict(compress=False),
    'cells':dict(compress=False,release_dead_cells=True),
    'vertices':dict(compress=False,release_dead_vertices=True),
    'both':dict(compress=False,release_dead_cells=True,release_dead_vertices=True),
    'both-rank':dict(compress=True,release_dead_cells=True,release_dead_vertices=True),
}
METHODS=list(CONFIG)+['cp-sat','greedy-cold','segment-control']


def worker(source,method,target,seconds):
    from cfar.actions import apply_actions
    from cfar.cp_sat import solve_cp_sat
    from cfar.dp_owned_interface import solve_owned_interface
    from cfar.errors import ValidationError
    from cfar.greedy import solve_greedy
    from cfar.objective import action_cost
    from cfar.obligations import verify_obligations
    import psutil
    instance=json.loads(Path(source).read_text())
    started=perf_counter()
    with Path(target).with_suffix('.events.jsonl').open('w',encoding='utf-8',buffering=1) as stream:
        def progress(event):
            stream.write(json.dumps(event,allow_nan=False)+'\n');stream.flush()
        try:
            if method in CONFIG:
                result=solve_owned_interface(instance,profile=True,max_states=100000,max_cut_columns=65536,**CONFIG[method])
            elif method=='cp-sat':
                result=solve_cp_sat(instance,time_limit=seconds-5,seed=0,progress=progress)
            elif method=='greedy-cold':
                result=solve_greedy(instance,improve=True,exchange_budget=100,time_limit=seconds-5,progress=progress,profile=True)
            elif method=='locality':
                from local_band_reference import solve
                from cfar.interface_recognition import recognize_physical_interface
                phase=perf_counter()
                recognize_physical_interface(instance)
                recognition=perf_counter()-phase
                phase=perf_counter();result=solve(instance);optimization=perf_counter()-phase
                phase=perf_counter();repair=apply_actions(instance,result['selected'])
                assert verify_obligations(repair['instance'],repair['active'])['satisfied']
                assert all(r['delta']==0 for r in repair['adjacency'].values())
                result['pipeline_phases']=dict(recognition_seconds=recognition,
                    optimization_seconds=optimization,replay_seconds=perf_counter()-phase)
            else:
                selected=sorted(a['action_id'] for a in instance['actions'] if a['action_id'].startswith('S'))
                repair=apply_actions(instance,selected)
                assert verify_obligations(repair['instance'],repair['active'])['satisfied']
                result=dict(status='feasible',selected=selected,cost=str(action_cost(instance,selected)),
                            method='all_original_segments',optimality_evidence=None)
                progress(dict(event='verified_incumbent',selected=selected,cost=result['cost'],
                              replay_verified=True,elapsed_seconds=perf_counter()-started))
        except ValidationError as error:
            result=dict(status='limit_exceeded' if 'LIMIT' in error.code else 'unsupported',error_code=error.code,error=str(error))
    memory=psutil.Process().memory_info()
    write_json(target,dict(status=result['status'],result=result,function_seconds=perf_counter()-started,
                          peak_memory_bytes=getattr(memory,'peak_wset',memory.rss)))


def clean_revision():
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip():
        raise RuntimeError('Campaign requires clean source')
    return subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()


def run(dataset,output,case_ids,seconds):
    if seconds<=5:raise ValueError('External budget must exceed replay reserve of five seconds')
    revision=clean_revision()
    metadata=json.loads((dataset/'dataset.json').read_text())
    cases={r['instance_id']:r for r in metadata['cases']}
    chosen=[cases[i] for i in case_ids]
    # Every method pair appears in opposite order in the two repetitions.
    schedule=[dict(instance_id=case['instance_id'],repeat_index=repeat,method=method)
              for repeat in range(2) for case in chosen
              for method in (METHODS if repeat==0 else list(reversed(METHODS)))]
    output.mkdir(parents=True,exist_ok=False)
    protocol=dict(campaign_id=output.name,code_revision=revision,cases=chosen,schedule=schedule,
        external_deadline_seconds=seconds,solver_budget_seconds=seconds-5,solver_seed=0,
        repetitions=2,methods=METHODS,dp_configurations=CONFIG,max_states=100000,
        max_cut_columns=65536,enforced_ram_cap=None,platform=platform.platform(),
        timing='Fresh sequential worker; parent pipeline includes imports, recognition, model, solve and required replay. Parent recovery audit is separately outside deadline.',
        order='Forward/reverse method order per case across two repetitions; actual schedule frozen here',
        classification=metadata['classification'])
    write_json(output/'protocol.json',protocol)
    for case in chosen:
        source=dataset/'instances'/(case['instance_id']+'.json')
        instance=json.loads(source.read_text())
        assert fingerprint(instance)==case['input_fingerprint']
        write_json(output/case['instance_id']/'input.json',instance)
    rows=[]
    for item in schedule:
        if clean_revision()!=revision:raise RuntimeError('Revision changed during campaign')
        folder=output/item['instance_id'];target=folder/f"{item['method']}-{item['repeat_index']}.json"
        started=perf_counter()
        try:
            process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',
                str(folder/'input.json'),item['method'],str(target),str(seconds)],
                capture_output=True,text=True,timeout=seconds)
            payload=json.loads(target.read_text()) if process.returncode==0 else dict(status='internal_error',stderr=process.stderr,result={})
        except subprocess.TimeoutExpired:
            payload=dict(status='timeout',result={})
        elapsed=perf_counter()-started
        if clean_revision()!=revision:
            write_json(output/'INVALIDATED.json',dict(reason='Code changed during execution'))
            raise RuntimeError('Code changed during execution')
        events=target.with_suffix('.events.jsonl')
        trace=[json.loads(line) for line in events.read_text().splitlines()] if events.exists() else []
        payload['last_started_stage']=next((e for e in reversed(trace) if e['event']=='stage_started'),None)
        payload['verified_checkpoint']=next((e for e in reversed(trace) if e.get('replay_verified')),None)
        candidate=next((e for e in reversed(trace) if e['event']=='incumbent'),None)
        if payload['status']=='timeout' and candidate is not None:
            from cfar.actions import apply_actions
            from cfar.obligations import verify_obligations
            audit_started=perf_counter()
            repaired=apply_actions(json.loads((folder/'input.json').read_text()),candidate['selected'])
            assert verify_obligations(repaired['instance'],repaired['active'])['satisfied']
            payload['recovered_candidate_audit']=dict(selected=candidate['selected'],cost=candidate['cost'],
                satisfied=True,outside_deadline=True,seconds=perf_counter()-audit_started)
        write_json(target,payload)
        instance=json.loads((folder/'input.json').read_text())
        write_json(target.with_suffix('.manifest.json'),manifest(instance,dict(protocol,run=item),payload['status'],0))
        row=dict(item,code_revision=revision,input_fingerprint=fingerprint(instance),
                 end_to_end_seconds=elapsed,raw_record=target.relative_to(output).as_posix(),**payload)
        rows.append(row);write_json(output/'records.json',rows)
        print(item['instance_id'],item['repeat_index'],item['method'],payload['status'],round(elapsed,3),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',nargs=4)
    p.add_argument('--dataset',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--cases',nargs='+');p.add_argument('--timeout',type=float,default=60)
    a=p.parse_args()
    if a.worker:worker(*a.worker[:3],float(a.worker[3]))
    else:run(a.dataset.resolve(),a.output.resolve(),a.cases,a.timeout)
