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
plt.rcParams.update({'font.family':'serif','font.size':8,'axes.labelsize':8,'legend.fontsize':7,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})


def save(fig,output,name):
    fig.savefig(output/(name+'.pdf'),bbox_inches='tight',pad_inches=.08)
    fig.savefig(output/(name+'.png'),bbox_inches='tight',pad_inches=.08,dpi=180)
    plt.close(fig)


def make(controlled,building,source_audit,output):
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('fresh output required')
    data=json.loads((controlled/'records.json').read_text())
    public=json.loads((building/'records.json').read_text())
    # Paired methods, all repetitions; ranges show descriptive variability.
    for family in ['catalogue','ownership','connectivity','profiles','support']:
        fig,ax=plt.subplots(figsize=(3.45,2.4))
        for method in ['compressed','uncompressed','cp-sat']:
            groups=defaultdict(list)
            for r in data:
                if r['generator_family']==family and r['solver']==method:
                    size=int(r['instance_id'].split('-')[1])
                    if r['status'] in {'optimal','infeasible'}:groups[size].append(r['function_seconds'])
                    else:ax.plot(size,60,marker='x',color=COLORS[method])
            if groups:
                xs=sorted(groups);ys=[median(groups[x]) for x in xs]
                ax.plot(xs,ys,'o-',ms=3,label=method,color=COLORS[method])
                ax.vlines(xs,[min(groups[x]) for x in xs],[max(groups[x]) for x in xs],color=COLORS[method],alpha=.6)
        ax.set(xlabel=family+' size (measured parameters in tables)',ylabel='Function wall seconds',yscale='log')
        ax.legend(frameon=False);fig.tight_layout();save(fig,output,'scaling_'+family)
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.6))
    for method in ['compressed','uncompressed']:
        groups=defaultdict(list);removed=defaultdict(list)
        for r in data:
            if r['generator_family']=='connectivity' and r['solver']==method and r['status']=='optimal':
                n=int(r['instance_id'].split('-')[1]);groups[n].append(r['peak_retained_states']);removed[n].append(r['statistics'].get('representative_rows_removed',0))
        xs=sorted(groups);axes[0].plot(xs,[median(groups[x]) for x in xs],'o-',label=method,color=COLORS[method])
        axes[1].plot(xs,[median(removed[x]) for x in xs],'o-',label=method,color=COLORS[method])
    axes[0].set(xlabel='Connectivity floors',ylabel='Peak retained states',yscale='log');axes[1].set(xlabel='Connectivity floors',ylabel='Total representative rows removed')
    for ax in axes:ax.legend(frameon=False)
    fig.tight_layout();save(fig,output,'compression_stress')
    methods=['compressed','uncompressed','cp-sat','greedy','greedy-improved']
    names=sorted({r['instance_id'] for r in data})
    status={'optimal':0,'feasible':1,'infeasible':2,'heuristic_failed':3,'limit_exceeded':4,'unsupported':5,'timeout':6,'internal_error':7}
    from matplotlib.colors import ListedColormap
    matrix=[]
    for name in names:
        matrix.append([status[next(r['status'] for r in data if r['instance_id']==name and r['solver']==m)] for m in methods])
    fig,ax=plt.subplots(figsize=(7.1,max(6,len(names)*.13)))
    im=ax.imshow(matrix,aspect='auto',cmap=ListedColormap(['#23764b','#70ad8a','#174d78','#aaaaaa','#dd9443','#bc6576','#7f65a8','#000000']),vmin=-.5,vmax=7.5)
    ax.set_xticks(range(len(methods)),methods,rotation=20,ha='right');ax.set_yticks(range(len(names)),names,fontsize=5)
    colorbar=fig.colorbar(im,ax=ax,ticks=range(8),fraction=.04,pad=.03);colorbar.ax.set_yticklabels(list(status),fontsize=7)
    fig.tight_layout();save(fig,output,'status_matrix_revised')
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
            for obstacle in f['obstacles']:
                xs,ys=zip(*obstacle);ax.fill(xs,ys,color='#777777',alpha=.1)
            # Plot only retained-room envelope; conservative remote background remains in input.
            coords=[p for r in f['rooms'] for p in r['polygon']];xs,ys=zip(*coords)
            ax.set(xlim=(min(xs)-1,max(xs)+1),ylim=(min(ys)-1,max(ys)+1),aspect='equal',title=name.split('-')[0]+f' / source floor {col+1}',xlabel='World X (m)',ylabel='World Y (m)')
    fig.tight_layout();save(fig,output,'multiroom_plans')
    # One complete worked example, schematic; no fabricated measured geometry.
    fig,axes=plt.subplots(1,3,figsize=(7.1,2.8))
    for ax in axes:
        ax.set(xlim=(-.5,2.6),ylim=(-.5,3.8));ax.axis('off')
        for i in range(4):
            for x,prefix in [(0,'R'),(2,'U')]:
                ax.scatter(x,i,s=180,facecolor='white',edgecolor='#174d78',zorder=3);ax.text(x,i,f'{prefix}{i}',ha='center',va='center',fontsize=7)
        ax.text(1,-.45,'Both profiles: R0 to R3',ha='center',fontsize=7)
    def line(ax,x,lo,hi,color,style='-'):
        ax.plot([x,x],[lo,hi],color=color,ls=style,lw=2,zorder=1)
    line(axes[0],0,0,2,'#174d78');line(axes[0],2,0,1,'#174d78','--');line(axes[0],0,1,3,'#23764b')
    axes[0].text(.12,.5,'A000: 4',fontsize=7);axes[0].text(.12,1.5,'A001: 1',fontsize=7);axes[0].text(1.1,.5,'paid spare',fontsize=7)
    axes[0].set_title('(a) Atomic bundle + same-owner reuse')
    line(axes[1],0,0,2,'#174d78');line(axes[1],0,2,3,'#a02c38');line(axes[1],2,0,1,'#174d78','--');line(axes[1],2,1,2,'#a02c38','--')
    axes[1].text(.1,1.5,'E: 0.5',fontsize=7);axes[1].text(1.1,1,'× overlap',color='#a02c38',fontsize=7)
    axes[1].set_title('(b) Thin-footprint error: cost 4.5')
    line(axes[2],0,0,3,'#23764b');line(axes[2],2,0,1,'#174d78','--')
    axes[2].text(.2,3.4,'Exact: A000 + A001 = 5',fontsize=7)
    axes[2].text(.3,1.1,'Cell remembers\nspare-owner;\nreject E',fontsize=7)
    axes[2].set_title('(c) Full paid occupancy survives')
    fig.tight_layout();save(fig,output,'integrated_example')
    # Source hashes + generated file hashes, no numbers copied into figures manually.
    import hashlib
    write_json(output/'figure-provenance.json',dict(inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [controlled/'records.json',building/'records.json',source_audit/'summary.json']},outputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob('*.pdf')}))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['controlled','building','source-audit','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();make(a.controlled,a.building,a.source_audit,a.output)

