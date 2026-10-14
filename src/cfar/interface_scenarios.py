"""Authored physical interface proof probes, not public-building evidence."""
from copy import deepcopy
from itertools import combinations

from .synthetic_shaft import make_shaft_instance
from .synthetic_star import rectangle


def _bundle(instance: dict, first: int, second: int) -> None:
    actions = instance["actions"]
    a, b = actions[first], actions[second]
    a["effects"].extend(deepcopy(b["effects"]))
    a["evidence_ids"].extend(b["evidence_ids"])
    a["geometry_certificate"]["connection_ids"].extend(b["geometry_certificate"]["connection_ids"])
    del actions[second]


def authored_interface_scenarios() -> dict[str, dict]:
    """Return fresh inputs with all endpoints, footprints and evidence records."""
    shared = make_shaft_instance(3, [(0,1,1),(1,2,1),(0,1,1),(0,2,1)],
                                 [4,1,1,10], profiles=1, physical=True, asset_groups=[0,0,4,1])
    partial = make_shaft_instance(2, [(0,0,1),(1,1,1),(0,1,1)], [1,1,3],
                                  profiles=1, physical=True, asset_groups=[0,1,2])
    shapes = {"asset-group-0": rectangle(.5,.5,1.5,1.5),
              "asset-group-1": rectangle(1.5,.5,2.5,1.5),
              "asset-group-2": rectangle(1,.5,2,1.5)}
    for connection in partial["connections"]:
        shape = shapes[connection["geometry"]["asset_id"]]
        for field in ("landings", "footprints"):
            for record in connection["geometry"][field]:
                record["polygon"] = deepcopy(shape)
    bundle = make_shaft_instance(2, [(0,0,1),(1,1,1),(0,0,1),(1,1,1)],
                                 [3,0,2,2], profiles=1, physical=True, asset_groups=[0,1,0,1])
    _bundle(bundle, 0, 1)
    unused = make_shaft_instance(3, [(0,0,1),(2,2,1),(1,1,1),(1,1,1)],
                                 [1,0,1,5], profiles=1, physical=True, asset_groups=[0,1,5,3])
    _bundle(unused, 0, 1)
    unused["obligations"][0]["target"] = "R2"
    profiles = make_shaft_instance(1, [(0,0,1),(0,0,2)], [1,3],
                                   profiles=2, physical=True, asset_groups=[0,0])
    cases = dict(shared_asset=shared, partial_footprints=partial, atomic_bundle=bundle,
                 unused_paid_geometry=unused, separate_profiles=profiles)
    for name, instance in cases.items():
        instance["building_id"] = "authored-interface-" + name
        instance["description"] = ("Authored strict interface proof probe: " + name +
                                   "; fixed 2D geometry only, no public BIM or construction claim.")
    return cases


EXPECTED_OPTIMA = {
    "shared_asset": ("5", ["A000", "A001"]),
    "partial_footprints": ("2", ["A000", "A001"]),
    "atomic_bundle": ("3", ["A000"]),
    "unused_paid_geometry": ("6", ["A000", "A003"]),
    "separate_profiles": ("3", ["A001"]),
}


def branching_interface_probe() -> dict:
    """Four-level cyclic effect graph sharing a fixed experimental asset."""
    instance = make_shaft_instance(3, [(0,2,1)], [1], profiles=1, physical=True, asset_groups=[0])
    template = instance["connections"][0]
    connections, actions = [], []
    for i, (u,v) in enumerate(combinations(range(4),2)):
        c = deepcopy(template)
        cid = f"E{i}"
        c.update(connection_id=cid, evidence_id="e"+cid, u=f"R{u}", v=f"R{v}")
        c["geometry"]["rise_m"] = 3*(v-u)
        for field in ("landings", "footprints"):
            for record, floor in zip(c["geometry"][field], (u,v)):
                record["room_id"] = f"R{floor}"
        connections.append(c)
        a = deepcopy(instance["actions"][0])
        a.update(action_id=f"A{i:03d}", evidence_ids=["e"+cid],
                 effects=[dict(op="activate_connection",connection_id=cid,permitted_profiles=["profile0"])])
        a["geometry_certificate"]["connection_ids"] = [cid]
        actions.append(a)
    instance.update(building_id="authored-cyclic-interface", connections=connections, actions=actions,
                    description="Authored cyclic access-graph compression probe; fixed 2D model, not construction evidence.")
    return instance


def dense_alternative_probe(count: int = 64) -> dict:
    """Private colliding alternatives with an analytically known optimum."""
    if type(count) is not int or count < 1:
        raise ValueError("positive alternative count required")
    instance = make_shaft_instance(1,[(0,0,1)],[1],profiles=1,physical=True,asset_groups=[0])
    template_c, template_a = instance["connections"][0], instance["actions"][0]
    connections, actions = [], []
    for i in range(count):
        cid = f"alternative{i}"
        c, a = deepcopy(template_c), deepcopy(template_a)
        c.update(connection_id=cid,evidence_id="e"+cid)
        c["geometry"]["asset_id"] = f"private-asset-{i}"
        a.update(action_id=f"A{i:04d}",cost=1+i%7,evidence_ids=["e"+cid],
                 effects=[dict(op="activate_connection",connection_id=cid,permitted_profiles=["profile0"])])
        a["geometry_certificate"]["connection_ids"] = [cid]
        connections.append(c)
        actions.append(a)
    instance.update(building_id=f"authored-dense-alternatives-{count}",connections=connections,actions=actions,
                    description="Authored density/state probe; known optimum cost one, not public-building evidence.")
    return instance
