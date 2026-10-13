from copy import deepcopy
import random

import pytest

from cfar.dp_partition import solve_partition
from cfar.errors import ValidationError
from cfar.oracle import exact_oracle
from cfar.schema import ROOT, load_instance
from cfar.synthetic_chain import make_chain_instance
from cfar.synthetic_star import make_star_instance


def assert_oracle(instance):
    before = deepcopy(instance)
    expected, actual = exact_oracle(instance), solve_partition(instance)
    for field in ("status", "selected", "cost"):
        assert actual[field] == expected[field]
    assert instance == before
    return actual


@pytest.mark.parametrize("seed", range(24))
def test_seeded_profile_bundles(seed):
    rng = random.Random(seed)
    n, k = rng.randint(1, 3), rng.randint(0, 7)
    bundles = [[(i, pid) for i in range(n) for pid in ("profile0", "profile1") if rng.random() < .4]
               for _ in range(k)]
    result = assert_oracle(make_chain_instance(n, bundles, [rng.randint(0, 6) for _ in range(k)]))
    assert result["states"] <= 2**(2*n)


def test_joint_path_and_shared_cost():
    instance = make_chain_instance(2, [[(0, "profile0"), (0, "profile1")],
                                       [(1, "profile0"), (1, "profile1")],
                                       [(0, "profile0"), (1, "profile0")],
                                       [(0, "profile1"), (1, "profile1")]], [2, 3, 4, 4])
    result = assert_oracle(instance)
    assert result["selected"] == ["A000", "A001"] and result["cost"] == "5"


@pytest.mark.parametrize("name", ["01_missing_metadata_link", "02_missing_door", "03_disconnected_stair",
                                  "06_coupled_portal_actions", "09_no_repair_needed", "10_empty_obligations",
                                  "15_zero_cost_tie", "16_same_floor_obligation"])
def test_supported_microcases(name):
    assert_oracle(load_instance(ROOT/"examples/micro"/(name+".json")))


def test_limits_and_scope_are_not_infeasibility():
    instance = make_chain_instance(2, [[(0, "profile0")], [(1, "profile0")]], [1, 1], profiles=1)
    with pytest.raises(ValidationError, match="COMPONENT_LIMIT"):
        solve_partition(instance, max_components=2)
    with pytest.raises(ValidationError, match="STATE_LIMIT"):
        solve_partition(instance, max_states=1)
    instance["actions"][0]["requires"] = ["A001"]
    with pytest.raises(ValidationError, match="PARTITION_SCOPE"):
        solve_partition(instance)


def test_conflicting_catalogue_rejected():
    path = next((ROOT/"examples/micro").glob("17*.json"))
    with pytest.raises(ValidationError, match="PARTITION_SCOPE.*jointly feasible"):
        solve_partition(load_instance(path))


def test_many_actions_no_oracle_and_order_independence(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("enumeration must not be used")
    monkeypatch.setattr("cfar.oracle.exact_oracle", forbidden)
    bundle = [(edge, pid) for edge in range(3) for pid in ("profile0", "profile1")]
    instance = make_chain_instance(3, [bundle]*200, [10**30+1]*200)
    first = solve_partition(instance)
    instance["actions"].reverse()
    instance["profiles"].reverse()
    second = solve_partition(instance)
    assert first == second
    assert first["selected"] == ["A000"] and first["cost"] == str(10**30+1)
    assert first["states"] == 2


def test_no_obligations_and_zero_cost_tie():
    instance = make_chain_instance(1, [[(0, "profile0")]]*2, [0, 0], profiles=1)
    assert assert_oracle(instance)["selected"] == ["A000"]
    instance["obligations"] = []
    assert assert_oracle(instance)["selected"] == []


@pytest.mark.parametrize("seed", range(12))
def test_cycles_different_baselines_and_arbitrary_obligations(seed):
    rng = random.Random(seed)
    instance = make_chain_instance(3, [], [])
    star = make_star_instance(3, [], [])
    for source in star["connections"][2:]:
        c = deepcopy(source)
        c["connection_id"] = "X"+c["connection_id"]
        c["evidence_id"] = "e"+c["connection_id"]
        c["physical_profiles"] = ["profile0", "profile1"]
        instance["connections"].append(c)
    # Different baseline contractions across profiles; candidate graph has cycles.
    instance["floors"][1]["access_edges"] = [{"edge_id": "baseD", "connection_id": "D0",
                                              "permitted_profiles": ["profile0"]}]
    instance["obligations"] = [{"obligation_id": "O0", "source": "T0", "target": "T2", "profile_id": "profile0"},
                                {"obligation_id": "O1", "source": "T1", "target": "S", "profile_id": "profile1"}]
    for i in range(7):
        effects = []
        for c in instance["connections"][1:]:
            permitted = [pid for pid in ("profile0", "profile1") if rng.random() < .4]
            if permitted:
                effects.append({"op": "activate_connection", "connection_id": c["connection_id"],
                                "permitted_profiles": permitted})
        if not effects:
            effects = [{"op": "activate_connection", "connection_id": "P", "permitted_profiles": ["profile0"]}]
        instance["actions"].append({"action_id": f"A{i}", "type": "representation_correction",
                                     "cost": rng.randint(0, 6), "effects": effects,
                                     "evidence_ids": ["e"+e["connection_id"] for e in effects],
                                     "requires": [], "excludes": []})
    assert_oracle(instance)
