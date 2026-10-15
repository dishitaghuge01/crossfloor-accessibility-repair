import random
from copy import deepcopy

import pytest

pytest.importorskip("ortools")

from cfar.cp_sat import integer_costs, solve_cp_sat
from cfar.dp_owned_interface import solve_owned_interface
from cfar.errors import ValidationError
from cfar.greedy import solve_greedy
from cfar.interface_scenarios import authored_interface_scenarios, branching_interface_probe
from cfar.oracle import exact_oracle
from cfar.synthetic_shaft import make_shaft_instance


@pytest.mark.parametrize("name", sorted(authored_interface_scenarios()))
def test_flow_matches_oracle_and_dp_on_full_physical_actions(name):
    instance = authored_interface_scenarios()[name]
    oracle, flow = exact_oracle(instance), solve_cp_sat(instance)
    dp = solve_owned_interface(instance, compress=False)
    for result in (flow, dp):
        assert (result["status"], result["cost"], result["selected"]) == (
            oracle["status"], oracle["cost"], oracle["selected"])


@pytest.mark.parametrize("seed", range(20))
def test_seeded_atomic_cost_owner_profile_selection(seed):
    rng = random.Random(seed)
    intervals = [(rng.randrange(3), 2, rng.randint(1, 2)) for _ in range(4)]
    instance = make_shaft_instance(3, intervals, [rng.randint(0, 4)/4 for _ in intervals],
                                  profiles=2, physical=True, asset_groups=[rng.randrange(3) for _ in intervals])
    expected, actual = exact_oracle(instance), solve_cp_sat(instance)
    assert (actual["status"], actual["cost"], actual["selected"]) == (
        expected["status"], expected["cost"], expected["selected"])


def test_cyclic_routes_and_deterministic_identifier_tie_break():
    instance = branching_interface_probe()
    flow, oracle = solve_cp_sat(instance), exact_oracle(instance)
    assert (flow["cost"], flow["selected"]) == (oracle["cost"], oracle["selected"])
    assert all(stage["status"] == "OPTIMAL" for stage in flow["statistics"]["stages"])


def test_cost_scaling_is_exact_and_rejects_solver_overflow():
    coefficients, scale = integer_costs([{"cost": "0.100000000000000001"}])
    assert coefficients[0] * 10**18 == 100000000000000001 * scale
    with pytest.raises(ValidationError, match="CP_SAT_COST_RANGE"):
        integer_costs([{"cost": "1e100"}])


def test_cost_scaling_preserves_small_decimal_difference():
    instance = deepcopy(authored_interface_scenarios()["atomic_bundle"])
    # Costs are arbitrary exact decimals; flow must honor the full objective.
    for i, action in enumerate(instance["actions"]):
        action["cost"] = i/10
    result, oracle = solve_cp_sat(instance), exact_oracle(instance)
    assert (result["cost"], result["selected"]) == (oracle["cost"], oracle["selected"])


def test_limit_is_never_reported_as_optimal_or_infeasible():
    result = solve_cp_sat(branching_interface_probe(), time_limit=1e-12)
    assert result["status"] == "limit_exceeded"
    assert result["selected"] is None


@pytest.mark.parametrize("name", sorted(authored_interface_scenarios()))
def test_greedy_only_returns_replayed_feasibility_or_failure(name):
    result = solve_greedy(authored_interface_scenarios()[name])
    assert result["status"] in {"feasible", "heuristic_failed"}
    if result["status"] == "feasible":
        assert result["reachability"]["satisfied"]
