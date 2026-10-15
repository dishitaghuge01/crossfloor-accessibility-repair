from copy import deepcopy

from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_recognition import recognize_physical_interface
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.oracle import exact_oracle
from cfar.synthetic_star import rectangle


def test_irrelevant_rooms_reduce_interface_without_changing_geometry_or_label():
    instance = deepcopy(authored_interface_scenarios()["atomic_bundle"])
    for floor in instance["floors"]:
        max_x = max(x for x, y in floor["boundary"])
        max_y = max(y for x, y in floor["boundary"])
        min_x = min(x for x, y in floor["boundary"])
        min_y = min(y for x, y in floor["boundary"])
        floor["boundary"] = rectangle(min_x, min_y, max_x + 24, max_y)
        for i in range(10):
            floor["rooms"].append(dict(room_id=f"unused-{floor['floor_id']}-{i}", label="unused",
                polygon=rectangle(max_x+2*i+1, min_y+.1, max_x+2*i+2, min_y+1.1)))
    before = deepcopy(instance)
    full = recognize_physical_interface(instance)
    pruned = recognize_physical_interface(instance, prune_irrelevant=True)
    assert full["parameters"]["r"] == 11
    assert pruned["parameters"]["r"] == 1
    assert full["action_cells"] == pruned["action_cells"]
    expected = exact_oracle(instance)
    for compress in (False, True):
        result = solve_owned_interface(instance, compress=compress, prune_irrelevant=True)
        assert (result["cost"], result["selected"]) == (expected["cost"], expected["selected"])
    assert instance == before


def test_pruning_preserves_disconnected_paid_effect_endpoints():
    instance = authored_interface_scenarios()["unused_paid_geometry"]
    recognized = recognize_physical_interface(instance, prune_irrelevant=True)
    catalog = {c["connection_id"]: c for c in instance["connections"]}
    for action in instance["actions"]:
        for effect in action["effects"]:
            for pid in effect["permitted_profiles"]:
                c = catalog[effect["connection_id"]]
                assert c["u"] in recognized["components"][pid]
                assert c["v"] in recognized["components"][pid]
    oracle = exact_oracle(instance)
    result = solve_owned_interface(instance, prune_irrelevant=True)
    assert (result["cost"], result["selected"]) == (oracle["cost"], oracle["selected"])
