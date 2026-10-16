"""Add an audited documentary case to the IEEE review master; no new benchmark claims."""
import argparse,hashlib,json,shutil
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def build(case,base,output):
    admission=json.loads((case/'admission.json').read_text());rows=json.loads((case/'scalar-records.json').read_text())
    assert not admission['manifest']['git_dirty']
    assert admission['source_sha256']=='31b125ed7371564f3c7e4254237464cac7bf9fc1ff68bb8c46dec556d9fcf3a1'
    assert admission['extractor_sha256']==hashlib.sha256(Path('scripts/audit_city_hall_document.py').read_bytes()).hexdigest()
    assert len(rows)==admission['scalar_rows']==580
    assert all(r['independent_action_cost'] is None for r in rows)
    assert Counter(r['accounting_role'] for r in rows)=={'priced_observation_not_admitted_action':533,'reference_not_independent_action':47}
    from decimal import Decimal
    for r in rows:
        if r['quantity_price_matches_total'] is not None:
            assert Decimal(r['quantity'])*Decimal(r['source_unit_cost'])==Decimal(r['source_total_cost'])
    assert admission['admissions']['physical_solver_instances']==0
    assert all(p['text_characters']==p['vector_lines']==p['vector_rectangles']==p['vector_curves']==0 for p in admission['plans'])
    original=((base/'pre-documentary-master.tex') if (base/'pre-documentary-master.tex').exists() else base/'master.tex').read_text(encoding='utf-8')
    assert 'Historical Documentary Admission Study' not in original
    shutil.copytree(base,output,ignore=shutil.ignore_patterns('preview','master.pdf','master.log','compile-console.txt','pdf-qa.json','extracted-text.txt'))
    (output/'pre-documentary-master.tex').write_text(original,encoding='utf-8')
    plt.rcParams.update({'font.family':'serif','font.size':8,'pdf.fonttype':42})
    fig,axs=plt.subplots(1,2,figsize=(7.1,2.8))
    ax=axs[0];ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
    levels=[('Second',.82),('First',.5),('Basement',.18)]
    for name,y in levels:
        ax.scatter([.16],[y],s=520,facecolors='white',edgecolors='#285878',zorder=3)
        ax.text(.27,y,name,va='center',fontsize=9)
    ax.plot([.16,.16],[.5,.82],color='#285878',linewidth=2)
    ax.text(.59,.7,'Reported elevator service;\naccessibility barriers remain',ha='center',va='center')
    ax.annotate('',xy=(.16,.47),xytext=(.16,.22),arrowprops=dict(arrowstyle='<->',color='#a85c20',linestyle='--',lw=1.7))
    ax.text(.59,.3,'Proposed basement extension\nand lobby: not admitted',ha='center',va='center',color='#8d4818')
    ax.set_title('(a) Reported service and proposal',fontsize=9)
    ax=axs[1];ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
    for y,label,color in [(.63,'One JOB row\nHistorical estimate: USD 900,000','#285878'),(.25,'Seven REF rows\nNot seven independent free actions','#8d4818')]:
        ax.add_patch(FancyBboxPatch((.05,y-.13),.9,.26,boxstyle='round,pad=.02',facecolor='white',edgecolor=color,lw=1))
        ax.text(.5,y,label,ha='center',va='center',fontsize=9,color=color)
    ax.set_title('(b) Source item 28 accounting',fontsize=9)
    fig.tight_layout()
    for ext in ['pdf','png']:fig.savefig(output/'figures'/('city_hall_documentary.'+ext),bbox_inches='tight',dpi=180)
    plt.close(fig)
    text=r'''
\section{Historical Documentary Admission Study}
\subsection{Evidence and Extraction Boundary}
A further source audit examines the City of Santa Barbara City Hall/Annex survey~\cite{cityhall}. This is a documentary admission study, not an additional solver benchmark or a validated repair. The 264-page PDF is pinned by SHA256; its machine-readable table dates are 14 April 2008. The audited first-floor, second-floor and basement reference plans are at PDF pages 44, 119 and 197. Each is a raster image with no text or vector drawing primitives; no metric scale, exact room polygons, floor elevations or complete room adjacency was verified. Pixel coordinates therefore do not supply the physical input required by the recognizer.

The deterministic extractor records scalar prices, quantities, units, item context and page/row positions. It recovers 580 machine-readable unit-anchored entries: 533 priced rows and 47 reference rows. All 533 priced rows satisfy exact decimal quantity-times-unit-cost arithmetic. This is an extraction/arithmetic check, not independent confirmation of construction prices or complete-document row recall. Scanned annex tables are outside the text-only extraction. The source first-floor summary and detailed header differ by USD 200; that discrepancy is retained without correction. Raw drawings, the PDF and private extracted wording are excluded from the release.

\subsection{Atomic Accounting and Physical Scope}
The elevator group (item 28, PDF pages 111--113) has one USD 900000 job row and seven reference entries. Reference zeros are not evidence of independently available free repairs, and an aggregate heading is not a second purchase. This distinction motivates retaining original action accounting; it does not establish that every reference entry may be selected or combined arbitrarily. The source value is a historical estimate, not a current installed quote, and is not transferred into the Clinic/Molio experiments.

The proposed elevator enlargement, basement extension and additional lobby do not establish a fixed-footprint activation in frozen geometry. Existing-asset remodeling and candidate-door/hardware improvements are outside the implemented owned-interface recognizer or require unsupported semantics. A recommended renovation also does not verify construction permission, reserved collision footprints or engineering feasibility. These gaps must not be filled by silently changing the model or reclassifying hypothetical assumptions as source facts.

\begin{figure*}[t]\centering
\includegraphics[width=.96\textwidth]{figures/city_hall_documentary.pdf}
\caption{Original documentary schematic, not a metric building drawing or a solver output. The reported elevator serves the first and second floors; the basement connection/lobby is proposed work. Item 28's costed job and reference entries are distinguished. Historical source facts do not certify feasibility under the frozen-geometry model.}\label{fig:cityhall}
\end{figure*}

\subsection{Admission Result}
No additional physical solver instance or validated building repair is admitted. Existing counts remain 2274 timed observations across the original and follow-up campaigns. The documentary study supplies traceable historical observations and prices, while revealing missing metric geometry and action-scope evidence. It cannot support present-day compliance, construction readiness or reported optimization performance. A source-admissible future case needs a checked metric model and action permissions/footprints consistent with the recognized scope; a source recommendation alone is insufficient. The implementation and contribution direction remain unchanged.
'''
    # Drain source-study floats before the one-piece bibliography.
    marker=r'\clearpage'+'\n'+r'\begin{thebibliography}'
    assert marker in original
    final=original.replace(marker,text+'\n'+marker,1)
    bib=r'''\bibitem{cityhall} Gilda Puente-Peters, Architects, ``City Hall and City Hall Annex: Accessibility Survey,'' City of Santa Barbara, Technical Appendix A.1, copyright 2007, item tables dated Apr. 14, 2008. [Online]. Available: \url{'''+admission['source_url']+r'''}.
'''
    final=final.replace(r'\end{thebibliography}',bib+r'\end{thebibliography}',1)
    final=final.replace(r'\begin{thebibliography}',r'\IEEEtriggeratref{12}'+'\n'+r'\begin{thebibliography}',1)
    (output/'master.tex').write_text(final,encoding='utf-8')
    paths=[case/'admission.json',case/'scalar-records.json',case/'plan-audit.json',Path(__file__),output/'master.tex',output/'pre-documentary-master.tex',output/'figures/city_hall_documentary.pdf']
    provenance=dict(documentary_source_sha256=admission['source_sha256'],documentary_extraction_commit=admission['manifest']['git_revision'],
        new_timed_observations=0,new_admitted_physical_instances=0,files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    (output/'documentary-provenance.json').write_text(json.dumps(provenance,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(output/'master.tex')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['case','base','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();build(a.case,a.base,a.output)
