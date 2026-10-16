"""Build a detailed IEEE master from audited normalized evaluation records."""
import argparse,csv,hashlib,json,re,shutil,sys
from collections import Counter,defaultdict
from pathlib import Path
from statistics import median
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_revised_evidence import audit
from build_ieee_master import order_references
from cfar.io import write_json


def esc(value):return str(value).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')


def table(caption,label,headers,rows,wide=False):
    env='table*' if wide else 'table'
    lines=[rf'\begin{{{env}}}[t]',rf'\caption{{{caption}}}\label{{{label}}}',r'\centering\footnotesize\setlength{\tabcolsep}{3pt}',r'\begin{tabular}{'+'l'+'r'*(len(headers)-1)+'}',r'\toprule',' & '.join(headers)+r' \\',r'\midrule']
    lines+=[' & '.join(esc(v) for v in row)+r' \\' for row in rows]
    return '\n'.join(lines+[r'\bottomrule\end{tabular}',rf'\end{{{env}}}'])


def figure(name,caption,label,wide=False):
    env='figure*' if wide else 'figure';unit=r'\textwidth' if wide else r'\columnwidth'
    return rf'\begin{{{env}}}[t]\centering\includegraphics[width=.97{unit}]{{figures/{name}.pdf}}'+'\n'+rf'\caption{{{caption}}}\label{{{label}}}\end{{{env}}}'+'\n'


def build(controlled,building,source_audit,three_audit,controls,geometry_profile,figures,output):
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('fresh output required')
    root=Path.cwd();audits=[audit(controlled,replay_certificates=False),audit(building,replay_certificates=False)]
    for study,verified in zip([controlled,building],audits):
        saved=json.loads((study/'audit.json').read_text())
        if saved['records_sha256']!=verified['records_sha256'] or saved['certificates_sha256']!=verified['certificates_sha256'] or saved['certificate_replays']!=verified['oracle_certificates']:
            raise ValueError('missing or stale independent certificate replay audit')
        verified['verified_certificate_replays']=saved['certificate_replays']
    figure_manifest=json.loads((figures/'figure-provenance.json').read_text())
    expected_inputs={hashlib.sha256(p.read_bytes()).hexdigest() for p in [controlled/'records.json',building/'records.json',source_audit/'summary.json']}
    if set(figure_manifest['inputs'].values())!=expected_inputs:raise ValueError('figures use different evidence')
    if figure_manifest['generator_normalized_sha256']!=hashlib.sha256((root/'scripts/make_revised_figures.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest() or figure_manifest['helper_normalized_sha256']!=hashlib.sha256((root/'scripts/make_ieee_figures.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest():raise ValueError('figure source changed')
    for name,digest in figure_manifest['outputs'].items():
        if hashlib.sha256((figures/name).read_bytes()).hexdigest()!=digest:raise ValueError('figure bytes changed')
    rows=json.loads((controlled/'records.json').read_text());public=json.loads((building/'records.json').read_text())
    sources=json.loads((source_audit/'summary.json').read_text())
    template=(root/'paper/ieee/master.template.tex').read_text()
    front=template[:template.index(r'\section{Experimental Design}')]
    n=len({r['instance_id'] for r in rows});nb=len({r['instance_id'] for r in public})
    abstract=f'''Restoring accessibility across existing floors requires optimizing complete interventions while preserving room layout and physical asset semantics. We formalize strict repair with frozen room polygons, identifiers and adjacency, separate rooted profile reachability, atomic action costs and consistent ownership. Rectangular footprints are compiled into owned collision cells. A floor-interface algorithm processes complete action--asset units and applies established representative-partition reduction only to connectivity witnesses. Its exactness argument preserves full paid effects while discarding unnecessary witness components; a physical two-floor reduction shows why floor count alone is insufficient. An independent constraint-programming flow formulation and whole-action greedy with bounded local improvement provide same-model comparators. Reproducible evaluation covers {n} authored inputs, seeded connectivity stress, valid preprocessing/cache ablations and {nb} multi-room variants from two licensed sources, including three consecutive source storeys. Building-derived experiments preserve original room geometry and use explicitly hypothetical doors, permissions, reservations and abstract costs. Restricting horizontal profile access changes the optimal intervention choice. Timings, memory, operational failures and replayed selections remain visible. The contribution is a specialized physical-to-interface construction and evaluation, rather than invention of labelled connectivity or weighted rank compression. The represented geometry does not establish construction safety or statutory compliance.'''
    front=re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda m:r'\begin{abstract}'+'\n'+abstract+'\n'+r'\end{abstract}',front,flags=re.S)
    front=front.replace('These distinctions matter when room topology is frozen rather than regenerated.','Here topology-preserving means equality of input room identifiers, polygons and shared-boundary adjacency after repair; profile-specific traversable access may change.')
    front=front.replace('door-connected IFC spaces','door-connected Industry Foundation Classes (IFC) spaces',1)
    front=front.replace('Candidate doors, dependencies, declared exclusions, shape changes and metadata-only corrections are outside this solver.','The optimum concerns the supplied finite intervention catalogue; candidate generation is preprocessing, not optimization over every constructible installation. Candidate doors, dependencies, declared exclusions, shape changes and metadata-only corrections are outside this solver.')
    start=front.index('Consider Fig.');end=front.index(r'\subsection{Research Question',start)
    intro=r'''Figure~\ref{fig:demo} gives a complete ownership example. Four floors each contain a main room $R_i$ and annex $U_i$; both profiles require $R_0$--$R_3$ access. A000 costs four and purchases $R_0R_1,R_1R_2$ plus a disconnected annex effect $U_0U_1$. A001 costs one and extends the same consistent main owner through $R_1R_2,R_2R_3$. Their cost-five repair is optimal. Competing E costs one-half and purchases $R_2R_3$ at another main location plus annex effect $U_1U_2$, overlapping the paid spare. No baseline access edges are assumed. Graph-only A000+E costs 4.5 and satisfies both routes, but is physically invalid solely at the annex overlap. Omitting the spare from a route witness cannot erase occupancy. A naive purchase vertex adjacent to every A000 endpoint would also falsely connect $R_0$ to annex $U_0$, although no supplied access edge joins the main and annex components. A complete independent alternative costs ten. Without that alternative, root access requires A000; reaching the last floor then requires A001 or E, and E is incompatible with A000. Thus the hand-derived optimum is five. The interface remembers the spare owner during its unit, then an occupied bit, and rejects E.
'''
    front=front[:start]+intro+figure('integrated_example','Complete authored example, schematically. Dashed effects remain physically paid. Compatible main-owner reuse is valid; the red annex owner conflicts with the unused spare. The source input, exhaustive optimum and physical counterexample are executable.','fig:demo',True)+front[end:]
    pstart=front.index(r'\begin{table}[t]',front.index(r'\section{Recognition'))
    pend=front.index(r'\end{table}',pstart)+len(r'\end{table}')
    front=front[:pstart]+(root/'paper/ieee/revised_parameters.tex').read_text()+front[pend:]
    proofmap=(root/'paper/ieee/revised_proof_map.tex').read_text()
    # Put the semantic comparison and proof map after all terms have been defined.
    pos=front.index(r'\subsection{Conditional Guarantee')
    front=front[:pos]+proofmap+front[pos:]
    outcomes=[]
    for method in ['compressed','uncompressed','cp-sat','greedy','greedy-improved']:
        c=Counter(r['status'] for r in rows if r['solver']==method and r['repeat_index']==0)
        outcomes.append([method]+[c[k] for k in ['optimal','feasible','infeasible','heuristic_failed','limit_exceeded','unsupported','timeout','internal_error']])
    result=r'\section{Results and Interpretation}'+'\n'
    result+=table('All Authored Inputs, First-Repetition Statuses; Every Repetition Is Retained','tab:outcomes',['Method','Opt.','Feas.','Inf.','Heur. fail','Cap','Unsup.','Timeout','Error'],outcomes,True)
    result+=f'The revised authored suite contains {n} inputs and {len(rows)} observations. Completed exact status/cost/count/sorted-ID labels agree. The deliberately forced state-cap and unsupported scope controls are distinguished from natural performance failures. Table~\\ref{{tab:outcomes}} retains unsupported and capped inputs; every repeated status is available in the released records.\n\n'
    interfaces=[];timing=[]
    for name in ['catalogue-128-s0','ownership-8-s0','profiles-4-s0','connectivity-7-s0','support-8-s0','rooms-12-s0']:
        subset=[r for r in rows if r['instance_id']==name];params=next(r['parameters'] for r in subset if r['parameters'])
        interfaces.append([name]+[params[k] for k in ['p','r','z','L','g','h']])
        values=[]
        for method in ['compressed','uncompressed','cp-sat','greedy-improved']:
            times=[r['function_seconds'] for r in subset if r['solver']==method and r['status'] in {'optimal','infeasible'}]
            values.append(f'{median(times):.4f} [{min(times):.4f},{max(times):.4f}]' if times else 'no completed solve')
        timing.append([name]+values)
    result+=table('Measured Interfaces; Structural Factors May Covary','tab:measured',['Case','$p$','$r$','$z$','$L$','$g$','$h$'],interfaces)
    result+=table('Function Seconds: Median [Minimum, Maximum]','tab:scaling',['Case','Compressed','Full','CP-SAT','Improved greedy'],timing,True)
    early=[r['function_seconds'] for r in rows if r['instance_id']=='dense-128' and r['solver']=='compressed' and r['function_seconds'] is not None]
    late=[r['function_seconds'] for r in rows if r['instance_id']=='catalogue-128-s0' and r['solver']=='compressed' and r['function_seconds'] is not None]
    result+=f"Recipe counts include {audits[0]['represented_model_classes']} distinct represented models after excluding only building-name/description metadata; deliberately duplicated controls and historical/structural overlap are not independent instances. The two physically identical 128-candidate recipes have compressed medians {median(early):.3f} and {median(late):.3f} seconds in different campaign positions. This observed between-batch variability is an explicit confound for cross-family or small timing claims; all repetitions and later timeouts remain included.\n\n"
    for family in ['catalogue','ownership','profiles','support','connectivity']:
        result+=figure('scaling_'+family,'Measured '+family+' scaling: medians and observed min--max ranges; crosses mark noncompletion.','fig:'+family)
    compression_rows=[]
    for size in range(3,8):
        comp=[r for r in rows if r['generator_family']=='connectivity' and r['instance_id'].startswith(f'connectivity-{size}-') and r['solver']=='compressed' and r['status']=='optimal']
        full=[r for r in rows if r['generator_family']=='connectivity' and r['instance_id'].startswith(f'connectivity-{size}-') and r['solver']=='uncompressed' and r['status']=='optimal']
        compression_rows.append([size,int(median(r['peak_raw_states'] for r in comp)),int(median(r['peak_retained_states'] for r in comp)),int(median(r['statistics']['representative_rows_removed'] for r in comp)),f"{median(r['statistics']['representative_reduction_seconds'] for r in comp):.4f}",f"{median(r['function_seconds'] for r in comp):.4f}",f"{median(r['function_seconds'] for r in full):.4f}"])
    result+=table('Connectivity Stress: Medians over Fixed Seeds/Repetitions; Raw Means Post-Deduplication, Pre-Basis','tab:compression',['Floors','Peak raw','Peak kept','Removed total','Reduction s','Comp. s','Full s'],compression_rows,True)
    pairs=[]
    for name in sorted({r['instance_id'] for r in rows if r['generator_family']=='connectivity'}):
        compressed_times=[r['function_seconds'] for r in rows if r['instance_id']==name and r['solver']=='compressed' and r['status']=='optimal']
        full_times=[r['function_seconds'] for r in rows if r['instance_id']==name and r['solver']=='uncompressed' and r['status']=='optimal']
        pairs.append(median(compressed_times)/median(full_times))
    result+=f'Across the {len(pairs)} cost-seeded connectivity inputs, compressed median function time is lower on {sum(ratio<1 for ratio in pairs)}; observed compressed/full ratios range from {min(pairs):.2f} to {max(pairs):.2f}. These are descriptive paired observations. State savings do not establish a broad runtime advantage or smaller whole-process RSS; where overhead wins, representative reduction is supported primarily as the theoretical state-bound mechanism.\n\n'
    result+=figure('compression_stress','Representative-reduction stress under shared physical ownership. Peak retained states and total removed rows are distinct measures. Paired timings determine whether elimination overhead offsets row savings.','fig:compression',True)
    result+=r'''The connectivity stress varies the number of connectivity partitions within equal physical occupancy, instead of varying only raw catalogue size. Both reduced-state and overhead behavior are retained. No broad speedup follows merely from removing rows. Valid preprocessing/cache ablations report exact-label agreement and separate states, memory and function time. Cached preparation is never hidden in the primary comparison.

Practical choice follows measured completion, time and quality. CP-SAT is the general exact common-class baseline and completes natural inputs exceeding representative cut caps. The DP offers explicit physical accounting and a measured-interface guarantee, without implying faster typical performance. Greedy is useful only when a replay-valid incumbent suffices. If recognition rejects geometry or the declared physical/evidence assumptions are inappropriate, neither optimizer certifies the actual building.
'''
    result+=figure('measured_width','Runtime and completion against the measured interface expression; each completed point is an input median and noncompletion crosses are placed at 60 seconds only for visibility, not as their elapsed times. The expression is not fitted as a performance predictor.','fig:width')
    result+=figure('phases_ablations','Direct DP phase measurements and valid irrelevant-component/cache ablations. Cache creation is excluded only from the separately labelled cached function time; process end-to-end includes it.','fig:phases',True)
    result+=figure('memory_greedy','Whole-worker peak resident memory (including imports) and feasible greedy excess costs. Only cases with a positive gap for at least one variant are shown; all failures and zero-gap inputs remain in the complete outcomes.','fig:memory',True)
    operations=json.loads((geometry_profile/'summary.json').read_text())
    expected_input_hashes={r['instance_id']:r['instance_sha256'] for r in rows+public}
    expected_parameters={r['instance_id']:r['parameters'] for r in rows+public if r['solver']=='compressed'}
    for operation in operations:
        folder=geometry_profile/operation['experiment']/operation['instance_id']
        meta=json.loads((folder/'manifest.json').read_text());raw=json.loads((folder/'profile.json').read_text())
        if meta['git_dirty'] or meta['input_fingerprint']!=expected_input_hashes[operation['instance_id']]:raise ValueError('geometry profile uses changed input/code')
        if raw!={k:v for k,v in operation.items() if k not in {'experiment','instance_id'}}:raise ValueError('geometry profile summary mismatch')
        if operation['status']=='recognized' and operation['parameters']!=expected_parameters[operation['instance_id']]:raise ValueError('geometry profile parameter mismatch')
    operation_rows=[]
    for name in ['catalogue-128-s0','ownership-8-s0','connectivity-7-s0','clinic-horizontal','molio-horizontal']:
        r=next(r for r in operations if r['instance_id']==name)
        operation_rows.append([name,r['physical_footprint_pair_intersection_tests'],r['generated_cells']])
    result+=table('Untimed Recognition Operation Counts, Separate from Performance Measurements','tab:operations',['Case','Portal footprint pair tests','Total cells'],operation_rows,True)
    controls_rows=[]
    from cfar.certificates import verify_certificate
    for folder in sorted(p for p in controls.iterdir() if p.is_dir()):
        c=json.loads((folder/'result.json').read_text());meta=json.loads((folder/'manifest.json').read_text());instance=json.loads((folder/'input.json').read_text())
        if meta['git_dirty'] or not verify_certificate(instance,json.loads((folder/'baseline-certificate.json').read_text()))['valid']:raise ValueError('semantic control provenance/replay failed')
        alias=folder.name.replace('shared_asset','shared').replace('atomic_bundle','bundle').replace('unused_paid_geometry','unused').replace('-no-owner-reuse',' / no reuse').replace('-per-effect-price',' / effect pricing').replace('-graph-only',' / graph-only')
        controls_rows.append([alias,c['strict_cost'],c['original_cost'],c['control_objective'],c['full_model_error'] or 'valid; altered model'])
    result+=table('Deliberately Altered Semantics, Not Valid Same-Model Baselines','tab:semantic',['Control','Strict cost','Original cost','Control objective','Full replay'],controls_rows,True)
    screen=[]
    for r in sources:
        s=r.get('selection',{});counts=r['source_counts'];screen.append([r['source_building_id'],counts['storeys'],counts['spaces'],counts['eligible_spaces'],counts['stairs'],counts['transport'],r['status'],s.get('retained_rooms','--'),s.get('omitted_rooms','--')])
    building_table=[]
    for name in sorted({r['instance_id'] for r in public}):
        i=json.loads((building/name/'input.json').read_text());r=next(r for r in public if r['instance_id']==name and r['solver']=='compressed' and r['repeat_index']==0)
        building_table.append([name,'/'.join(str(len(f['rooms'])) for f in i['floors']),'/'.join(str(len(f['adjacency_edges'])) for f in i['floors']),len(i['obligations']),r['status'],r['objective_cost'],','.join(r['selected_action_ids'] or [])])
    from cfar.interface_recognition import recognize_physical_interface
    structural=[]
    for name in sorted({r['instance_id'] for r in public}):
        instance=json.loads((building/name/'input.json').read_text())
        params=next(r['parameters'] for r in public if r['instance_id']==name and r['solver']=='compressed')
        pruned=next(r['parameters'] for r in public if r['instance_id']==name and r['solver']=='pruned')
        sample=next(r for r in public if r['instance_id']==name and r['solver']=='compressed' and r['repeat_index']==0)
        structural.append([name,params['p'],params['r'],pruned['r'],params['z'],params['L'],params['g'],params['h'],sample['peak_raw_states'],sample['peak_retained_states']])
    before_structure=table('Building Interfaces and Default DP States; Marked r Is Separately Computed','tab:building-interface',['Case','$p$','$r$','$r_{eff}$','$z$','$L$','$g$','$h$','Raw','Retained'],structural,True)
    source_timing=[]
    for name in sorted({r['instance_id'] for r in public}):
        group=[r for r in public if r['instance_id']==name]
        def measured(method,key='function_seconds'):
            samples=[r for r in group if r['solver']==method]
            values=[r[key] for r in samples if r['status'] in {'optimal','feasible','infeasible'} and r[key] is not None]
            failures=sum(r['status'] not in {'optimal','feasible','infeasible'} for r in samples)
            return (f'{median(values):.4f}' if values else '--')+(f' +{failures}F' if failures else '')
        source_timing.append([name,measured('compressed','recognition_seconds'),measured('compressed'),measured('uncompressed'),measured('cp-sat'),measured('pruned'),measured('cached'),measured('cached','end_to_end_seconds'),measured('greedy-improved')])
    source_timing_table=table('Source Function-Time Medians (Seconds); F Counts Noncompleted Runs; Cache Preparation Excluded Only from Warm Function Time','tab:source-times',['Case','Rec.','DP','Full','CP-SAT','Pruned','Warm cache','Cache E2E','Imp. greedy'],source_timing,True)
    experiment=(root/'paper/ieee/revised_evaluation.tex').read_text()
    pos=experiment.index(r'\section{Discussion')
    before,discussion=experiment[:pos],experiment[pos:]
    before+=table('Five-Source Screening Denominator; Counts Refer to Two-Floor Inputs','tab:screen',['Source','Storeys','Spaces','Eligible','Stair objects','Transport','Outcome','Retained','Omitted'],screen,True)
    before+=table('Original Rooms and Adjacency per Source Floor; All Costs Abstract','tab:building',['Case','Rooms/floor','A/floor','Demands','Status','Cost','Actions'],building_table,True)
    before+=before_structure+source_timing_table
    before+=figure('multiroom_plans','Retained source projections (gray), hypothetical baseline doors (blue), candidate patches (red) and conservative background. Original room rings/IDs stay frozen; colored access and intervention annotations are experimental assumptions. Insets resolve the candidate patches; the overview is clipped to the retained-room envelope, while every background obstacle remains in the supplied input.','fig:buildingplans',True)
    before+=f'The separate building study has {nb} controlled inputs and {len(public)} observations. Every returned selection is replayed and small oracle certificates are verified independently within the shared geometry contract.\n'
    original=(root/'paper/manuscript.template.tex').read_text()
    proof=original[original.index(r'\begin{lemma}[Ownership locality]'):original.index(r'\section{Experimental protocol}')]
    proof=re.sub(r'\\begin\{theorem\}.*?\\end\{theorem\}',lambda m:r'\subsection{Completeness, Soundness and Bit Complexity}',proof,flags=re.S)
    appendices=r'\appendices\section{Complete State and Correctness Argument}\label{app:proof}'+'\n'+proof
    appendices+=r'\section{Generic Encoding and Exact Objective Transfer}\label{app:generic}'+'\n'+(root/'paper/ieee/generic_appendix.tex').read_text()
    appendices+=r'\section{Full Outcome Coverage and Reproducibility}\label{app:coverage}'+'\n'
    appendices+=figure('status_matrix_revised','All authored input outcomes, first repetition. Every repeated status, explicit operational failure and raw observation remains in the evidence.','fig:status',True)
    appendices+=figure('status_matrix_structural','Additional structural and integrated-example outcomes, first repetition. All observations and statuses remain in the evidence.','fig:statusstructural',True)
    appendices+=f'The authored study is pinned to \\texttt{{{audits[0]["code_commit"][:7]}}}; the separate building study to \\texttt{{{audits[1]["code_commit"][:7]}}}. Excluded pilot results are absent from these tables. Manifests record hardware, packages, GEOS, settings, seed, source/input hashes and exact statuses. A smoke workflow uses one structural input per family and one repeat. Full JSON records retain cost, count, IDs, bounds, phase times, memory and certificates; CSV summaries expose min/median/max variability.\n'
    appendices+=r'''\section{Source Evidence Boundaries}
Weighted-rank and logic source inspection locators remain in the ledger; the owner/cell and original-objective transfers are separately stated project arguments. Architectural comparator limits follow the inspected methods, with uninspected extensions unknown. Sources are pinned to the buildingSMART community revision 7ddf57a. Attribution: BSI (2020), ``Medical-Dental Test Files'' and ``Duplex Apartment Test Files,'' buildingSMART International; Molio original authors as recorded by the IFC/source registry. Root licence: CC BY 4.0; Clinic/Duplex folder notices repeat attribution/change requirements. Esplanades has a lowercase readme stating CC BY 4.0; Molio has no folder notice. Schependomlaan's parent notice permits scientific/academic use. Notice URLs, hashes and unavailable folder README paths are retained. Changes comprise XY projection, deterministic subsets, conservative background and hypothetical doors/profiles/reservations/templates/permissions/costs. Raw IFCs are not redistributed.
'''
    section_start=before.index(r'\section{Multi-Room Building-Derived Controlled Experiments}')
    design,building_section=before[:section_start],before[section_start:]
    text=front+design+result+building_section+discussion+appendices+template[template.index(r'\begin{thebibliography}'):]
    text=order_references(text)
    if '@@' in text or len(abstract.split())>250:raise ValueError('unresolved slot or abstract length')
    (output/'master.tex').write_text(text,encoding='utf-8');shutil.copy2(root/'paper/ieee/IEEEtran.cls',output/'IEEEtran.cls');shutil.copytree(figures,output/'figures')
    grouped=defaultdict(list)
    for r in rows+public:grouped[(r['experiment_id'],r['instance_id'],r['solver'])].append(r)
    with (output/'summary.csv').open('w',newline='',encoding='utf-8') as handle:
        w=csv.writer(handle);w.writerow(['experiment','instance','method','repetitions','statuses','function_min','function_median','function_max','peak_memory_max','end_to_end_median','objective_costs','selected_action_ids','parameters','recognition_median','optimization_median','replay_median','peak_raw_states','peak_retained_states'])
        for key,group in sorted(grouped.items()):
            times=[r['function_seconds'] for r in group if r['function_seconds'] is not None];memory=[r['peak_memory_bytes'] for r in group if r['peak_memory_bytes'] is not None]
            def med(field):
                values=[r[field] for r in group if r[field] is not None]
                return median(values) if values else None
            raw=[r['peak_raw_states'] for r in group if r['peak_raw_states'] is not None];retained=[r['peak_retained_states'] for r in group if r['peak_retained_states'] is not None]
            w.writerow(list(key)+[len(group),json.dumps(dict(Counter(r['status'] for r in group))),min(times) if times else None,median(times) if times else None,max(times) if times else None,max(memory) if memory else None,med('end_to_end_seconds'),
                json.dumps(sorted({r['objective_cost'] for r in group if r['objective_cost'] is not None})),json.dumps(group[0]['selected_action_ids']),json.dumps(group[0]['parameters']),med('recognition_seconds'),med('optimization_seconds'),med('replay_seconds'),max(raw) if raw else None,max(retained) if retained else None])
    paths=[controlled/'records.json',building/'records.json',source_audit/'summary.json',three_audit/'summary.json',controls/'summary.json',geometry_profile/'summary.json',Path(__file__),root/'paper/ieee/master.template.tex',root/'paper/ieee/revised_proof_map.tex',root/'paper/ieee/revised_evaluation.tex',root/'paper/ieee/revised_parameters.tex',root/'paper/manuscript.template.tex',root/'paper/ieee/generic_appendix.tex',root/'scripts/audit_revised_evidence.py',root/'scripts/make_revised_figures.py',root/'spec/evaluation-records.schema.json']
    paths+=list(controls.rglob('*.json'))+list(geometry_profile.rglob('*.json'))+[figures/'figure-provenance.json']
    write_json(output/'master-provenance.json',dict(audits=audits,abstract_words=len(abstract.split()),source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}))
    print(output/'master.tex')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['controlled','building','source-audit','three-audit','controls','geometry-profile','figures','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();build(a.controlled,a.building,a.source_audit,a.three_audit,a.controls,a.geometry_profile,a.figures,a.output)
