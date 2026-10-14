from copy import deepcopy
from itertools import combinations
import random

import pytest

from cfar.actions import apply_actions
from cfar.errors import ValidationError
from cfar.labelled_network import compile_labelled_forest, evaluate_labels
from cfar.objective import action_cost
from cfar.obligations import verify_obligations
from cfar.schema import ROOT, load_instance
from cfar.synthetic_chain import make_chain_instance


def check_all_subsets(instance):
    before = deepcopy(instance)
    network = compile_labelled_forest(instance)
    aids = sorted(a["action_id"] for a in instance["actions"])
    count = 0
    for size in range(len(aids)+1):
        for selected in combinations(aids, size):
            labels = evaluate_labels(network, list(selected))
            repair = apply_actions(instance, list(selected), validated=True)
            expected = verify_obligations(instance, repair["active"])
            assert labels["satisfied"] == expected["satisfied"]
            assert labels["cost"] == str(action_cost(instance, list(selected)))
            count += 1
    assert count == 2**len(aids)
    assert instance == before
    return network


@pytest.mark.parametrize("seed", range(16))
def test_every_subset_preserves_cost_and_connectivity(seed):
    rng = random.Random(seed)
    n = rng.randint(1, 3)
    bundles = [[(edge, pid) for edge in range(n) for pid in ("profile0", "profile1") if rng.random() < .5]
               for _ in range(6)]
    instance = make_chain_instance(n, bundles, [rng.randint(0, 6) for _ in bundles])
    if seed % 2:
        instance["floors"][1]["access_edges"] = [{"edge_id": "baseD", "connection_id": "D0",
                                                  "permitted_profiles": ["profile0"]}]
    check_all_subsets(instance)


@pytest.mark.parametrize("name", ["01_missing_metadata_link", "02_missing_door", "03_disconnected_stair",
                                  "06_coupled_portal_actions", "09_no_repair_needed", "10_empty_obligations",
                                  "15_zero_cost_tie", "16_same_floor_obligation"])
def test_microcase_mapping(name):
    check_all_subsets(load_instance(ROOT/"examples/micro"/(name+".json")))


def test_layers_do_not_allow_profile_switching():
    # Profile0 gets only the first edge, profile1 only the second: union is NOT a valid path.
    instance = make_chain_instance(2, [[(0, "profile0")], [(1, "profile1")]], [2, 3])
    network = check_all_subsets(instance)
    assert not evaluate_labels(network, ["A000", "A001"])["satisfied"]
    vertices = {v["vertex_id"]: v for v in network["vertices"]}
    for edge in network["edges"]:
        assert vertices[edge["u"]]["profile_id"] == vertices[edge["v"]]["profile_id"]


def test_overlap_shared_cost_and_irrelevant_label():
    instance = make_chain_instance(1, [[(0, "profile0"), (0, "profile1")]]*2+[[]], [3, 5, 7])
    network = check_all_subsets(instance)
    assert evaluate_labels(network, ["A000"])["cost"] == "3"
    assert evaluate_labels(network, ["A000", "A001", "A002"])["cost"] == "15"
    assert sum(e["label"] == "A002" for e in network["edges"]) == 1
    assert evaluate_labels(network, ["A002"])["satisfied"] is False


def test_unknown_selection_and_duplicates():
    network = compile_labelled_forest(make_chain_instance(1, [], []))
    with pytest.raises(ValidationError, match="UNKNOWN_SELECTION"):
        evaluate_labels(network, ["unknown"])
    with pytest.raises(ValidationError, match="DUPLICATE_SELECTION"):
        evaluate_labels(network, ["unknown", "unknown"])


@pytest.mark.parametrize("prefix", ["07", "11", "12", "17"])
def test_no_transfer_outside_scope(prefix):
    with pytest.raises(ValidationError, match="PARTITION_SCOPE"):
        compile_labelled_forest(load_instance(next((ROOT/"examples/micro").glob(prefix+"*.json"))))
