"""Audit and summarize the fixed building-network campaign, without rerunning it."""
import argparse
from collections import Counter,defaultdict
from fractions import Fraction
import hashlib,json,sys
from pathlib import Path
from statistics import median
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon as Patch
from matplotlib.colors import ListedColormap
from cfar.io import fingerprint,write_json
from network_study_structure import structure

METHODS=['uncompressed','cells-uncompressed','lifetime-compressed','lifetime-uncompressed','cp-sat','greedy-improved']
LABELS=['Original DP','Cells only','Lifetime + rank','Lifetime DP','CP-SAT','Improved greedy']

def summarize(root,dataset,audits,output):
 output.mkdir(parents=True,exist_ok=False)
 rows=json.loads((root/'records.json').read_text());protocol=json.loads((root/'protocol.json').read_text())
 cases=json.loads((dataset/'dataset.json').read_text())['cases'];bycase={c['case']:c for c in cases}
 assert len(rows)==70,(len(rows),'expected fixed70 observations')
 assert len({r['code_commit'] for r in rows})==1
 assert len({r['input_fingerprint'] for r in rows})==15
 expected=[]
 for case in bycase:
  methods=METHODS if case.endswith('-s0') else ['lifetime-uncompressed','cp-sat']
  for method in methods:
   for repeat in range(3 if case.endswith('-s0') and method in ('lifetime-uncompressed','cp-sat') else 1):expected.append((case,method,repeat))
 assert Counter((r['case'],r['method'],r['repeat']) for r in rows)==Counter(expected)
 from audit_revised_evidence import paid_rectangles
 selections=0;manifests={};structures={};exact={};models={}
 source={n:json.loads((audits/(n+'.json')).read_text()) for n in ('clinic','molio')}
 for case in bycase:
  a=json.loads((root/case/'input.json').read_text());models[case]=a
  assert fingerprint(a)==bycase[case]['input_fingerprint']
  original={r['global_id']:r for r in source[case.split('-')[0]]['spaces']}
  for f in a['floors']:
   for room in f['rooms']:
    src=original[room['room_id']]
    assert room['polygon']==src['polygon'] and f['floor_id']==src['storey_id']
  structures[case]=structure(a)
 for r in rows:
  raw=root/r['raw_record'];payload=json.loads(raw.read_text());meta=json.loads(raw.with_suffix('.manifest.json').read_text())
  assert not meta['git_dirty'] and meta['git_revision']==r['code_commit']
  assert meta['input_fingerprint']==r['input_fingerprint']==fingerprint(models[r['case']])
  assert meta['solver_status']==r['status']==payload['status']
  for k in ('result','function_seconds','replay','peak_memory_bytes'):assert r.get(k)==payload.get(k),(r['raw_record'],k)
  manifests[r['raw_record']]=hashlib.sha256(raw.read_bytes()).hexdigest()
  result=r['result'];selected=result.get('selected')
  if selected is None:selected=result.get('incumbent',{}).get('selected')
  if selected is not None:
   assert paid_rectangles(models[r['case']],selected)==Fraction(result.get('cost') or result['incumbent']['cost'])
   assert r['replay']==dict(satisfied=True,delta_A=0,paid_box_cost=True)
   selections+=1
  if r['status'] in ('optimal','infeasible'):
   label=(r['status'],result.get('cost'),result.get('selected'))
   if r['case'] in exact:assert label==exact[r['case']],r['case']
   exact[r['case']]=label
 summaries=[]
 for case in sorted(bycase):
  for method in METHODS:
   subset=[r for r in rows if r['case']==case and r['method']==method]
   if not subset:continue
   completed=[r for r in subset if r['status'] in ('optimal','infeasible','feasible')]
   times=[r['function_seconds'] for r in completed]
   states=[r['result']['statistics']['peak_raw_states'] for r in completed if r['result'].get('statistics',{}).get('peak_raw_states') is not None]
   stages=[r['result']['statistics']['stages'] for r in completed if method=='cp-sat']
   summaries.append(dict(case=case,method=method,n=len(subset),statuses=dict(Counter(r['status'] for r in subset)),
    seconds_median=median(times) if times else None,seconds_min=min(times) if times else None,seconds_max=max(times) if times else None,
    peak_raw_states=max(states) if states else None,objective=completed[0]['result'].get('cost') if completed else None,
    selected=completed[0]['result'].get('selected') if completed else None,
    cp_cost_search_seconds=median(s[0]['wall_seconds'] for s in stages) if stages else None,
    cp_tie_search_seconds=median(sum(x['wall_seconds'] for x in s[1:]) for s in stages) if stages else None))
 write_json(output/'summary.json',dict(protocol=protocol,observations=len(rows),returned_selections_checked=selections,
  code_commit=rows[0]['code_commit'],records_sha256=hashlib.sha256((root/'records.json').read_bytes()).hexdigest(),
  original_rooms_preserved=True,structures=structures,methods=summaries,raw_record_hashes=manifests,
  status_totals={m:dict(Counter(r['status'] for r in rows if r['method']==m)) for m in METHODS}))
 plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10.5,'pdf.fonttype':42,'ps.fonttype':42})
 figdir=output/'figures';figdir.mkdir()
 names=sorted(n for n in bycase if n.endswith('-s0'))
 mapping={'optimal':0,'limit_exceeded':1,'timeout':2,'feasible':3,'unsupported':4,'internal_error':5,'infeasible':6,'heuristic_failed':7,'mixed':8}
 matrix=[];annotations=[]
 for name in names:
  line=[];texts=[]
  for m in METHODS:
   s=next(s for s in summaries if s['case']==name and s['method']==m)
   statuses=list(s['statuses']);status=statuses[0] if len(statuses)==1 else 'mixed'
   line.append(mapping[status]);value=s['seconds_median']
   texts.append((f'{value:.2f}s' if value is not None else status.replace('_','\n'))+'\n'+(' / '.join(k[:3]+':'+str(v) for k,v in s['statuses'].items()) if status=='mixed' else f'n={s["n"]}'))
  matrix.append(line);annotations.append(texts)
 fig,ax=plt.subplots(figsize=(8.5,4.6));ax.imshow(matrix,cmap=ListedColormap(['#c4e5d3','#ffdb9c','#edb6bd','#c9d9f0','#ddd','#c66','#b7d9da','#d7c8e5','#d9d9d9']),vmin=0,vmax=8,aspect='auto')
 ax.set_xticks(range(len(METHODS)),LABELS,rotation=20,ha='right');ax.set_yticks(range(len(names)),[n.replace('-network-',' / ').replace('-s0','') for n in names])
 for i,row in enumerate(annotations):
  for j,t in enumerate(row):ax.text(j,i,t,ha='center',va='center',fontsize=10)
 ax.set_title('Seed 0: complete exact objectives, retained caps and timeouts\nTimes include recognition and solve replay; n differs by preregistered method role',fontsize=11)
 fig.tight_layout();fig.savefig(figdir/'network-outcomes.pdf',metadata={'CreationDate':None,'ModDate':None});fig.savefig(figdir/'network-outcomes.png',dpi=160);plt.close(fig)
 # Full source room geometry, with actual selected paid patches if available.
 case='clinic-network-48-s0';a=models[case]
 selected=next((s['selected'] for s in summaries if s['case']==case and s['method']=='lifetime-uncompressed' and s['selected'] is not None),[])
 paid={e['connection_id'] for action in a['actions'] if action['action_id'] in selected for e in action['effects']}
 targets={o['target'] for o in a['obligations']};fig,axes=plt.subplots(1,len(a['floors']),figsize=(10.5,4.6),squeeze=False)
 for f,ax in zip(a['floors'],axes[0]):
  rids={r['room_id'] for r in f['rooms']}
  for room in f['rooms']:ax.add_patch(Patch(room['polygon'],facecolor='#c4dce8' if room['room_id'] in targets else '#ededed',edgecolor='#666',lw=.35))
  for c in a['connections']:
   if c['existing']:continue
   for rec in c['geometry']['footprints']:
    if rec['room_id'] in rids:ax.add_patch(Patch(rec['polygon'],facecolor='#006b45' if c['connection_id'] in paid else '#db8a37',edgecolor='none',alpha=.85))
  ax.autoscale_view();ax.set_aspect('equal');ax.set_title(f'{f["elevation_m"]:.2f} m; {len(f["rooms"])} rooms',fontsize=12);ax.tick_params(labelsize=11)
 fig.suptitle('Clinic: 253 retained original room polygons, 78 hypothetical purchases\nBlue: demanded rooms; orange: candidate patches; green: complete lifetime-DP paid patches',fontsize=12)
 fig.tight_layout();fig.savefig(figdir/'network-building.pdf',metadata={'CreationDate':None,'ModDate':None});fig.savefig(figdir/'network-building.png',dpi=160);plt.close(fig)
 # Explicit graph difficulty rather than using room count as a proxy.
 fig,axes=plt.subplots(1,2,figsize=(9,3.4))
 x=np.arange(len(names));axes[0].bar(x-.17,[structures[n]['contracted_active_nodes'] for n in names],.34,label='Active components')
 axes[0].bar(x+.17,[structures[n]['active_cycle_rank'] for n in names],.34,label='Independent graph cycles');axes[0].legend(fontsize=9.5)
 axes[1].bar(x-.17,[structures[n]['actions'] for n in names],.34,label='Purchases');axes[1].bar(x+.17,[structures[n]['bundled_actions'] for n in names],.34,label='Bundled purchases');axes[1].legend(fontsize=9.5)
 for ax in axes:ax.set_xticks(x,[n.split('-')[0]+' '+n.split('-')[2] for n in names],rotation=25,ha='right');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
 axes[0].set_title('Potential graph after baseline contraction');axes[1].set_title('Actual catalogue choices, not room count')
 fig.tight_layout();fig.savefig(figdir/'network-difficulty.pdf',metadata={'CreationDate':None,'ModDate':None});fig.savefig(figdir/'network-difficulty.png',dpi=160);plt.close(fig)
 print('Audited',len(rows),'observations and',selections,'returned selections; wrote three vector figures.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--dataset',type=Path,required=True);p.add_argument('--audits',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();summarize(a.evidence,a.dataset,a.audits,a.output)
