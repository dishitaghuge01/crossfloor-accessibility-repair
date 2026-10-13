"""Replay checker with separate action materialization and union-find reachability.

Shares the schema and geometric predicate kernel; never calls the solver or its BFS.
Optimality is checked by re-enumeration, not by trusting a reported optimum/hash.
"""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, InvalidOperation
from itertools import product

from .errors import ValidationError, require
from .geometry import computed_adjacency, joint_geometry, room_index, validate_floor_geometry
from .io import fingerprint
from .objective import exact_product, exact_sum, validate_topology_weight
from .validation import baseline_active, validate_instance


def _replay(instance: dict, selected: list[str], variant: str, weight: Decimal) -> dict:
    choices = set(selected)
    actions = {a["action_id"]: a for a in instance["actions"]}
    require(len(choices) == len(selected), "DUPLICATE_SELECTION", str(selected))
    require(choices <= actions.keys(), "UNKNOWN_SELECTION", str(choices-actions.keys()))
    repaired = deepcopy(instance)
    active = deepcopy(baseline_active(instance))
    replacements, additions = {}, {}
    for aid in sorted(choices):
        action = actions[aid]
        require(set(action["requires"]) <= choices, "ACTION_REQUIRES", aid)
        require(not choices & set(action["excludes"]), "ACTION_EXCLUDES", aid)
        for effect in action["effects"]:
            if effect["op"] == "replace_floor_rooms":
                require(variant == "RCFAR", "STRICT_GEOMETRY_EDIT", aid)
                fid = effect["floor_id"]
                require(fid not in replacements, "EFFECT_CONFLICT", aid)
                replacements[fid] = effect["rooms"]
            else:
                cid = effect["connection_id"]
                additions[cid] = sorted(set(additions.get(cid, [])) | set(effect["permitted_profiles"]))
    for cid, permitted in additions.items():
        active[cid] = sorted(set(active.get(cid, [])) | set(permitted))
    adjacency = {}
    originals = {f["floor_id"]: f for f in instance["floors"]}
    for floor in repaired["floors"]:
        fid = floor["floor_id"]
        if fid in replacements:
            floor["rooms"] = deepcopy(replacements[fid])
        validate_floor_geometry(floor)
        original = originals[fid]
        require({r["room_id"] for r in floor["rooms"]} == {r["room_id"] for r in original["rooms"]}, "ROOM_IDENTITY", fid)
        before, after = computed_adjacency(original), computed_adjacency(floor)
        require(variant != "SCFAR" or before == after, "STRICT_TOPOLOGY", fid)
        adjacency[fid] = {"preserved": before == after, "delta": len(before ^ after),
                          "edges": [list(p) for p in sorted(after)]}
    geometry = joint_geometry(repaired, active)
    delta = sum(a["delta"] for a in adjacency.values())
    cost = exact_sum(Decimal(str(actions[aid]["cost"])) for aid in sorted(choices))
    if variant == "RCFAR":
        cost = exact_sum([cost,exact_product(weight,Decimal(delta))])
    connections = {c["connection_id"]: c for c in instance["connections"]}
    edges = {p["profile_id"]: set() for p in instance["profiles"]}
    parents = {pid: {rid: rid for rid in room_index(repaired)} for pid in edges}

    def find(parent: dict, node: str) -> str:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for cid, permitted in sorted(active.items()):
        c = connections[cid]
        for pid in permitted:
            edges[pid].add(tuple(sorted((c["u"],c["v"]))))
            parent = parents[pid]
            parent[find(parent,c["u"])] = find(parent,c["v"])
    satisfied = all(find(parents[o["profile_id"]],o["source"]) == find(parents[o["profile_id"]],o["target"])
                    for o in instance["obligations"])
    return {"satisfied": satisfied, "edges": edges, "cost": str(cost), "delta_A": delta,
            "geometry": geometry, "adjacency": adjacency}


def make_certificate(instance: dict, result: dict) -> dict:
    selected = result["selected"]
    original = set(instance["original_restoration_actions"])
    actual = set(selected or [])
    recovery = {"reference_actions": sorted(original),
                "selected_matches_reference": actual == original if selected is not None else None,
                "action_symmetric_difference": len(actual ^ original) if selected is not None else None,
                "interpretation": "action-set agreement only; reference is not assumed optimal"}
    if original:
        try:
            replay = _replay(instance, sorted(original), result["variant"], Decimal(result["topology_weight"]))
            recovery.update(reference_feasible=replay["satisfied"], reference_cost=replay["cost"])
        except ValidationError as error:
            recovery.update(reference_feasible=False, reference_error=error.code)
    return {"certificate_version": "0.1.0", "input_fingerprint": fingerprint(instance),
            "variant": result["variant"], "topology_weight": result["topology_weight"],
            "selected": selected, "cost": result["cost"],
            "reachability_and_preservation": {"reachability": result.get("reachability"),
                                              "adjacency": result.get("adjacency"), "delta_A": result.get("delta_A")},
            "geometric_feasibility": result.get("geometry"), "optimality": result["optimality"],
            "recovery": recovery}


def _verify_certificate(instance: dict, certificate: dict, max_actions: int = 20) -> dict:
    validate_instance(instance)
    require(certificate.get("certificate_version") == "0.1.0", "CERTIFICATE_VERSION", "unsupported")
    require(certificate.get("input_fingerprint") == fingerprint(instance), "CERTIFICATE_INPUT", "fingerprint mismatch")
    variant = certificate["variant"]
    require(variant in {"SCFAR","RCFAR"}, "VARIANT", variant)
    weight = Decimal(certificate["topology_weight"])
    validate_topology_weight(weight)
    ids = sorted(a["action_id"] for a in instance["actions"])
    require(len(ids) <= max_actions, "ACTION_LIMIT", str(len(ids)))
    # Product order is reversed so the independent ledger matches the documented bitmask order.
    ledger, best = [], None
    for bits in product((0,1), repeat=len(ids)):
        selected = [aid for aid, bit in zip(ids, reversed(bits)) if bit]
        record = {"selected": selected}
        try:
            replay = _replay(instance, selected, variant, weight)
            record.update(status="feasible" if replay["satisfied"] else "unsatisfied", cost=replay["cost"])
            key = (Decimal(replay["cost"]),len(selected),tuple(selected))
            if replay["satisfied"] and (best is None or key < best):
                best = key
        except ValidationError as error:
            record.update(status="invalid", error_code=error.code)
        ledger.append(record)
    opt = certificate["optimality"]
    expected = {"method": "complete_action_subset_enumeration", "status": "optimal" if best else "infeasible",
                "subsets": len(ledger), "ledger_fingerprint": fingerprint(ledger),
                "lower_bound": str(best[0]) if best else None,"gap": "0" if best else None}
    require(opt == expected, "CERTIFICATE_OPTIMALITY", "independent enumeration disagrees")
    if best is None:
        require(certificate["selected"] is None and certificate["cost"] is None,
                "CERTIFICATE_INFEASIBLE", "solution claimed for infeasible instance")
        require(certificate["geometric_feasibility"] is None
                and all(v is None for v in certificate["reachability_and_preservation"].values()),
                "CERTIFICATE_INFEASIBLE", "witness supplied for infeasible instance")
    else:
        selected = certificate["selected"]
        require(selected == list(best[2]) and certificate["cost"] == str(best[0]), "CERTIFICATE_SOLUTION", "wrong optimum/tie break")
        replay = _replay(instance, selected, variant, weight)
        evidence = certificate["reachability_and_preservation"]
        require(evidence["adjacency"] == replay["adjacency"] and evidence["delta_A"] == replay["delta_A"],
                "CERTIFICATE_TOPOLOGY", "wrong adjacency evidence")
        require(certificate["geometric_feasibility"] == replay["geometry"], "CERTIFICATE_GEOMETRY", "wrong geometry evidence")
        reachability = evidence["reachability"]
        require(reachability["satisfied"] is True, "CERTIFICATE_PATH", "false satisfaction flag")
        paths = reachability["paths"]
        require(set(paths) == {o["obligation_id"] for o in instance["obligations"]}, "CERTIFICATE_PATH", "missing/extra obligations")
        for o in instance["obligations"]:
            path = paths[o["obligation_id"]]
            require(isinstance(path,list) and bool(path) and path[0] == o["source"] and path[-1] == o["target"]
                    and all(rid in room_index(instance) for rid in path)
                    and all(tuple(sorted((a,b))) in replay["edges"][o["profile_id"]] for a,b in zip(path,path[1:])),
                    "CERTIFICATE_PATH", o["obligation_id"])
    # Reference agreement is checked separately from feasibility/optimality.
    shell = {"selected":certificate["selected"],"cost":certificate["cost"],"variant":variant,
             "topology_weight":str(weight),"optimality":opt}
    require(certificate["recovery"] == make_certificate(instance, shell)["recovery"],
            "CERTIFICATE_RECOVERY", "wrong original-reference evidence")
    return {"valid": True, "status": opt["status"], "independent_subsets": len(ledger),
            "independence_scope": "separate replay and union-find; shared schema/geometry kernel"}


def verify_certificate(instance: dict, certificate: dict, max_actions: int = 20) -> dict:
    try:
        return _verify_certificate(instance,certificate,max_actions)
    except (KeyError,TypeError,AttributeError,InvalidOperation) as error:
        raise ValidationError("CERTIFICATE_FORMAT", "missing or incorrectly typed certificate field") from error
