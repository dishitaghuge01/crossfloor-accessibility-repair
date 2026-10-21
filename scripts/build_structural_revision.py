"""Main narrative: certified frontier, schedule separation, measured bounded regime."""
import argparse,json,re,shutil
from pathlib import Path
from build_frontier_revision import revise
from build_focused_revision import table


def build(a):
    revise(a)
    data=json.loads((a.structural_summary/'summary.json').read_text())
    p=a.output/'master.tex';body=p.read_text()
    shutil.copy2(a.structural_summary/'figures/structural-locality.pdf',a.output/'figures/structural-locality.pdf')
    body=body.replace('Earlier building-derived interaction experiments continue to favor CP-SAT on larger joint instances, and the general decomposition machinery remains attributed to prior work.',
        'A separate frozen structural extension changes boundary conflicts, permissions and demand depth at fixed prices: lifetime DP and an elementary eight-mask locality solver each finish 16/16 full objectives, versus 12/16 for CP-SAT. The locality solver is faster on all eight input medians, so the favorable chain regime is not an exclusive DP advantage. Larger building-derived interaction cases continue to favor CP-SAT.')
    start=body.index(r'\item An explicit recognized physical-to-owned-interface')
    end=body.index(r'\end{enumerate}',start)
    body=body[:start]+r'''\item A statically certified transient-frontier theorem preserving complete physical purchases, and an exponential retained-key separation from floor retirement.
\item A physical-to-owned-interface construction whose route witnesses may expire before complete-unit owner identities and paid occupancy, with an exact full-objective transfer.
\item A reproducible bounded-band regime tested under structural variation and against an elementary locality solver, with explicit unfavorable boundaries on larger building-derived cases.
'''+body[end:]
    # The original floor guarantee and secondary reductions remain reproducible
    # in the preserved focused manuscript and supplementary source notes.
    start=body.index(r'\section{Complexity and Hardness Boundary}')
    end=body.index(r'\section{Experimental Protocol}',start)
    body=body[:start]+r'''\subsection{Relation to the Earlier Floor Guarantee}
Theorem~\ref{thm:transient} is the main bound for the evaluated uncompressed
lifetime DP. The earlier representative-reduced floor construction gives
\begin{equation}T_{\rm rec}+2^{O(prL+zL\log(h+2))}\poly(B).\label{eq:bound}\end{equation}
Here $p$ counts profiles, $r$ within-floor components, $z$ collision cells, $L$
complete support span, and $h$ owners per unit/cell. Its derivation and optional
marked-component preprocessing are supplementary. This coarse description can
grow while the event certificate stays constant, as Proposition~\ref{prop:bays}
shows. Two-floor arbitrary bundles already inherit Set Cover hardness
\cite{karp}; floor count alone therefore does not guarantee tractability.
The implementation's 100000-state and 65536-cut caps are operational limits,
not infeasibility results. The physical correctness argument remains in
Appendix~\ref{app:proof}; standard connectivity/decomposition machinery is attributed.

'''+body[end:]
    section=r'''\subsection{Structural Variation and a Locality-Aware Baseline}
To distinguish locality from price variation, a separate frozen extension uses
8 and 24 bands with four prespecified variants per size. Price seed0 and all
action costs/counts stay fixed. Identity is the previous control; alternating
cyclic slot assignments and seeded per-band permutations (seed713) change
cross-band collision incidence. The fourth variant also swaps restricted-profile
permissions in odd bands and moves the second demand to the chain midpoint.
That last comparison couples mechanisms; the two slot controls isolate conflict
incidence. The generator and evaluation list were committed before timing,
after the earlier family was studied; this is no blind holdout or new building sample.

The elementary locality solver independently enumerates256 whole-action subsets
per band and propagates at most eight occupied-slot masks. For this admitted
chain class, per-profile prefix coverage and disjoint adjacent masks are necessary
and sufficient; owner equality is checked before masking. Its objective is the
same exact cost/count/ID label. Unlike a bare combinatorial timing, its measured
pipeline charges the same physical recognizer and complete-action replay as DP.
It does not support arbitrary recognized access networks.

Revision \texttt{REV} supplies48 observations: eight inputs, three methods,
two counterbalanced fresh repetitions,45s external/40s CP budgets, otherwise the
same caps and single-worker seed0. All rows are retained. These timings are not
pooled with the earlier90s study. All exact labels agree, and REPLAYS distinct
returned selections pass full replay. Static certificates are recomputed for
each structural input, not inherited from the identity case.
'''.replace('REV',data['measured_revision'][:7]).replace('REPLAYS',str(data['unique_replays']))
    rows=[]
    names={'identity':'Identity','alternating':'Alternating','permuted':'Permuted','permuted-permissions-targets':'Perm.+policy'}
    for r in data['rows']:
        vals=[]
        for m in ('both','locality','cp-sat'):
            s=r['methods'][m];t='--' if s['pipeline_median'] is None else f"{s['pipeline_median']:.2f}"
            vals.append(f"{s['exact']}/2; {t}")
        rows.append([r['bands'],names[r['variant']],r['conflict_pairs'],r['b'],r['domain_product']]+vals)
    section+=table('Frozen Structural Extension: Exact Runs and Full-Pipeline Median Seconds; Unfinished Runs Excluded from Time Medians','tab:structural-locality',
        ['Bands','Variant','Conflicts','$b$','$2^\\rho$','DP','Locality','CP-SAT'],rows)
    section+=r'''\begin{figure*}[t]\centering\includegraphics[width=.96\textwidth]{figures/structural-locality.pdf}
\caption{Fixed-price structural extension. Bars show two-run full-pipeline medians
when both exact objectives complete. Crosses mark zero of two exact completions
at the45s budget reference, not their actual runtime or successful solves. The locality baseline includes
physical recognition and replay.}\label{fig:structural-locality}\end{figure*}
DP and locality each complete16/16 objectives (all eight input combinations,
each repeated twice); CP-SAT completes12/16 (six combinations, each twice).
The locality baseline is faster on every per-input median. Thus the chain family
supports a useful locality-based regime, including changed conflict structure,
but not an advantage unique to owned-interface DP. The elementary solver is the
preferred implementation within its strict subclass. The general construction's
value is preserving complete physical semantics on its broader recognized class;
these experiments do not show it outperforming a tailored decomposition there.

'''
    body=body.replace(r'\section{Results and Ablations}',r'\section{Results and Ablations}'+'\n'+section)
    # Shorten the secondary floor counting repeated in the correctness appendix.
    body=re.sub(r'\\subsection\{Completeness, Soundness and Bit Complexity\}.*?(?=\\clearpage)',lambda _:r'''\subsection{Completeness, Soundness and Bit Complexity}
Ownership locality and thin witnesses provide a branch for every optimum;
state sufficiency, projection and minimum-label merging preserve its best
continuation. Every accepting branch is fully materialized and replayed.
Theorem~\ref{thm:transient} counts transient states and witness choices for the
main lifetime variant. The supplementary floor derivation additionally uses
representative preservation for its coarse bound. Exact labels and original IDs
need polynomial bit work. Geometry uses the recorded tolerance and checked
collision equivalence; neither argument certifies construction suitability.

''',body,flags=re.S)
    body=body.replace('The useful algorithmic result is the complete-action construction and the safe',
        'The main results are the static transient-frontier theorem, the floor-retirement separation and the measured bounded regime shared with the locality baseline. The complete-action construction supplies the safe')
    body=body.replace('The two buildings and five layouts are a limited evaluation population;',
        'The two source buildings and five derived layouts are a limited application population; the authored structural extension remains a chain family;')
    for old,new in [('seed0','seed 0'),('seed713','seed 713'),('enumerates256','enumerates 256'),('supplies48','supplies 48'),('repetitions,45s','repetitions, 45s'),('earlier90s','earlier 90s'),('the45s','the 45s'),('successful45s','successful 45s'),('complete16/16','complete 16/16'),('completes12/16','completes 12/16')]:body=body.replace(old,new)
    # Removing secondary material changes first citation order.
    used=[]
    for keys in re.findall(r'\\cite\{([^}]+)\}',body):
        for key in keys.split(','):
            if key not in used:used.append(key)
    blocks=dict(re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})',body,re.S))
    bibliography='\n'.join(r'\bibitem{'+k+'}'+blocks[k].strip() for k in used)+'\n'
    body=re.sub(r'(\\begin\{thebibliography\}\{99\}).*?(?=\\end\{thebibliography\})',lambda m:m[1]+'\n'+bibliography,body,flags=re.S)
    p.write_text(body,encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('base','summary','output','asynchronous-figure','parameter-summary','segment-controls','event-width-summary','matched-summary','scaling-summary','local-summary','structural-summary'):
        p.add_argument('--'+name,type=Path,required=True)
    build(p.parse_args())
