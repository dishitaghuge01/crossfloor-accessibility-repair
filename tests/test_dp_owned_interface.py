import random

import pytest

from cfar.dp_owned_interface import solve_owned_interface
from cfar.errors import ValidationError
from cfar.interface_scenarios import (EXPECTED_OPTIMA, authored_interface_scenarios,
                                     branching_interface_probe, dense_alternative_probe)
from cfar.oracle import exact_oracle
from cfar.synthetic_shaft import make_shaft_instance


@pytest.mark.parametrize("name", sorted(EXPECTED_OPTIMA))
def test_full_solver_matches_authored_optimum_with_and_without_compression(name):
    instance = authored_interface_scenarios()[name]
    for compress in (False, True):
        result = solve_owned_interface(instance, compress=compress)
        assert (result["cost"], result["selected"]) == EXPECTED_OPTIMA[name]
        assert result["status"] == "optimal"
        assert result["reachability"]["satisfied"]


@pytest.mark.parametrize("seed", range(40))
def test_seeded_shared_asset_conflicts_profiles_and_zero_costs_against_oracle(seed):
    rng = random.Random(seed)
    edges, profiles, count = rng.randint(1,4), rng.randint(1,3), rng.randint(1,6)
    intervals = []
    for _ in range(count):
        left = rng.randrange(edges)
        intervals.append((left,rng.randrange(left,edges),rng.randint(1,profiles)))
    instance = make_shaft_instance(edges, intervals, [rng.randrange(5)/4 for _ in range(count)],
                                  profiles=profiles, physical=True,
                                  asset_groups=[rng.randrange(8) for _ in range(count)])
    expected = exact_oracle(instance)
    for compress in (False, True):
        result = solve_owned_interface(instance, compress=compress)
        assert (result["status"], result["cost"], result["selected"]) == (
            expected["status"], expected["cost"], expected["selected"])


def test_state_limit_never_reports_an_unexplored_optimum():
    with pytest.raises(ValidationError, match="INTERFACE_STATE_LIMIT"):
        solve_owned_interface(authored_interface_scenarios()["shared_asset"], max_states=1)


def test_cyclic_effect_graph_exercises_actual_row_removal():
    instance = branching_interface_probe()
    expected = exact_oracle(instance)
    compressed = solve_owned_interface(instance)
    uncompressed = solve_owned_interface(instance, compress=False)
    assert compressed["selected"] == uncompressed["selected"] == expected["selected"]
    assert compressed["cost"] == uncompressed["cost"] == expected["cost"]
    assert compressed["statistics"]["representative_rows_removed"] > 0


def test_cut_limit_is_explicit():
    with pytest.raises(ValidationError, match="INTERFACE_CUT_LIMIT"):
        solve_owned_interface(authored_interface_scenarios()["shared_asset"], max_cut_columns=1)


def test_solver_cli_emits_scoped_result_and_manifest(tmp_path):
    import json
    import subprocess
    import sys
    from cfar.io import write_json

    source, output = tmp_path/"input.json", tmp_path/"solved"
    write_json(source, authored_interface_scenarios()["atomic_bundle"])
    run = subprocess.run([sys.executable,"-m","cfar.cli","solve-owned-interface",str(source),
                          "--output",str(output)],capture_output=True,text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)["cost"] == "3"
    assert json.loads((output/"manifest.json").read_text())["solver_status"] == "optimal"


def test_64_private_alternatives_keep_a_bounded_state_frontier():
    result = solve_owned_interface(dense_alternative_probe())
    assert result["status"] == "optimal"
    assert (result["cost"],result["selected"]) == ("1",["A0000"])
    assert result["statistics"]["peak_raw_states"] <= 5
    assert result["parameters"] == dict(p=1,r=1,z=1,L=2,g=1,h=1)
