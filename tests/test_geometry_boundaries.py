from copy import deepcopy

import pytest

from cfar.actions import apply_actions
from cfar.errors import ValidationError
from cfar.geometry import polygon, polygons_touch
from cfar.schema import ROOT, load_instance
from cfar.validation import validate_instance


def rect(a,b,c,d):
    return [[a,b],[c,b],[c,d],[a,d]]


def base():
    return load_instance(ROOT/"examples/micro/02_missing_door.json")


def test_point_contact_is_not_adjacency():
    assert not polygons_touch(rect(0,0,1,1),rect(1,1,2,2))
    assert polygons_touch(rect(0,0,1,1),rect(1,0,2,1))


@pytest.mark.parametrize("points,code",[
    ([[0,0],[2,0],[1,1],[0,1]],"ORTHOGONAL"),
    ([[0,0],[1,1],[0,1],[1,0]],"POLYGON"),
])
def test_invalid_polygons(points,code):
    with pytest.raises(ValidationError,match=code):
        polygon(points)


def test_room_obstacle_disconnects_profile_motion():
    instance=base()
    instance["floors"][0]["obstacles"]=[rect(1,0,1.2,4)]
    with pytest.raises(ValidationError,match="ROOM_PROFILE_CONNECTIVITY"):
        validate_instance(instance)


def test_landing_box_cannot_mask_concave_clearance():
    instance=base()
    # A U-shaped clear patch has a large bounding box but insufficient rectangular clearance.
    instance["connections"][0]["geometry"]["landings"][0]["polygon"]=[[3,1],[4,1],[4,2],[3.8,2],[3.8,1.2],[3.2,1.2],[3.2,2],[3,2]]
    with pytest.raises(ValidationError,match="LANDING_RECTANGLE"):
        apply_actions(instance,["add_door"])


def test_wrong_elevation_and_alignment():
    instance=load_instance(ROOT/"examples/micro/01_missing_metadata_link.json")
    instance["connections"][-1]["geometry"]["rise_m"]=2
    with pytest.raises(ValidationError,match="PORTAL_RISE"):
        apply_actions(instance,["restore_W"])
    instance["connections"][-1]["geometry"]["rise_m"]=3
    instance["connections"][-1]["geometry"]["footprints"][1]["polygon"]=rect(5.1,1,7.1,3)
    with pytest.raises(ValidationError,match="PORTAL_ALIGNMENT"):
        apply_actions(instance,["restore_W"])


def test_door_joint_overlap():
    instance=base()
    clone=deepcopy(instance["connections"][0])
    clone.update(connection_id="Dnew",evidence_id="eDnew")
    instance["connections"].append(clone)
    a=deepcopy(instance["actions"][0]); a.update(action_id="other_door",evidence_ids=["eDnew"])
    a["effects"][0]["connection_id"]="Dnew"
    a["geometry_certificate"]["connection_ids"]=["Dnew"]
    instance["actions"].append(a)
    apply_actions(instance,["add_door"])
    apply_actions(instance,["other_door"])
    with pytest.raises(ValidationError,match="DOOR_COLLISION"):
        apply_actions(instance,["add_door","other_door"])


def test_reservation_required_even_inside_room():
    instance=load_instance(ROOT/"examples/micro/01_missing_metadata_link.json")
    instance["floors"][0]["reserved_portal_zones"]=[]
    with pytest.raises(ValidationError,match="PORTAL_RESERVED_ZONE"):
        apply_actions(instance,["restore_W"])
