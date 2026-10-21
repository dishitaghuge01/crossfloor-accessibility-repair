"""Post-hoc matched-budget extension, retaining original30s failures."""
import argparse,json,subprocess,sys,hashlib,platform
from pathlib import Path
from time import perf_counter
from fractions import Fraction
from cfar.io import write_json,manifest,fingerprint

def worker(source,method,target):
 from cfar.dp_owned_interface import solve_owned_interface
 from cfar.cp_sat import solve_cp_sat
 from cfar.errors import ValidationError
 from cfar.actions import apply_actions
 from cfar.obligations import verify_obligations
 from audit_revised_evidence import paid_rectangles
 from ortools.sat.python import cp_model
 import psutil
 a=json.loads(Path(source).read_text());t=perf_counter()
 try:
  r=solve_cp_sat(a,time_limit=75,seed=0) if method=='cp-sat' else solve_owned_interface(a,compress=False,release_dead_cells=True,release_dead_vertices=True,max_states=500000,profile=True)
  status=r['status']
 except ValidationError as e:r=dict(error_code=e.code,error=str(e));status='limit_exceeded' if 'LIMIT' in e.code else 'unsupported'
 elapsed=perf_counter()-t;ids=r.get('selected');ids=ids if ids is not None else r.get('incumbent',{}).get('selected');replay=None
 if ids is not None:
  repaired=apply_actions(a,ids);assert verify_obligations(repaired['instance'],repaired['active'])['satisfied']
  assert not any(x['delta'] for x in repaired['adjacency'].values())
  assert paid_rectangles(a,ids)==Fraction(r.get('cost') or r['incumbent']['cost'])
  replay=dict(satisfied=True,delta_A=0,paid_box_cost=True)
 memory=psutil.Process().memory_info()
 write_json(target,dict(status=status,result=r,function_seconds=elapsed,replay=replay,peak_memory_bytes=getattr(memory,'peak_wset',memory.rss)))

def run(source,output):
 assert not subprocess.check_output(['git','status','--porcelain'],text=True).strip()
 output.mkdir(parents=True,exist_ok=False);a=json.loads(source.read_text());write_json(output/'input.json',a)
 protocol=dict(classification='post-hoc matched-budget extension; original30s failures retained',parent_seconds=90,cp_sat_seconds=75,max_states=500000,max_cut_columns=65536,repeats=3,solver_seed=0,price_seed=0,
  case='clinic-network-96-s0',order='rotate two methods per repeat; sequential fresh processes',platform=platform.platform(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 write_json(output/'protocol.json',protocol);rows=[]
 for repeat in range(3):
  methods=['lifetime-uncompressed','cp-sat'] if repeat%2==0 else ['cp-sat','lifetime-uncompressed']
  for method in methods:
   target=output/f'{method}-{repeat}.json';t=perf_counter()
   try:
    p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(output/'input.json'),method,str(target)],capture_output=True,text=True,timeout=90)
    payload=json.loads(target.read_text()) if p.returncode==0 else dict(status='internal_error',result={},stderr=p.stderr)
   except subprocess.TimeoutExpired:payload=dict(status='timeout',result={})
   wall=perf_counter()-t;write_json(target,payload);meta=manifest(a,dict(protocol,method=method,repeat=repeat),payload['status'],0)
   write_json(target.with_suffix('.manifest.json'),meta);rows.append(dict(case=protocol['case'],method=method,repeat=repeat,input_fingerprint=fingerprint(a),code_commit=meta['git_revision'],raw_record=target.name,end_to_end_seconds=wall,**payload));write_json(output/'records.json',rows)
   print(repeat,method,payload['status'],round(payload.get('function_seconds',wall),2),flush=True)
 labels=[(r['status'],r['result'].get('cost'),r['result'].get('selected')) for r in rows if r['status'] in ('optimal','infeasible')]
 assert not labels or all(x==labels[0] for x in labels)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worker',nargs=3);p.add_argument('--source',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 if a.worker:worker(*a.worker)
 else:run(a.source,a.output)
