import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("ifcopenshell")

from cfar.actions import apply_actions
from cfar.obligations import verify_obligations
from cfar.synthetic_star import rectangle

spec = importlib.util.spec_from_file_location("public_building_controlled", Path(__file__).parents[1]/"scripts/public_building_controlled.py")
protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol)


def audit_fixture():
    return dict(provenance=dict(building="authored-protocol-test"), background=[],
                spaces=[dict(global_id="r0", name="r0", storey_id="f0", z_min=0,
                             polygon=rectangle(0,0,4,4), eligible=True),
                        dict(global_id="r1", name="r1", storey_id="f1", z_min=3,
                             polygon=rectangle(0,0,4,4), eligible=True)])


def test_hypothetical_reference_is_replayed_and_source_polygons_unchanged():
    audit = audit_fixture()
    instance, rejected = protocol.select_reference(audit)
    assert not rejected
    for floor, source in zip(instance["floors"], audit["spaces"]):
        assert floor["rooms"][0]["polygon"] == source["polygon"]
        assert floor["rooms"][0]["room_id"] == source["global_id"]
    reference = apply_actions(instance, ["D"])
    assert verify_obligations(reference["instance"], reference["active"])["satisfied"]
    corrupted = apply_actions(instance, [])
    assert not verify_obligations(corrupted["instance"], corrupted["active"])["satisfied"]


def test_unmapped_background_is_not_ignored():
    audit = audit_fixture()
    audit["background"] = [dict(global_id="stair", error="unmapped")]
    with pytest.raises(ValueError, match="unmapped physical background"):
        protocol.select_reference(audit)
