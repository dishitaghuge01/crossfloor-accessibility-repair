"""Add a separate permission-backed CAD pilot to the existing review master."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon as Patch
from shapely.geometry import LineString, box


def build(dataset, evaluation, base, output):
    audit=json.loads((dataset/'source-audit.json').read_text())
    results=json.loads((evaluation/'audit.json').read_text())
    if results['observations']!=12 or not results['exact_label_agreement'] or results['git_dirty']:
        raise ValueError('pilot is not fully audited at a clean revision')
    assert results['independent_paid_rectangle_checks']==9
    assert results['independently_reenumerated_oracle_certificates']==4
    private_path=dataset/'private-selected-source.json'
    private=json.loads(private_path.read_text()) if private_path.exists() else None
    cached_underlay=json.loads((base/'cad-wall-underlay.json').read_text()) if private is None else None
    source=base/'pre-cad-master.tex' if (base/'pre-cad-master.tex').exists() else base/'master.tex'
    text=source.read_text(encoding='utf-8')
    assert 'Permission-Backed CAD Input Pilot' not in text
    shutil.copytree(base,output,ignore=shutil.ignore_patterns('preview','master.pdf','master.log',
                    'compile-console.txt','pdf-qa.json','extracted-text.txt'))
    (output/'pre-cad-master.tex').write_text(text,encoding='utf-8')
    plt.rcParams.update({'font.family':'serif','font.size':8,'pdf.fonttype':42})
    fig,axs=plt.subplots(1,2,figsize=(7.1,3.5))
    instance=json.loads((dataset/'instances/bundle.json').read_text())
    underlay=[]
    for index,(ax,room) in enumerate(zip(axs,audit['rooms'])):
        ring=room['registered_ring'];origin=ring[0]
        shift=audit['registration']['lower_to_upper_translation'] if index==0 else [0,0]
        segments=[]
        for row in private or []:
            if row['type'] not in {'LINE','LWPOLYLINE'} or row.get('layer','').lower()!='wall':continue
            ps=row['points'];center=sum(p[1] for p in ps)/len(ps)
            if (index==0 and not 119<center<165) or (index==1 and not 47<center<96):continue
            if row.get('closed'):ps=ps+[ps[0]]
            segments.extend(zip([[x+shift[0]-origin[0],y+shift[1]-origin[1]] for x,y in ps],
                                [[x+shift[0]-origin[0],y+shift[1]-origin[1]] for x,y in ps][1:]))
        if cached_underlay is not None:
            segments=cached_underlay[index]
        else:
            clipped=[]
            for segment in segments:
                shape=LineString(segment).intersection(box(-.3,-.3,6,5.1))
                parts=list(shape.geoms) if hasattr(shape,'geoms') else [shape]
                clipped.extend([list(part.coords) for part in parts if part.geom_type=='LineString' and not part.is_empty])
            segments=clipped
        underlay.append(segments)
        ax.add_collection(LineCollection(segments,colors='#888',linewidths=.6))
        for ob in instance['floors'][index]['obstacles']:
            ax.add_patch(Patch([[x-origin[0],y-origin[1]] for x,y in ob],facecolor='#bbbbbb',edgecolor='none'))
        ax.add_patch(Patch([[x-origin[0],y-origin[1]] for x,y in ring],facecolor='none',edgecolor='#235a81',linestyle='--',linewidth=1.3))
        for j,slot in enumerate(instance['floors'][index]['reserved_portal_zones']):
            coords=[[x-origin[0],y-origin[1]] for x,y in slot]
            ax.add_patch(Patch(coords,facecolor=['#c7e4ce','#f5d6aa'][j],edgecolor=['#397e49','#a96015'][j],alpha=.9))
            ax.text(coords[0][0]+.6,coords[0][1]+.6,f'Slot {j}\nexperimental',ha='center',va='center',fontsize=7)
        ax.set_xlim(-.3,6);ax.set_ylim(-.3,5.1);ax.set_aspect('equal')
        ax.set_xlabel('Registered local x (m)');ax.set_ylabel('Registered local y (m)')
        ax.set_title(['(a) Lower-ground guest bedroom','(b) Upper-ground master bedroom'][index],fontsize=8)
    fig.suptitle('Dimension-checked room pair: 5.700 x 4.800 m; manual boundary annotation',fontsize=9)
    fig.tight_layout()
    for ext in ['pdf','png']:fig.savefig(output/'figures'/f'user_cad_pair.{ext}',dpi=180,bbox_inches='tight')
    plt.close(fig)
    (output/'cad-wall-underlay.json').write_text(json.dumps(underlay,indent=2)+'\n',encoding='utf-8')
    added=r'''
\section{Permission-Backed CAD Input Pilot}\label{app:cad}
\subsection{Source Selection and Metric Reconstruction}
A user-supplied DWG, used with the user's explicit thesis-research permission, provides a third source-file workflow. GNU LibreDWG 0.14 decodes it successfully. Raw CAD and private source extracts are not redistributed. The selected working-drawing group contains separately drawn lower- and upper-ground plans; unrelated plan groups and repeated typical-floor sheets are excluded. This does not certify the design as approved or as built.

The conservative pilot retains one bedroom from each plan. Their printed $5.700\times4.800$\,m dimensions agree with selected inner-face wall/window endpoints within $10^{-6}$ drawing units. This supports a local metre scale despite conflicting global unit metadata; no global unit conversion is asserted for unrelated drawing groups. The room rings are manually reconstructed rectangles, with door/window apertures closed as a declared annotation. They are not claimed to be automatically extracted original semantic room polygons. Derived room IDs retain CAD label handles. Source coordinates, insertion paths and one rigid registration translation remain auditable. Source column envelopes and a conservative lift/stair exclusion envelope are retained; the drawn lift is not sold as a new intervention. Other rooms/circulation are outside this two-room subset.

\begin{figure*}[t]\centering\includegraphics[width=.96\textwidth]{figures/user_cad_pair.pdf}
\caption{Permission-backed CAD pilot, cropped to the two retained rooms. Grey lines are selected source wall segments; dashed outlines are manually reconstructed room boundaries. Coloured slots are hypothetical experimental reservations, not approved lift locations. The lift/stair background exclusion is carried outside this crop. Plot coordinates use a common registered room origin; the instances retain registered source coordinates.}\label{fig:cad}
\end{figure*}

\subsection{Experimental Catalogue and Executed Checks}
Profiles, permissions, two $1.2$\,m-square candidate slots, a $3.6$\,m rise and atomic abstract costs are experimental assumptions. Furniture is not modeled as a structural obstacle in this pilot. Neither candidate construction feasibility nor actual building accessibility follows from the drawings. Four catalogue variants of this one room-pair model are checked; they are not four independent buildings. Each is run once with compressed DP, uncompressed DP and the exhaustive oracle in fresh processes. This is an input/semantics pilot with no comparative timing claim.

\begin{table}[t]\caption{Separate CAD Pilot: All Three Exact Methods Agree}\label{tab:cad}\centering\footnotesize
\begin{tabular}{lccc}\toprule Variant & Status & Abstract cost & Original actions\\\midrule
Bundle & optimal & 3 & A\\
Separate & optimal & 4 & B,C\\
Unavailable profile & infeasible & -- & --\\
Single purchase & optimal & 4 & D\\\bottomrule\end{tabular}\end{table}

The 12 new observations comprise nine optimal results and three infeasible results. All nine returned selections pass full materialization/reachability replay, unchanged-topology checks and independent paid-box/cost/owner arithmetic. Four oracle certificates are independently re-enumerated, including the infeasible case. The frozen original/follow-up campaigns retain their 2274 observations; the separate CAD pilot brings delivered observations to 2286, returned-selection checks to 1949 and oracle certificates to 62. Three targeted adapter tests verify transformed block placement, rejection of unresolved external references and wrong-source rejection. Test counts are not an algorithmic contribution.

This permission-backed CAD-derived controlled experiment strengthens the input workflow; it does not close actual-building intervention validation or literature priority. A verified intervention catalogue and qualified design/site evidence remain necessary for that stronger interpretation.
'''
    # Queue the wide figure before the subsection text, allowing it onto the
    # next text page instead of producing a mostly empty float-only page.
    start=added.index(r'\begin{figure*}')
    stop=added.index(r'\end{figure*}',start)+len(r'\end{figure*}')
    added=added[start:stop]+'\n'+added[:start]+added[stop:]
    marker=r'\clearpage'+'\n'+r'\IEEEtriggeratref{12}'
    assert text.count(marker)==1
    final=text.replace(marker,added+'\n'+marker)
    (output/'master.tex').write_text(final,encoding='utf-8')
    paths=[dataset/'source-audit.json',dataset/'dataset-manifest.json',evaluation/'audit.json',
           Path(__file__),source,output/'master.tex',output/'figures/user_cad_pair.pdf']
    write=dict(source_sha256=audit['source_sha256'],cad_code_commit=results['git_revision'],
        cad_observations=12,prior_observations=2274,total_observations=2286,
        actual_building_validation='not_established',files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    (output/'cad-provenance.json').write_text(json.dumps(write,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(output/'master.tex')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['dataset','evaluation','base','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();build(a.dataset,a.evaluation,a.base,a.output)
