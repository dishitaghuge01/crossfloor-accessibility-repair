from copy import deepcopy

import pytest

from cfar.actions import apply_actions
from cfar.errors import ValidationError
from cfar.interface_recognition import recognize_physical_interface
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.oracle import enumerate_action_subsets
from cfar.synthetic_star import rectangle


@pytest.mark.parametrize("name", sorted(authored_interface_scenarios()))
def test_recognized_cell_ownership_matches_every_selection(name):
    instance = authored_interface_scenarios()[name]
    recognized = recognize_physical_interface(instance)
    assert recognized["recognized"]
    assert recognized["parameters"]["r"] == 1
    assert recognized["parameters"]["p"] == len(instance["profiles"])
    units = recognized["units"]
    assert sorted(aid for u in units for aid in u["action_ids"]) == sorted(recognized["action_cells"])
    assert sum(len(u["asset_ids"]) for u in units) == len({o for u in units for o in u["asset_ids"]})
    for selected in enumerate_action_subsets(list(recognized["action_cells"])):
        owners = {}
        collision = False
        for aid in selected:
            for cid, owner in recognized["action_cells"][aid].items():
                if cid in owners and owners[cid] != owner:
                    collision = True
                owners[cid] = owner
        try:
            apply_actions(instance, selected)
        except ValidationError as error:
            assert collision and error.code == "PORTAL_COLLISION"
        else:
            assert not collision
    if name == "partial_footprints":
        assert recognized["parameters"]["z"] == 4
    if name in {"atomic_bundle", "unused_paid_geometry"}:
        assert recognized["parameters"]["g"] == 2
    if name == "shared_asset":
        assert any(u["action_ids"] == ["A000", "A001"] for u in units)
        assert recognized["parameters"]["L"] == 4


def test_dependencies_are_explicitly_outside_scope():
    instance = authored_interface_scenarios()["shared_asset"]
    instance["actions"][0]["requires"] = ["A001"]
    with pytest.raises(ValidationError, match="INTERFACE_SCOPE"):
        recognize_physical_interface(instance)


def test_unary_blocked_actions_do_not_inflate_units_or_occupancy():
    instance = authored_interface_scenarios()["shared_asset"]
    for c in instance["connections"]:
        if c["geometry"]["asset_id"] == "asset-group-0":
            c["geometry"]["width_m"] = 10
    recognized = recognize_physical_interface(instance)
    assert set(recognized["blocked"]) == {"A000", "A001"}
    assert set(recognized["action_cells"]) == {"A002", "A003"}
    assert all("asset-group-0" not in u["asset_ids"] for u in recognized["units"])


def test_cli_writes_recognition_and_manifest(tmp_path):
    import json
    import subprocess
    import sys
    from cfar.io import write_json

    source, output = tmp_path/"input.json", tmp_path/"recognized"
    write_json(source, authored_interface_scenarios()["atomic_bundle"])
    run = subprocess.run([sys.executable, "-m", "cfar.cli", "recognize-interface", str(source),
                          "--output", str(output)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout)["parameters"]["g"] == 2
    assert json.loads((output/"manifest.json").read_text())["solver_status"] == "recognized"
    assert json.loads((output/"recognition.json").read_text())["witness_status"].startswith("recognition only")


def test_nonrooted_demands_are_explicitly_outside_scope():
    instance = authored_interface_scenarios()["shared_asset"]
    other = deepcopy(instance["obligations"][0])
    other.update(obligation_id="other", source="R1")
    instance["obligations"].append(other)
    with pytest.raises(ValidationError, match="INTERFACE_ROOTED"):
        recognize_physical_interface(instance)


def test_tiny_arrangement_cells_are_not_assumed_exact():
    instance = authored_interface_scenarios()["shared_asset"]
    for c in instance["connections"]:
        if c["geometry"]["asset_id"] == "asset-group-1":
            for field in ("landings", "footprints"):
                for record in c["geometry"][field]:
                    record["polygon"] = rectangle(.500000001,.5,1.500000001,1.5)
    with pytest.raises(ValidationError, match="INTERFACE_CELL_EPS"):
        recognize_physical_interface(instance)
