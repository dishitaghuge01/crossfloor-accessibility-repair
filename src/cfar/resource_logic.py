"""Exact owner-cell usage graph for a fixed neighborhood-logic baseline.

No generic metatheorem solver is implemented. Evaluation uses separate graph
traversal and cell-neighbor counts; physical recognition is shared.
"""
from fractions import Fraction
from math import prod

from .errors import require
from .interface_recognition import recognize_physical_interface
from .io import canonical, fingerprint
from .validation import baseline_active


def compile_resource_logic(instance: dict) -> dict:
    recognition = recognize_physical_interface(instance)
    graph, kinds = {}, {}

    def add(name,kind):
        graph.setdefault(name,set())
        kinds[name] = kind

    def edge(u,v):
        graph[u].add(v)
        graph[v].add(u)

    add("hub","hub")
    vertices, anchors, targets, baseline = {}, set(), set(), set()
    for pid, components in recognition["components"].items():
        for rid, component in components.items():
            vid = "vertex:"+canonical([pid,component])
            vertices[(pid,rid)] = vid
            add(vid,"vertex")
        root = vertices[(pid,recognition["anchors"][pid])]
        anchors.add(root)
        edge("hub",root)
    for obligation in instance["obligations"]:
        targets.add(vertices[(obligation["profile_id"],obligation["target"])])
    for c in recognition["cells"]:
        add("cell:"+c["cell_id"],"cell")
    for aid, occupancy in recognition["action_cells"].items():
        action = "action:"+aid
        add(action,"action")
        for cid,owner in occupancy.items():
            usage = "usage:"+canonical([owner,cid])
            add(usage,"usage")
            edge(action,usage)
            edge(usage,"cell:"+cid)
    catalog = {c["connection_id"]: c for c in instance["connections"]}
    occurrences = []

    def occurrence(cid,pid,supplier=None):
        c = catalog[cid]
        u,v = vertices[(pid,c["u"])],vertices[(pid,c["v"])]
        if u == v:
            return
        oid = f"occurrence:{len(occurrences)}"
        occurrences.append(oid)
        add(oid,"occurrence")
        edge(oid,u)
        edge(oid,v)
        if supplier is None:
            baseline.add(oid)
        else:
            edge(oid,"action:"+supplier)

    for cid, permitted in baseline_active(instance).items():
        for pid in permitted:
            occurrence(cid,pid)
    actions = {a["action_id"]: a for a in instance["actions"]}
    ordered = sorted(actions)
    rational = {aid: Fraction(str(actions[aid]["cost"])) for aid in ordered}
    denominator = prod(c.denominator for c in rational.values())
    K = len(ordered)
    Q = K*(1 << K)+1
    integer_weights = {aid: int(rational[aid]*denominator)*(K+1)*Q + Q + ((1 << K)-(1 << (K-i-1)))
                       for i,aid in enumerate(ordered)}
    for aid in recognition["action_cells"]:
        for effect in actions[aid]["effects"]:
            for pid in effect["permitted_profiles"]:
                occurrence(effect["connection_id"],pid,aid)
    return dict(format="owner_cell_resource_logic_v1",input_fingerprint=fingerprint(instance),
                adjacency={v:sorted(neighbors) for v,neighbors in sorted(graph.items())},
                kinds=kinds,targets=sorted(targets),anchors=sorted(anchors),baseline=sorted(baseline),
                action_ids=sorted(actions),blocked=sorted(recognition["blocked"]),
                action_integer_weights=integer_weights,cost_scale=denominator,
                parameters=recognition["parameters"],
                scope="recognized M09 class; exact usage-graph evaluator, not a generic logic optimizer")


def evaluate_resource_logic(compiled: dict, selected: list[str]) -> dict:
    require(len(selected) == len(set(selected)),"DUPLICATE_SELECTION",str(selected))
    require(set(selected) <= set(compiled["action_ids"]),"UNKNOWN_SELECTION",str(selected))
    graph, kinds = compiled["adjacency"],compiled["kinds"]
    if set(selected) & set(compiled["blocked"]):
        return dict(admissible=False,satisfied=False,reason="unary_blocked")
    X = {"action:"+aid for aid in selected}
    neighbor = {v for x in X for v in graph[x]}
    Z = {v for v in neighbor if kinds[v] == "usage"}
    collisions = [v for v in graph if kinds[v] == "cell" and len(set(graph[v]) & Z) > 1]
    active_occurrences = set(compiled["baseline"]) | {v for v in neighbor if kinds[v] == "occurrence"}
    allowed = {v for v in graph if kinds[v] in {"vertex","hub"}} | active_occurrences
    reached, pending = {"hub"}, ["hub"]
    while pending:
        for v in graph[pending.pop()]:
            if v in allowed and v not in reached:
                reached.add(v)
                pending.append(v)
    reachable = set(compiled["targets"]) <= reached
    return dict(admissible=not collisions,satisfied=not collisions and reachable,
                reachable=reachable,collision_cells=sorted(collisions),
                selected_usages=sorted(Z),witness_vertices=sorted(reached),
                maximization_reward=sum(w for aid,w in compiled["action_integer_weights"].items() if aid not in selected))
