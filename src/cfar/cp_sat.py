"""Independent flow optimization on the same recognized strict physical model.

Recognition/geometry are shared with the DP; connectivity and optimization are
not. No owner or purchase vertex is introduced into the route graph.
"""
from collections import defaultdict
from fractions import Fraction
from math import isfinite, lcm, floor
from time import perf_counter

from .actions import apply_actions
from .errors import require
from .geometry import room_index
from .interface_recognition import recognize_physical_interface
from .objective import action_cost
from .obligations import verify_obligations
from .validation import baseline_active


def integer_costs(actions):
    """Scale finite decimal costs without floating point or Decimal rounding."""
    values = [Fraction(str(a["cost"])) for a in actions]
    scale = lcm(*(v.denominator for v in values)) if values else 1
    coefficients = [v.numerator * (scale // v.denominator) for v in values]
    require(all(c >= 0 for c in coefficients) and sum(coefficients) < 2**61,
            "CP_SAT_COST_RANGE", "exact integer cost sum exceeds safe solver range")
    return coefficients, scale


def solve_cp_sat(instance, *, time_limit=60.0, seed=0, progress=None):
    from ortools.sat.python import cp_model
    import ortools

    require(isfinite(time_limit) and time_limit > 0, "CP_SAT_LIMIT", "positive finite seconds required")
    started = perf_counter()
    def emit(event, **fields):
        if progress is not None:
            progress(dict(event=event, elapsed_seconds=perf_counter()-started, **fields))

    emit("recognition_started")
    recognized = recognize_physical_interface(instance)
    emit("recognition_finished")
    model = cp_model.CpModel()
    actions = sorted(instance["actions"], key=lambda a: a["action_id"])
    x = {a["action_id"]: model.new_bool_var("action:" + a["action_id"]) for a in actions}
    for aid in recognized["blocked"]:
        model.add(x[aid] == 0)

    # Full purchased occupancy, including effects unused in any route witness.
    users = defaultdict(list)
    for aid, occupancy in recognized["action_cells"].items():
        for cell, owner in occupancy.items():
            users[owner, cell].append(x[aid])
    by_cell = defaultdict(list)
    for (owner, cell), variables in sorted(users.items()):
        y = model.new_bool_var("usage:" + owner + ":" + cell)
        model.add_max_equality(y, variables)
        by_cell[cell].append(y)
    for variables in by_cell.values():
        model.add(sum(variables) <= 1)

    catalog = {c["connection_id"]: c for c in instance["connections"]}
    baseline = baseline_active(instance)
    rooms = sorted(room_index(instance))
    flow_variables = 0
    for pid, root in sorted(recognized["anchors"].items()):
        targets = {o["target"] for o in instance["obligations"] if o["profile_id"] == pid} - {root}
        demand = len(targets)
        if not demand:
            continue
        suppliers = defaultdict(set)
        for action in actions:
            for effect in action["effects"]:
                if pid in effect["permitted_profiles"]:
                    c = catalog[effect["connection_id"]]
                    suppliers[tuple(sorted((c["u"], c["v"])))].add(action["action_id"])
        fixed = {tuple(sorted((catalog[cid]["u"], catalog[cid]["v"])))
                 for cid, permissions in baseline.items() if pid in permissions}
        balance = defaultdict(list)
        for u, v in sorted(fixed | suppliers.keys()):
            if u == v:
                continue
            if (u, v) in fixed:
                enabled = 1
            else:
                enabled = model.new_bool_var("edge:" + pid + ":" + u + ":" + v)
                model.add_max_equality(enabled, [x[a] for a in sorted(suppliers[u, v])])
            for first, second in ((u, v), (v, u)):
                flow = model.new_int_var(0, demand, "flow:" + pid + ":" + first + ":" + second)
                flow_variables += 1
                model.add(flow <= demand * enabled)
                balance[first].append(flow)
                balance[second].append(-flow)
        for room in rooms:
            supply = demand if room == root else (-1 if room in targets else 0)
            model.add(sum(balance[room]) == supply)

    coefficients, scale = integer_costs(actions)
    cost = sum(c * x[a["action_id"]] for c, a in zip(coefficients, actions))
    count = sum(x.values())
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed
    stages = []
    incumbent = None
    failure_status = None
    cost_lower_bound = None
    first_feasible_seconds = None
    best_cost_seconds = None
    best_observed_cost = None
    cost_proof_seconds = None

    class IncumbentTrace(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            nonlocal first_feasible_seconds, best_cost_seconds, best_observed_cost
            selected = sorted(aid for aid, var in x.items() if self.value(var))
            exact = action_cost(instance, selected)
            now = perf_counter()-started
            if first_feasible_seconds is None:
                first_feasible_seconds = now
            if best_observed_cost is None or exact < best_observed_cost:
                best_observed_cost, best_cost_seconds = exact, now
            emit("incumbent", stage="cost" if not stages else "count" if len(stages)==1 else "identifier",
                 selected=selected, cost=str(exact), replay_verified=False,
                 stage_bound=self.best_objective_bound)

    def optimize(expression, maximize=False):
        nonlocal incumbent, failure_status, cost_lower_bound, cost_proof_seconds
        remaining = time_limit - (perf_counter() - started)
        if remaining <= 0:
            failure_status = "limit_exceeded"
            return False
        solver.parameters.max_time_in_seconds = remaining
        if maximize:
            model.maximize(expression)
        else:
            model.minimize(expression)
        stage = "cost" if not stages else "count" if len(stages)==1 else "identifier"
        emit("stage_started", stage=stage, stage_index=len(stages), remaining_seconds=remaining)
        status = solver.solve(model, IncumbentTrace())
        stages.append(dict(status=solver.status_name(status), wall_seconds=solver.wall_time,
                           branches=solver.num_branches, conflicts=solver.num_conflicts,
                           objective_stage="cost" if not stages else "count" if len(stages)==1 else "identifier",
                           best_bound=solver.best_objective_bound))
        emit("stage_finished", stage_index=len(stages)-1, **stages[-1])
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            incumbent = sorted(aid for aid, var in x.items() if solver.value(var))
        if len(stages) == 1 and status in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.UNKNOWN):
            if status == cp_model.OPTIMAL:
                cost_proof_seconds = perf_counter()-started
            cost_lower_bound = (str(action_cost(instance, incumbent)) if status == cp_model.OPTIMAL
                                else str(Fraction(floor(solver.best_objective_bound), scale))
                                if sum(coefficients) <= 2**53 else None)
        if status != cp_model.OPTIMAL:
            failure_status = ("infeasible" if status == cp_model.INFEASIBLE else
                              "model_invalid" if status == cp_model.MODEL_INVALID else "limit_exceeded")
            return False
        model.add(expression == solver.value(expression))
        # Each stage solves a new model. Explicitly retain the known feasible
        # purchase assignment; CpSolver does not implicitly warm-start solve().
        model.clear_hints()
        for aid, variable in x.items():
            model.add_hint(variable, int(aid in incumbent))
        return True

    # Exact cost, cardinality, then lexicographically smallest sorted ID tuple.
    # With cardinality fixed, prefer inclusion of the earliest available ID.
    done = optimize(cost) and optimize(count)
    if done:
        for aid in sorted(x):
            if aid in recognized["blocked"]:
                continue  # Already fixed to zero, so no identifier decision.
            if not optimize(x[aid], maximize=True):
                done = False
                break
    result = dict(method="strict_flow_cp_sat_v1", status="optimal" if done else failure_status,
                  variant="SCFAR", selected=incumbent if done else None,
                  cost=str(action_cost(instance, incumbent)) if done else None,
                  input_fingerprint=recognized["input_fingerprint"], parameters=recognized["parameters"],
                  statistics=dict(stages=stages, flow_variables=flow_variables, cost_scale=scale,
                                  solver_version=ortools.__version__, workers=1,
                                  stage_hints="previous optimum purchase assignment; no external warm start",
                                  elapsed_seconds=perf_counter()-started),
                  scope=recognized["scope"],
                  optimality_evidence="CP-SAT OPTIMAL at every lexicographic stage; shared geometry recognizer")
    result["best_cost_bound"] = cost_lower_bound
    cost_stage = stages[0] if stages else None
    count_stage = stages[1] if len(stages)>1 else None
    id_stages = stages[2:]
    result["task_status"] = dict(
        cost_stage_status=cost_stage["status"] if cost_stage else "NOT_STARTED",
        cost_incumbent=str(action_cost(instance, incumbent)) if incumbent is not None else None,
        cost_lower_bound=cost_lower_bound,
        cost_stage_seconds=cost_stage["wall_seconds"] if cost_stage else 0,
        count_stage_status=count_stage["status"] if count_stage else "NOT_STARTED",
        count_stage_seconds=count_stage["wall_seconds"] if count_stage else 0,
        id_stage_status=("OPTIMAL" if done else
                         (id_stages[-1]["status"] if id_stages[-1]["status"] != "OPTIMAL" else "INCOMPLETE")
                         if id_stages else "NOT_STARTED"),
        id_stage_seconds=sum(s["wall_seconds"] for s in id_stages),
        full_objective_status=result["status"],
        first_feasible_seconds=first_feasible_seconds,
        best_cost_seconds=best_cost_seconds,
        cost_proof_seconds=cost_proof_seconds)
    if incumbent is not None and result["status"] != "infeasible":
        emit("replay_started", selected=incumbent)
        repair = apply_actions(instance, incumbent)
        verification = verify_obligations(repair["instance"], repair["active"])
        require(verification["satisfied"], "CP_SAT_INTERNAL_REPLAY", "flow selection failed materialization")
        result.update(reachability=verification, geometry=repair["geometry"], adjacency=repair["adjacency"])
        if not done:
            result["incumbent"] = dict(selected=incumbent, cost=str(action_cost(instance, incumbent)))
        emit("replay_finished", selected=incumbent, cost=str(action_cost(instance, incumbent)), replay_verified=True)
    emit("finished", status=result["status"], task_status=result["task_status"])
    return result
