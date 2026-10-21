from pathlib import Path
import json
from collections import defaultdict
from itertools import combinations

def structure(a):
 ids={r['room_id'] for f in a['floors'] for r in f['rooms']};parent={v:v for v in ids}
 def find(v):
  while parent[v]!=v:parent[v]=parent[parent[v]];v=parent[v]
  return v
 active={e['connection_id'] for f in a['floors'] for e in f['access_edges']}
 for c in a['connections']:
  if c['connection_id'] in active:parent[find(c['u'])]=find(c['v'])
 edges={tuple(sorted((find(c['u']),find(c['v'])))) for c in a['connections'] if not c['existing'] and find(c['u'])!=find(c['v'])}
 nodes={v for e in edges for v in e};graph={v:set() for v in nodes}
 for u,v in edges:graph[u].add(v);graph[v].add(u)
 seen=set();parts=[]
 for u in sorted(nodes):
  if u in seen:continue
  component={u};stack=[u]
  while stack:
   v=stack.pop()
   for w in graph[v]-component:component.add(w);stack.append(w)
  seen|=component;parts.append(component)
 root=find(a['obligations'][0]['source']);comp=next((p for p in parts if root in p),{root})
 component_edges=[e for e in edges if e[0] in comp]
 physical=[c for c in a['connections'] if not c['existing']]
 suppliers=defaultdict(set)
 for action in a['actions']:
  for e in action['effects']:suppliers[e['connection_id']].add(action['action_id'])
 return dict(storeys=len(a['floors']),rooms=len(ids),actions=len(a['actions']),obligations=len(a['obligations']),
  targets=len({o['target'] for o in a['obligations']}),profiles=len(a['profiles']),
  candidate_connections=len(physical),bundled_actions=sum(len(x['effects'])>1 for x in a['actions']),
  contracted_active_nodes=len(comp),contracted_active_edges=len(component_edges),
  active_cycle_rank=len(component_edges)-len(comp)+1,
  maximum_supplier_count=max(map(len,suppliers.values()),default=0),
  baseline_doors=len(active),cost_domain='hypothetical abstract integers')

if __name__=='__main__':
 for p in sorted(Path('runs/building-network-dataset/instances').glob('*-s0.json')):
  print(p.stem,structure(json.loads(p.read_text())))
