"""Audited scaling tables and plots, keeping campaigns and failures separate."""
import argparse,json,statistics,sys
from pathlib import Path
from cfar.io import write_json


def summarize(local,bays,certificates,output):
    l=json.loads((local/'summary.json').read_text());b=json.loads((bays/'summary.json').read_text())
    cert=json.loads((certificates/'index.json').read_text())
    output.mkdir(parents=True,exist_ok=False)
    assert l['observations']==36 and b['observations']==24
    assert l['kernel_fingerprints']==b['kernel_fingerprints']
    groups=[]
    for size in (8,24,48):
        ids=[c['instance_id'] for c in l['protocol']['cases'] if c['level']==size]
        methods={}
        for method in ('both','cp-sat'):
            ss=[s for s in l['summaries'] if s['instance_id'] in ids and s['method']==method]
            completed_times=[s['pipeline_median'] for s in ss if s['exact']==2]
            memory=[x/1048576 for s in ss for x in s['memory_bytes'] if x is not None]
            phases=[x for s in ss for x in s['phase_seconds'] if x is not None]
            methods[method]=dict(exact=sum(s['exact'] for s in ss),feasible=sum(s['verified_feasible'] for s in ss),
                pipeline_median_of_price_medians=statistics.median(completed_times) if completed_times else None,
                price_median_min=min(completed_times) if completed_times else None,
                price_median_max=max(completed_times) if completed_times else None,
                returned_worker_memory_n=len(memory),returned_worker_memory_median_mib=statistics.median(memory) if memory else None,
                recognition_median=statistics.median(p['recognition'] for p in phases) if phases else None,
                optimization_median=statistics.median(p['optimization'] for p in phases) if phases else None,
                replay_median=statistics.median(p['materialization_replay'] for p in phases) if phases else None,
                raw_state_max=max((p['peak_raw_states'] for s in ss for p in s['statistics'] if p and 'peak_raw_states' in p),default=None))
        tasks=[t for t in l['cp_tasks'] if t['instance_id'] in ids]
        ratios=[]
        for iid in ids:
            d=next(s for s in l['summaries'] if s['instance_id']==iid and s['method']=='both')
            c=next(s for s in l['summaries'] if s['instance_id']==iid and s['method']=='cp-sat')
            if d['exact']==c['exact']==2:ratios.append(c['pipeline_median']/d['pipeline_median'])
        groups.append(dict(bands=size,actions=8*size,storeys=2*size+1,price_variants=3,runs_per_method=6,
            methods=methods,cp_cost_proofs=sum(t['cost_stage_status']=='OPTIMAL' for t in tasks),
            cp_count_proofs=sum(t['count_stage_status']=='OPTIMAL' for t in tasks),
            paired_price_ratios_cp_over_dp=ratios,
            max_b=max(cert[i]['b'] for i in ids),max_domain_product=max(cert[i]['max_resource_domain_product'] for i in ids)))
    private=[]
    for n in (2,8,16,32):
        iid=f'private-bays-{n}';ss={s['method']:s for s in b['summaries'] if s['instance_id']==iid}
        private.append(dict(bays=n,certificate=cert[iid],methods={k:dict(exact=v['exact'],statuses=v['statuses'],
            median=v['pipeline_median'],raw_states=max((x['peak_raw_states'] for x in v['statistics'] if x and 'peak_raw_states' in x),default=None)) for k,v in ss.items()}))
    data=dict(local_groups=groups,private_bays=private,local_method_totals=l['method_totals'],bay_method_totals=b['method_totals'],
        local_measured_revision=l['protocol']['code_revision'],bay_measured_revision=b['protocol']['code_revision'],
        local_observations=36,bay_observations=24,
        interpretation='Development-guided authored families. Three price variants per topology, two counterbalanced repeats; not independent buildings. No timed limits averaged as completed runs.')
    write_json(output/'summary.json',data)
    plot(data,output/'figures')
    lines=['# Frontier/scaling results','',data['interpretation'],'',
        '| Bands / actions | DP exact | CP exact | CP cost proofs | DP price-median range (s) | CP completed price-median range (s) | Paired CP/DP ratios |',
        '|---|---:|---:|---:|---|---|---|']
    for g in groups:
        d,c=g['methods']['both'],g['methods']['cp-sat']
        fmt=lambda x:'--' if x['price_median_min'] is None else f"{x['price_median_min']:.2f}–{x['price_median_max']:.2f}"
        lines.append(f"| {g['bands']} / {g['actions']} | {d['exact']}/6 | {c['exact']}/6 | {g['cp_cost_proofs']}/6 | {fmt(d)} | {fmt(c)} | {', '.join(f'{x:.2f}' for x in g['paired_price_ratios_cp_over_dp']) or '--'} |")
    (output/'results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def plot(data,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder.mkdir()
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42})
    fig,axs=plt.subplots(1,2,figsize=(7.1,3.1))
    for method,label,color in [('both','Lifetime DP','#2166ac'),('cp-sat','CP-SAT','#b2182b')]:
        x=[];y=[];lo=[];hi=[]
        for g in data['local_groups']:
            m=g['methods'][method];v=m['pipeline_median_of_price_medians']
            if v is not None:
                x.append(g['bands']);y.append(v);lo.append(v-m['price_median_min']);hi.append(m['price_median_max']-v)
        axs[0].errorbar(x,y,yerr=[lo,hi],marker='o',capsize=3,label=label,color=color)
        groups=data['local_groups'];axs[1].plot([g['bands'] for g in groups],[g['methods'][method]['exact'] for g in groups],marker='o',label=label,color=color)
    for g in data['local_groups']:
        c=g['methods']['cp-sat']
        if c['exact']<6:axs[0].annotate(f"CP: {6-c['exact']}/6 limited",(g['bands'],70),ha='center',fontsize=8)
    axs[0].set_yscale('log');axs[0].set_ylabel('Completed pipeline (s)');axs[0].set_xlabel('Local bands');axs[0].legend(fontsize=8)
    axs[0].set_title('Price-median range; limits excluded',fontsize=10)
    axs[1].set_xlabel('Local bands');axs[1].set_ylabel('Full exact completions / 6');axs[1].set_ylim(-.2,6.5)
    axs[1].plot([g['bands'] for g in data['local_groups']],[g['cp_cost_proofs'] for g in data['local_groups']],linestyle='--',marker='s',label='CP cost proofs',color='#ef8a62')
    axs[1].legend(fontsize=8);fig.tight_layout()
    for ext in ('pdf','png'):fig.savefig(folder/('local-band-scaling.'+ext),dpi=190,metadata={'CreationDate':None,'ModDate':None} if ext=='pdf' else None)
    plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(7.1,2.8));rows=data['private_bays'];ns=[x['bays'] for x in rows]
    axs[0].plot(ns,[x['certificate']['parameters']['r'] for x in rows],marker='o',label='Coarse r=z')
    axs[0].plot(ns,[x['certificate']['b'] for x in rows],marker='s',label='Transient b (with anchor)')
    axs[0].set_xlabel('Private bays');axs[0].set_ylabel('Static width');axs[0].legend(fontsize=8)
    for method,label in [('floor','Floor DP'),('both','Lifetime DP')]:
        xs=[];ys=[]
        for row in rows:
            m=row['methods'][method]
            if m['raw_states'] is not None:xs.append(row['bays']);ys.append(m['raw_states'])
        axs[1].plot(xs,ys,marker='o',label=label)
    axs[1].set_yscale('log');axs[1].set_xlabel('Private bays');axs[1].set_ylabel('Returned peak raw states');axs[1].legend(fontsize=8)
    axs[1].set_title('Capped rows have no returned peak',fontsize=9);fig.tight_layout()
    for ext in ('pdf','png'):fig.savefig(folder/('private-bay-frontier.'+ext),dpi=190,metadata={'CreationDate':None,'ModDate':None} if ext=='pdf' else None)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('local','bays','certificates','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();summarize(a.local,a.bays,a.certificates,a.output)
