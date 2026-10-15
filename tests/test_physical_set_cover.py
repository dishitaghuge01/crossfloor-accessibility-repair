from itertools import combinations

import pytest

from cfar.actions import apply_actions
from cfar.interface_recognition import recognize_physical_interface
from cfar.obligations import verify_obligations
from cfar.oracle import exact_oracle
from cfar.physical_set_cover import make_physical_set_cover


@pytest.mark.parametrize("subsets", [[[0, 1], [1, 2], [0, 2]], [[0], [1]], [[0, 1, 2], [0], [2]]])
def test_every_repair_selection_equals_covered_universe(subsets):
    instance = make_physical_set_cover(3, subsets)
    recognized = recognize_physical_interface(instance)
    assert recognized["parameters"]["p"] == recognized["parameters"]["h"] == 1
    assert recognized["parameters"]["L"] == 2
    assert not recognized["geometry_conflicts"] and not recognized["blocked"]
    for count in range(len(subsets)+1):
        for indices in combinations(range(len(subsets)), count):
            selected = [f"A{i:03d}" for i in indices]
            repaired = apply_actions(instance, selected)
            covers = set().union(*(set(subsets[i]) for i in indices)) == {0, 1, 2}
            assert verify_obligations(repaired["instance"], repaired["active"])["satisfied"] == covers


def test_two_floor_physical_hardness_witness_has_expected_optimum():
    instance = make_physical_set_cover(3, [[0, 1], [1, 2], [0, 2]])
    result = exact_oracle(instance)
    assert (result["cost"], result["selected"]) == ("2", ["A000", "A001"])
