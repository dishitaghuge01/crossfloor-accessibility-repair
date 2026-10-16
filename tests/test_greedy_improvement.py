import pytest

from cfar.actions import apply_actions
from cfar.greedy import improve_greedy, solve_greedy
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.objective import action_cost
from cfar.obligations import verify_obligations


@pytest.mark.parametrize("name", sorted(authored_interface_scenarios()))
def test_improvement_preserves_full_feasibility_and_never_worsens(name):
    instance = authored_interface_scenarios()[name]
    old = solve_greedy(instance)
    new = solve_greedy(instance, improve=True, exchange_budget=12)
    assert new["status"] == "feasible"
    repair = apply_actions(instance, new["selected"])
    assert verify_obligations(repair["instance"], repair["active"])["satisfied"]
    assert (action_cost(instance, new["selected"]), len(new["selected"]), new["selected"]) <= (
        action_cost(instance, old["selected"]), len(old["selected"]), old["selected"])
    assert new["statistics"]["exchange_trials"] <= 12
    assert new == solve_greedy(instance, improve=True, exchange_budget=12)


def test_exchange_escapes_feasible_profile_local_choice():
    instance = authored_interface_scenarios()["separate_profiles"]
    assert solve_greedy(instance)["cost"] == "4"
    assert solve_greedy(instance, improve=True)["cost"] == "3"


def test_prune_redundant_actions_even_with_zero_exchange_budget():
    instance = authored_interface_scenarios()["atomic_bundle"]
    selected, stats = improve_greedy(instance, [a["action_id"] for a in instance["actions"]], exchange_budget=0)
    assert len(selected) < len(instance["actions"])
    assert stats["removed_actions"] > 0
    assert stats["exchange_trials"] == 0


def test_failed_construction_stays_heuristic_failure():
    instance = authored_interface_scenarios()["shared_asset"]
    instance["actions"] = [a for a in instance["actions"] if a["action_id"] != "A003"]
    assert solve_greedy(instance, improve=True)["status"] == "heuristic_failed"


@pytest.mark.parametrize("budget", [-1, 1.5, True])
def test_invalid_budget_rejected(budget):
    with pytest.raises(ValueError, match="exchange_budget"):
        improve_greedy(authored_interface_scenarios()["atomic_bundle"], [], exchange_budget=budget)
