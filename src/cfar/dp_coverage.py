"""Exact coverage DP for the recognized single-profile contracted-star subclass.

Not a solver for arbitrary portal interfaces. See docs/complexity_memo.md.
"""
from __future__ import annotations

from decimal import Decimal

from .actions import apply_actions
from .errors import require
from .geometry import room_index
from .graphs import build_profile_graph
from .obligations import verify_obligations
from .objective import exact_sum
from .validation import baseline_active, validate_instance


def recognize_bundle_star(instance: dict) -> dict:
    validate_instance(instance)
    require(len(instance["profiles"]) == 1, "STAR_SCOPE", "exactly one profile required")
    pid = instance["profiles"][0]["profile_id"]
    require(bool(instance["obligations"]), "STAR_SCOPE", "at least one obligation required")
    graph = build_profile_graph(instance,pid)
    components, component_of = [], {}
    for root in sorted(graph):
        if root in component_of:
            continue
        unseen=[root]; component=set()
        while unseen:
            u=unseen.pop()
            if u in component:
                continue
            component.add(u)
            unseen.extend(graph[u]-component)
        index=len(components)
        components.append(component)
        for u in component:
            component_of[u]=index
    root_component=component_of[instance["obligations"][0]["source"]]
    require(all(component_of[o["source"]] == root_component for o in instance["obligations"]),
            "STAR_SCOPE", "all sources must lie in one baseline component")
    terminals=sorted({component_of[o["target"]] for o in instance["obligations"]}-{root_component})
    bits={component:1<<i for i,component in enumerate(terminals)}
    connections={c["connection_id"]:c for c in instance["connections"]}
    masks={}
    for a in sorted(instance["actions"],key=lambda a:a["action_id"]):
        require(a["type"] == "representation_correction" and not a["requires"] and not a["excludes"],
                "STAR_SCOPE", "only independent evidenced corrections supported")
        mask=0
        for e in a["effects"]:
            require(e["op"] == "activate_connection" and e["permitted_profiles"] == [pid],
                    "STAR_SCOPE", "only same-profile activations supported")
            c=connections[e["connection_id"]]
            cu,cv=component_of[c["u"]],component_of[c["v"]]
            require(cu == cv or root_component in {cu,cv}, "STAR_SCOPE", "non-star candidate link")
            if cu != cv:
                mask |= bits.get(cv if cu == root_component else cu,0)
        # Full union precheck below guarantees that selecting individually valid evidence is jointly safe.
        masks[a["action_id"]]=mask
    apply_actions(instance,list(masks),"SCFAR",validated=True)
    return {"profile_id":pid,"terminal_components":terminals,"coverage_masks":masks,
            "full_mask":(1<<len(terminals))-1,"components":components}


def solve_bundle_star(instance: dict, max_terminals: int = 22) -> dict:
    recognized=recognize_bundle_star(instance)
    m=len(recognized["terminal_components"])
    require(m <= max_terminals,"TERMINAL_LIMIT",f"{m} > {max_terminals}")
    costs={a["action_id"]:Decimal(str(a["cost"])) for a in instance["actions"]}
    # Value stores (cost, cardinality, lexical IDs) for the same tie rule as the oracle.
    states={0:(Decimal(0),0,())}
    transitions=0
    for aid,coverage in recognized["coverage_masks"].items():
        updated=dict(states)
        for mask,key in states.items():
            transitions+=1
            nxt=mask|coverage
            candidate=(exact_sum([key[0],costs[aid]]),key[1]+1,key[2]+(aid,))
            if nxt not in updated or candidate < updated[nxt]:
                updated[nxt]=candidate
        states=updated
    best=states.get(recognized["full_mask"])
    if best is not None:
        repair=apply_actions(instance,list(best[2]),validated=True)
        require(verify_obligations(instance,repair["active"])["satisfied"],"DP_POSTCHECK","reachability disagrees")
    return {"status":"optimal" if best else "infeasible","variant":"SCFAR",
            "method":"contracted_star_coverage_dp","cost":str(best[0]) if best else None,
            "selected":list(best[2]) if best else None,"terminal_components":m,
            "states":len(states),"transitions":transitions,
            "guarantee_scope":"single-profile independent representation corrections with a jointly feasible contracted star"}
