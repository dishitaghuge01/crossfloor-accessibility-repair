from copy import deepcopy
from itertools import combinations
import random

import pytest

from cfar.actions import apply_actions
from cfar.conflict_compilation import compile_activation_constraints, selection_admissibility
from cfar.errors import ValidationError
from cfar.schema import ROOT, load_instance
from cfar.synthetic_chain import make_chain_instance


MICROS = [p for p in sorted((ROOT/"examples/micro").glob("*.json")) if not p.name.startswith("07")]


def assert_all_subsets(instance):
    before = deepcopy(instance)
    compiled = compile_activation_constraints(instance)
    aids = compiled["action_ids"]
    for size in range(len(aids)+1):
        for selected in combinations(aids, size):
            try:
                apply_actions(instance, list(selected), validated=True)
                actual = True
            except ValidationError:
                actual = False
            assert selection_admissibility(compiled, list(selected))["admissible"] == actual
    assert instance == before
    assert compiled["geometry_calls_after_validation"] <= len(aids)+len(aids)*(len(aids)-1)//2
    return compiled


@pytest.mark.parametrize("path", MICROS, ids=lambda p: p.stem)
def test_all_micro_selections_match_strict_replay(path):
    assert_all_subsets(load_instance(path))


@pytest.mark.parametrize("seed", range(8))
def test_bundled_profile_dependencies_and_exclusions(seed):
    rng = random.Random(seed)
    pairs = [(edge, pid) for edge in range(3) for pid in ("profile0", "profile1")]
    bundles = [[pair for pair in pairs if rng.random() < .4] for _ in range(6)]
    instance = make_chain_instance(3, bundles, [1]*6)
    instance["actions"][0]["requires"] = ["A001"]
    instance["actions"][2]["requires"] = ["A003"]
    instance["actions"][3]["requires"] = ["A002"]
    instance["actions"][4]["excludes"] = ["A005"]
    assert_all_subsets(instance)


def test_collision_has_pair_witness_and_invalid_width_is_unary():
    collision = assert_all_subsets(load_instance(next((ROOT/"examples/micro").glob("17*.json"))))
    assert not collision["blocked"]
    assert any(c["code"] == "PORTAL_COLLISION" for c in collision["geometry_conflicts"])
    narrow = assert_all_subsets(load_instance(next((ROOT/"examples/micro").glob("14*.json"))))
    assert any(c["code"] == "PROFILE_WIDTH" for c in narrow["blocked"].values())


def test_does_not_treat_dependency_as_geometric_invalidity():
    instance = load_instance(next((ROOT/"examples/micro").glob("11*.json")))
    compiled = assert_all_subsets(instance)
    assert not compiled["blocked"]
    assert any(compiled["requires"].values())


def test_scope_limits_and_malformed_selections():
    with pytest.raises(ValidationError, match="CONFLICT_SCOPE"):
        compile_activation_constraints(load_instance(next((ROOT/"examples/micro").glob("07*.json"))))
    instance = make_chain_instance(1, [[]], [1])
    with pytest.raises(ValidationError, match="CONFLICT_ACTION_LIMIT"):
        compile_activation_constraints(instance, max_actions=0)
    compiled = compile_activation_constraints(instance)
    with pytest.raises(ValidationError, match="UNKNOWN_SELECTION"):
        selection_admissibility(compiled, ["bad"])
    with pytest.raises(ValidationError, match="DUPLICATE_SELECTION"):
        selection_admissibility(compiled, ["A000", "A000"])
