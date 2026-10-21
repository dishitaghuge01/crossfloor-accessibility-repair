"""Research-first manuscript from preserved theory and the frozen joint study."""
import argparse,json,re,shutil,statistics
from decimal import Decimal
from pathlib import Path


def esc(value):
    return str(value).replace('_',r'\_').replace('%',r'\%')


def table(caption,label,headers,rows):
    return ('\\begin{table*}[t]\\caption{'+caption+'}\\label{'+label+'}\n'
        '\\centering\\footnotesize\\setlength{\\tabcolsep}{4pt}\\begin{tabular}{'+'l'*len(headers)+'}\n'
        '\\toprule '+' & '.join(headers)+r'\\\midrule'+'\n'+
        '\n'.join(' & '.join(esc(x) for x in row)+r'\\' for row in rows)+
        '\n\\bottomrule\\end{tabular}\\end{table*}\n')


def build(base,summary,output,async_figure,parameter_summary=None,segment_controls=None,event_width_summary=None):
    data=json.loads((summary/'summary.json').read_text())
    output.mkdir(parents=True,exist_ok=False)
    (output/'figures').mkdir()
    shutil.copy2(base/'IEEEtran.cls',output/'IEEEtran.cls')
    for p in (base/'figures').glob('*.pdf'):
        if p.name in ('integrated_example.pdf','unit_witness.pdf','pipeline.pdf'):
            shutil.copy2(p,output/'figures'/p.name)
    for p in (summary/'figures').glob('*.pdf'):
        if p.name in ('joint-outcomes.pdf','joint-cp-tasks.pdf','joint-selected-graph.pdf'):
            shutil.copy2(p,output/'figures'/p.name)
    parameters=json.loads((parameter_summary/'summary.json').read_text()) if parameter_summary else None
    controls={c['instance_id']:c for c in json.loads(segment_controls.read_text())['cases']} if segment_controls else {}
    width_data=json.loads((event_width_summary/'summary.json').read_text()) if event_width_summary else None
    if parameters:
        shutil.copy2(parameter_summary/'figures/parameter-families.pdf',output/'figures/parameter-families.pdf')
    shutil.copy2(async_figure,output/'figures/asynchronous-retirement.pdf')
    old=(base/'master.tex').read_text()
    preamble=old[:old.index(r'\begin{abstract}')]
    preamble=preamble.replace('[BoldFont=','[NFSSFamily=ptm,BoldFont=')
    preamble=preamble.replace(r'\begin{document}',r'''
\setcounter{topnumber}{4}
\setcounter{dbltopnumber}{6}
\setcounter{totalnumber}{12}
\renewcommand{\topfraction}{.95}
\renewcommand{\dbltopfraction}{.95}
\renewcommand{\textfraction}{.05}
\makeatletter
\setlength{\@fptop}{0pt}
\setlength{\@fpsep}{12pt}
\setlength{\@fpbot}{0pt plus 1fil}
\setlength{\@dblfptop}{0pt}
\setlength{\@dblfpsep}{12pt}
\setlength{\@dblfpbot}{0pt plus 1fil}
\makeatother
\begin{document}''')
    totals=data['method_totals'];both=totals['both']['exact'];floor=totals['floor']['exact'];cp=totals['cp-sat']['exact']
    abstract=r'''\begin{abstract}
We study exact cross-floor accessibility repair over frozen room geometry, profile-specific demands and a finite catalogue of physical interventions.
Bundled purchases may share one owner or conflict through an effect unused by every access route, so graph connectivity alone cannot determine feasibility.
We construct an owned-interface dynamic program that retains complete paid occupancy while compressing separate profile route witnesses using established representative-partition machinery.
We establish safe event-lifetime projection: connectivity vertices retire after their final incident event, while physical owner information survives complete action--owner units, preserving the cost/count/identifier objective.
In a frozen, counterbalanced building-derived interaction study, combined projection completes BOTH of14 exact runs compared with FLOOR for floor retirement, while the strengthened CP-SAT baseline completes CP.
Neither a practical speedup from representative reduction nor general superiority over CP-SAT is supported, and explicit segment controls distinguish heuristic failure from infeasibility.
The results concern hypothetical intervention catalogues and abstract costs on source-derived geometry, rather than validated construction repairs.
\end{abstract}
\begin{IEEEkeywords}accessibility repair, ownership constraints, bundled network design, exact optimization, event lifetimes\end{IEEEkeywords}
'''.replace('BOTH',str(both)).replace('FLOOR',str(floor)).replace('CP.',str(cp)+'.')
    intro=old[old.index(r'\section{Introduction}'):old.index(r'\subsection{Research Question and Contributions}')]
    contribution=r'''
We ask whether complete physical purchases can be preserved while retaining only
information needed by the unprocessed catalogue. The paper has three contributions:
\begin{enumerate}
\item An explicit recognized physical-to-owned-interface construction, with exact
whole-purchase accounting and a scoped floor-interface guarantee.
\item A model-specific asynchronous projection argument separating route-vertex
expiry from complete-unit owner retirement; the underlying last-use and weighted
partition techniques are attributed to prior work.
\item A reproducible evaluation of all five retirement/compression variants on
identical interacting inputs, including strengthened exact and heuristic baselines,
stage traces, feasibility controls and preserved failures.
\end{enumerate}
These claims concern the stated construction and evidence. Priority of the complete
construction remains unconfirmed; no exclusive expressive power or generic-method
lower bound is asserted.
\section{Closest Formulations and Distinction}
Condition Steiner networks already buy infrastructure once for condition-specific
demands~\cite{condition}; simultaneous restricted-link design makes overlapping
permissions explicit~\cite{simultaneous}. Labelled connectivity supplies shared
purchase semantics~\cite{labels}, and Steiner selection with conflicts supplies
incompatibilities~\cite{conflicts}. These features individually are prior work.
Their inspected formulations do not themselves give this complete recognized
physical-to-owned-interface construction. That is a formulation distinction, not
proof that every equivalent construction is absent from the literature.

Weighted partition project/forget operations and representative families are prior
machinery~\cite{rank}: deleting a vertex while rejecting a vanished unrooted block
is not claimed as an invented technique. Our additional obligation is to show when
that deletion is safe without erasing a paid footprint or a reusable owner.
Weighted A\&C neighborhood logic~\cite{logic} can express the complete selections
through our Action/Occurrence/Usage/Cell reduction. Expressibility is therefore
not the research gap. Its applicable optimizer needs a supplied decomposition;
our explicit expression transfers its guarantee with the bound in
Appendix~\ref{app:generic}. A finite-domain resource DP supplied with our schedule
can match the owner-domain factor, so that factor alone proves no separation.
The artifact's closest-work matrix records input, purchases, demands, conflicts,
objectives, parameters and exact section/theorem locators for these comparisons.
The explicit Boolean Usage encoding transfers the generic theorem as
\begin{equation}
T_{\rm rec}+2^{O(prL+zL+p+zLh)}\poly(B),\label{eq:generic}
\end{equation}
where the symbols are defined in Table~\ref{tab:parameters}. This is an upper
bound for that encoding, not a lower bound for other generic constructions.
'''
    core=old[old.index(r'\section{Strict Repair Model}'):old.index(r'\section{Experimental Design}')]
    core=re.sub(r'\\begin\{table\*\}\[t\]\s*\\caption\{Operational Proof Map\}.*?\\end\{table\*\}', '',core,flags=re.S)
    core=core.replace('These operational names map to the implemented steps, not additional unimplemented routines. ', '')
    core=core.replace('the unlimited-state algorithm returns the optimum strict original-action label. Its bit-complexity bound is',
        'the algorithm with representative reduction after every event and without operational caps returns the optimum strict original-action label. Its bit-complexity bound is')
    core=core.replace('This guarantee concerns the recognized finite model.',
        'All uncapped variants retain exactness; the displayed single-exponential connectivity bound specifically uses representative reduction. This guarantee concerns the recognized finite model.')
    split=core.index(r'\subsection{Conditional Guarantee and State Size}')
    before,after=core[:split],core[split:]
    event=r'''
\section{Event-Lifetime Projection}
Fix ordered events $e_1,\ldots,e_m$. Introduce the initial $L$ floors. At each
floor process baseline edges in stable catalogue/profile order, complete units
starting there in recognized order, and sorted original IDs inside each unit;
then close each unit, forget the floor and introduce the next window floor.
Reverse-order tests reverse local edge/unit/action lists, never split units or
reverse floor introduction. Required targets enter once before incident events;
optional witness vertices enter when a selected effect uses them.
For profile-component vertex $v$, define
\begin{equation}\lambda_V(v)=\max\{t:e_t\text{ can introduce an edge incident to }v\}.
\end{equation}
The maximum ranges over available actions and baseline edges, independently of
which purchases or witness effects are selected. Nodes with no such event retain
ordinary floor forgetting. Permanent virtual anchors never retire.

Include unit-close operations among physical events and define
\begin{equation}\lambda_C(c)=\max\{t:e_t\text{ closes a unit touching }c\}.
\end{equation}
Here a unit touches $c$ when an available action occupies it.
This conservative physical lifetime includes every paid effect, even disconnected
effects omitted from all route witnesses. A cell keeps current owner identity
until its unit closes; later units see external occupancy. It can be erased only
after its final relevant unit or the already valid floor boundary.
\begin{lemma}[Asynchronous projection]\label{lem:lifetime}
Projecting a vertex after $\lambda_V$, rejecting any vanished nonanchor block,
and erasing a cell after $\lambda_C$ preserves the exact complete-action optimum.
\end{lemma}
\begin{proof}
No continuation can attach an edge to a retired vertex; restricting a surviving
block preserves relations on all vertices still usable by a continuation. A
vanished nonanchor block can never reach its root. Required nodes enter before
their incident events, and no later event can reintroduce an expired node. No
future unit can inspect or occupy an erased cell. Identity is erased only after
all actions sharing it have been processed, by incidence-component closure.
Projection changes no original-action label or final materialized effects.
Identical projected keys retain their minimum label; adding a fixed disjoint
suffix preserves exact cost, count and sorted-ID order. These continuation
equivalences also preserve the applicability of the attributed weighted bases.
Induction over the schedule proves the claim.
\end{proof}

Figure~\ref{fig:async} illustrates two purchases using the same connector owner:
$a$ activates profile0 for cost2 and $b$ profile1 for cost3. After $a$, profile0's
target vertex can retire, but the owner must remain to admit compatible $b$.
Converting it to external occupancy too early rejects the cost5 repair. Erasing
the cell instead would allow a later competing owner $Q$.
Here $Q$ shares the root-floor cell but connects to a different third-floor room,
so it has no later incidence at either expiring target.
At unit closure owner identity becomes an occupied bit; only after $Q$'s unit may that bit disappear.
Skipping $a$ leaves its required vertex in a disappearing unrooted block and
rejects that row. The artifact supplies the event-by-event state/label trace and
exhaustive cross-solver checks. This example demonstrates unnecessary retention,
not an asymptotic speedup by itself.
\begin{figure*}[t]\centering
\includegraphics[width=.95\textwidth]{figures/asynchronous-retirement.pdf}
\caption{Connectivity and physical resources have different last uses. A deleted
route vertex does not authorize deleting paid occupancy or erasing a reusable
owner. This is an explanatory semantic trace, not building measurement.}
\label{fig:async}\end{figure*}

A tighter event-width theorem would need potential vertices across all states,
eager target introductions, transient action branching, cell domains and actual
reduction work. A maximum observed selected boundary after projection is not
sufficient. We retain the proved floor-interface bound below and claim no new
event-width separation. The implementation refinement can help even though its
coarse worst-case theorem is unchanged.
'''
    after=after.replace(r'\subsection{Conditional Guarantee and State Size}',r'\section{Complexity and Hardness Boundary}')
    protocol=r'''
\section{Experimental Protocol}
The primary study uses frozen revision \texttt{REVISION}, seven layout/constraint
combinations from five catalogue layouts and two licensed source buildings.
The licensed source geometry~\cite{publicifc} retains253 Clinic rooms on three storeys and93 Molio rooms on eight
storeys. Fifteen generated inputs comprise three tiers per layout; the measured
subset contains all five full-interaction layouts and the smallest Clinic layout
in connectivity/resource tiers. Price seed is fixed at zero. These are not seven
independent buildings, and the design is not a complete factorial experiment.

Connectivity tier retains the original bundled network choices. Resource tier
adds alternative owners with overlapping whole paid footprints in every second
candidate column; original segment/bundle actions preserve compatible owner reuse.
Full tier restricts the cheaper alternatives to one profile and divides the
original destination set into nonempty complementary profile demands, so neither
profile's requirements subsume the other. Baseline access, reservations, connector
design, permissions and abstract costs are declared experimental assumptions.
They are not verified interventions or monetary construction estimates.
The original destination set comprises every nonroot room in the largest potential
connected network, rooted at a lowest-storey room. Other retained rooms stay in
geometry checking but are excluded from obligations; full-tier demand unions keep
the original destination set.

Every input is run twice with eight methods: floor retirement; cells only;
vertices only; both rules; both plus rank reduction; strengthened CP-SAT; cold
improved greedy; and the all-original-segment feasibility control. Method order
is forward then reverse per input, counterbalancing every pair. All112 scheduled
observations are retained. Fresh workers execute sequentially with a common60s
external pipeline deadline,55s internal CP/greedy budget,100000 raw-state cap,
65536 cut-column cap and no enforced RAM cap. Primary time includes startup,
recognition, model construction, optimization and required replay; optional parent
recovery auditing is outside the deadline. Two repetitions give descriptive
ranges, not confidence intervals. Unrelated machine activity is not controlled.

\subsection{Exact Baseline and Declared Tasks}
CP-SAT uses the same recognized unary filters and whole owner/cell capacities,
separate profile flows and original purchase variables. It solves cost, then count,
then sorted-ID membership preferences with equality constraints on prior optima.
Each stage receives the previous optimum as a purchase hint; blocked fixed-zero
IDs need no additional solve. This is internal continuation, not external warm
starting. One search worker and solver seed0 are fixed. No unnecessary identifier
stages are attributed to minimum-cost optimization.

Task A is minimum cost: incumbent, lower bound, first/best feasible time and cost
proof time. Task B is the full cost/count/IDs objective. Flushed stage/solution
events survive termination; callback candidates remain unverified until replay.
Event times start at the CP solver clock after OR-Tools import and include
recognition/model construction; full parent pipeline time additionally includes
worker/import startup. Search-stage seconds have a still narrower scope.
Post-deadline recovery checks do not convert a timeout into completed Task B.
The separate three-run78-action diagnostic proves cost and count in all runs,
completes Task B once and reaches ID-stage deadlines twice. Those three posthoc
observations are not pooled with the112 primary observations or used to reconstruct
lost historical stages.

\subsection{Heuristic, Controls and Profiling}
Development profiling identified repeated proposal materialization as the dominant
heuristic overhead. The revised greedy tests complete paid-cell compatibility and
reachability through the immutable recognized model, with full replay of returned
repairs. It preserves a verified incumbent before local improvement and can stop
at an internal deadline. The transparent original-segment control establishes
feasibility where a cold greedy choice fails; it claims no optimality.

All DP variants use the same optional profiling, separately measuring recognition,
event construction, state generation, dictionary merging, reduction, labels,
reconstruction and replay. Label handling is a subset of generation, not additive.
Live-vertex statistics describe observed state unions/selected rows; they do not
instantiate an unproved event theorem. Missing data after hard termination remain
missing. Instrumentation overhead prevents attributing cross-revision timing
differences solely to projection. Caps are distinct from timeouts and infeasibility.
Memory denotes the fresh worker's peak working set, including imports; parent-driver
and whole-machine memory are not included.
'''.replace('REVISION',data['protocol']['code_revision'][:7])
    results=r'\section{Results and Ablations}'+'\n'
    result_rows=[]
    for m in data['protocol']['methods']:
        t=totals[m]
        failures=', '.join(f'{k}:{v}' for k,v in t['failures'].items()) or 'none'
        result_rows.append([m,f"{t['exact']}/14",f"{t['verified_feasible']}/14",failures])
    results+=table('Primary Joint Study: Completed Exact Objectives and Verified Feasibility; Recovered Candidates Are Not Completed Pipelines','tab:joint-total',['Method','Exact','Verified feasible','Failures'],result_rows)
    stats_rows=[]
    for case in data['protocol']['cases']:
        s=data['structures'][case['instance_id']]
        stats_rows.append([case['instance_id'].replace('-network-','/').replace('-s0',''),s['storeys'],s['rooms'],s['actions'],
            '/'.join(str(v) for k,v in sorted(s['demands_by_profile'].items())),s.get('conflict_pairs','--'),
            s['bundled_actions'],s['contracted_active_nodes'],s['active_cycle_rank']])
    results+=table('Instance Statistics: Potential Simple Graph after Common Baseline-Door Contraction; Price Seed Zero','tab:joint-size',
        ['Input','Storeys','Rooms','Actions','Targets p0/p1','Conflicts','Bundles','Nodes','Cycles'],stats_rows)
    results+=r'''\begin{figure*}[t]\centering
\includegraphics[width=.97\textwidth]{figures/joint-selected-graph.pdf}
\caption{Paid profile-specific effects in the109-purchase Clinic instance, using
the saved optimum. Schematic component positions follow storeys; blue nodes are
required components, and the red star is the root. Gray edges are potential
connections. Orange alternative-owner effects are permitted only in profile0.
Ownership conflicts are checked separately through all paid footprints; a graph
view alone does not certify physical compatibility.}
\label{fig:selected-graph}\end{figure*}
'''
    results+=r'''\begin{figure*}[t]\centering
\includegraphics[width=.97\textwidth]{figures/joint-outcomes.pdf}
\caption{All primary outcomes by input and method. Each cell reports two
repetitions. Feasible controls and recovered candidates are distinguished from
completed exact pipelines. Failure details remain in the per-run artifacts.}
\label{fig:joint}\end{figure*}
'''
    results+='The floor variant completes '+str(floor)+' of14 exact runs; both rules complete '+str(both)+', and CP-SAT completes '+str(cp)+'. These are counts of repeated runs across the declared seven input combinations, not independent building samples. Table~\\ref{tab:joint-total} and Fig.~\\ref{fig:joint} retain failure causes and feasible controls. No average treats a timeout as a completed solve.\n'
    result_rows=[]
    for case in data['protocol']['cases']:
        matches=[s for s in data['summaries'] if s['instance_id']==case['instance_id']]
        cells=[]
        for m in ('floor','cells','vertices','both','both-rank','cp-sat'):
            s=next(x for x in matches if x['method']==m)
            cells.append(f"{s['exact']}/2"+(' '+f"{s['pipeline_median']:.2f}" if s['pipeline_median'] is not None else ''))
        result_rows.append([case['instance_id'].replace('-network-','/').replace('-s0','')]+cells)
    results+=table('Exact Completion and Completed Pipeline Median Seconds; No Time Is Imputed for Failed Runs','tab:joint-case',
                   ['Input','Floor','Cells','Vertices','Both','Both+rank','CP-SAT'],result_rows)
    results+=r'''\begin{figure*}[t]\centering
\includegraphics[width=.48\textwidth]{figures/joint-cp-tasks.pdf}
\caption{Minimum-cost proof, count proof and full identifier objective are
different completion criteria. Search traces preserve this distinction at limits.}
\label{fig:cp-tasks}\end{figure*}
'''
    task_rows=[]
    for case in data['protocol']['cases']:
        tasks=[t for t in data['cp_tasks'] if t['instance_id']==case['instance_id']]
        task_rows.append([case['instance_id'].replace('-network-','/').replace('-s0',''),
            sum(t['cost_stage_status']=='OPTIMAL' for t in tasks),
            sum(t['count_stage_status']=='OPTIMAL' for t in tasks),
            sum(t['full_objective_status']=='optimal' for t in tasks),
            '/'.join(str(t['cost_incumbent']) for t in tasks),
            '/'.join(str(t['cost_lower_bound']) for t in tasks),
            '/'.join(f"{100*(Decimal(t['cost_incumbent'])-Decimal(str(t['cost_lower_bound'])))/Decimal(t['cost_incumbent']):.1f}%" if t['cost_incumbent'] is not None and t['cost_lower_bound'] is not None and Decimal(t['cost_incumbent'])>0 else '--' for t in tasks)])
    results+=table('CP-SAT Tasks: Proof Counts out of Two; Cost Incumbents and Bounds Remain Separate by Repetition','tab:cp-task-data',
        ['Input','Cost proof','Count proof','Full IDs','Incumbents','Bounds','Gap'],task_rows)
    paired=[];metric_rows=[]
    for case in data['protocol']['cases']:
        iid=case['instance_id'];lookup={s['method']:s for s in data['summaries'] if s['instance_id']==iid}
        a,b=lookup['both'],lookup['cp-sat']
        if a['exact']==b['exact']==2:
            paired.append([iid.replace('-network-','/').replace('-s0',''),f"{a['pipeline_median']:.2f}",f"{b['pipeline_median']:.2f}",f"{a['pipeline_median']/b['pipeline_median']:.2f}"])
        for method in ('both','cp-sat'):
            s=lookup[method];mem=[m/1048576 for m in s['memory_bytes'] if m is not None]
            ss=[x for x in s['statistics'] if x is not None and 'peak_raw_states' in x]
            if ss:
                metric_rows.append([iid.replace('-network-','/').replace('-s0',''),
                    max(x['peak_raw_states'] for x in ss),max(x['peak_live_selected_vertices'] for x in ss),
                    max(x['peak_live_occupancy_cells'] for x in ss),max(x['peak_owner_domain_size'] for x in ss),
                    f"{max(mem):.0f}" if mem else '--',
                    f"{statistics.median(x['state_generation_seconds'] for x in ss):.3f}",
                    f"{statistics.median(x['state_merge_seconds'] for x in ss):.3f}",
                    f"{statistics.median(x['objective_label_seconds'] for x in ss):.3f}"])
    if paired:
        results+=table('Paired Fully Completed Inputs Only: Pipeline Medians and Their Descriptive Ratio','tab:paired',
            ['Input','Both DP (s)','CP-SAT (s)','DP/CP'],paired)
    phase_figure=''
    if metric_rows:
        results+=table('Returned Combined-DP Profiles; Caps/Killed Workers Do Not Supply These State Measurements','tab:profile',
            ['Input','Peak raw','Vertices','Cells','Domain','MiB','Gen. (s)','Merge (s)','Labels (s)'],metric_rows)
        phase_figure=r'''\begin{figure*}[t]\centering
\includegraphics[width=.97\textwidth]{figures/joint-phases.pdf}
\caption{Combined-DP phase profiles on fully completed inputs only. Objective
label handling is included in generation. Other optimization includes uninstrumented
work and profiling overhead; capped runs are not assigned invented phase times.}
\label{fig:phases}\end{figure*}
'''
    quality=[]
    for case in data['protocol']['cases']:
        iid=case['instance_id'];lookup={s['method']:s for s in data['summaries'] if s['instance_id']==iid}
        def costs(method):
            return '/'.join(str(c) if c is not None else '--' for c in lookup[method]['feasible_costs'])
        first=[t for t in lookup['greedy-cold']['first_verified_seconds'] if t is not None]
        quality.append([iid.replace('-network-','/').replace('-s0',''),costs('cp-sat'),costs('greedy-cold'),costs('segment-control'),
                        controls[iid]['cost'] if iid in controls else '--',
                        f"{min(first):.2f}--{max(first):.2f}" if first else '--'])
    results+=table('Feasible Abstract Costs by Repetition; Greedy First Verified Time Uses Its Function Clock, Excluding Worker Startup','tab:quality',
        ['Input','CP feasible','Greedy feasible','Timed all S','Relevant S','Greedy first (s)'],quality)
    if controls:
        results+=r'''Relevant-S controls omit original segments outside the union
of demanded rooms and roots. These seven additionally replayed constructive
controls are untimed and excluded from the112 primary observations; the timed
all-S observations remain unchanged. Neither construction certifies optimality.
Each retained S is a whole original action; no bundle is shortened.
'''
    results+=r'''The profile table reports generation, merging and label costs
separately; labels are included in generation, so the columns must not be summed.
The supplementary phase plot retains recognition, reconstruction and replay as
well. On capped runs these internal measurements are missing rather than
reconstructed from the deadline; the state-cap error itself proves that the
raw-state limit was exceeded. No unmeasured memory saving is claimed.
'''
    if parameters:
        assert parameters['observations']==276
        assert all(t['exact']==46 for t in parameters['method_totals'].values())
        results+=r'''\subsection{Separate Structural Families}
The authored structural study has23 inputs in eight families: active connectivity,
action count, within-unit owner competition, bundle size, unit span, event ordering,
profile heterogeneity and conflict density. Five DP variants and CP-SAT run twice
in forward/reverse order, giving276 separate observations with a30s external
deadline and25s internal CP budget. All methods agree on the complete original
cost/count/ID objective for every input in both repetitions.

Figure~\ref{fig:parameters} reports descriptive pipeline medians, including worker
startup. These short runs are substantially affected by import/recognition overhead;
their timing ratios are not evidence of broad optimization superiority. The artifact
states fixed and varying quantities per family. Complete-graph growth couples width,
actions and span; owner competition couples h,g and action count; unit sharing changes
footprint locations and z; action-ID reordering can change identifier ties; footprint
changes alter cell arrangements. No isolated causal effect is inferred from these
coupled families. Bundle coverage and profile permissions vary on otherwise fixed
catalogues; zero/nonzero conflict levels have fixed route graphs and costs.
\begin{figure*}[p]\centering
\includegraphics[width=.97\textwidth,height=.85\textheight,keepaspectratio]{figures/parameter-families.pdf}
\caption{Eight separate structural families, two counterbalanced repetitions per
input and method. Family levels are declared design changes, not independent
building samples. Every run completes here; medians are descriptive pipeline times
with startup included, and coupled changes prevent width-only causal attribution.}
\label{fig:parameters}\end{figure*}
'''
    if width_data:
        assert width_data['observations']==24 and all(t['exact']==4 for t in width_data['method_totals'].values())
        width_rows=[]
        for order in ('paired','batched'):
            for method in ('floor','both'):
                row=next(r for r in width_data['summaries'] if r['instance_id']=='event-width-'+order and r['method']==method)
                stats=row['statistics']
                width_rows.append([order,method,max(x['peak_live_vertex_union'] for x in stats),
                    max(x['peak_live_occupancy_cells'] for x in stats),max(x['peak_raw_states'] for x in stats),'3'])
        results+=r'''\subsection{Targeted Event-Frontier Followup}
The original complete-graph schedule pair has measured width4 in both orders,
so it does not demonstrate a width change. A separate posthoc control uses the
same six-floor $K_{2,4}$ graph, eight purchases, one complete owner unit, edge
costs and source/target. Paired events retire each intermediate vertex before
introducing the next; batched events retain all four. All six methods agree in
24 additional counterbalanced runs under the30s protocol. The unique physical
optimum costs3 in both ID orderings. Connectivity width changes while six paid
cells remain live; Table~\ref{tab:event-width} isolates the retention mechanism.
This is a separate followup, not a replacement for the276-run null-control
record or a proof of asymptotic full-interface separation. Worker startup
dominates these small timings, so state counts provide the informative result.
'''
        results+=table('Posthoc Event-Frontier Control: Same Graph, Geometry, Prices and Ownership; Two Identical State Profiles per Row','tab:event-width',
            ['Order','Variant','Live vertices','Occupied cells','Peak raw states','Optimum'],width_rows)
    results+=r'''
The historical connectivity stress study remains unfavorable to rank compression:
it was slower on all15 seeded inputs and CP-SAT completed four natural inputs
that exceeded compressed caps. That campaign used an earlier revision and is
reported separately in the supplementary evidence. It is not pooled with the
new ablation. The separate larger-budget historical Clinic boundary returned
CP-SAT cost470 with bound335 and no proof; lifetime DP timed out.

\begin{samepage}\noindent Incumbent costs and lower bounds are separate evidence;
neither an incomplete objective nor a state cap certifies an optimum.\par\end{samepage}
'''
    parameter_plot=re.search(r'\\begin\{figure\*\}\[p\].*?\\label\{fig:parameters\}\\end\{figure\*\}',results,re.S)
    if parameter_plot:
        results=results.replace(parameter_plot.group(0),'')+'\n'+parameter_plot.group(0)+'\n'
    limitations=r'''
\section{Limitations and Conclusion}
The construction is exact within a recognized finite strict model. It does not
optimize all constructible interventions or validate structure, headroom,
operational lift capacity or statutory accessibility. Source-derived geometry
does not authenticate our hypothetical reservations, permissions and abstract
costs. The two buildings and five layouts are a limited evaluation population;
two repetitions do not support general runtime superiority. The tier changes
couple action count, conflicts, permissions and demands, so they do not isolate
individual causal parameter effects. Full event-width asymptotics and literature
priority are not claimed. Generic finite-domain methods can use the same resource
domains when supplied an equivalent schedule and compression.

The useful algorithmic result is the complete-action construction and the safe
separation of route and physical-resource lifetimes. The evaluation is strongest
where an exact ablation isolates information retention; every unresolved hard
case and stronger baseline result remains part of that evidence. Future actual
building validation requires verified intervention data, beyond these controlled
catalogues.
\section*{Acknowledgment and AI Disclosure}
OpenAI Codex assisted in code, automated checks, analysis, figures and manuscript
drafting. Figures are saved-data visualizations or labelled schematics. Responsible
human authors must verify the argument, sources and code. No independent human
proof approval, conference acceptance, affiliation or funding is inferred.
'''
    appendix=old[old.index(r'\appendices'):old.index(r'\section{Full Outcome Coverage and Reproducibility}')]
    # Keep only cited references; remove unrelated historical literature sections.
    body=preamble+abstract+intro+contribution+before+event+after+protocol+results+'\n\\clearpage\n'+limitations+appendix
    used=[]
    for keys in re.findall(r'\\cite\{([^}]+)\}',body):
        for key in keys.split(','):
            if key not in used:used.append(key)
    bibliography=old[old.index(r'\begin{thebibliography}'):old.index(r'\end{thebibliography}')]
    entries=re.split(r'(?=\\bibitem\{)',bibliography)[1:]
    lookup={re.match(r'\\bibitem\{([^}]+)\}',entry).group(1):entry for entry in entries}
    selected=[lookup[key] for key in used]
    split=min(range(1,len(selected)),key=lambda i:abs(sum(map(len,selected[:i]))-sum(map(len,selected[i:]))))
    body+='\n\\clearpage\n\\IEEEtriggeratref{'+str(split+1)+'}\n\\begin{thebibliography}{99}\n'+''.join(selected)+'\\end{thebibliography}\n\\end{document}\n'
    for before,after in {
        'of14':'of 14','all15':'all 15','retains253':'retains 253','and93':'and 93',
        'All112':'All 112','common60s':r'common 60\,s',',55s':r', 55\,s',
        'budget,100000':'budget, 100,000',',65536':', 65,536','seed0':'seed 0',
        'cost2':'cost 2','cost3':'cost 3','cost5':'cost 5','cost470':'cost 470','bound335':'bound 335',
        'three-run78-action':'three-run 78-action','17.694 of19.519s':r'17.694 of 19.519\,s',
        'the112':'the 112','Historical default runs retain all components.':'Default recognition retains all components.'
        ,'the109':'the 109','has23':'has 23','giving276':'giving 276','a30s':r'a 30\,s','and25s':r'and 25\,s',
        'width4':'width 4','the30s':r'the 30\,s','costs3':'costs 3','the276':'the 276'
    }.items():body=body.replace(before,after)
    (output/'master.tex').write_text(body,encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True)
    p.add_argument('--summary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--asynchronous-figure',type=Path,required=True)
    p.add_argument('--parameter-summary',type=Path)
    p.add_argument('--segment-controls',type=Path)
    p.add_argument('--event-width-summary',type=Path)
    a=p.parse_args();build(a.base,a.summary,a.output,a.asynchronous_figure,a.parameter_summary,a.segment_controls,a.event_width_summary)
