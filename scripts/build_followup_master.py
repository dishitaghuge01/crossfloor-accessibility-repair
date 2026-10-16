"""Audit frozen follow-up records and add a data-derived appendix to the reviewed master."""
import argparse,hashlib,json,shutil,csv
from collections import Counter
from pathlib import Path
from statistics import median
from cfar.io import fingerprint,write_json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def build(evidence,index,base,output):
 rows=json.loads((evidence/'records.json').read_text());assert len(rows)==180
 assert len({r['instance_id'] for r in rows})==12
 grouped={};replayed=0;commits=set()
 for r in rows:
  path=evidence/r['raw_record'];raw=json.loads(path.read_text());meta=json.loads(path.with_suffix('.manifest.json').read_text())
  a=json.loads((path.parent/'input.json').read_text());assert fingerprint(a)==r['input_fingerprint']==meta['input_fingerprint']
  assert not meta['git_dirty'];commits.add(meta['git_revision'])
  for key in raw:assert raw[key]==r[key]
  assert r['status'] in {'optimal','infeasible','limit_exceeded','timeout'},r
  grouped.setdefault((r['instance_id'],r['method']),[]).append(r)
  if r['status']=='optimal':
   from audit_revised_evidence import paid_rectangles
   from cfar.actions import apply_actions
   from cfar.obligations import verify_obligations
   from fractions import Fraction
   result=r['result'];assert paid_rectangles(a,result['selected'])==Fraction(result['cost'])
   repair=apply_actions(a,result['selected']);assert verify_obligations(repair['instance'],repair['active'])['satisfied']
   oldroot=Path('runs/revised-building-portable') if r['instance_id'].startswith(('clinic','molio')) else Path('runs/revised-controlled-portable')
   old=json.loads((oldroot/r['instance_id']/'compressed-0.json').read_text())['result']
   assert [result[k] for k in ['status','cost','selected']]==[old[k] for k in ['status','cost','selected']]
   replayed+=1
 assert len(commits)==1
 assert all(len(g)==3 for g in grouped.values())
 comparisons=json.loads((index/'summary.json').read_text());assert len(comparisons)==78
 for comparison in comparisons:
  matches=list(index.glob('*/'+comparison['instance_id']+'/results.json'));assert len(matches)==1
  saved=json.loads(matches[0].read_text());meta=json.loads(matches[0].with_name('manifest.json').read_text())
  assert not meta['git_dirty'] and meta['git_revision'] in commits
  original_root=Path('runs/revised-building-portable') if comparison['instance_id'].startswith(('clinic','molio')) else Path('runs/revised-controlled-portable')
  assert meta['input_fingerprint']==fingerprint(json.loads((original_root/comparison['instance_id']/'input.json').read_text()))
  assert saved[0][0]==saved[1][0]==comparison['status']
  fields=['error_code'] if comparison['status']=='unsupported' else ['cells','action_cells','units','components','anchors','parameters','geometry_conflicts','blocked']
  for field in fields:assert saved[0][1].get(field)==saved[1][1].get(field)
  assert saved[0][1].get('operation_counts')==comparison['plain_counts']
  assert saved[1][1].get('operation_counts')==comparison['indexed_counts']

 statuses=Counter(r['status'] for r in rows)
 write_json(evidence/'audit.json',dict(records=len(rows),instances=12,code_commit=next(iter(commits)),statuses=dict(statuses),independent_solution_checks=replayed,index_comparisons=78,records_sha256=hashlib.sha256((evidence/'records.json').read_bytes()).hexdigest()))
 shutil.copytree(base,output,ignore=shutil.ignore_patterns('preview','master.pdf','master.log','pdf-qa.json','extracted-text.txt'))
 methods=['compressed','uncompressed','histories','reverse','indexed']
 names=list(dict.fromkeys(r['instance_id'] for r in rows));short=['example','cat8','cat32','conn3','conn5','conn7','owner4','rooms12','Clinic2','Clinic3R','Molio2','Molio3R']
 def times(name,method):return [r['function_seconds'] for r in grouped[name,method] if r['status'] in {'optimal','infeasible'}]
 def value(name,method):
  g=grouped[name,method];t=times(name,method)
  if len(t)==3:return f'{median(t):.4f}'
  return '/'.join(f"{v} {dict(limit_exceeded='cap').get(k,k)}" for k,v in sorted(Counter(r['status'] for r in g).items())).replace('_',r'\_')
 plt.rcParams.update({'font.family':'serif','font.size':8,'pdf.fonttype':42})
 fig,axs=plt.subplots(1,2,figsize=(7.1,2.8))
 for ax,method,title in zip(axs,['reverse','indexed'],['Reverse / canonical','Indexed / unindexed']):
  values=[median(times(n,method))/median(times(n,'compressed')) for n in names]
  ax.bar(range(len(names)),values,color='#285878');ax.axhline(1,color='black',linewidth=.7,linestyle='--')
  ax.set_xticks(range(len(names)),short,rotation=65,ha='right');ax.set_ylabel('Ratio of completed median times');ax.set_title(title);ax.set_ylim(bottom=0)
 fig.tight_layout();fig.savefig(output/'figures/followup_ratios.pdf',bbox_inches='tight');fig.savefig(output/'figures/followup_ratios.png',dpi=180,bbox_inches='tight');plt.close(fig)
 with (output/'followup-summary.csv').open('w',newline='') as h:
  w=csv.writer(h);w.writerow(['instance','method','statuses','completed_function_min','completed_function_median','completed_function_max','peak_raw_max'])
  for n in names:
   for m in methods:
    t=times(n,m);g=grouped[n,m];peaks=[r['result'].get('statistics',{}).get('peak_raw_states') for r in g];peaks=[p for p in peaks if p is not None]
    w.writerow([n,m,json.dumps(dict(Counter(r['status'] for r in g))),min(t) if t else None,median(t) if t else None,max(t) if t else None,max(peaks) if peaks else None])
 def text_table(headers,body,caption,label):
  return r'\begin{table*}[t]\caption{'+caption+r'}\label{'+label+r'}\centering\footnotesize\setlength{\tabcolsep}{4pt}\begin{tabular}{lrrrrr}\toprule'+'\n'+' & '.join(headers)+r'\\\midrule'+'\n'+'\n'.join(' & '.join(row)+r'\\' for row in body)+r'\bottomrule\end{tabular}\end{table*}'+'\n'
 appendix=r'''
\section{Additional State, Schedule and Geometry Ablations}
The original 2,094 observations remain frozen. A separate pinned campaign evaluates twelve existing inputs, five modes and three fresh processes per pair (180 observations). Method order rotates across repeats, with fixed input order. All modes use a 30-second parent limit, 100000 raw rows/histories and 65536 cut columns. They run independently of the original 60-second campaign; times are not pooled across campaigns. RSS, statuses, manifests, seeds, hashes and full returned selections remain in the evidence. These are descriptive workstation timings without significance claims.

\subsection{Precisely Disabled Operations}
The history mode disables both minimum-label state merging and representative compression. It retains every generated history, including duplicates, and is compared with the uncompressed merged-state mode to isolate merging. Its raw cap counts histories rather than distinct states. A cap is not an infeasibility result. Retaining duplicates may be more expensive than a variant that removes exact duplicate histories; this is an explicit no-merging control.

Reverse mode retains normal merging/compression and reverses baseline events, complete units with the same first floor, and actions within each unit. It preserves complete owner units and the floor introduction/forgetting schedule. It tests this admissible deterministic schedule, not arbitrary event permutations.

Index mode retains canonical order and normal reductions. STRtree envelope queries shortlist occupied portal-footprint pairs inside joint-geometry compilation and owner polygons for collision-cell coverage. Original area/EPS, same-owner equality and covers predicates still decide feasibility; bounding boxes alone never accept a collision or coverage claim. Baseline validation, room/obstacle checks, action-pair enumeration and materialization replay remain unindexed. Index construction overhead is included. The option is off by default and a cached recognition must match its setting.
'''
 appendix+=text_table(['Input','Compressed','Uncompressed','Histories','Reverse','Indexed'],[[short[i]]+[value(n,m) for m in methods] for i,n in enumerate(names)],'Additional ablations: completed function-time medians (seconds), or all noncompletion statuses. Three observations per cell.','tab:followup')
 def peak(n,m):
  g=grouped[n,m]
  if any(r['status']=='limit_exceeded' for r in g):return 'cap'
  if any(r['status']=='timeout' for r in g):return 'timeout'
  return str(max(r['result']['statistics']['peak_raw_states'] for r in g))
 appendix+=text_table(['Input','Compressed','Uncompressed','Histories','Reverse','Indexed'],[[short[i]]+[peak(n,m) for m in methods] for i,n in enumerate(names)],'Additional campaign: maximum peak raw rows over three repeats. History mode counts histories; other modes count distinct states before representative reduction. Cap denotes termination above the common 100000 limit.','tab:followupstates')
 appendix+=r'\begin{figure*}[t]\centering\includegraphics[width=.96\textwidth]{figures/followup_ratios.pdf}\caption{Additional campaign only: ratios of medians of completed times. A value below one means a lower observed median. Labels ending 3R denote three-level restricted hypothetical source cases. These ratios do not establish population or statistical speedup.}\label{fig:followup}\end{figure*}'+'\n'
 plain=sum(x['plain_counts']['cell_owner_coverage_tests'] for x in comparisons if x['plain_counts'])
 indexed=sum(x['indexed_counts']['cell_owner_coverage_tests'] for x in comparisons if x['indexed_counts'])
 appendix+=f'''\\subsection{{Agreement and Boundaries}}
All {replayed} returned selections in the additional campaign match the frozen canonical exact cost/count/ID labels and pass full materialization plus independent paid-box/owner/cost checking. Outcomes are {', '.join(str(v)+' '+k.replace('_',' ') for k,v in sorted(statuses.items()))}. A separate untimed all-input comparison checks all 78 original inputs: cells, action-cell ownership, units, components, anchors, blocked actions, conflicts and parameters agree between indexed and unindexed recognition; both reject the same two unsupported inputs. Across recognized inputs, actual cell-owner covers calls decrease from {plain} to {indexed}. These are coverage-call counts, not all GEOS calls or the older physical-footprint intersection counter. Indexing therefore closes an implementation omission without changing the recognized physical contract or asserting a universal runtime gain.

\\subsection{{Bounded Closest-Work Recheck}}
A targeted recheck on 16 October 2026 reconfirmed the inspected formulations: heterogeneous-network connectivity permits condition-specific edges and shared purchases~\\cite{{condition}}; simultaneous restricted-link design has per-color route constraints and an FPT parameter counting multicolored links~\\cite{{simultaneous}}; conflict Steiner selection excludes declared vertex pairs~\\cite{{conflicts}}; weighted neighborhood logic already supplies generic optimization machinery~\\cite{{logic}}. These features are credited to prior work. The supported claim remains the explicit full-action physical-to-owned-interface transfer and its scoped bound/evaluation. This check establishes neither absence of an equivalent construction nor literature priority. Independent human proof review and verified actual-building intervention data remain open; neither can be substituted by these implementation experiments.
'''
 tex=((base/'base-master.tex') if (base/'base-master.tex').exists() else (base/'master.tex')).read_text()
 assert 'Additional State, Schedule and Geometry Ablations' not in tex, 'supply original base source'
 (output/'base-master.tex').write_text(tex,encoding='utf-8')
 tex=tex.replace(r'\begin{thebibliography}',appendix+'\n'+r'\clearpage'+ '\n'+r'\begin{thebibliography}',1);(output/'master.tex').write_text(tex,encoding='utf-8')
 paths=[output/'base-master.tex',evidence/'records.json',evidence/'audit.json',index/'summary.json',Path(__file__),output/'master.tex',output/'figures/followup_ratios.pdf',output/'followup-summary.csv']
 write_json(output/'followup-provenance.json',dict(code_commit=next(iter(commits)),files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}))
 print(json.dumps(json.loads((evidence/'audit.json').read_text()),indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for key in ['evidence','index','base','output']:p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();build(a.evidence,a.index,a.base,a.output)
