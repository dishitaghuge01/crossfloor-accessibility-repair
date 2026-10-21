"""Tables, static certificates and graph from the complete audited frozen study."""
import argparse,json,statistics
from pathlib import Path
from cfar.io import write_json
from event_frontier_certificate import certificate


def summarize(source,output,campaign=None):
    a=json.loads((source/'summary.json').read_text());assert a['observations']==48
    output.mkdir(parents=True,exist_ok=False);rows=[]
    for c in a['protocol']['cases']:
        iid=c['instance_id']
        # The campaign folder is supplied explicitly by the caller's audited protocol location.
        campaign=campaign or source.parent/a['protocol']['campaign_id']
        cert=certificate(json.loads((campaign/iid/'input.json').read_text()))
        write_json(output/'certificates'/(iid+'.json'),cert)
        methods={s['method']:s for s in a['summaries'] if s['instance_id']==iid}
        rows.append(dict(instance_id=iid,bands=c['level'],variant=c['structural_variant'],
            b=cert['b'],domain_product=cert['max_resource_domain_product'],cells=cert['max_potential_cells'],
            conflict_pairs=a['structures'][iid]['conflict_pairs'],methods=methods))
    result=dict(rows=rows,method_totals=a['method_totals'],observations=48,measured_revision=a['protocol']['code_revision'],
        unique_replays=len(a['audit_unique_selections']),audit_record_sha256=a['record_sha256'],
        scope='Development-guided authored structural variants; fixed prices; 45/40-second budget. Locality baseline includes recognition and replay. Not independent buildings or general algorithm superiority.')
    write_json(output/'summary.json',result)
    lines=['# Structural variation and locality baseline','',result['scope'],'',
        '| Bands | Variant | b / domain product | Conflicts | DP exact/time | Locality exact/time | CP exact/time |',
        '|---|---|---|---:|---|---|---|']
    for r in rows:
        values=[]
        for m in ('both','locality','cp-sat'):
            s=r['methods'][m];t='--' if s['pipeline_median'] is None else f"{s['pipeline_median']:.2f}s"
            values.append(f"{s['exact']}/2; {t}")
        lines.append('| '+' | '.join([str(r['bands']),r['variant'],f"{r['b']} / {r['domain_product']}",str(r['conflict_pairs'])]+values)+' |')
    assert all(r['methods']['locality']['pipeline_median']<r['methods']['both']['pipeline_median'] for r in rows)
    lines+=['',f"Full exact objectives: {a['method_totals']}. Distinct full replays: {result['unique_replays']}.",
        '', 'Locality is faster on every per-input median. Thus the positive chain regime is shared by an elementary local solver; it is not an exclusive advantage of general owned-interface DP. The latter supports broader recognized graphs, but this study establishes no speed advantage over the restricted baseline.']
    (output/'results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.2),sharey=True)
    labels=['Identity','Alternating','Permuted','Perm.+policy']
    for ax,n in zip(axes,(8,24)):
        rs=[r for r in rows if r['bands']==n]
        for k,(m,label,color) in enumerate([('both','Lifetime DP','#20639b'),('locality','Slot locality','#3b9957'),('cp-sat','CP-SAT','#d77c22')]):
            for i,r in enumerate(rs):
                s=r['methods'][m];x=i+(k-1)*.22
                if s['exact']==2:ax.bar(x,s['pipeline_median'],width=.20,color=color,label=label if i==0 else None)
                else:ax.scatter(x,45,marker='x',color=color);ax.text(x,49,'0/2',ha='center',fontsize=7)
        ax.set_xticks(range(4),labels,rotation=22,ha='right');ax.set_title(f'{n} bands / {8*n} actions')
        ax.set_yscale('log');ax.set_ylim(.7,70);ax.grid(axis='y',alpha=.2)
    axes[0].set_ylabel('Full pipeline median (seconds, log scale)');axes[0].legend(fontsize=7)
    fig.tight_layout();(output/'figures').mkdir()
    fig.savefig(output/'figures/structural-locality.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(output/'figures/structural-locality.png',dpi=180);plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--campaign',type=Path)
    a=p.parse_args();summarize(a.source,a.output,a.campaign)
