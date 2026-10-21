"""Integrate the audited network/lifetime results into the detailed master."""
import argparse,json,re,shutil
from pathlib import Path
from statistics import median


def esc(s):return str(s).replace('_',r'\_').replace('%',r'\%')

def tab(caption,label,headers,rows):
 return r'\begin{table*}[t]\caption{'+caption+'}\\label{'+label+'}\n'+r'\centering\footnotesize\setlength{\tabcolsep}{5pt}\begin{tabular}{'+'l'*len(headers)+'}\n'+r'\toprule '+' & '.join(headers)+r'\\\midrule'+'\n'+'\n'.join(' & '.join(esc(v) for v in row)+r'\\' for row in rows)+'\n'+r'\bottomrule\end{tabular}\end{table*}'+'\n'

def build(base,summary,output,extension=None):
 output.mkdir(parents=True,exist_ok=False)
 for p in base.rglob('*'):
  if p.is_file() and (p.name in ('master.tex','IEEEtran.cls') or 'figures' in p.parts):
   target=output/p.relative_to(base);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 data=json.loads((summary/'summary.json').read_text());methods=data['methods'];structures=data['structures']
 for p in (summary/'figures').glob('*.pdf'):shutil.copy2(p,output/'figures'/p.name)
 names=sorted(n for n in structures if n.endswith('-s0'))
 def row(name,method):return next(r for r in methods if r['case']==name and r['method']==method)
 def cell(r):
  if r['seconds_median'] is None:return '/'.join(r['statuses']).replace('limit_exceeded','cap')
  return f"{r['seconds_median']:.2f} [{r['seconds_min']:.2f},{r['seconds_max']:.2f}]" + (f" ({sum(v for k,v in r['statuses'].items() if k in ('optimal','infeasible','feasible'))}/{r['n']})" if len(r['statuses'])>1 else "")
 states=[];runtime=[];size=[]
 for n in names:
  s=structures[n];short=n.replace('-network-',' / ').replace('-s0','')
  size.append([short,s['storeys'],s['rooms'],s['targets'],s['actions'],s['bundled_actions'],s['contracted_active_nodes'],s['active_cycle_rank']])
  runtime.append([short,cell(row(n,'uncompressed')),cell(row(n,'lifetime-uncompressed')),cell(row(n,'cp-sat')),cell(row(n,'greedy-improved'))])
  life=row(n,'lifetime-uncompressed');cp=row(n,'cp-sat')
  states.append([short,life['peak_raw_states'] or '--',life['objective'] or '--',cp['objective'] or '--',
   f"{cp['cp_cost_search_seconds']:.4f}" if cp['cp_cost_search_seconds'] is not None else '--',
   f"{cp['cp_tie_search_seconds']:.4f}" if cp['cp_tie_search_seconds'] is not None else '--'])
 solved={m:sum(r['statuses'].get('optimal',0)>0 for r in methods if r['method']==m) for m in ('uncompressed','lifetime-uncompressed','cp-sat')}
 rescued=[n for n in names if row(n,'lifetime-uncompressed')['statuses']=={'optimal':3} and 'optimal' not in row(n,'uncompressed')['statuses']]
 paired=[n for n in names if row(n,'lifetime-uncompressed')['statuses']==row(n,'cp-sat')['statuses']=={'optimal':3}]
 deadline_wins=[n for n in names if row(n,'lifetime-uncompressed')['statuses']=={'optimal':3} and not row(n,'cp-sat')['statuses'].get('optimal',0)]
 wins=[n for n in paired if row(n,'lifetime-uncompressed')['seconds_median']<row(n,'cp-sat')['seconds_median']]
 finding=(f"Across the 15 price variants, lifetime DP completes {solved['lifetime-uncompressed']} and CP-SAT completes {solved['cp-sat']}. On seed 0, lifetime DP completes {len(rescued)} of the five layouts whose original DP controls fail. Its median pipeline time is lower on {len(wins)}/{len(paired)} layouts with three optimal repetitions for both methods. Layouts with three lifetime-DP optima and no CP-SAT optimal pipeline completion under the same deadline: {len(deadline_wins)}. These are descriptive workstation results, not a general runtime superiority claim.")
 body=r'''
\section{Building-Network Study and Event Lifetimes}\label{app:network}
\subsection{Question, Construction and Claim Boundary}
This separate study addresses the earlier evaluation's small active catalogues. It uses the previously fingerprinted clinic and Molio IFC inventories~\cite{publicifc}, preserving original room rings, GlobalIds and consecutive source storeys. The clinic retains 253 rooms on three storeys; Molio retains 93 rooms on eight storeys after the existing nonoverlap selection. All conservative stair/transport background envelopes remain. A fixed 1.6 m grid yields 0.7 m square candidate patches, retaining at most two positions per consecutive room pair, in round-robin endpoint-pair order independent of costs and optimization outcomes. Requested column counts 16, 48, 96 saturate at 36 available Molio columns; duplicate saturated variants are removed. Seeds 0, 1, 2 assign integer abstract segment costs. A complete column bundle costs the sum of its segment prices minus a seeded positive discount; each segment is also separately purchasable. Complete effects and atomic prices remain unchanged by witness selection.

Baseline doors use the existing experimental shared-wall annotation routine. All doors, accessibility profiles, permissions, reservations, connector designs and costs are hypothetical assumptions, not source facts, verified interventions or construction prices. Every room of the largest potential network is demanded from its lowest-storey root for each profile; rooms outside that network are retained in geometry but explicitly excluded from obligations. Source buildings are the independence unit:15 price variants are five catalogue layouts from two sources, not 15 independent buildings. The two profile layers have identical route permissions and demands in this campaign, so they do not independently test permission heterogeneity. The separated grid patches do not introduce competing-owner overlaps; these instances test network choices and atomic bundles, not large owner multiplicity. Original semantic/collision cases remain the evidence for those mechanisms.

The largest clinic catalogue has 190 atomic purchases, 103 destinations, 102 active components after baseline contraction and 22 independent cycles in its potential simple graph. This is materially beyond the former two/three-action source catalogues. Active cycle rank is reported explicitly rather than treating total room count as decision complexity. Molio has more source storeys but a relatively sparse active graph, and is not advertised as equally difficult. Geometric admissibility, exact solving and construction validation are distinct: even a returned optimum certifies only this controlled 2D abstraction.
'''
 body+=tab('New Controlled Network Sizes, Seed 0; Active Nodes and Cycle Rank Use the Potential Simple Graph After Baseline Contraction','tab:network-size',['Source / columns','Storeys','Rooms','Targets','Actions','Bundles','Active nodes','Cycles'],size)
 body+=r'''
\subsection{Safe Early Forgetting}
The floor-interface schedule can retain obsolete information much longer than needed. We add two optional transitions, keeping the original modes as controls. A collision cell is deleted only after the last complete available ownership unit that can occupy it. Owner identities remain throughout each complete unit; full original purchases remain in the objective label and materialized repair. A profile/component vertex is deleted after its last incident baseline edge or individual available action. Connectivity may expire inside a physical unit while its owner identities remain live.

\begin{lemma}[Last-use projection]
Under the fixed recognized catalogue and event schedule, deleting a cell after its last occupying complete unit, and deleting a profile vertex after its last incident event while rejecting a vanished unanchored partition block, preserves every optimal complete-action objective label.
\end{lemma}
\begin{proof}
A continuation cannot occupy a deleted cell, so its previous occupancy cannot affect any later compatibility test. No physical paid effect is deleted from the selection. For a retired vertex, no continuation can attach an edge to it. Deleting it from a surviving block preserves the connectivity relation on every vertex a continuation can touch. If a block disappears without the permanent anchor, that partial witness can never be connected to the root and must be rejected, as in ordinary floor forgetting. Required targets are introduced before incident events by the complete support window; an expired vertex is not reintroduced. Identical projected states retain the minimum original cost/count/ID label. These completion equivalences also justify the unchanged, attributed representative reduction. Induction over the event sequence proves the claim.
\end{proof}
The worst-case interface bound is unchanged; this is an implementation refinement, not a new parameter separation or priority claim. Cell-only and vertex-plus-cell modes are separately observed. A compilation-local cache reuses successful fixed connection/profile, pair-overlap, room/profile free-space and landing predicates for one immutable input. Every method shares this recognizer improvement; it is not attributed solely to DP. Final materialization recomputes the returned selection without reusing the compilation cache. The final implementation passes 765 regression tests, including seeded exhaustive comparisons and cached/uncached geometry equivalence; test counts are correctness evidence, not research novelty.

\subsection{Fixed Measurement Protocol}
Final measurements use clean revision \texttt{COMMIT}, 15 frozen price variants and 70 fresh-process observations. The incomplete earlier clean campaign and changing-code probes are preserved separately and excluded; no measurements are spliced. Seed 0 runs lifetime DP and CP-SAT three times per layout. Other price seeds run those methods once. Original uncompressed DP, cell-only DP, compressed lifetime DP and improved greedy run once on seed 0 per layout; their times are descriptive single observations. The six-method list rotates by repetition; the primary DP/CP-SAT relative order is not reversed in these three repetitions. No randomized order or thermal control is claimed. The parent limit is 30 s, CP-SAT's internal budget 27 s, with one worker/seed 0; DP caps are 100000 raw states and 65536 cut columns. Manifest seed 0 is the solver seed; the separately stored price-generation seeds are 0, 1, 2.

Function wall time includes fresh recognition and solver materialization/replay, excluding imports. Parent wall time includes imports and the additional audit replay. CP-SAT must finish exact cost, count and sorted-ID stages; Table~\ref{tab:network-states} separately reports its cost-search and subsequent tie-search wall times. These search times exclude model construction and are not directly interchangeable with DP optimization-phase time. A pipeline gain caused by tie handling is not evidence of harder minimum-cost optimization. Every returned selection is checked for obligations, unchanged room identity/polygons/adjacency, complete paid-box overlap and exact cost. Large optima are cross-method agreement, not exhaustive enumeration; small exhaustive cases validate the transitions.
'''.replace('COMMIT',data['code_commit'][:12])
 body+=tab('Pipeline Seconds: Median [Minimum,Maximum] for Completed Runs; Original/Greedy Controls Have One Observation, Lifetime DP/CP-SAT Three on Seed 0','tab:network-runtime',['Source / columns','Original DP','Lifetime DP','CP-SAT','Improved greedy'],runtime)
 body+=tab('Peak Lifetime-DP States, Exact Abstract Costs and CP-SAT Search-Stage Medians, Seed 0; Missing Completion Is Not Infeasibility','tab:network-states',['Source / columns','DP states','DP cost','CP cost','CP cost search(s)','CP tie search(s)'],states)
 body+='\n\\subsection{Outcomes and Limits}\n'+finding+'\n'
 body+=r'''
Explicit nonoptimal all-segment witnesses also pass full materialization for all 15 price variants, so unresolved cases are not unexplained feasibility failures. The medium clinic seed 0 control costs 342 abstract units, versus the DP-proven optimum 267; the largest clinic control costs 726 and the larger Molio control 198. These are reproducible feasibility controls, not independent optimality certificates or actual prices.

The earlier 15 connectivity cases remain slower with representative compression; no claim that rank reduction caused the new gain is made. Compressed lifetime runs retain their cut-limit outcomes. The useful refinement here is earlier event forgetting in the uncompressed floor-interface implementation. Tables preserve infeasibility, caps and timeouts separately; heuristic failure or timeout is never an infeasibility certificate. This study expands the optimization workload and can establish bounded implementation utility. It cannot establish representative real-building performance, approved intervention feasibility, generic algorithmic superiority or literature priority.
\begin{figure*}[t]\centering\includegraphics[width=.96\textwidth]{figures/network-outcomes.pdf}
\caption{New seed 0 outcomes. Green cells denote completed optimal pipelines, orange operational caps and red parent timeouts; each cell states its repetition count. All price-seed outcomes remain in the release records.}\label{fig:network-outcomes}\end{figure*}
\begin{figure*}[t]\centering\includegraphics[width=.96\textwidth]{figures/network-building.pdf}
\caption{Original clinic room projections for the 78-purchase case: green patches are the complete lifetime-DP selection and orange patches the unselected hypothetical candidates. Source geometry is retained; this is a controlled network overlay, not a proposed approved lift layout or construction drawing.}\label{fig:network-building}\end{figure*}
\begin{figure*}[t]\centering\includegraphics[width=.88\textwidth]{figures/network-difficulty.pdf}
\caption{Active network and purchase complexity. The larger clinic variants introduce many destinations and independent cycles. Molio's eight storeys alone do not imply equally difficult connectivity.}\label{fig:network-difficulty}\end{figure*}
'''
 if extension is not None:
  e=json.loads(extension.read_text())
  erows=[]
  for method in ('lifetime-uncompressed','cp-sat'):
   r=e['methods'][method]
   statuses=', '.join(str(v)+' '+k.replace('_',' ') for k,v in r['statuses'].items())
   time='--' if r['seconds_median'] is None else f"{r['seconds_median']:.2f} [{r['seconds_min']:.2f},{r['seconds_max']:.2f}]"
   erows.append([method,statuses,time,', '.join(str(x) if x is not None else '--' for x in r['costs'])])
  ext=r'\subsection{Separate Larger-Budget Boundary Check}'+'\n'
  ext+=('After the fixed campaign, the same largest clinic seed 0 input is rerun three times per method with a 90s parent deadline, 75s internal CP-SAT budget and 500000 DP states. The two methods alternate order by repetition. This post-hoc resource extension is kept separate from the original 70 observations and does not replace their failures. ' + 'The original failures remain in the primary tables.\n')
  ext+=tab('Separate 90s Extension on the 190-Purchase Clinic Case; Incumbents Are Feasible Repairs, Not Proven Exact Optima','tab:network-budget',['Method','Outcomes (n=3)','Returned repair seconds','Returned costs'],erows)
  cp=e['methods']['cp-sat']
  cost_values=', '.join(sorted({str(c) for c in cp['costs'] if c is not None}))
  bound_values=', '.join(sorted({str(c) for c in cp['best_cost_bounds'] if c is not None}))
  gaps=', '.join(sorted({f'{100*g:.2f}' for g in cp.get('relative_cost_gaps',[])}))
  search_times=[t for t in cp['cp_cost_search_seconds'] if t is not None]
  search=median(search_times) if search_times else 0
  ext+=(f'The three CP-SAT runs return replay-valid incumbent repairs of abstract cost {cost_values}, with cost lower bounds {bound_values} and remaining relative gaps {gaps}'+r'\%.'+f' Its median minimum-cost search time is {search:.2f}s; this stage remains unproved, before count/identifier tie optimization. The DP returns no completed repair at the larger deadline. Table~'+r'\ref{tab:network-budget} reports the elapsed time of feasible incumbent returns despite their nonoptimal status. These solver bounds establish unresolved minimum-cost optimization, not verified construction prices or real-building repair validation.'+'\n')
  if (summary/'figures/network-budget.pdf').exists():
   ext+=r'\begin{figure*}[t]\centering\includegraphics[width=.85\textwidth]{figures/network-budget.pdf}\caption{Larger-budget minimum-cost intervals. Each upper endpoint is a replay-valid complete repair; each lower endpoint is the solver bound. The interval is unresolved optimization, not a statistical confidence interval or construction-price estimate.}\label{fig:network-budget}\end{figure*}'+'\n'
  body=body.replace(r'\begin{figure*}[t]',ext+r'\begin{figure*}[t]',1)
 text=(output/'master.tex').read_text()
 text=text.replace('The source-derived catalogues contain only two or three actions and use hypothetical access permissions, reservations and costs. They support input and semantic checks, not difficult practical building optimization.', 'The earlier source catalogues contain only two or three actions. A separate network study adds 15 hypothetical price variants from five catalogue layouts on three clinic and eight Molio storeys, reaching 190 purchases and 103 destinations. Safe event-lifetime forgetting expands the exact DP completion range; Appendix~\\ref{app:network} reports all comparisons and failures. These building-derived controlled experiments do not validate real interventions.')
 text=text.replace('No compelling practical advantage or priority over every generic connectivity/resource method is established.', 'The new refinement establishes bounded implementation utility rather than general superiority; priority over generic connectivity/resource methods remains unconfirmed.')
 text=text.replace('No compelling practical advantage has emerged.', 'The original campaign establishes no compelling practical advantage. The separate event-lifetime study (Appendix~\\ref{app:network}) demonstrates bounded completion improvements over that DP implementation; it does not establish general superiority over CP-SAT.')
 text=text.replace('Current timings do not justify a performance claim; decision-simple source-derived catalogues do not establish practical building utility. A convincing practical evaluation requires nontrivial evidence-backed intervention choices, while a theoretical publication claim requires a stronger checked distinctness argument for the complete construction.', 'The earlier timings do not justify a compression speedup. The new event-lifetime refinement and larger source-derived networks expand the tested completion range, with all limits and CP-SAT comparisons retained in Appendix~\\ref{app:network}. Actual-building repair utility still requires verified interventions and permissions; theoretical priority still requires a stronger checked distinctness argument for the complete construction.')
 marker=r'\clearpage'
 assert marker in text
 text=text.replace(marker,body+'\n'+marker,1)
 text=text.replace(r'\begin{thebibliography}{00}',r'\IEEEtriggeratref{11}'+'\n'+r'\begin{thebibliography}{00}',1)
 (output/'master.tex').write_text(text,encoding='utf-8')
 (output/'network-section.tex').write_text(body,encoding='utf-8')
 (output/'network-findings.json').write_text(json.dumps(dict(solved_variants=solved,rescued_seed0_layouts=rescued,paired_optimal_layouts=paired,lower_median_layouts=wins,deadline_advantage_layouts=deadline_wins,finding=finding),indent=2))
 print(finding)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--summary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--extension',type=Path);a=p.parse_args();build(a.base,a.summary,a.output,a.extension)
