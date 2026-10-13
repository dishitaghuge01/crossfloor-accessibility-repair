"""Explicit hand-designed cases; not a random/public-data benchmark generator.

Regenerates checked-in examples/micro/*.json and their manually specified answers.
"""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rect(x1, y1, x2, y2):
    return [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]


def room(rid, shape):
    return {"room_id":rid,"label":rid,"polygon":shape}


def landing(rid, shape):
    return {"room_id":rid,"polygon":shape}


def door(i, existing=True, width=1):
    return {"connection_id":f"D{i}","evidence_id":f"eD{i}","u":f"L{i}","v":f"C{i}",
            "kind":"door","physical_profiles":["ambulant","wheelchair"],"existing":existing,
            "geometry":{"width_m":width,"opening":[[4,1],[4,1+width]],
                        "landings":[landing(f"L{i}",rect(3,1,4,2)),landing(f"C{i}",rect(4,1,5,2))]}}


def portal(cid="W", u="C0", v="C1", kind="lift", existing=True, ps=None, footprint=None, asset=None):
    shape = footprint or rect(5,1,7,3)
    x,y = shape[0]
    return {"connection_id":cid,"evidence_id":"e"+cid,"u":u,"v":v,"kind":kind,
            "physical_profiles":ps or ["ambulant","wheelchair"],"existing":existing,
            "geometry":{"asset_id":asset or cid,"width_m":1,"rise_m":3,"run_m":6,
                        "landings":[landing(u,rect(x,y,x+1,y+1)),landing(v,rect(x,y,x+1,y+1))],
                        "footprints":[landing(u,shape),landing(v,shape)]}}


def action(instance, aid, cid, cost=1, requires=None, excludes=None):
    c = next(c for c in instance["connections"] if c["connection_id"] == cid)
    physical = not c["existing"]
    a = {"action_id":aid,"type":"physical_intervention" if physical else "representation_correction",
         "cost":cost,"effects":[{"op":"activate_connection","connection_id":cid,"permitted_profiles":c["physical_profiles"]}],
         "requires":requires or [],"excludes":excludes or [],"evidence_ids":[c["evidence_id"]]}
    if physical:
        a["geometry_certificate"] = {"geometry_model":"reserved_interfaces_2d_v1","connection_ids":[cid],"changed_floor_ids":[]}
    instance["actions"].append(a)
    return a


def activate_portal(instance, cid="W"):
    c = next(c for c in instance["connections"] if c["connection_id"] == cid)
    instance["portals"].append({"portal_id":"P"+cid,"kind":c["kind"],
                                "transitions":[{"connection_id":cid,"permitted_profiles":c["physical_profiles"]}]})


def base(floors=2):
    instance = {"schema_version":"0.1.0","building_id":"unset","description":"unset",
                "profiles":[{"profile_id":"ambulant","min_width_m":0.6,"clearance_m":0.8,"can_use_stairs":True,"max_slope":0.5},
                            {"profile_id":"wheelchair","min_width_m":0.9,"clearance_m":1,"can_use_stairs":False,"max_slope":1/12}],
                "floors":[],"connections":[],"portals":[],"obligations":[],"actions":[],"original_restoration_actions":[]}
    for i in range(floors):
        instance["floors"].append({"floor_id":f"F{i}","elevation_m":3*i,"boundary":rect(0,0,8,4),
                                  "rooms":[room(f"L{i}",rect(0,0,4,4)),room(f"C{i}",rect(4,0,8,4))],
                                  "adjacency_edges":[[f"L{i}",f"C{i}"]],
                                  "access_edges":[{"edge_id":f"E{i}","connection_id":f"D{i}","permitted_profiles":["ambulant","wheelchair"]}],
                                  "obstacles":[],"reserved_portal_zones":[rect(4,0,8,4)]})
        instance["connections"].append(door(i))
    instance["connections"].append(portal())
    instance["obligations"] = [{"obligation_id":"O","source":"L0","target":f"L{floors-1}","profile_id":"wheelchair"}]
    return instance


def remove_door(instance,i):
    instance["floors"][i]["access_edges"] = []


def expected(selected=None,cost=None,delta=0):
    return {"status":"infeasible" if selected is None else "optimal","selected":selected,
            "cost":cost,"delta_A":None if selected is None else delta}


def build():
    cases, answers = {}, {}
    def save(name,description,instance,strict,relaxed=None):
        instance["building_id"],instance["description"] = name,description
        cases[name] = deepcopy(instance)
        answers[name] = {"SCFAR":strict,"RCFAR":relaxed or strict,"topology_weight":"1"}

    b=base(); action(b,"restore_W","W")
    save("01_missing_metadata_link","Existing evidenced lift missing only its model relation.",b,expected(["restore_W"],"1"))

    b=base(); activate_portal(b); remove_door(b,0); b["connections"][0]["existing"]=False; action(b,"add_door","D0",2)
    save("02_missing_door","Physical door through an existing shared wall; A stays fixed.",b,expected(["add_door"],"2"))

    b=base(); b["connections"][-1]=portal(kind="stair",ps=["ambulant"],footprint=rect(5,1,7,7)); activate_portal(b)
    for f in b["floors"]:
        f["boundary"]=rect(0,0,8,8)
        f["rooms"][0]["polygon"]=rect(0,0,4,8)
        f["rooms"][1]["polygon"]=rect(4,0,8,8)
        f["reserved_portal_zones"]=[rect(4,0,8,8)]
    b["obligations"][0]["profile_id"]="ambulant"; remove_door(b,1); action(b,"restore_landing_door","D1")
    save("03_disconnected_stair","Stair exists but the destination landing has no access relation.",b,expected(["restore_landing_door"],"1"))

    b=base(); b["connections"][-1]=portal(ps=["ambulant"],footprint=rect(5,1,6,2)); activate_portal(b)
    b["connections"].append(portal("W2",existing=False,footprint=rect(6.5,2.5,7.5,3.5))); action(b,"add_accessible_lift","W2",4)
    save("04_profile_incompatible_lift","Existing lift unavailable to the requested profile; independent accessible asset can be installed in a reserved zone.",b,expected(["add_accessible_lift"],"4"))

    b=base(); b["connections"][-1]=portal(existing=False,footprint=rect(8.5,1,10.5,3)); action(b,"impossible_lift","W",1)
    save("05_impossible_portal_footprint","Candidate footprint leaves the frozen endpoint room and floor.",b,expected())

    b=base(3); b["connections"][-1]=portal(asset="shared_shaft")
    b["connections"].append(portal("W12",u="C1",v="C2",asset="shared_shaft"))
    a=action(b,"coupled_chain","W",3)
    a["effects"].append({"op":"activate_connection","connection_id":"W12","permitted_profiles":["ambulant","wheelchair"]})
    a["evidence_ids"].append("eW12")
    action(b,"separate_01","W",2); action(b,"separate_12","W12",2)
    save("06_coupled_portal_actions","One charged action restores two transitions of the same evidenced three-storey shaft.",b,expected(["coupled_chain"],"3"))

    b=base(); activate_portal(b); remove_door(b,0)
    b["floors"][0]["rooms"][0]["polygon"]=rect(0,0,3,4); b["floors"][0]["adjacency_edges"]=[]
    d=b["connections"][0]; d["existing"]=False
    d["geometry"]["opening"]=[[3,1],[3,2]]
    d["geometry"]["landings"]=[landing("L0",rect(2,1,3,2)),landing("C0",rect(3,1,4,2))]
    a=action(b,"reshape_and_door","D0",4)
    newrooms=deepcopy(b["floors"][0]["rooms"]); newrooms[1]["polygon"]=rect(3,0,8,4)
    a["effects"].insert(0,{"op":"replace_floor_rooms","floor_id":"F0","rooms":newrooms})
    a["geometry_certificate"]["changed_floor_ids"]=["F0"]
    save("07_strict_vs_relaxed","Gap between rooms forbids strict repair; explicit reshaping changes exactly one adjacency edge.",b,expected(),expected(["reshape_and_door"],"5",1))

    b=base(); action(b,"restore_original","W",5)
    b["connections"].append(portal("W2",existing=False)); action(b,"cheaper_alternative","W2",2)
    b["original_restoration_actions"]=["restore_original"]
    save("08_original_not_optimal","Restoring original BIM connectivity costs five; a feasible alternative costs two.",b,expected(["cheaper_alternative"],"2"))

    b=base(); activate_portal(b)
    save("09_no_repair_needed","All obligations already hold; empty selected set is optimal.",b,expected([],"0"))

    b=base(); b["obligations"]=[]; action(b,"optional_restore","W",1)
    save("10_empty_obligations","Vacuous reachability obligations do not force an edit.",b,expected([],"0"))

    b=base(); remove_door(b,1); action(b,"restore_W","W",1,requires=["restore_D1"]); action(b,"restore_D1","D1",2)
    save("11_action_dependency","Portal action requires the destination connector action; charge both.",b,expected(["restore_D1","restore_W"],"3"))

    b=base(); remove_door(b,0); action(b,"restore_W","W",1,excludes=["restore_D0"]); action(b,"restore_D0","D0",1)
    save("12_mutually_exclusive_actions","Both missing links are necessary but their actions conflict.",b,expected())

    b=base(); b["connections"][-1]["existing"]=False
    b["floors"][0]["obstacles"]=[rect(5.1,1.1,5.4,1.4)]; action(b,"blocked_lift","W")
    save("13_obstructed_portal","Clear landing and footprint are blocked by an explicit obstacle.",b,expected())

    b=base(); activate_portal(b); remove_door(b,0); b["connections"][0]=door(0,existing=False,width=0.7); action(b,"narrow_door","D0",2)
    save("14_insufficient_width","Door fits the wall but is too narrow for the wheelchair profile.",b,expected())

    b=base(); action(b,"a_free_restore","W",0); action(b,"b_free_restore","W",0)
    save("15_zero_cost_tie","Equal free alternatives use a documented cardinality then lexical tie break.",b,expected(["a_free_restore"],"0"))

    b=base(); remove_door(b,0); b["connections"][0]["existing"]=False; action(b,"local_door","D0",2)
    b["obligations"]=[{"obligation_id":"O","source":"L0","target":"C0","profile_id":"wheelchair"}]
    save("16_same_floor_obligation","Building model also supports a purely local obligation without requiring a portal.",b,expected(["local_door"],"2"))

    b=base(); b["connections"][-1]=portal(existing=False,ps=["ambulant"]); action(b,"lift_ambulant","W",1)
    b["connections"].append(portal("W2",existing=False,ps=["wheelchair"])); action(b,"lift_wheelchair","W2",1)
    b["obligations"].append({"obligation_id":"Oa","source":"L0","target":"L1","profile_id":"ambulant"})
    save("17_joint_portal_collision","Two individually feasible profile-specific assets overlap; no joint feasible solution.",b,expected())

    b=base(); b["connections"][-1]=portal(kind="ramp",existing=False); action(b,"steep_ramp","W",2)
    save("18_ramp_slope","Reserved footprint is adequate but rise/run exceeds the requested profile slope.",b,expected())

    folder=ROOT/"examples/micro"; folder.mkdir(parents=True,exist_ok=True)
    for name,instance in cases.items():
        (folder/(name+".json")).write_text(json.dumps(instance,indent=2)+"\n",encoding="utf-8")
    (ROOT/"examples/expected.json").write_text(json.dumps(answers,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return cases,answers


if __name__ == "__main__":
    build()
