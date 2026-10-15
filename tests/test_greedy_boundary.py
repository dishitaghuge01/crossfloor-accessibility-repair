from cfar.greedy import solve_greedy
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.oracle import exact_oracle


def test_greedy_dead_end_does_not_claim_infeasibility():
    instance = authored_interface_scenarios()["shared_asset"]
    instance["actions"] = [a for a in instance["actions"] if a["action_id"] != "A003"]
    oracle = exact_oracle(instance)
    heuristic = solve_greedy(instance)
    assert oracle["status"] == "optimal"
    assert heuristic["status"] == "heuristic_failed"
