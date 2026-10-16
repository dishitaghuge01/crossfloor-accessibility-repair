"""Tables and research figures derived solely from normalized evidence."""
import argparse,json
from collections import defaultdict
from pathlib import Path
from statistics import median
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from cfar.io import write_json

COLORS={'compressed':'#174d78','uncompressed':'#ba5a1c','cp-sat':'#23764b','greedy':'#777777','greedy-improved':'#a02c38','pruned':'#744c9e','cached':'#2a8e91'}
STYLES={'compressed':'o-','uncompressed':'s--','cp-sat':'^-.','greedy-improved':'D:','greedy':'x:','pruned':'v--','cached':'P:'}
plt.rcParams.update({'font.family':'serif','font.size':8,'axes.labelsize':8,'legend.fontsize':7,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})


def save(fig,output,name):
    fig.savefig(output/(name+'.pdf'),bbox_inches='tight',pad_inches=.08)
    fig.savefig(output/(name+'.png'),bbox_inches='tight',pad_inches=.08,dpi=180)
    plt.close(fig)


def make(controlled,building,source_audit,output):
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('fresh output required')
    from make_ieee_figures import pipeline,unit_witness
    pipeline(output);unit_witness(output)
    data=json.loads((controlled/'records.json').read_text())
    public=json.loads((building/'records.json').read_text())
    # Paired methods, all repetitions; ranges show descriptive variability.
    for family in ['catalogue','ownership','connectivity','profiles','support']:
        fig,ax=plt.subplots(figsize=(3.45,2.4))
        for method in ['compressed','uncompressed','cp-sat','greedy-improved']:
            groups=defaultdict(list)
            for r in data:
                if r['generator_family']==family and r['solver']==method:
                    size=int(r['instance_id'].split('-')[1])
                    if r['status'] in {'optimal','infeasible','feasible'}:groups[size].append(r['function_seconds'])
                    else:ax.plot(size,60,marker='x',color=COLORS[method])
            if groups:
                xs=sorted(groups);ys=[median(groups[x]) for x in xs]
                ax.plot(xs,ys,STYLES[method],ms=3,label=method,color=COLORS[method])
                ax.vlines(xs,[min(groups[x]) for x in xs],[max(groups[x]) for x in xs],color=COLORS[method],alpha=.6)
        ax.set(xlabel=family+' size (measured parameters in tables)',ylabel='Function wall seconds',yscale='log')
        ax.legend(frameon=False);fig.tight_layout();save(fig,output,'scaling_'+family)
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.6))
    for method in ['compressed','uncompressed']:
        groups=defaultdict(list);removed=defaultdict(list)
        for r in data:
            if r['generator_family']=='connectivity' and r['solver']==method and r['status']=='optimal':
                n=int(r['instance_id'].split('-')[1]);groups[n].append(r['peak_retained_states']);removed[n].append(r['statistics'].get('representative_rows_removed',0))
        xs=sorted(groups);axes[0].plot(xs,[median(groups[x]) for x in xs],STYLES[method],label=method,color=COLORS[method])
        axes[1].plot(xs,[median(removed[x]) for x in xs],STYLES[method],label=method,color=COLORS[method])
    axes[0].set(xlabel='Connectivity floors',ylabel='Peak retained states',yscale='log');axes[1].set(xlabel='Connectivity floors',ylabel='Total representative rows removed')
    for ax in axes:ax.legend(frameon=False)
    fig.tight_layout();save(fig,output,'compression_stress')
    methods=['compressed','uncompressed','cp-sat','greedy','greedy-improved']
    names=sorted({r['instance_id'] for r in data})
    status={'optimal':0,'feasible':1,'infeasible':2,'heuristic_failed':3,'limit_exceeded':4,'unsupported':5,'timeout':6,'internal_error':7}
    from matplotlib.colors import ListedColormap
    from run_controlled_benchmark import cases
    historical={name for name,seed,category,instance in cases()}
    for subset,suffix in [([n for n in names if n in historical],'revised'),([n for n in names if n not in historical],'structural')]:
        matrix=[[status[next(r['status'] for r in data if r['instance_id']==name and r['solver']==m)] for m in methods] for name in subset]
        fig,ax=plt.subplots(figsize=(7.1,max(4.5,len(subset)*.14)))
        im=ax.imshow(matrix,aspect='auto',cmap=ListedColormap(['#23764b','#70ad8a','#174d78','#aaaaaa','#dd9443','#bc6576','#7f65a8','#000000']),vmin=-.5,vmax=7.5)
        letters=['O','F','I','H','L','U','T','E']
        for i,row in enumerate(matrix):
            for j,value in enumerate(row):ax.text(j,i,letters[value],ha='center',va='center',fontsize=5.5,color='white' if value in {0,2,5,6,7} else 'black')
        ax.set_xticks(range(len(methods)),methods,rotation=20,ha='right');ax.set_yticks(range(len(subset)),subset,fontsize=6)
        colorbar=fig.colorbar(im,ax=ax,ticks=range(8),fraction=.04,pad=.03);colorbar.ax.set_yticklabels(list(status),fontsize=7)
        fig.tight_layout();save(fig,output,'status_matrix_'+suffix)
    # Actual retained IFC geometry, plus experimental doors and candidates.
    fig,axes=plt.subplots(2,2,figsize=(7.1,5.3))
    for row,name in enumerate(['clinic-horizontal','molio-horizontal']):
        instance=json.loads((building/name/'input.json').read_text());catalog={c['connection_id']:c for c in instance['connections']}
        for col,f in enumerate(instance['floors']):
            ax=axes[row,col]
            for room in f['rooms']:
                xs,ys=zip(*room['polygon']);ax.plot(xs,ys,color='#999999',lw=.4)
            for edge in f['access_edges']:
                xs,ys=zip(*catalog[edge['connection_id']]['geometry']['opening']);ax.plot(xs,ys,color='#174d78',lw=2)
            for c in instance['connections']:
                if c['kind']=='lift':
                    points=c['geometry']['footprints'][col]['polygon'];xs,ys=zip(*points);ax.fill(xs,ys,color='#a02c38',alpha=.6)
                    ring=points[:-1] if points[0]==points[-1] else points
                    px,py=zip(*ring);ax.plot(sum(px)/len(px),sum(py)/len(py),'o',ms=3,color='#a02c38')
            for obstacle in f['obstacles']:
                xs,ys=zip(*obstacle);ax.fill(xs,ys,color='#eeeeee',zorder=0)
            # Plot only retained-room envelope; conservative remote background remains in input.
            coords=[p for r in f['rooms'] for p in r['polygon']];xs,ys=zip(*coords)
            ax.set(xlim=(min(xs)-1,max(xs)+1),ylim=(min(ys)-1,max(ys)+1),aspect='equal',title=name.split('-')[0]+f' / selected level {col+1}',xlabel='World X (m)',ylabel='World Y (m)')
            patches=[c['geometry']['footprints'][col]['polygon'] for c in instance['connections'] if c['kind']=='lift']
            detail=ax.inset_axes([.60,.04,.37,.44])
            for obstacle in f['obstacles']:
                xs,ys=zip(*obstacle);detail.fill(xs,ys,color='#eeeeee',zorder=0)
            for room in f['rooms']:
                xs,ys=zip(*room['polygon']);detail.plot(xs,ys,color='#999999',lw=.5)
            for edge in f['access_edges']:
                xs,ys=zip(*catalog[edge['connection_id']]['geometry']['opening']);detail.plot(xs,ys,color='#174d78',lw=1.5)
            for i,points in enumerate(patches):
                xs,ys=zip(*points);detail.fill(xs,ys,color='#a02c38',alpha=.5)
                ring=points[:-1] if points[0]==points[-1] else points;px,py=zip(*ring)
                detail.text(sum(px)/len(px),sum(py)/len(py),f'X{i}',ha='center',va='center',fontsize=5)
            px,py=zip(*[p for shape in patches for p in shape])
            detail.set(xlim=(min(px)-1,max(px)+1),ylim=(min(py)-1,max(py)+1),aspect='equal',xticks=[],yticks=[])
            detail.set_title('Candidate detail',fontsize=6,pad=1,bbox=dict(facecolor='white',edgecolor='none',pad=.4))
            ax.indicate_inset_zoom(detail,edgecolor='#555555',linewidth=.5)
    fig.tight_layout();save(fig,output,'multiroom_plans')
    # One complete worked example, schematic; no fabricated measured geometry.
    fig,grid=plt.subplots(2,2,figsize=(7.1,4.7));axes=list(grid.flat)
    for ax in axes:
        ax.set(xlim=(-.5,2.6),ylim=(-.5,3.8));ax.axis('off')
        for i in range(4):
            for x,prefix in [(0,'R'),(2,'U')]:
                ax.scatter(x,i,s=170,facecolor='white',edgecolor='#174d78',zorder=3);ax.text(x,i,f'{prefix}{i}',ha='center',va='center',fontsize=7)
        ax.text(1,-.45,'Both profiles require R0 to R3',ha='center',fontsize=7)
    for i in range(4):axes[0].plot([0,2],[i,i],ls=':',lw=.8,color='#999999',zorder=1)
    axes[0].text(.4,1.5,'Gray dotted lines:\nroom adjacency,\nnot traversable access',fontsize=7)
    axes[0].set_title('(a) Frozen baseline: no access')
    def line(ax,x,lo,hi,color,style='-'):
        ax.plot([x,x],[lo,hi],color=color,ls=style,lw=2,zorder=1)
    line(axes[1],0,0,2,'#174d78');line(axes[1],2,0,1,'#174d78','--');line(axes[1],0,1,3,'#23764b')
    axes[1].plot([0,0],[1,2],color='#174d78',lw=4,zorder=.9)
    axes[1].text(.15,1.5,'shared owner',fontsize=7,color='#174d78')
    axes[1].text(.15,.5,'A000: cost 4',fontsize=7);axes[1].text(.15,2.5,'A001: cost 1',fontsize=7);axes[1].text(1.1,.5,'paid spare',fontsize=7)
    axes[1].set_title('(b) Full bundle and same-owner reuse')
    line(axes[2],0,0,2,'#174d78');line(axes[2],0,2,3,'#a02c38');line(axes[2],2,0,1,'#174d78','--');line(axes[2],2,1,2,'#a02c38','--')
    axes[2].text(.15,2.5,'E: cost 0.5',fontsize=7);axes[2].text(1.1,1,'X overlap',color='#a02c38',fontsize=7)
    axes[2].set_title('(c) Graph-only repair 4.5 is invalid')
    line(axes[3],0,0,3,'#23764b');line(axes[3],2,0,1,'#174d78','--')
    axes[3].text(.2,3.4,'A000 + A001 = 5',fontsize=7)
    axes[3].text(.25,1.25,'Inside unit: reuse owner\nAfter unit: annex occupied\nReject competing E',fontsize=7)
    axes[3].set_title('(d) Exact repair and interface state')
    fig.tight_layout();save(fig,output,'integrated_example')
    # Measured interface expression, completion and censored statuses.
    from math import log2
    fig,ax=plt.subplots(figsize=(3.45,2.7))
    for method in ['compressed','uncompressed','cp-sat']:
        groups=defaultdict(list)
        for r in data:
            if r['solver']==method and r['parameters']:
                groups[r['instance_id']].append(r)
        for name,samples in groups.items():
            p=samples[0]['parameters'];width=p['p']*p['r']*p['L']+p['z']*p['L']*log2(p['h']+2)
            times=[r['function_seconds'] for r in samples if r['status'] in {'optimal','infeasible'}]
            if times:ax.scatter(width,median(times),s=10,marker=STYLES[method][0],color=COLORS[method],alpha=.5)
            else:ax.scatter(width,60,s=20,marker='x',color=COLORS[method])
        ax.plot([],[],STYLES[method][0],ms=3,color=COLORS[method],label=method)
    ax.set(xscale='log',yscale='log',xlabel='prL + zL log2(h+2), measured',ylabel='Function seconds (noncompletion x at 60)')
    ax.legend(frameon=False);fig.tight_layout();save(fig,output,'measured_width')
    # Direct phase measurements; sums represent the timed DP function only.
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.8))
    cases=['catalogue-128-s0','connectivity-7-s0','rooms-12-s0'];bottom=[0.,0.,0.]
    phases=['recognition','event_construction','optimization','solution_reconstruction','materialization_replay']
    for phase in phases:
        values=[median([r['phase_seconds'][phase] for r in data if r['instance_id']==name and r['solver']=='compressed' and r['phase_seconds']]) for name in cases]
        axes[0].bar(range(3),values,bottom=bottom,label=phase.replace('_',' '));bottom=[a+b for a,b in zip(bottom,values)]
    axes[0].set_xticks(range(3),['catalogue128','connectivity7','rooms12'],rotation=15);axes[0].set_ylabel('Direct DP phase seconds');axes[0].legend(frameon=False,fontsize=6)
    for method in ['compressed','uncompressed','pruned','cached']:
        groups=defaultdict(list)
        for r in data:
            if r['generator_family']=='rooms' and r['solver']==method and r['function_seconds'] is not None:groups[int(r['instance_id'].split('-')[1])].append(r)
        xs=sorted(groups);axes[1].plot(xs,[median(r['function_seconds'] for r in groups[x]) for x in xs],STYLES[method],label=method,color=COLORS[method],ms=3)
    axes[1].set(xlabel='Added irrelevant rooms per floor',ylabel='Function seconds (cached excludes preparation)');axes[1].legend(frameon=False,fontsize=6)
    fig.tight_layout();save(fig,output,'phases_ablations')
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.7))
    for method in ['compressed','uncompressed','cp-sat']:
        groups=defaultdict(list)
        for r in data:
            if r['generator_family']=='connectivity' and r['solver']==method and r['peak_memory_bytes'] is not None:groups[int(r['instance_id'].split('-')[1])].append(r['peak_memory_bytes']/2**20)
        xs=sorted(groups);axes[0].plot(xs,[median(groups[x]) for x in xs],STYLES[method],label=method,color=COLORS[method],ms=3)
    axes[0].set(xlabel='Connectivity floors',ylabel='Whole-worker peak RSS (MiB)');axes[0].legend(frameon=False)
    opt={r['instance_id']:float(r['objective_cost']) for r in data if r['solver']=='cp-sat' and r['status']=='optimal'}
    gaps={m:{} for m in ['greedy','greedy-improved']}
    for r in data:
        if r['solver'] in gaps and r['repeat_index']==0 and r['status']=='feasible' and r['instance_id'] in opt:
            gaps[r['solver']][r['instance_id']]=float(r['objective_cost'])-opt[r['instance_id']]
    names=sorted({name for values in gaps.values() for name,gap in values.items() if gap>0})
    for j,method in enumerate(gaps):
        xs=[i+(j-.5)*.3 for i,n in enumerate(names) if n in gaps[method]];values=[gaps[method][n] for n in names if n in gaps[method]]
        axes[1].bar(xs,values,width=.28,label=method,color=COLORS[method])
    axes[1].set_xticks(range(len(names)),names,rotation=65,ha='right',fontsize=5);axes[1].set_ylabel('Abstract cost above proven optimum');axes[1].legend(frameon=False,fontsize=6)
    fig.tight_layout();save(fig,output,'memory_greedy')
    # Source hashes + generated file hashes, no numbers copied into figures manually.
    import hashlib
    write_json(output/'figure-provenance.json',dict(generator_normalized_sha256=hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),helper_normalized_sha256=hashlib.sha256((Path(__file__).resolve().parent/'make_ieee_figures.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),helper_sha256=hashlib.sha256((Path(__file__).resolve().parent/'make_ieee_figures.py').read_bytes()).hexdigest(),inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [controlled/'records.json',building/'records.json',source_audit/'summary.json']},outputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob('*.pdf')}))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['controlled','building','source-audit','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();make(a.controlled,a.building,a.source_audit,a.output)

