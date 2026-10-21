"""Static conservative transient frontier for the existing both-projection DP.

Counts catalogue potential, not a selected-state measurement. Includes eager
targets, action introductions before projection and cells through unit closure.
"""
from collections import defaultdict
import argparse,json,math
from pathlib import Path
from cfar.interface_recognition import recognize_physical_interface
from cfar.io import fingerprint,write_json
from cfar.validation import baseline_active
from cfar.geometry import room_index


def certificate(instance, recognized=None, order='canonical'):
    rec=recognized or recognize_physical_interface(instance)
    assert rec['input_fingerprint']==fingerprint(instance)
    assert order in ('canonical','reverse')
    floors=rec['floor_order'];rank={f:i for i,f in enumerate(floors)}
    room_floor={r:f['floor_id'] for r,(f,_) in room_index(instance).items()}
    pids=sorted(rec['components']);catalog={c['connection_id']:c for c in instance['connections']}
    node=lambda q,r:(q,'v:'+rec['components'][pids[q]][r])
    baseline=defaultdict(list);units=defaultdict(list);touch=defaultdict(set)
    for cid,allowed in baseline_active(instance).items():
        c=catalog[cid]
        for q,pid in enumerate(pids):
            if pid not in allowed or c['u'] not in rec['components'][pid]:continue
            u,v=node(q,c['u']),node(q,c['v'])
            if u!=v:baseline[min(rank[room_floor[c['u']]],rank[room_floor[c['v']]])].append({u,v})
    actions={a['action_id']:a for a in instance['actions']}
    for aid in rec['action_cells']:
        for e in actions[aid]['effects']:
            c=catalog[e['connection_id']]
            for q,pid in enumerate(pids):
                if pid in e['permitted_profiles']:touch[aid].update((node(q,c['u']),node(q,c['v'])))
    for j,u in enumerate(rec['units']):units[u['first_floor']].append((j,u))
    events=[];introduced={};forgotten={};first={};last={};cell_first={};cell_last={}
    vertex_floor={node(q,r):room_floor[r] for q,pid in enumerate(pids) for r in rec['components'][pid]}
    required={node(q,o['target']) for q,pid in enumerate(pids) for o in instance['obligations'] if o['profile_id']==pid}
    required.update(node(q,rec['anchors'][pid]) for q,pid in enumerate(pids))
    def emit(kind,vertices=(),cells=(),unit=None,floor=None):
        t=len(events);events.append(dict(kind=kind,unit=unit,floor=floor))
        for v in vertices:first.setdefault(v,t);last[v]=t
        for c in cells:cell_first.setdefault(c,t)
        return t
    def intro(fid):
        t=emit('introduce',floor=fid);introduced[fid]=t
    L=rec['parameters']['L']
    for fid in floors[:L]:intro(fid)
    for f,fid in enumerate(floors):
        for vertices in (list(reversed(baseline[f])) if order=='reverse' else baseline[f]):emit('baseline',vertices)
        for j,u in (list(reversed(units[f])) if order=='reverse' else units[f]):
            for aid in (list(reversed(u['action_ids'])) if order=='reverse' else u['action_ids']):
                emit('action',touch[aid],rec['action_cells'][aid],unit=j)
            t=emit('unit-close',unit=j)
            for aid in u['action_ids']:
                for c in rec['action_cells'][aid]:cell_last[c]=t
        forgotten[fid]=emit('floor-forget',floor=fid)
        if f+L<len(floors):intro(floors[f+L])
    intervals={}
    for v in required|set(first):
        fid=vertex_floor[v]
        left=introduced[fid] if v in required else first[v]
        right=min(last.get(v,forgotten[fid]),forgotten[fid])
        assert left<=right,(v,left,right)
        intervals[v]=(left,right)
    cells={c['cell_id']:c for c in rec['cells']}
    rows=[]
    for t,e in enumerate(events):
        vertices=[v for v,(l,h) in intervals.items() if l<=t<=h]
        active=[c for c,l in cell_first.items() if l<=t<=cell_last[c]]
        owners=set(rec['units'][e['unit']]['asset_ids']) if e['unit'] is not None else set()
        domains={c:2+len(owners&set(cells[c]['asset_ids'])) for c in active}
        product=math.prod(domains.values())
        rows.append(dict(index=t,**e,potential_vertices=len(vertices),including_anchors=len(vertices)+len(pids),
            potential_cells=len(active),resource_domain_product=product,
            resource_log2=math.log2(product),maximum_cell_domain=max(domains.values(),default=1)))
    return dict(format='static_transient_frontier_v1',input_fingerprint=fingerprint(instance),event_order=order,
        scope='Uncompressed exact DP with both projections; finite recognized model; static potential including eager introductions and pre-projection action branching',
        parameters=rec['parameters'],events=rows,
        max_potential_vertices=max(r['potential_vertices'] for r in rows),
        b=max(r['including_anchors'] for r in rows),
        max_potential_cells=max(r['potential_cells'] for r in rows),
        max_resource_log2=max(r['resource_log2'] for r in rows),
        max_resource_domain_product=max(r['resource_domain_product'] for r in rows))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();write_json(a.output,certificate(json.loads(a.input.read_text())))
