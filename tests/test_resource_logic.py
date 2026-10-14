import pytest

from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_scenarios import authored_interface_scenarios, coupled_owner_probe, branching_rooms_probe
from cfar.oracle import exact_oracle
from cfar.resource_logic import compile_resource_logic, evaluate_resource_logic


@pytest.mark.parametrize("name", sorted(authored_interface_scenarios()))
def test_usage_formula_matches_every_oracle_selection(name):
    instance = authored_interface_scenarios()[name]
    compiled, oracle = compile_resource_logic(instance),exact_oracle(instance)
    for row in oracle["ledger"]:
        result = evaluate_resource_logic(compiled,row["selected"])
        assert result["admissible"] == (row["status"] != "invalid")
        assert result["satisfied"] == (row["status"] == "feasible")


@pytest.mark.parametrize("owners", [2,3,4])
def test_genuine_within_unit_competition_matches_oracle(owners):
    instance = coupled_owner_probe(owners)
    oracle, dp = exact_oracle(instance),solve_owned_interface(instance)
    assert (oracle["cost"],oracle["selected"]) == ("2",["L000","M000"])
    assert (dp["cost"],dp["selected"]) == (oracle["cost"],oracle["selected"])
    assert dp["parameters"] == dict(p=1,r=1,z=2,L=4,g=owners+1,h=owners)
    compiled = compile_resource_logic(instance)
    for row in oracle["ledger"]:
        result = evaluate_resource_logic(compiled,row["selected"])
        assert result["admissible"] == (row["status"] != "invalid")
        assert result["satisfied"] == (row["status"] == "feasible")


def test_one_asset_does_not_enable_unselected_effect_floors():
    compiled = compile_resource_logic(authored_interface_scenarios()["shared_asset"])
    left = evaluate_resource_logic(compiled,["A000"])
    both = evaluate_resource_logic(compiled,["A000","A001"])
    assert set(left["selected_usages"]) < set(both["selected_usages"])
    assert not left["satisfied"] and both["satisfied"]


def test_paid_disconnected_bundle_does_not_create_a_purchase_vertex_shortcut():
    compiled = compile_resource_logic(authored_interface_scenarios()["unused_paid_geometry"])
    result = evaluate_resource_logic(compiled,["A000"])
    assert not result["reachable"]
    assert len(result["selected_usages"]) == 4


def test_multiple_rooms_and_profile_specific_baseline_contractions():
    from cfar.interface_recognition import recognize_physical_interface

    instance = branching_rooms_probe()
    recognized = recognize_physical_interface(instance)
    assert recognized["parameters"] == dict(p=2,r=3,z=2,L=2,g=2,h=1)
    assert recognized["components"]["controlled0"]["C"] == recognized["components"]["controlled0"]["T0"]
    assert recognized["components"]["controlled1"]["C"] != recognized["components"]["controlled1"]["T0"]
    oracle = exact_oracle(instance)
    assert (oracle["cost"],oracle["selected"]) == ("3",["A"])
    for compressed in (True,False):
        result = solve_owned_interface(instance,compress=compressed)
        assert (result["cost"],result["selected"]) == ("3",["A"])
    compiled = compile_resource_logic(instance)
    for row in oracle["ledger"]:
        result = evaluate_resource_logic(compiled,row["selected"])
        assert result["admissible"] == (row["status"] != "invalid")
        assert result["satisfied"] == (row["status"] == "feasible")


def test_nonnegative_membership_weights_preserve_fractional_cost_count_and_ids():
    from cfar.objective import action_cost
    from cfar.oracle import enumerate_action_subsets

    instance = authored_interface_scenarios()["shared_asset"]
    for action,cost in zip(instance["actions"],[0.1,0.1,0,10**30]):
        action["cost"] = cost
    compiled = compile_resource_logic(instance)
    subsets = list(enumerate_action_subsets(compiled["action_ids"]))
    actual = sorted(subsets,key=lambda selected: -sum(w for aid,w in compiled["action_integer_weights"].items()
                                                     if aid not in selected))
    expected = sorted(subsets,key=lambda selected: (action_cost(instance,selected),len(selected),tuple(selected)))
    assert actual == expected
    assert all(w >= 0 for w in compiled["action_integer_weights"].values())
