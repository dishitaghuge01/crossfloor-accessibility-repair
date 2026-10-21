"""Audit the separate larger-budget check; never pool its timings with core."""
import argparse,json,hashlib
from collections import Counter
from fractions import Fraction
from pathlib import Path
from statistics import median
from cfar.io import fingerprint,write_json
from audit_revised_evidence import paid_rectangles


def audit(root,output):
 rows=json.loads((root/'records.json').read_text());a=json.loads((root/'input.json').read_text())
 assert len(rows)==6
 assert Counter((r['method'],r['repeat']) for r in rows)==Counter((m,i) for m in ('lifetime-uncompressed','cp-sat') for i in range(3))
 checked=0;labels=[];report={}
 for r in rows:
  path=root/r['raw_record'];payload=json.loads(path.read_text());meta=json.loads(path.with_suffix('.manifest.json').read_text())
  assert not meta['git_dirty'] and r['code_commit']==meta['git_revision']
  assert r['input_fingerprint']==meta['input_fingerprint']==fingerprint(a)
  assert r['status']==payload['status']==meta['solver_status']
  for k in ('function_seconds','result','replay','peak_memory_bytes'):assert r.get(k)==payload.get(k)
  result=r['result'];ids=result.get('selected');ids=ids if ids is not None else result.get('incumbent',{}).get('selected')
  if ids is not None:
   assert paid_rectangles(a,ids)==Fraction(result.get('cost') or result['incumbent']['cost'])
   assert r['replay']==dict(satisfied=True,delta_A=0,paid_box_cost=True);checked+=1
  if r['status'] in ('optimal','infeasible'):labels.append((r['status'],result.get('cost'),result.get('selected')))
 assert not labels or all(x==labels[0] for x in labels)
 for method in ('lifetime-uncompressed','cp-sat'):
  subset=[r for r in rows if r['method']==method];times=[r['function_seconds'] for r in subset if r['status'] in ('optimal','infeasible') or r.get('replay')]
  report[method]=dict(statuses=dict(Counter(r['status'] for r in subset)),seconds_median=median(times) if times else None,
   seconds_min=min(times) if times else None,seconds_max=max(times) if times else None,
   costs=[r['result'].get('cost') or r['result'].get('incumbent',{}).get('cost') for r in subset],
   best_cost_bounds=[r['result'].get('best_cost_bound') for r in subset],
   cp_cost_stage_statuses=[r['result'].get('statistics',{}).get('stages',[{}])[0].get('status') for r in subset] if method=='cp-sat' else None,
   cp_cost_search_seconds=[r['result'].get('statistics',{}).get('stages',[{}])[0].get('wall_seconds') for r in subset] if method=='cp-sat' else None)
 cp=report['cp-sat']
 gaps=[float((Fraction(c)-Fraction(b))/Fraction(c)) for c,b in zip(cp['costs'],cp['best_cost_bounds']) if c is not None and b is not None and Fraction(c)>0]
 cp['relative_cost_gaps']=gaps
 branches=[r['result'].get('statistics',{}).get('stages',[{}])[0].get('branches') for r in rows if r['method']=='cp-sat']
 conflicts=[r['result'].get('statistics',{}).get('stages',[{}])[0].get('conflicts') for r in rows if r['method']=='cp-sat']
 cp['cost_stage_branches']=branches;cp['cost_stage_conflicts']=conflicts
 finding=('A separate post-hoc check reruns clinic-network-96-s0 at 90 s parent time, 500000 DP states and 75 s CP-SAT internal time, three repetitions per method. Lifetime DP statuses: '+', '.join(str(v)+' '+k.replace('_',' ') for k,v in report['lifetime-uncompressed']['statuses'].items())+'; CP-SAT statuses: '+', '.join(str(v)+' '+k.replace('_',' ') for k,v in report['cp-sat']['statuses'].items())+'. Every returned repair passes independent paid-box/cost arithmetic and full reachability/topology replay. These six observations are kept separate from the 70-observation 30 s campaign; original failures remain. Larger-budget times are not pooled with the primary comparison.')
 if gaps:
  finding+=' CP-SAT incumbent costs: '+str(cp['costs'])+'; cost lower bounds: '+str(cp['best_cost_bounds'])+'; remaining relative cost gaps: '+', '.join(f'{100*g:.2f}%' for g in gaps)+'. The unresolved interval is optimization uncertainty, not construction-price uncertainty.'
 write_json(output,dict(observations=6,returned_selections_checked=checked,methods=report,finding=finding,
  code_commit=rows[0]['code_commit'],input_fingerprint=fingerprint(a),records_sha256=hashlib.sha256((root/'records.json').read_bytes()).hexdigest()))
 print(finding)
 if gaps:
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  plt.rcParams.update({'font.family':'DejaVu Serif','font.size':11,'pdf.fonttype':42})
  fig,ax=plt.subplots(figsize=(8,3.3))
  for i,(c,b) in enumerate(zip(cp['costs'],cp['best_cost_bounds'])):
   if c is None or b is None:continue
   upper,lower=float(Fraction(c)),float(Fraction(b))
   ax.plot([lower,upper],[i,i],lw=5,color='#e2b168')
   ax.scatter([lower],[i],marker='|',s=230,color='#32658c',label='Lower bound' if i==0 else None,zorder=3)
   ax.scatter([upper],[i],marker='o',s=65,color='#00744c',label='Replay-valid repair' if i==0 else None,zorder=3)
   ax.annotate(f'{lower:g}',(lower,i),xytext=(-10,10),textcoords='offset points')
   ax.annotate(f'{upper:g}',(upper,i),xytext=(-10,10),textcoords='offset points')
  ax.set_yticks(range(3),['Repeat 1','Repeat 2','Repeat 3']);ax.set_ylim(-.5,2.65)
  ax.set_xlabel('Abstract action cost (not construction prices)');ax.set_title('Largest clinic case: unresolved minimum-cost intervals at 90 s',fontsize=12)
  ax.legend(loc='lower left',fontsize=9);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
  fig.tight_layout();folder=output.parent/'figures';folder.mkdir(exist_ok=True)
  fig.savefig(folder/'network-budget.pdf',metadata={'CreationDate':None,'ModDate':None});fig.savefig(folder/'network-budget.png',dpi=160);plt.close(fig)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.evidence,a.output)
