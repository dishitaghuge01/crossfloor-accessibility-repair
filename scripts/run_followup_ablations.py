"""Pinned follow-up ablations; fresh workers, retained caps/timeouts and exact replay."""
import argparse, hashlib, json, subprocess, sys, platform, importlib.metadata
from pathlib import Path
from time import perf_counter
from cfar.io import write_json, manifest, fingerprint

CONFIG = {'compressed':{}, 'uncompressed':{'compress':False},
 'histories':{'compress':False,'dominance':False},
 'reverse':{'event_order':'reverse'}, 'indexed':{'spatial_index':True}}

def worker(source,method,target):
 from cfar.dp_owned_interface import solve_owned_interface
 from cfar.errors import ValidationError
 from audit_revised_evidence import paid_rectangles
 from fractions import Fraction
 import psutil
 a=json.loads(Path(source).read_text());start=perf_counter()
 try:
  result=solve_owned_interface(a,profile=True,max_states=100000,**CONFIG[method]);status=result['status']
 except ValidationError as e:
  result={'error_code':e.code,'error':str(e)};status='limit_exceeded' if 'LIMIT' in e.code else 'unsupported'
 elapsed=perf_counter()-start
 if result.get('selected') is not None:
  assert paid_rectangles(a,result['selected'])==Fraction(result['cost'])
 write_json(target,dict(status=status,result=result,function_seconds=elapsed,peak_memory_bytes=psutil.Process().memory_info().peak_wset))

def run(output):
 if subprocess.check_output(['git','status','--porcelain'],text=True).strip():raise ValueError('commit first')
 output.mkdir(parents=True,exist_ok=False)
 protocol=dict(methods=CONFIG,repetitions=3,seed=0,max_states=100000,max_cut_columns=65536,parent_seconds=30,
  order='repeat-major; rotate method order by repeat; inputs fixed; descriptive timings only',
  dominance_off='retain all generated histories, including duplicate states/labels; compression also disabled; compare with uncompressed',
  reverse='reverse baseline events, complete same-first-floor units and actions inside units; never split units or change floor introduction/forgetting',
  spatial_index='STRtree envelopes for portal footprint candidates inside compiler and cell-owner covers candidates; original exact predicates retained; validation and replay stay unindexed',
  packages={p:importlib.metadata.version(p) for p in ['shapely','numpy','psutil']},platform=platform.platform())
 write_json(output/'protocol.json',protocol)
 names=['integrated-example','catalogue-8-s0','catalogue-32-s0','connectivity-3-s0','connectivity-5-s0','connectivity-7-s0','ownership-4-s0','rooms-12-s0']
 sources=[Path('runs/revised-controlled-portable')/n/'input.json' for n in names]
 sources += [Path('runs/revised-building-portable')/n/'input.json' for n in ['clinic-horizontal','clinic-three-storey-restricted','molio-horizontal','molio-three-storey-restricted']]
 records=[]
 for source in sources:
  a=json.loads(source.read_text());folder=output/source.parent.name;write_json(folder/'input.json',a)
  labels=[]
  for repeat in range(3):
   methods=list(CONFIG);methods=methods[repeat:]+methods[:repeat]
   for method in methods:
    target=folder/f'{method}-{repeat}.json';start=perf_counter()
    try:
     p=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(folder/'input.json'),method,str(target)],capture_output=True,text=True,timeout=30)
     payload=json.loads(target.read_text()) if not p.returncode else dict(status='internal_error',result={},stderr=p.stderr)
    except subprocess.TimeoutExpired:payload=dict(status='timeout',result={})
    wall=perf_counter()-start;write_json(target,payload)
    result=payload['result']
    label=(payload['status'],result.get('cost'),result.get('selected'))
    if label[0] in {'optimal','infeasible'}:labels.append(label)
    row=dict(instance_id=folder.name,method=method,repeat=repeat,input_fingerprint=fingerprint(a),raw_record=target.relative_to(output).as_posix(),end_to_end_seconds=wall,**payload)
    records.append(row);write_json(output/'records.json',records)
    write_json(target.with_suffix('.manifest.json'),manifest(a,dict(protocol,method=method,configuration=CONFIG[method],repeat=repeat),payload['status'],0))
   print(folder.name,repeat,flush=True)
  if any(x!=labels[0] for x in labels):raise RuntimeError('exact-label mismatch '+folder.name)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worker',nargs=3);p.add_argument('--output',type=Path);a=p.parse_args()
 if a.worker:worker(*a.worker)
 else:run(a.output)
