"""Validate a complete frozen schedule, retain failures, and plot saved evidence."""
import argparse
from collections import Counter,defaultdict
from decimal import Decimal
import hashlib,json,statistics
from pathlib import Path

from cfar.io import fingerprint,write_json
from cfar.objective import action_cost


def summarize(source,output,audit=False,reuse_audit=None):
    protocol=json.loads((source/'protocol.json').read_text())
    rows=json.loads((source/'records.json').read_text())
    cached=json.loads(reuse_audit.read_text()) if reuse_audit else None
    if cached:
        assert cached['record_sha256']==hashlib.sha256((source/'records.json').read_bytes()).hexdigest()
    assert len(rows)==len(protocol['schedule'])
    if len(protocol['cases'])==7:assert len(rows)==112
    assert not (source/'SUPERSEDED.json').exists() and not (source/'INVALIDATED.json').exists()
    expected=[(r['instance_id'],r['repeat_index'],r['method']) for r in protocol['schedule']]
    assert [(r['instance_id'],r['repeat_index'],r['method']) for r in rows]==expected
    output.mkdir(parents=True,exist_ok=False)
    groups=defaultdict(list);labels=defaultdict(set);audit_cache={};evidence=[];structures={};cp_tasks=[];kernel_fingerprints=None
    for row in rows:
        raw=source/row['raw_record'];payload=json.loads(raw.read_text())
        assert row['status']==payload['status']
        assert all(row[k]==v for k,v in payload.items()),'Raw/aggregate payload mismatch'
        manifest=json.loads(raw.with_suffix('.manifest.json').read_text())
        assert manifest['git_revision']==row['code_revision']==protocol['code_revision']
        assert not manifest['git_dirty']
        assert manifest['seed']==0
        if kernel_fingerprints is None:kernel_fingerprints=manifest['source_fingerprints']
        assert manifest['source_fingerprints']==kernel_fingerprints
        instance=json.loads((raw.parent/'input.json').read_text())
        assert fingerprint(instance)==row['input_fingerprint']==manifest['input_fingerprint']
        result=row.get('result',{})
        assert row['status']!='infeasible','Constructive segment control proves each study input feasible'
        iid=row['instance_id']
        if iid not in structures:
            structures[iid]=dict(storeys=len(instance['floors']),rooms=sum(len(f['rooms']) for f in instance['floors']),
                actions=len(instance['actions']),profiles=len(instance['profiles']),
                demands_by_profile=dict(Counter(o['profile_id'] for o in instance['obligations'])))
            from network_study_structure import structure
            structures[iid].update(structure(instance))
            if cached:structures[iid].update(cached['structures'][iid])
            if audit:
                from cfar.interface_recognition import recognize_physical_interface
                rec=recognize_physical_interface(instance)
                structures[iid].update(parameters=rec['parameters'],conflict_pairs=len(rec['geometry_conflicts']))
        if row['method']=='cp-sat':
            assert all(Decimal(str(a['cost']))==Decimal(str(a['cost'])).to_integral_value() for a in instance['actions']), 'These study bounds use integer cost scale one'
            trace_path=raw.with_suffix('.events.jsonl')
            trace=[json.loads(line) for line in trace_path.read_text().splitlines()] if trace_path.exists() else []
            finished=[e for e in trace if e['event']=='stage_finished']
            cost_stage=next((e for e in finished if e['objective_stage']=='cost'),None)
            count_stage=next((e for e in finished if e['objective_stage']=='count'),None)
            candidates=[e for e in trace if e['event']=='incumbent']
            identifiers=[e for e in finished if e['objective_stage']=='identifier']
            cp_tasks.append(dict(instance_id=iid,repeat_index=row['repeat_index'],pipeline_status=row['status'],
                cost_stage_status=cost_stage['status'] if cost_stage else 'NOT_FINISHED',
                cost_stage_seconds=cost_stage['wall_seconds'] if cost_stage else None,
                cost_lower_bound=cost_stage['best_bound'] if cost_stage else None,
                cost_incumbent=min((Decimal(e['cost']) for e in candidates),default=None),
                cost_proof_seconds=cost_stage['elapsed_seconds'] if cost_stage and cost_stage['status']=='OPTIMAL' else None,
                first_feasible_seconds=candidates[0]['elapsed_seconds'] if candidates else None,
                best_cost_seconds=(next(e['elapsed_seconds'] for e in candidates if Decimal(e['cost'])==min(Decimal(x['cost']) for x in candidates)) if candidates else None),
                event_clock_scope='CP solver origin after OR-Tools imports; includes recognition/model, excludes worker startup',
                count_stage_status=count_stage['status'] if count_stage else 'NOT_FINISHED',
                count_stage_seconds=count_stage['wall_seconds'] if count_stage else None,
                id_stage_status='OPTIMAL' if row['status']=='optimal' else 'INCOMPLETE' if identifiers or (row.get('last_started_stage') or {}).get('stage')=='identifier' else 'NOT_STARTED',
                id_stage_seconds=sum(e['wall_seconds'] for e in identifiers),
                id_seconds_scope='completed identifier stages only; a killed unfinished stage is excluded',
                full_objective_status=row['status'],last_started_stage=row.get('last_started_stage')))
            if cp_tasks[-1]['cost_incumbent'] is not None:cp_tasks[-1]['cost_incumbent']=str(cp_tasks[-1]['cost_incumbent'])
        if row['status']=='optimal':
            labels[row['instance_id']].add((str(Decimal(result['cost'])),tuple(result['selected'])))
        ids=result.get('selected')
        cost=result.get('cost')
        if ids is None and result.get('incumbent'):
            ids=result['incumbent']['selected'];cost=result['incumbent']['cost']
        if ids is None and row.get('recovered_candidate_audit'):
            ids=row['recovered_candidate_audit']['selected'];cost=row['recovered_candidate_audit']['cost']
        if ids is not None:
            assert action_cost(instance,ids)==Decimal(cost)
            key=fingerprint([row['input_fingerprint'],ids])
            if audit and key not in audit_cache:
                from cfar.actions import apply_actions
                from cfar.obligations import verify_obligations
                repair=apply_actions(instance,ids)
                assert verify_obligations(repair['instance'],repair['active'])['satisfied']
                assert all(r['delta']==0 for r in repair['adjacency'].values())
                audit_cache[key]=dict(input_fingerprint=row['input_fingerprint'],selected=ids,cost=cost,satisfied=True,delta_A=0)
        groups[row['instance_id'],row['method']].append(row)
        evidence.append(dict(raw_record=row['raw_record'],sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                             manifest_sha256=hashlib.sha256(raw.with_suffix('.manifest.json').read_bytes()).hexdigest()))
    assert all(len(v)<=1 for v in labels.values()),'Exact complete labels disagree'
    if cached:
        assert evidence==cached['raw_evidence']
        audit_cache={fingerprint([a['input_fingerprint'],a['selected']]):a for a in cached['audit_unique_selections']}
    summaries=[]
    for (iid,method),rs in groups.items():
        completed=[r for r in rs if r['status'] in ('optimal','infeasible','feasible')]
        values=[r['end_to_end_seconds'] for r in completed]
        feasible=[r for r in rs if r.get('result',{}).get('selected') is not None or r.get('result',{}).get('incumbent') or r.get('verified_checkpoint') or r.get('recovered_candidate_audit')]
        summaries.append(dict(instance_id=iid,method=method,n=len(rs),statuses=dict(Counter(r['status'] for r in rs)),
            exact=sum(r['status'] in ('optimal','infeasible') for r in rs),verified_feasible=len(feasible),
            pipeline_median=statistics.median(values) if values else None,
            pipeline_min=min(values) if values else None,pipeline_max=max(values) if values else None,
            memory_bytes=[r.get('peak_memory_bytes') for r in rs],
            feasible_costs=[r.get('result',{}).get('cost') or r.get('result',{}).get('incumbent',{}).get('cost') or r.get('recovered_candidate_audit',{}).get('cost') for r in rs],
            first_verified_seconds=[r.get('result',{}).get('first_feasible_seconds') or (r.get('verified_checkpoint') or {}).get('elapsed_seconds') for r in rs],
            statistics=[r.get('result',{}).get('statistics') for r in rs],
            phase_seconds=[r.get('result',{}).get('phase_seconds') for r in rs]))
    def failure_cause(row):
        error=row.get('result',{}).get('error_code')
        if error:return {'INTERFACE_STATE_LIMIT':'state_cap','INTERFACE_CUT_LIMIT':'cut_cap'}.get(error,error)
        if row['status']=='limit_exceeded' and row.get('last_started_stage'):
            return row['last_started_stage']['stage']+'_limit'
        return row['status']
    totals={m:dict(exact=sum(s['exact'] for s in summaries if s['method']==m),
        verified_feasible=sum(s['verified_feasible'] for s in summaries if s['method']==m),
        failures=dict(Counter(failure_cause(r) for r in rows if r['method']==m and r['status'] not in ('optimal','infeasible','feasible')))) for m in protocol['methods']}
    data=dict(protocol=protocol,observations=len(rows),summaries=summaries,method_totals=totals,structures=structures,cp_tasks=cp_tasks,
        exact_labels={k:[list(x) for x in v] for k,v in labels.items()},
        record_sha256=hashlib.sha256((source/'records.json').read_bytes()).hexdigest(),kernel_fingerprints=kernel_fingerprints,
        raw_evidence=evidence,audit_unique_selections=list(audit_cache.values()),
        audit_scope='Full replay on each distinct returned selection plus exact cost; geometry engine shared with solvers',
        reused_audit_sha256=hashlib.sha256(reuse_audit.read_bytes()).hexdigest() if reuse_audit else None)
    write_json(output/'summary.json',data)
    parameter_study=all('family' in c for c in protocol['cases'])
    if parameter_study:plot_parameters(data,output/'figures')
    else:
        plot(data,output/'figures')
        plot_selected_graph(source,data,output/'figures')
    denominator=2*len(protocol['cases'])
    description=('Authored parameter levels; separate families with declared coupled changes.' if parameter_study else
        'Seven layout/constraint combinations from five layouts and two buildings.')
    lines=['# Controlled campaign results','',f"Measured code: {protocol['code_revision']}. {len(rows)} observations. {description} Two repetitions. All costs and intervention assumptions are experimental.",'',
        f'| Method | Exact /{denominator} | Verified feasible /{denominator} | Failure causes |','|---|---:|---:|---|']
    for method,total in totals.items():
        lines.append(f"| {method} | {total['exact']} | {total['verified_feasible']} | {total['failures']} |")
    lines+=['','Timeouts are excluded from completed-time summaries. Recovered candidates were audited outside the deadline; their presence does not establish completed full-objective pipelines. The segment method is a feasibility control, never an exact optimizer. No broad superiority or construction-validity claim follows.','',
        '| Input | Method | Status counts | Completed pipeline median [min,max] s |','|---|---|---|---|']
    for s in summaries:
        timing='—' if s['pipeline_median'] is None else f"{s['pipeline_median']:.2f} [{s['pipeline_min']:.2f},{s['pipeline_max']:.2f}]"
        lines.append(f"| {s['instance_id']} | {s['method']} | {s['statuses']} | {timing} |")
    (output/'results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def plot(data,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    folder.mkdir(parents=True,exist_ok=True)
    methods=data['protocol']['methods'];cases=[c['instance_id'] for c in data['protocol']['cases']]
    index={(s['instance_id'],s['method']):s for s in data['summaries']}
    values=np.array([[index[c,m]['exact']/2 for m in methods] for c in cases])
    plt.rcParams.update({'font.size':9,'pdf.fonttype':42})
    fig,ax=plt.subplots(figsize=(7.1,3.8))
    ax.imshow(values,vmin=0,vmax=1,cmap='Blues',aspect='auto')
    for y,c in enumerate(cases):
        for x,m in enumerate(methods):
            s=index[c,m]
            ax.text(x,y,f"{s['exact']}/2\nF:{s['verified_feasible']}/2",ha='center',va='center',fontsize=7,
                    color='white' if s['exact']==2 else 'black')
    ax.set_xticks(range(len(methods)),methods,rotation=35,ha='right')
    ax.set_yticks(range(len(cases)),[c.replace('-network-',' ').replace('-s0','') for c in cases])
    ax.set_title('Exact completion; F = verified feasible (including recovered candidates)',fontsize=9)
    fig.tight_layout()
    fig.savefig(folder/'joint-outcomes.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(folder/'joint-outcomes.png',dpi=200);plt.close(fig)
    # Raw-state peaks are only available when a worker returns normally. Caps
    # are displayed separately and never imputed as an observed state count.
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.5))
    for ax,field,label in [(axes[0],'state_generation_seconds','Generation (s)'),
                           (axes[1],'state_merge_seconds','Dictionary merging (s)')]:
        names=[];values=[]
        for m in methods[:5]:
            samples=[s[field] for row in data['summaries'] if row['method']==m
                     for s in row['statistics'] if s is not None and field in s]
            names.append(m);values.append(statistics.median(samples) if samples else float('nan'))
        ax.bar(names,values,color='#3478b7')
        ax.set_ylabel(label);ax.tick_params(axis='x',rotation=45)
        ax.set_title('Returned-worker medians',fontsize=8)
    fig.tight_layout();fig.savefig(folder/'joint-generation.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(folder/'joint-generation.png',dpi=200);plt.close(fig)
    tasks=data['cp_tasks']
    counts=[sum(t['cost_stage_status']=='OPTIMAL' for t in tasks),
            sum(t['count_stage_status']=='OPTIMAL' for t in tasks),
            sum(t['full_objective_status']=='optimal' for t in tasks)]
    fig,ax=plt.subplots(figsize=(3.5,2.8))
    ax.bar(['Cost proof','Count proof','Full IDs'],counts,color=['#3478b7','#55a868','#8a5ca5'])
    ax.set_ylim(0,len(tasks)+1);ax.set_ylabel(f'Proved stages / {len(tasks)} runs')
    for i,n in enumerate(counts):ax.text(i,n+.1,str(n),ha='center')
    fig.tight_layout();fig.savefig(folder/'joint-cp-tasks.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(folder/'joint-cp-tasks.png',dpi=200);plt.close(fig)
    completed=[s for s in data['summaries'] if s['method']=='both' and s['exact']==2]
    if completed:
        fig,axes=plt.subplots(1,2,figsize=(7.1,3.6))
        labels=[s['instance_id'].replace('clinic-network-16-s0-','C16 ') for s in completed]
        phases=[('recognition','Recognition'),('event_construction','Events'),('optimization','Optimization'),
                ('solution_reconstruction','Reconstruct'),('materialization_replay','Replay')]
        bottom=np.zeros(len(completed))
        for key,label in phases:
            values=np.array([statistics.median(p[key] for p in s['phase_seconds']) for s in completed])
            axes[0].bar(labels,values,bottom=bottom,label=label);bottom+=values
        axes[0].set_ylabel('Median phase time (s)');axes[0].legend(fontsize=6)
        axes[0].set_title('Combined DP: completed inputs',fontsize=8)
        bottom=np.zeros(len(completed));components=[]
        for key,label in [('state_generation_seconds','Generation'),('state_merge_seconds','Merge'),('representative_reduction_seconds','Reduction')]:
            values=np.array([statistics.median(p[key] for p in s['statistics']) for s in completed]);components.append(values)
            axes[1].bar(labels,values,bottom=bottom,label=label);bottom+=values
        total=np.array([statistics.median(p['optimization'] for p in s['phase_seconds']) for s in completed])
        axes[1].bar(labels,np.maximum(0,total-bottom),bottom=bottom,label='Other/profiling')
        axes[1].set_ylabel('Optimization time (s)');axes[1].legend(fontsize=6)
        axes[1].set_title('Labels are included in generation',fontsize=8)
        for ax in axes:ax.tick_params(axis='x',rotation=25)
        fig.tight_layout();fig.savefig(folder/'joint-phases.pdf',metadata={'CreationDate':None,'ModDate':None})
        fig.savefig(folder/'joint-phases.png',dpi=200);plt.close(fig)


def plot_parameters(data,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42})
    families=list(dict.fromkeys(c['family'] for c in data['protocol']['cases']))
    fig,axes=plt.subplots(4,2,figsize=(7.1,9))
    index={(s['instance_id'],s['method']):s for s in data['summaries']}
    for ax,family in zip(axes.flat,families):
        cases=[c for c in data['protocol']['cases'] if c['family']==family]
        for method in data['protocol']['methods']:
            ax.plot(range(len(cases)),[index[c['instance_id'],method]['pipeline_median'] for c in cases],marker='o',markersize=3,label=method)
        ax.set_xticks(range(len(cases)),[str(c['level']) for c in cases],rotation=20)
        ax.set_title(family);ax.set_ylabel('Pipeline median (s)');ax.set_xlabel('Declared family level')
        ax.grid(alpha=.2)
    handles,labels=axes.flat[0].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=3,loc='lower center',fontsize=9)
    fig.tight_layout(rect=(0,.06,1,1))
    fig.savefig(folder/'parameter-families.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(folder/'parameter-families.png',dpi=200);plt.close(fig)


def plot_selected_graph(source,data,folder):
    """Paid effects in each profile, not invented purchase-vertex paths."""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from cfar.validation import baseline_active
    iid='clinic-network-48-s0-full'
    a=json.loads((source/iid/'input.json').read_text())
    selected=set(data['exact_labels'][iid][0][1])
    rooms={r['room_id']:(i,r) for i,f in enumerate(a['floors']) for r in f['rooms']}
    parent={rid:rid for rid in rooms}
    def find(r):
        while parent[r]!=r:parent[r]=parent[parent[r]];r=parent[r]
        return r
    catalog={c['connection_id']:c for c in a['connections']}
    pids=[p['profile_id'] for p in a['profiles']]
    for cid,permissions in baseline_active(a).items():
        assert set(pids)<=set(permissions),'This shared layout assumes common baseline permissions'
        c=catalog[cid];parent[find(c['u'])]=find(c['v'])
    graph=defaultdict(set)
    for c in a['connections']:
        u,v=find(c['u']),find(c['v'])
        if u!=v:graph[u].add(v);graph[v].add(u)
    root=find(a['obligations'][0]['source']);component={root};stack=[root]
    while stack:
        u=stack.pop()
        for v in graph[u]-component:component.add(v);stack.append(v)
    potential={tuple(sorted((u,v))) for u in component for v in graph[u]}
    members=defaultdict(list)
    for rid,(floor,r) in rooms.items():
        members[find(rid)].append((floor,sum(x for x,y in r['polygon'])/len(r['polygon'])))
    xs=[x for node in component for floor,x in members[node]];low,high=min(xs),max(xs)
    positions={node:((sum(x for f,x in members[node])/len(members[node])-low)/max(high-low,1),members[node][0][0]) for node in component}
    # Small deterministic jitter separates component centroids with identical x.
    for j,node in enumerate(sorted(component)):
        x,y=positions[node];positions[node]=(x,y+.12*((j%5)-2))
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.8),sharex=True,sharey=True)
    for q,(pid,ax) in enumerate(zip(pids,axes)):
        for u,v in sorted(potential):
            ax.plot([positions[u][0],positions[v][0]],[positions[u][1],positions[v][1]],color='#dddddd',lw=.6,zorder=0)
        for action in a['actions']:
            if action['action_id'] not in selected:continue
            for e in action['effects']:
                if pid not in e['permitted_profiles']:continue
                c=catalog[e['connection_id']];u,v=find(c['u']),find(c['v'])
                if u==v or u not in component:continue
                ax.plot([positions[u][0],positions[v][0]],[positions[u][1],positions[v][1]],
                        color='#d58520' if action['action_id'].startswith('Q') else '#278354',lw=1.1,zorder=1)
        targets={find(o['target']) for o in a['obligations'] if o['profile_id']==pid}
        for node in sorted(component):
            x,y=positions[node]
            ax.scatter(x,y,s=18 if node in targets else 9,c='#3478b7' if node in targets else 'white',edgecolors='#666666',linewidths=.4,zorder=2)
        ax.scatter(*positions[root],s=100,marker='*',c='#b32929',zorder=3)
        ax.set_title(f'Profile {q}: {len(targets)} required components',fontsize=9)
        ax.set_yticks(range(len(a['floors'])),[f'Storey {i}' for i in range(len(a['floors']))])
        ax.set_xticks([]);ax.set_ylim(-.4,len(a['floors'])-.6)
        for spine in ax.spines.values():spine.set_visible(False)
    legend=[Line2D([],[],color='#278354',label='Paid shared-permission effect'),Line2D([],[],color='#d58520',label='Paid profile-0 alternative'),
            Line2D([],[],marker='*',color='none',markerfacecolor='#b32929',label='Root'),Line2D([],[],marker='o',color='none',markerfacecolor='#3478b7',label='Required component')]
    fig.legend(handles=legend,ncol=2,loc='lower center',fontsize=7)
    fig.suptitle(f"Clinic full interaction: CP-SAT optimum {data['exact_labels'][iid][0][0]}; {sum(x.startswith('Q') for x in selected)} selected restricted alternatives",fontsize=9)
    fig.tight_layout(rect=(0,.15,1,.94))
    fig.savefig(folder/'joint-selected-graph.pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(folder/'joint-selected-graph.png',dpi=200);plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--campaign',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--audit',action='store_true')
    p.add_argument('--reuse-audit',type=Path)
    a=p.parse_args();summarize(a.campaign,a.output,a.audit,a.reuse_audit)
