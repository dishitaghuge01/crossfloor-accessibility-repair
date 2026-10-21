"""Evidence-led paper revision: correct reporting and separate documentary evidence."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
from statistics import median

from build_revised_master import table, completed_time_summary


def bibliography_for(text, bibliography):
    used={key.strip() for group in re.findall(r'\\cite\{([^}]+)\}',text) for key in group.split(',')}
    items=re.findall(r'\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})',bibliography,re.S)
    available={key for key,_ in items}
    if not used<=available:
        raise ValueError('unresolved bibliography keys: '+str(used-available))
    return r'\begin{thebibliography}{00}'+'\n'+''.join(
        r'\bibitem{'+key+'}'+body for key,body in items if key in used)+r'\end{thebibliography}'+'\n'


def build(base, controlled, building, output):
    output.mkdir(parents=True,exist_ok=False)
    text=(base/'master.tex').read_text(encoding='utf-8')
    assert 'Permission-Backed CAD Input Pilot' in text
    rows=json.loads((controlled/'records.json').read_text())
    oldaudit=json.loads((controlled/'audit.json').read_text())
    assert hashlib.sha256((controlled/'records.json').read_bytes()).hexdigest()==oldaudit['records_sha256']
    public=json.loads((building/'records.json').read_text())
    assert hashlib.sha256((building/'records.json').read_bytes()).hexdigest()==json.loads((building/'audit.json').read_text())['records_sha256']
    names=['catalogue-128-s0','ownership-8-s0','profiles-4-s0','connectivity-7-s0','support-8-s0','rooms-12-s0']
    evidence=[];table_rows=[]
    for name in names:
        subset=[r for r in rows if r['instance_id']==name]
        line=[name]
        for solver in ['compressed','uncompressed','cp-sat','greedy-improved']:
            records=[r for r in subset if r['solver']==solver]
            for record in records:
                raw=json.loads((controlled/record['raw_record']).read_text())
                assert raw['status']==record['status']
                assert raw.get('function_seconds')==record['function_seconds']
            line.append(completed_time_summary(subset,solver))
            evidence.append(dict(instance=name,solver=solver,statuses=dict(Counter(r['status'] for r in records)),
                                 displayed_time=line[-1],raw_records=[r['raw_record'] for r in records]))
        table_rows.append(line)
    revised=table('Function Seconds: Median [Minimum, Maximum]. Feasible Greedy Returns Count as Completed, Without an Optimality Claim; Failed Runs Remain in the Outcome Matrices',
                  'tab:scaling',['Case','Compressed','Full','CP-SAT','Improved greedy'],table_rows,True)
    pattern=r'\\begin\{table\*\}\[t\]\s*\\caption\{Function Seconds:.*?\\end\{table\*\}'
    text,count=re.subn(pattern,lambda _:revised,text,count=1,flags=re.S)
    assert count==1
    stale='Dominance disabling and alternate scheduling were not implemented, and no unmeasured benefit is claimed.'
    final_ablation=('The final implementation includes no-merging history enumeration, admissible complete-unit reverse ordering and optional spatial filtering, evaluated in the separately pinned 180-observation campaign in Appendix E. History mode disables both minimum-label state merging and representative compression; it does not isolate either mechanism alone. Reverse ordering preserves complete ownership units and the floor schedule; arbitrary schedules are not tested.')
    if stale in text:
        text=text.replace(stale,final_ablation)
    else:
        assert 'no-merging history enumeration' in text
    old='A narrower encoding or domain-valued resource/connectivity method might match our dependence.'
    assert old not in text  # Preserve the already completed finite-domain comparison.
    text=text.replace(r'Appendix~\ref{app:assessment} states the remaining claim boundary.',
                      'Priority of the complete construction remains unconfirmed; the state-domain term alone cannot establish novelty.')
    abstract=r'''We study strict cross-floor accessibility repair with frozen room geometry and adjacency, complete physical interventions, shared ownership, separate profile reachability and original atomic costs. An owned-cell floor-interface dynamic program processes complete action--asset units and applies established weighted representative-partition reduction to route witnesses while retaining all paid effects. The contribution is an explicit physical-to-interface construction, scoped correctness/complexity argument and reproducible implementation. Evaluation includes 70 authored recipes, an independent CP-SAT formulation, whole-action greedy, seeded connectivity stress, implemented state/order/geometry ablations and eight building-derived variants from two licensed sources. Compression is slower than uncompressed DP on all 15 seeded connectivity inputs; CP-SAT completes four natural inputs that hit compressed-mode caps. The source-derived catalogues contain only two or three actions and use hypothetical access permissions, reservations and costs. They support input and semantic checks, not difficult practical building optimization. No compelling practical advantage or priority over every generic connectivity/resource method is established. The construction preserves full-action semantics under its declared 2D kernel; it does not certify construction feasibility or statutory accessibility.'''
    text=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',text,flags=re.S)
    intro='These are scoped method and evaluation contributions.'
    assert intro in text
    text=text.replace(intro,intro+' The empirical evidence does not establish a practical runtime advantage: representative reduction is slower on every seeded connectivity input, and the building catalogues are decision-simple. The scientific contribution must therefore be assessed through the correctness and distinctness of the complete construction; neither favorable application performance nor first-in-literature priority is supplied by these experiments.',1)
    # Remove staged-development phrasing while retaining separate campaign settings.
    text=text.replace(r'\section{Additional State, Schedule and Geometry Ablations}',
                      r'\section{State-Merging, Schedule and Geometry Ablations}')
    text=text.replace('The original 2,094 observations remain frozen. A separate pinned campaign evaluates twelve existing inputs, five modes and three fresh process repetitions each (180 observations).',
                      'The evaluation comprises the frozen 2094-observation campaign and a separately pinned 180-observation ablation campaign on twelve existing inputs, five implemented modes and three fresh process repetitions each. Their different budgets are retained, and their timings are not pooled.')
    text=text.replace('The original 2,094 observations remain frozen. A separate pinned campaign evaluates twelve existing inputs, five modes and three fresh processes per pair (180 observations).',
                      'The evaluation comprises a 2094-observation baseline campaign and a separately pinned 180-observation ablation campaign on twelve existing inputs, five implemented modes and three fresh processes per pair. Both form the final study; their distinct timing budgets are retained.')
    text=text.replace('The richer controlled source experiments have multi-room adjacency, horizontally dependent intervention choices and consecutive three-storey routes, but admit only two source models.',
        'The eight source-derived cases retain multiple rooms and some horizontal/vertical coupling, but their candidate catalogues have only two or three actions and marked effective within-floor component counts of one or two. They do not test difficult access-network optimization or establish an advantage on realistic intervention choices. The source geometry does not make these small authored catalogues natural optimization instances.')
    text=text.replace('The supported advance is the specialized physical-to-owned-interface construction and its exactness/complexity transfer, supplemented by reproducible evaluation.',
                      'The supported result is the specialized physical-to-owned-interface construction and its scoped exactness/complexity transfer, supplemented by reproducible evaluation. No compelling practical advantage has emerged. General weighted connectivity/resource machinery already supplies the algorithmic ingredients; the complete construction must carry the distinctness claim, whose literature priority remains unconfirmed.')
    text=text.replace('Same-model optimization, seeded stress, valid ablations, semantic counterexamples and multi-room source-derived experiments make the construction and its limits inspectable.',
                      'Same-model optimization, seeded stress and valid ablations make the construction and its limits inspectable. Current timings do not justify a performance claim; decision-simple source-derived catalogues do not establish practical building utility. A convincing practical evaluation requires nontrivial evidence-backed intervention choices, while a theoretical publication claim requires a stronger checked distinctness argument for the complete construction.')
    first=text.index(r'\section{Historical Documentary Admission Study}')
    bib_start=text.index(r'\begin{thebibliography}')
    bib_stop=text.index(r'\end{thebibliography}',bib_start)+len(r'\end{thebibliography}')
    bibliography=text[bib_start:bib_stop]
    before_bib=text[:bib_start]
    main=before_bib[:first]
    supplement_body=before_bib[first:]
    # The old bibliography trigger/float drain belonged to the combined master.
    trailer=r'\clearpage'+'\n'+r'\IEEEtriggeratref{12}'
    supplement_body=supplement_body.replace(trailer,'')
    main+=('\nDocumentary price extraction, source-access/admission studies and the two-room CAD pilot are supplied separately in the supplementary evidence report. They are not additional evidence of practical access-network optimization.\n')
    main+='\n'+r'\clearpage'+'\n'+r'\raggedbottom'+'\n'+bibliography_for(main,bibliography)+r'\end{document}'+'\n'
    preamble=text[:text.index(r'\title{')]
    supplement=preamble+r'''\title{Supplementary Evidence: Source Admission Studies and CAD Input Pilot}
\author{Research evidence supplement}
\begin{document}\maketitle
\begin{abstract}
This supplement records documentary source assessments and a small CAD input pilot. These are provenance/input-handling studies, not evidence of difficult building optimization, construction validation, practical advantage or established literature priority. The main manuscript contains the algorithm, proof and controlled optimization evaluation. Historical prices and unsuccessful source admissions are retained here for auditability.
\end{abstract}
'''+supplement_body+'\n'+r'\clearpage'+'\n'+bibliography_for(supplement_body,bibliography)+r'\end{document}'+'\n'
    for name,document in [('main',main),('supplement',supplement)]:
        folder=output/name;folder.mkdir();(folder/'figures').mkdir()
        shutil.copy2(base/'IEEEtran.cls',folder/'IEEEtran.cls')
        (folder/'master.tex').write_text(document,encoding='utf-8')
        for relative in set(re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',document)):
            shutil.copy2(base/relative,folder/relative)
            png=(base/relative).with_suffix('.png')
            if png.exists():shutil.copy2(png,(folder/relative).with_suffix('.png'))
    ratios=[]
    for name in sorted({r['instance_id'] for r in rows if r['instance_id'].startswith('connectivity-')}):
        med={method:median(r['function_seconds'] for r in rows if r['instance_id']==name and
             r['solver']==method and r['status']=='optimal') for method in ['compressed','uncompressed']}
        ratios.append(dict(instance=name,ratio=med['compressed']/med['uncompressed']))
    source_catalogues={}
    for row in public:
        if row['instance_id'] not in source_catalogues:
            a=json.loads((building/row['raw_record']).parent.joinpath('input.json').read_text())
            source_catalogues[row['instance_id']]=len(a['actions'])
    assert len(ratios)==15 and all(r['ratio']>1 for r in ratios)
    assert set(source_catalogues.values())=={2,3}
    natural_caps={}
    for name in sorted({r['instance_id'] for r in rows if r['solver']=='compressed' and
                         r['status']=='limit_exceeded' and r['instance_id']!='state-limit'}):
        natural_caps[name]={method:dict(Counter(r['status'] for r in rows if
            r['instance_id']==name and r['solver']==method)) for method in ['compressed','uncompressed','cp-sat']}
        assert all(r['status'] in {'optimal','infeasible'} for r in rows if
                   r['instance_id']==name and r['solver'] in {'uncompressed','cp-sat'})
    assert len(natural_caps)==4
    assert 'were not implemented' not in main and 'no completed solve' not in main
    assert r'\ref{app:assessment}' not in main
    report=dict(table_completion_policy='optimal/infeasible/feasible with measured time; heuristic feasible is not optimal',
        table_rows=evidence,connectivity_ratios=ratios,source_catalogue_action_counts=source_catalogues,
        natural_compressed_caps_with_completed_comparators=natural_caps,
        main_claim='scoped physical construction/correctness/evaluation; no established practical advantage or priority',
        no_new_benchmarks=True,
        inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [base/'master.tex',controlled/'records.json',building/'records.json',Path(__file__)]})
    (output/'reporting-audit.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('Built main manuscript and separate evidence supplement:',output)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['base','controlled','building','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();build(a.base,a.controlled,a.building,a.output)
