import importlib.util
import json
from pathlib import Path

from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_recognition import recognize_physical_interface

spec=importlib.util.spec_from_file_location('event_width_generator',Path(__file__).resolve().parents[1]/'scripts/build_event_width_followup.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_order_control_changes_live_width_but_not_physical_optimum(tmp_path):
    output=tmp_path/'inputs';module.build(output)
    metrics={};effects=[];payloads=[]
    for order in ('paired','batched'):
        a=json.loads((output/'instances'/('event-width-'+order+'.json')).read_text())
        r=solve_owned_interface(a,compress=False,profile=True,release_dead_cells=True,release_dead_vertices=True)
        rec=recognize_physical_interface(a)
        assert len(rec['units'])==1 and len(rec['units'][0]['action_ids'])==8
        assert r['cost']=='3' and len(r['selected'])==2
        catalog={c['connection_id']:c for c in a['connections']}
        costs={frozenset((catalog[x['effects'][0]['connection_id']]['u'],catalog[x['effects'][0]['connection_id']]['v'])):x['cost'] for x in a['actions']}
        path_costs=[costs[frozenset(('R0',f'R{i}'))]+costs[frozenset((f'R{i}','R5'))] for i in range(1,5)]
        assert min(path_costs)==3 and path_costs.count(3)==1
        effects.append({e['connection_id'] for action in a['actions'] if action['action_id'] in r['selected'] for e in action['effects']})
        payloads.append(sorted((x['effects'][0]['connection_id'],x['cost']) for x in a['actions']))
        metrics[order]=(r['statistics']['peak_live_vertex_union'],r['statistics']['peak_live_occupancy_cells'])
    assert effects[0]==effects[1] and payloads[0]==payloads[1]
    assert metrics=={'paired':(3,6),'batched':(6,6)}
