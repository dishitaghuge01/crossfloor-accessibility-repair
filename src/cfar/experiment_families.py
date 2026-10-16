"""Fixed, seeded structural probes; no building or construction interpretation."""
from copy import deepcopy
from itertools import combinations
from random import Random

from .interface_scenarios import dense_alternative_probe, coupled_owner_probe, branching_rooms_probe
from .synthetic_shaft import make_shaft_instance


def integrated_example():
    """Three floors, two profiles, disconnected paid geometry and owner reuse."""
    from .interface_scenarios import authored_interface_scenarios
    from .synthetic_star import rectangle
    from .geometry import computed_adjacency
    a = authored_interface_scenarios()['shared_asset']
    pids=['profile0','profile1']
    a['profiles'].append(dict(a['profiles'][0],profile_id=pids[1]))
    for f in a['floors']:
        index=int(f['floor_id'][1:])
        f['boundary']=rectangle(0,0,8,4)
        f['reserved_portal_zones']=[deepcopy(f['boundary'])]
        f['rooms'].append(dict(room_id=f'U{index}',label='annex',polygon=rectangle(4,0,8,4)))
        f['adjacency_edges']=[list(e) for e in sorted(computed_adjacency(f))]
    for c in a['connections']:c['physical_profiles']=pids[:]
    for action in a['actions']:
        for effect in action['effects']:effect['permitted_profiles']=pids[:]
    def edge(cid,u,v,owner,shape):
        records=[dict(room_id=r,polygon=deepcopy(shape)) for r in (u,v)]
        return dict(connection_id=cid,evidence_id='e'+cid,u=u,v=v,kind='lift',existing=False,
                    physical_profiles=pids[:],geometry=dict(asset_id=owner,width_m=1,rise_m=3,run_m=1,landings=records,footprints=records))
    spare=edge('SPARE','U0','U1','spare-owner',rectangle(5,.5,6,1.5))
    rival=edge('RIVAL','U1','U2','rival-owner',rectangle(5,.5,6,1.5))
    useful=edge('USEFUL','R1','R2','useful-owner',rectangle(2.5,.5,3.5,1.5))
    a['connections'] += [spare,rival,useful]
    def add_effect(action,cid):
        action['effects'].append(dict(op='activate_connection',connection_id=cid,permitted_profiles=pids[:]))
        action['evidence_ids'].append('e'+cid)
        action['geometry_certificate']['connection_ids'].append(cid)
    add_effect(a['actions'][0],'SPARE')
    rival_action=deepcopy(a['actions'][0])
    rival_action.update(action_id='E',cost=.5,effects=[],evidence_ids=[])
    rival_action['geometry_certificate']['connection_ids']=[]
    for cid in ['RIVAL','USEFUL']:add_effect(rival_action,cid)
    a['actions'].append(rival_action)
    a['obligations'].append(dict(a['obligations'][0],obligation_id='O1',profile_id=pids[1]))
    a['building_id']='integrated-owned-interface-example'
    return a


def generate_instance(family, size, seed=0, settings=None):
    settings = settings or {}
    rng = Random(seed)
    if family == "catalogue":
        instance = dense_alternative_probe(size)
    elif family == "ownership":
        instance = coupled_owner_probe(size)
    elif family == "profiles":
        instance = make_shaft_instance(2, [(0, 1, size)], [1], profiles=size,
                                       physical=True, asset_groups=[0])
    elif family == "support":
        instance = make_shaft_instance(size-1, [(0, size-2, 1)], [1], profiles=1,
                                       physical=True, asset_groups=[0])
    elif family == "connectivity":
        if size < 2:
            raise ValueError("at least two floors")
        instance = make_shaft_instance(size-1, [(0, size-2, 1)], [1], profiles=1,
                                       physical=True, asset_groups=[0])
        template = instance["connections"][0]
        connections, actions = [], []
        pairs = list(combinations(range(size), 2)) if family == "connectivity" else [(0, size-1)]
        for i, (u, v) in enumerate(pairs):
            c = deepcopy(template)
            cid = f"E{i:03d}"
            c.update(connection_id=cid, evidence_id="e"+cid, u=f"R{u}", v=f"R{v}")
            c["geometry"]["rise_m"] = 3*(v-u)
            # Abstract long edges use the represented endpoint-only kernel.
            # The support family instead purchases every consecutive segment.
            c["geometry"]["landings"] = [dict(room_id=f"R{j}", polygon=deepcopy(template["geometry"]["landings"][0]["polygon"])) for j in (u,v)]
            c["geometry"]["footprints"] = deepcopy(c["geometry"]["landings"])
            connections.append(c)
            a = deepcopy(instance["actions"][0])
            a.update(action_id=f"A{i:03d}", cost=rng.randint(1, 5), evidence_ids=["e"+cid],
                     effects=[dict(op="activate_connection", connection_id=cid, permitted_profiles=["profile0"])])
            a["geometry_certificate"]["connection_ids"] = [cid]
            actions.append(a)
        instance.update(connections=connections, actions=actions)
    elif family == "rooms":
        instance = branching_rooms_probe()
        # Deliberately irrelevant real geometry for the safe-pruning ablation.
        for floor in instance["floors"]:
            from .synthetic_star import rectangle
            floor["boundary"] = rectangle(0, 0, 4+size, 4)
            for i in range(size):
                floor["rooms"].append(dict(room_id=f"extra-{floor['floor_id']}-{i}", label="isolated", polygon=rectangle(4+i, 0, 5+i, 4)))
            from .geometry import computed_adjacency
            floor["adjacency_edges"] = [list(e) for e in sorted(computed_adjacency(floor))]
    else:
        raise ValueError("unknown experiment family: " + family)
    instance["building_id"] = f"controlled-{family}-{size}-seed{seed}"
    instance["description"] = f"Authored structural experiment; family={family}; size={size}; seed={seed}; settings={settings}. Abstract costs, no construction claim."
    return instance
