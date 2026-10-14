"""IFC polygons/IDs with explicitly hypothetical experimental action catalogues."""
import json
from copy import deepcopy
from cfar.synthetic_star import rectangle


def make_duplex_controlled(audit_path, apartment='A'):
    spaces=json.loads((audit_path/'spaces.json').read_text())
    names={r['name']:r for r in spaces}
    profiles=[dict(profile_id=f'experimental{i}',min_width_m=w,clearance_m=w,can_use_stairs=False,max_slope=.1) for i,w in enumerate((.4,.5))]
    rooms=[names[n] for n in (('A101','A201') if apartment == 'A' else ('B101','B201'))]
    floors=[]
    background=json.loads((audit_path/'background.json').read_text())
    for i,r in enumerate(rooms):
     floors.append(dict(floor_id=r['storey_id'],elevation_m=3.10000000000038*i,boundary=rectangle(0,-18,9,0),rooms=[dict(room_id=r['global_id'],label=r['name'],polygon=r['projected_exterior'])],adjacency_edges=[],access_edges=[],obstacles=[rectangle(*b['conservative_xy_bounds']) for b in background],reserved_portal_zones=([rectangle(6.5,-10.8,7.2,-10.1),rectangle(6.5,-9.8,7.2,-9.1)] if apartment == 'A' else [rectangle(1.6,-9.3,2.3,-8.6),rectangle(1.6,-8.3,2.3,-7.6)])))
    pids=[p['profile_id'] for p in profiles];ids=[r['global_id'] for r in rooms]
    connections=[]
    for i,shape in enumerate(floors[0]['reserved_portal_zones']):
     connections.append(dict(connection_id=f'X{i}',evidence_id=f'hypothetical-X{i}',u=ids[0],v=ids[1],kind='lift',physical_profiles=pids,existing=False,geometry=dict(width_m=.7,asset_id=f'hypothetical-owner{i}',rise_m=3.10000000000038,run_m=1,landings=[dict(room_id=rid,polygon=shape) for rid in ids],footprints=[dict(room_id=rid,polygon=shape) for rid in ids])))
    actions=[]
    for aid,cost,effects in [('A',3,[('X0',[pids[0]]),('X1',[pids[1]])]),('B',2,[('X0',[pids[0]])]),('C',2,[('X1',[pids[1]])]),('D',4,[('X0',pids)])]:
     cids=[c for c,p in effects]
     actions.append(dict(action_id=aid,type='physical_intervention',cost=cost,effects=[dict(op='activate_connection',connection_id=c,permitted_profiles=p) for c,p in effects],requires=[],excludes=[],evidence_ids=['hypothetical-'+c for c in cids],geometry_certificate=dict(geometry_model='reserved_interfaces_2d_v1',connection_ids=cids,changed_floor_ids=[])))
    instance=dict(schema_version='0.1.0',building_id='duplex-derived-hypothetical-'+apartment,description='Building-derived controlled experiment; original IFC room polygons and IDs, hypothetical reservations/profiles/activations/costs; no validated real-building repair.',profiles=profiles,floors=floors,connections=connections,portals=[],actions=actions,obligations=[dict(obligation_id=f'O{i}',source=ids[0],target=ids[1],profile_id=pid) for i,pid in enumerate(pids)],original_restoration_actions=[])
    return instance


def building_cases(audit_path):
    for apartment in ('A', 'B'):
        base = make_duplex_controlled(audit_path, apartment)
        yield f'duplex-{apartment}-bundle', 0, 'building-derived-controlled', base
        expensive = deepcopy(base)
        expensive['actions'][0]['cost'] = 5
        expensive['actions'] = expensive['actions'][:3]
        yield f'duplex-{apartment}-separate', 0, 'building-derived-controlled', expensive
        unavailable = deepcopy(base)
        unavailable['actions'] = [unavailable['actions'][1]]
        yield f'duplex-{apartment}-infeasible', 0, 'building-derived-controlled', unavailable
        partial = deepcopy(base)
        partial['actions'] = [partial['actions'][3]]
        yield f'duplex-{apartment}-single', 0, 'building-derived-controlled', partial
