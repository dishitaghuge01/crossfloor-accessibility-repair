"""Rooted physical-interface DP with full occupancy and thin route witnesses.

Working M09/M14 implementation; rank machinery is established prior work.
"""
from collections import defaultdict
from decimal import Decimal
from itertools import product
from time import perf_counter

from .actions import apply_actions
from .errors import require
from .geometry import room_index
from .interface_recognition import recognize_physical_interface
from .objective import exact_sum
from .obligations import verify_obligations
from .representative_partitions import representative_indices
from .validation import baseline_active


def _glue(partition, vertices):
    merged = set(vertices)
    untouched = []
    for block in partition:
        if merged.intersection(block):
            merged.update(block)
        else:
            untouched.append(block)
    return tuple(sorted(untouched + [tuple(sorted(merged))]))


def _components(edges):
    partition = ()
    for u, v in edges:
        if u != v:
            partition = _glue(partition, (u,v))
    return partition


def solve_owned_interface(instance: dict, *, compress: bool = True,
                          max_states: int = 100000, max_cut_columns: int = 65536,
                          prune_irrelevant: bool = False, profile: bool = False,
                          recognized_cache: dict | None = None) -> dict:
    started = perf_counter()
    require(type(max_states) is int and max_states > 0 and type(max_cut_columns) is int
            and max_cut_columns > 0, "INTERFACE_LIMIT", "positive integer limits required")
    if recognized_cache is not None:
        from .io import fingerprint
        require(recognized_cache["input_fingerprint"] == fingerprint(instance)
                and recognized_cache["prune_irrelevant"] == prune_irrelevant,
                "INTERFACE_CACHE", "cache must match input and pruning setting")
        recognized = recognized_cache
    else:
        recognized = recognize_physical_interface(instance, prune_irrelevant=prune_irrelevant, profile=profile)
    recognition_done = perf_counter()
    pids = sorted(recognized["components"])
    floors = recognized["floor_order"]
    ranks = {fid: i for i, fid in enumerate(floors)}
    rooms = room_index(instance)
    room_floor = {rid: f["floor_id"] for rid, (f, _) in rooms.items()}
    node = lambda pid, rid: "v:" + recognized["components"][pid][rid]
    node_floor = [{node(pid,rid): room_floor[rid] for rid in recognized["components"][pid]} for pid in pids]
    targets = [{node(pid,o["target"]) for o in instance["obligations"] if o["profile_id"] == pid}
               for pid in pids]
    roots = [node(pid,recognized["anchors"][pid]) for pid in pids]
    cells = {c["cell_id"]: c for c in recognized["cells"]}
    actions = {a["action_id"]: a for a in instance["actions"]}
    catalog = {c["connection_id"]: c for c in instance["connections"]}
    units = defaultdict(list)
    for unit in recognized["units"]:
        units[unit["first_floor"]].append(unit)
    baseline_events = defaultdict(list)
    for cid, permitted in baseline_active(instance).items():
        c = catalog[cid]
        for q, pid in enumerate(pids):
            if pid in permitted:
                if c["u"] not in recognized["components"][pid]:
                    continue
                u, v = node(pid,c["u"]), node(pid,c["v"])
                if u != v:
                    baseline_events[min(ranks[room_floor[c["u"]]], ranks[room_floor[c["v"]]])].append((q,u,v))
    effect_components = {}
    for aid in recognized["action_cells"]:
        layers = []
        for pid in pids:
            edges = []
            for effect in actions[aid]["effects"]:
                if pid in effect["permitted_profiles"]:
                    c = catalog[effect["connection_id"]]
                    edges.append((node(pid,c["u"]), node(pid,c["v"])))
            layers.append(_components(edges))
        effect_components[aid] = layers
    schedule_done = perf_counter()
    # Label order is exact cost, original count, then sorted original IDs.
    states = {((), tuple((("anchor",),) for _ in pids)): (Decimal(0),0,())}
    stats = dict(events=0, peak_raw_states=1, peak_retained_states=1, representative_rows_removed=0)
    if profile:
        stats.update(total_deduplicated_rows=0, representative_reduction_seconds=0.0)

    def retain(generated):
        nonlocal states
        deduplicated = {}
        for key, label in generated:
            if key not in deduplicated or label < deduplicated[key]:
                deduplicated[key] = label
            require(len(deduplicated) <= max_states, "INTERFACE_STATE_LIMIT", str(max_states))
        stats["events"] += 1
        reduction_started = perf_counter()
        if profile:
            stats["total_deduplicated_rows"] += len(deduplicated)
        stats["peak_raw_states"] = max(stats["peak_raw_states"], len(deduplicated))
        if not compress:
            states = deduplicated
        else:
            groups = defaultdict(list)
            for key, label in deduplicated.items():
                occupancy, partitions = key
                boundary = tuple(tuple(sorted(v for block in pi for v in block if v != "anchor"))
                                 for pi in partitions)
                groups[(occupancy,boundary)].append((key,label))
            states = {}
            for (_, boundary), records in groups.items():
                columns = 1 << sum(len(vs) for vs in boundary)
                require(columns <= max_cut_columns, "INTERFACE_CUT_LIMIT", str(columns))
                rows = []
                for (_, partitions), _label in records:
                    tuple_row = []
                    for pi, vs in zip(partitions,boundary):
                        blocks = {v: b for b, block in enumerate(pi) for v in block}
                        tuple_row.append(tuple(blocks[v] for v in ("anchor",)+vs))
                    rows.append(tuple(tuple_row))
                kept = representative_indices(rows, [label for _,label in records])
                stats["representative_rows_removed"] += len(records)-len(kept)
                for index in kept:
                    key, label = records[index]
                    states[key] = label
        stats["peak_retained_states"] = max(stats["peak_retained_states"], len(states))
        if profile and compress:
            stats["representative_reduction_seconds"] += perf_counter()-reduction_started

    def introduce(fid):
        def generated():
            for (occupancy, partitions), label in states.items():
                updated = list(partitions)
                for q in range(len(pids)):
                    for vertex in sorted(targets[q]):
                        if node_floor[q][vertex] == fid:
                            updated[q] = _glue(updated[q], (vertex,))
                    if node_floor[q][roots[q]] == fid:
                        updated[q] = _glue(updated[q], ("anchor",roots[q]))
                yield (occupancy,tuple(updated)), label
        retain(generated())

    L = recognized["parameters"]["L"]
    for fid in floors[:L]:
        introduce(fid)
    for f, fid in enumerate(floors):
        for q, u, v in baseline_events[f]:
            def baseline_generated():
                for (occupancy, partitions), label in states.items():
                    yield (occupancy,partitions), label
                    updated = list(partitions)
                    updated[q] = _glue(updated[q], (u,v))
                    yield (occupancy,tuple(updated)), label
            retain(baseline_generated())
        for unit in units[f]:
            for aid in unit["action_ids"]:
                action = actions[aid]
                layer_choices = [[tuple(component for i,component in enumerate(layer) if mask & (1 << i))
                                  for mask in range(1 << len(layer))] for layer in effect_components[aid]]

                def action_generated():
                    for (occupancy, partitions), label in states.items():
                        yield (occupancy,partitions), label
                        occupied = dict(occupancy)
                        valid = True
                        for cid, owner in recognized["action_cells"][aid].items():
                            token = "owner:"+owner
                            if cid in occupied and occupied[cid] != token:
                                valid = False
                                break
                            occupied[cid] = token
                        if not valid:
                            continue
                        new_label = (exact_sum([label[0],Decimal(str(action["cost"]))]), label[1]+1,
                                     tuple(sorted(label[2]+(aid,))))
                        for witness in product(*layer_choices):
                            updated = list(partitions)
                            for q, selected in enumerate(witness):
                                for component in selected:
                                    updated[q] = _glue(updated[q], component)
                            yield (tuple(sorted(occupied.items())),tuple(updated)), new_label
                retain(action_generated())
            retain((((tuple((cid,"external") for cid,_owner in occupancy), partitions),label)
                    for (occupancy,partitions),label in states.items()))
        def forget_generated():
            for (occupancy, partitions), label in states.items():
                updated = []
                valid = True
                for q, pi in enumerate(partitions):
                    layer = []
                    for block in pi:
                        remaining = tuple(v for v in block if v == "anchor" or node_floor[q][v] != fid)
                        if not remaining:
                            valid = False
                            break
                        layer.append(remaining)
                    if not valid:
                        break
                    updated.append(tuple(sorted(layer)))
                if valid:
                    live = tuple((cid,owner) for cid,owner in occupancy if cells[cid]["floor_id"] != fid)
                    yield (live,tuple(updated)), label
        retain(forget_generated())
        if f+L < len(floors):
            introduce(floors[f+L])
    optimized = perf_counter()
    best = min(states.values(), default=None)
    result = dict(method="owned_cell_rooted_interface_dp_v1", status="optimal" if best else "infeasible",
                  variant="SCFAR", cost=str(best[0]) if best else None,
                  selected=list(best[2]) if best else None, parameters=recognized["parameters"],
                  input_fingerprint=recognized["input_fingerprint"], statistics=stats,
                  compression=compress,
                  optimality_evidence="complete scoped DP; independent oracle comparison required",
                  scope=recognized["scope"])
    reconstructed = perf_counter()
    if best:
        repair = apply_actions(instance, result["selected"])
        verification = verify_obligations(repair["instance"],repair["active"])
        require(verification["satisfied"], "INTERFACE_INTERNAL_REPLAY", "witness failed materialization")
        result.update(reachability=verification, geometry=repair["geometry"], adjacency=repair["adjacency"])
    if profile:
        result["phase_seconds"] = dict(recognition=recognition_done-started,
            event_construction=schedule_done-recognition_done, optimization=optimized-schedule_done,
            solution_reconstruction=reconstructed-optimized, materialization_replay=perf_counter()-reconstructed)
        result["recognition_phase_seconds"] = recognized.get("phase_seconds") if recognized_cache is None else None
        result["recognition_operation_counts"] = recognized.get("operation_counts")
        result["recognition_cached"] = recognized_cache is not None
    return result
