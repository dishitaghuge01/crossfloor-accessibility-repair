"""Research master promoting the static theorem and frozen scaling evidence."""
import argparse,json,re,shutil,statistics
from pathlib import Path
from build_focused_revision import build,table


def revise(a):
    build(a.base,a.summary,a.output,a.asynchronous_figure,a.parameter_summary,a.segment_controls,a.event_width_summary,a.matched_summary)
    data=json.loads((a.scaling_summary/'summary.json').read_text())
    local=json.loads((a.local_summary/'summary.json').read_text())
    for p in (a.scaling_summary/'figures').glob('*.pdf'):shutil.copy2(p,a.output/'figures'/p.name)
    p=a.output/'master.tex';body=p.read_text()
    body=body.replace(r'\newtheorem{lemma}{Lemma}',r'\newtheorem{lemma}{Lemma}'+'\n'+r'\newtheorem{proposition}{Proposition}')
    body=body.replace('Exact Topology-Preserving Cross-Floor Accessibility Repair with Shared Physical Assets',
        'Certified Event Frontiers for Exact Cross-Floor Accessibility Repair with Shared Physical Assets')
    d,c=data['local_method_totals']['both']['exact'],data['local_method_totals']['cp-sat']['exact']
    ratios=data['local_groups'][1]['paired_price_ratios_cp_over_dp']
    gain=f'{min(ratios):.1f}--{max(ratios):.1f}' if ratios else 'unavailable'
    abstract=r'''\begin{abstract}
We study exact cross-floor accessibility repair with indivisible physical purchases, reusable owners and profile-dependent access demands.
Route connectivity cannot represent feasibility alone because even unused purchased effects occupy space and may block another intervention.
We construct a complete-action owned-interface dynamic program and certify its transient potential vertices and resource domains directly from the catalogue schedule.
For potential frontier size $b$ and logarithmic resource-domain product $\rho$, the uncompressed exact algorithm takes $T_{\rm rec}+2^{O(b\log(b+2)+\rho)}\poly(B)$ time; a three-floor family has constant certified parameters while floor retirement retains at least $2^n$ occupancy keys.
On a frozen authored local-band study with bundles, inter-band collisions and profile-restricted alternatives, the specialized DP completes D/18 exact objectives versus C/18 for CP-SAT; at24 bands its paired full-pipeline advantage is GAIN times across three price variants, each repeated twice.
Earlier building-derived interaction experiments continue to favor CP-SAT on larger joint instances, and the general decomposition machinery remains attributed to prior work.
These results establish a bounded computational regime and a reproducible intervention benchmark, rather than validated actual-building construction repairs.
\end{abstract}'''.replace('D/18',str(d)+'/18').replace('C/18',str(c)+'/18').replace('GAIN',gain).replace('at24','at 24')
    body=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:abstract,body,flags=re.S)
    body=body.replace('A model-specific asynchronous projection argument separating route-vertex\nexpiry from complete-unit owner retirement; the underlying last-use and weighted\npartition techniques are attributed to prior work.',
        'A static transient-frontier bound and an exponential retained-key separation from floor retirement, preserving complete-unit owner information; the underlying decomposition and partition techniques remain attributed to prior work.')
    body=body.replace('A reproducible evaluation of all five retirement/compression variants on\nidentical interacting inputs, including strengthened exact and heuristic baselines,\nstage traces, feasibility controls and preserved failures.',
        'A characterized bounded-band computational regime, a reusable intervention benchmark and independent family-specific objective checks, alongside the earlier five-way ablation and its unfavorable larger building-derived results.')
    theorem=r'''\subsection{Certified Transient Frontier}
Count every potentially selected profile vertex from its first possible event
through its last incident event, with required vertices counted from their actual
eager introduction and isolated required vertices through floor exit. Include
permanent anchors and action endpoints before projection; let $b$ be the maximum
count. A cell is potentially live from its first touching action through its
last touching unit's closure. During unit $J$, use domain
$D_t(c)=\{\emptyset,\mathrm{external}\}\cup\{\text{owners of }J\text{ covering }c\}$;
outside a unit use the first two values. Define
\begin{equation}\rho=\max_t\sum_{c\text{ potentially live at }t}\log_2|D_t(c)|.\end{equation}
These are polynomially computable static catalogue certificates, independent of
chosen witnesses or measured peak states. They include all transient branching
and eagerly introduced targets; a post-projection row maximum would not suffice.
\begin{theorem}[Transient-frontier exactness and bound]\label{thm:transient}
On a recognized strict instance, uncapped minimum-label-merged DP with both
lifetime projections, without representative reduction, returns the full exact
objective in
\begin{equation}T_{\rm rec}+2^{O(b\log(b+2)+\rho)}\poly(B)\end{equation}
time and $2^{O(b\log(b+2)+\rho)}\poly(B)$ additional DP working memory.
\end{theorem}
\begin{proof}
At a fixed event there are at most $2^\rho$ occupancy maps. Selected subsets and
profile partitions inject into partitions of the $b$ potential elements plus one
distinguished absence marker, hence at most $\operatorname{Bell}(b+1)$ keys per
occupancy map. An action has at most $b$ connected supplied profile components,
so its witness branching is at most $2^b$ per incoming key. Every transient
endpoint and paid cell is counted before projection. Projection/merging compares
polynomial-length keys and exact labels; there are polynomially many events.
Lemma~\ref{lem:lifetime} supplies continuation equivalence and objective
preservation. Streaming transitions and two consecutive tables give the memory
bound. Recognition and complete final replay remain charged.
\end{proof}

\begin{proposition}[Separating floor retirement]\label{prop:bays}
There is a three-floor recognized family with $b=4$, $2^\rho=27$, but $r=z=n$,
on which uncapped floor-retirement DP retains at least $2^n$ keys before
the first floor exit.
\end{proposition}
\begin{proof}
Source and target rooms lie below and above $n$ optional middle rooms. Each bay
has a private owner, two consecutive edges and one atomic two-edge bundle, on
three private cells. Process complete bays consecutively: only one middle vertex
and its three cells need coexist with source, target and anchor. Under floor
retirement, however, select any subset of bay bundles and omit all their route
witness effects. All $2^n$ prefixes share the root/target partition but differ in
paid occupancy. No floor has exited and no required block has vanished. Equal-key
merging and occupancy-grouped representative selection cannot merge these keys.
Under both projections the static bound is constant apart from polynomial input
and recognition work. The positive-cost optimum is the earliest cost-three bundle.
\end{proof}

This is a state-space separation for the specified floor and lifetime schedules,
not a lower bound on all algorithms. The Bell-number argument is conventional
frontier DP; a generic finite-domain method supplied the same physical encoding
and schedule can match it, and standard small-width machinery also solves this
$K_{2,n}$ family. The new certificate makes the complete physical-action transfer
and the previously coarse floor description explicit; it does not establish a
stronger generic connectivity theorem.
'''
    body=re.sub(r'A tighter event-width theorem would need.*?coarse worst-case theorem is unchanged\.',lambda _:theorem,body,flags=re.S)
    section=r'''\subsection{Bounded Local-Band Computational Regime}
The follow-up freezes three authored chain sizes (8,24,48 two-edge bands) and
three price seeds per topology, with two counterbalanced fresh-process repetitions
per method:36 observations, distinct from the primary study. Every band offers
shared-owner segments/bundles, an overlapping profile0-only shaft, a separate
profile1-only bundle and an alternative shared shaft. Different owners in adjacent
bands collide at their common landing floor, so choices cannot be optimized
independently. Profile demands end at different rooms. All geometry, reservations,
permissions and prices are authored, not source-building facts.

The unchanged DP/CP kernels run at revision \texttt{REV}, with90s external and85s
internal CP budgets, the same100000-state/65536-cut caps, seed0 and no RAM cap.
Development probes guided this family and budget; this is no blind holdout.
Static certificates give $b=8$, at most five live cells and $2^\rho=108$ for all
nine price variants. The potential interface remains bounded while storeys and
action count grow; this is a characterized algorithmic regime, not a representative
distribution of actual high-rise buildings.
'''.replace('REV',data['local_measured_revision'][:7])
    rows=[]
    for g in data['local_groups']:
        dp,cp=g['methods']['both'],g['methods']['cp-sat']
        fmt=lambda x:'--' if x['price_median_min'] is None else f"{x['price_median_min']:.2f}--{x['price_median_max']:.2f}"
        ratios=g['paired_price_ratios_cp_over_dp'];rat='--' if not ratios else f'{min(ratios):.1f}--{max(ratios):.1f}'
        rows.append([g['bands'],g['actions'],str(dp['exact'])+'/6',str(cp['exact'])+'/6',str(g['cp_cost_proofs'])+'/6',fmt(dp),fmt(cp),rat])
    section+=table('Authored Local Bands: Three Price Variants per Size, Two Runs per Method; Time Ranges Are per-Price Pipeline Medians on Exact Completions','tab:local-scaling',
        ['Bands','Actions','DP exact','CP exact','CP cost proof','DP (s)','CP (s)','Paired CP/DP'],rows)
    section+=r'''\begin{figure*}[t]\centering\includegraphics[width=.96\textwidth]{figures/local-band-scaling.pdf}
\caption{Scaling on bounded local-band catalogues. Left: medians and ranges of
completed per-price pipeline medians; limited runs are excluded, not plotted as
ordinary90s solves. Right: full exact completions and separate CP minimum-cost
proof counts. Three prices share one topology at each size.}\label{fig:local-scaling}\end{figure*}
'''
    largest=data['local_groups'][-1];dp=largest['methods']['both']
    section+=f"At48 bands the DP completes {dp['exact']}/6 full objectives, with median recognition/optimization/replay phases {dp['recognition_median']:.2f}/{dp['optimization_median']:.2f}/{dp['replay_median']:.2f}s and peak raw states {dp['raw_state_max']}. Its returned worker memory median is {dp['returned_worker_memory_median_mib']:.0f}MiB ({dp['returned_worker_memory_n']}/6 measurements); imports and recognition are included. This is an end-to-end completion result, not an isolated search-clock comparison.\n"
    large_rows=[]
    for seed in (0,1,2):
        iid=f'local-bands-48-s{seed}';s=next(x for x in local['summaries'] if x['instance_id']==iid and x['method']=='both')
        c=next(x for x in local['summaries'] if x['instance_id']==iid and x['method']=='cp-sat')
        ts=[t for t in local['cp_tasks'] if t['instance_id']==iid]
        large_rows.append([seed,s['feasible_costs'][0],'/'.join(str(x) if x is not None else '--' for x in c['feasible_costs']),
            '/'.join(str(t['cost_lower_bound']) if t['cost_lower_bound'] is not None else '--' for t in ts),
            '/'.join(t['cost_stage_status'] for t in ts)])
    section+=table('Largest Local-Band Inputs: Exact DP Costs versus CP Incumbents and Cost-Stage Bounds, by Repetition','tab:local-bounds',
        ['Price seed','DP optimum','CP feasible costs','CP cost bounds','CP cost status'],large_rows)
    section+=r'''All distinct returned repairs are fully replay-audited. A separate
family-specific reference enumerates256 local subsets per band and propagates
at most eight three-slot boundary masks; it agrees on the full cost/count/ID label
for all nine inputs. It calls neither the owned-interface DP nor the geometry
compiler: admitted fixed rectangles make same-slot owner conflicts exact, and
each profile's chain demand requires every preceding edge. Disjoint adjacent
boundary masks are necessary and sufficient for inter-band compatibility. This
independent family check does not validate arbitrary geometry or construction.
More generally, for bands with at most $a$ purchases and $s$ boundary slots under
these restrictions, local enumeration and mask propagation take
$O(m2^{a+s}\poly(B))$ time. This elementary finite-state subclass is an independent
check and a structural explanation, not a new general decomposition technique.

\subsection{Certified Separating-Family Measurements}
The private-bay study measures four three-floor catalogues with2,8,16,32 bays,
three methods and two repetitions (24 observations), under the same90s protocol.
Its analytic full-objective optimum is the first cost-three bundle. Static
certificates and returned peak states are compared in Fig.~\ref{fig:bay-frontier};
capped floor rows have no invented internal peak. This mechanism witness
demonstrates Proposition~\ref{prop:bays}; it is not a difficult building validation.
\begin{figure*}[t]\centering\includegraphics[width=.96\textwidth]{figures/private-bay-frontier.pdf}
\caption{Private-bay family: coarse floor parameters grow while the certified
transient potential frontier is constant. Returned state profiles exclude capped
workers; missing profiles are not treated as zero.}\label{fig:bay-frontier}\end{figure*}
\subsection{Earlier Building-Derived Interaction Study}
'''
    body=body.replace(r'\section{Results and Ablations}',r'\section{Results and Ablations}'+'\n'+section)
    body=body.replace('Full event-width asymptotics and literature\npriority are not claimed.',
        'The transient theorem is a model-specific frontier guarantee; literature\npriority and superiority over general decomposition algorithms are not established.')
    # The earlier eight-panel structural plot remains in the supplementary data.
    body=re.sub(r'\\begin\{figure\*\}\[p\].*?\\label\{fig:parameters\}\\end\{figure\*\}', '',body,flags=re.S)
    body=body.replace('Figure~\\ref{fig:parameters}','The supplementary structural figure')
    body=body.replace('Fig.~\\ref{fig:parameters}','the supplementary structural figure')
    unused=a.output/'figures/parameter-families.pdf'
    if unused.exists():unused.unlink()
    for old,new in [('with90s','with 90s'),('and85s','and 85s'),('same100000','same 100000'),('enumerates256','enumerates 256'),('with2,8,16,32','with 2,8,16,32'),('At48','At 48')]:body=body.replace(old,new)
    p.write_text(body,encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('base','summary','output','asynchronous-figure','parameter-summary','segment-controls','event-width-summary','matched-summary','scaling-summary','local-summary'):
        p.add_argument('--'+name,type=Path,required=True)
    revise(p.parse_args())
