from copy import deepcopy
from decimal import Decimal
import json

import pytest

from cfar.actions import apply_actions
from cfar.certificates import make_certificate, verify_certificate
from cfar.errors import ValidationError
from cfar.geometry import connection_feasible
from cfar.graphs import build_access_graph, build_adjacency_graph, build_profile_graph
from cfar.obligations import verify_obligations
from cfar.oracle import exact_oracle
from cfar.schema import ROOT, load_instance
from cfar.validation import validate_instance

EXPECTATIONS=json.loads((ROOT/"examples/expected.json").read_text())


def case(name):
    return load_instance(ROOT/"examples/micro"/(name+".json"))


@pytest.mark.parametrize("name",sorted(EXPECTATIONS))
@pytest.mark.parametrize("variant",["SCFAR","RCFAR"])
def test_hand_answers_and_independent_certificate(name,variant):
    instance=case(name)
    before=deepcopy(instance)
    result=exact_oracle(instance,variant)
    answer=EXPECTATIONS[name][variant]
    for key in ("status","selected","cost"):
        assert result[key] == answer[key]
    assert result.get("delta_A") == answer["delta_A"]
    assert len(result["ledger"]) == 2**len(instance["actions"])
    assert instance == before
    certificate=make_certificate(instance,result)
    assert verify_certificate(instance,certificate)["valid"]


def test_adjacency_is_not_traversability():
    instance=case("02_missing_door")
    assert build_adjacency_graph(instance["floors"][0])["L0"] == {"C0"}
    assert build_access_graph(instance,"F0","wheelchair")["L0"] == set()
    assert not verify_obligations(instance)["satisfied"]
    repair=apply_actions(instance,["add_door"])
    assert repair["adjacency"]["F0"]["preserved"]
    assert verify_obligations(instance,repair["active"])["satisfied"]


def test_profile_graph_and_stairs():
    instance=case("03_disconnected_stair")
    repair=apply_actions(instance,["restore_landing_door"])
    assert "C1" in build_profile_graph(instance,"ambulant",repair["active"])["C0"]
    assert "C1" not in build_profile_graph(instance,"wheelchair",repair["active"])["C0"]
    with pytest.raises(ValidationError,match="PHYSICAL_PROFILE"):
        connection_feasible(instance,instance["connections"][-1],["wheelchair"])


def test_original_reference_is_not_optimality():
    instance=case("08_original_not_optimal")
    certificate=make_certificate(instance,exact_oracle(instance))
    assert certificate["recovery"]["reference_feasible"]
    assert certificate["recovery"]["reference_cost"] == "5"
    assert certificate["cost"] == "2"
    assert not certificate["recovery"]["selected_matches_reference"]


@pytest.mark.parametrize("mutation,code",[
    (lambda b: b["actions"][0].update(type="representation_correction"),"SCHEMA"),
    (lambda b: b["actions"][0].update(cost=-1),"SCHEMA"),
    (lambda b: b["actions"][0].update(cost=float("nan")),"NONFINITE_NUMBER"),
    (lambda b: b["actions"][0].update(evidence_ids=[]),"ACTION_EVIDENCE"),
    (lambda b: b["actions"][0]["geometry_certificate"].update(connection_ids=[]),"CERTIFICATE_SCOPE"),
    (lambda b: b["obligations"][0].update(source="missing"),"OBLIGATION_ENDPOINT"),
    (lambda b: b["floors"][0].update(adjacency_edges=[]),"ADJACENCY_GEOMETRY"),
    (lambda b: b["floors"][0]["rooms"][1].update(room_id="L0"),"DUPLICATE_ID"),
    (lambda b: b["profiles"][0].update(min_width_m=0),"SCHEMA"),
    (lambda b: b.update(schema_version="9"),"SCHEMA"),
])
def test_named_input_failures(mutation,code):
    instance=case("02_missing_door")
    mutation(instance)
    with pytest.raises(ValidationError) as error:
        validate_instance(instance)
    assert error.value.code == code


def test_metadata_cannot_invent_a_route():
    instance=case("02_missing_door")
    instance["actions"][0]["type"]="representation_correction"
    del instance["actions"][0]["geometry_certificate"]
    with pytest.raises(ValidationError,match="CORRECTION_INVENTS_ROUTE"):
        validate_instance(instance)


def test_missing_physical_evidence_is_not_a_boolean_certificate():
    instance=case("05_impossible_portal_footprint")
    with pytest.raises(ValidationError,match="LANDING_CONTAINMENT|PORTAL_CONTAINMENT"):
        apply_actions(instance,["impossible_lift"])


def test_collision_requires_joint_verification():
    instance=case("17_joint_portal_collision")
    for action in instance["actions"]:
        apply_actions(instance,[action["action_id"]])
    with pytest.raises(ValidationError,match="PORTAL_COLLISION"):
        apply_actions(instance,[a["action_id"] for a in instance["actions"]])


def test_strict_and_relaxed_are_separate():
    instance=case("07_strict_vs_relaxed")
    with pytest.raises(ValidationError,match="STRICT_GEOMETRY_EDIT"):
        apply_actions(instance,["reshape_and_door"],"SCFAR")
    result=exact_oracle(instance,"RCFAR",topology_weight="2.5")
    assert result["delta_A"] == 1
    assert Decimal(result["cost"]) == Decimal("6.5")


@pytest.mark.parametrize("mutation,code",[
    (lambda c: c.update(input_fingerprint="forged"),"CERTIFICATE_INPUT"),
    (lambda c: c.update(cost="0"),"CERTIFICATE_SOLUTION"),
    (lambda c: c["optimality"].update(lower_bound="0"),"CERTIFICATE_OPTIMALITY"),
    (lambda c: c["optimality"].update(subsets=1),"CERTIFICATE_OPTIMALITY"),
    (lambda c: c["reachability_and_preservation"]["reachability"]["paths"].update(O=["L0","L1"]),"CERTIFICATE_PATH"),
    (lambda c: c["reachability_and_preservation"].update(delta_A=5),"CERTIFICATE_TOPOLOGY"),
    (lambda c: c.update(geometric_feasibility={}),"CERTIFICATE_GEOMETRY"),
    (lambda c: c["recovery"].update(selected_matches_reference=True),"CERTIFICATE_RECOVERY"),
])
def test_certificate_tampering(mutation,code):
    instance=case("01_missing_metadata_link")
    certificate=make_certificate(instance,exact_oracle(instance))
    mutation(certificate)
    with pytest.raises(ValidationError) as error:
        verify_certificate(instance,certificate)
    assert error.value.code == code


def test_oracle_guard_and_unknown_selection():
    instance=case("01_missing_metadata_link")
    with pytest.raises(ValidationError,match="ACTION_LIMIT"):
        exact_oracle(instance,max_actions=0)
    with pytest.raises(ValidationError,match="UNKNOWN_SELECTION"):
        apply_actions(instance,["invented"])
    with pytest.raises(ValidationError,match="DUPLICATE_SELECTION"):
        apply_actions(instance,["restore_W","restore_W"])


def test_input_order_does_not_change_optimum():
    instance=case("06_coupled_portal_actions")
    first=exact_oracle(instance)
    instance["actions"].reverse()
    instance["floors"].reverse()
    instance["connections"].reverse()
    second=exact_oracle(instance)
    assert (first["selected"],first["cost"],first["ledger"]) == (second["selected"],second["cost"],second["ledger"])


def test_verifier_does_not_call_solver_replay_or_bfs(monkeypatch):
    instance=case("06_coupled_portal_actions")
    certificate=make_certificate(instance,exact_oracle(instance))
    def forbidden(*args,**kwargs):
        raise AssertionError("solver implementation must not be used by verifier")
    monkeypatch.setattr("cfar.actions.apply_actions",forbidden)
    monkeypatch.setattr("cfar.oracle.exact_oracle",forbidden)
    monkeypatch.setattr("cfar.obligations.shortest_profile_path",forbidden)
    assert verify_certificate(instance,certificate)["valid"]


def test_duplicate_json_keys_rejected(tmp_path):
    path=tmp_path/"duplicate.json"
    path.write_text('{"schema_version":"0.1.0","schema_version":"0.1.0"}')
    with pytest.raises(ValidationError,match="JSON_DUPLICATE_KEY"):
        load_instance(path)


def test_enums_agree_with_schema():
    schema=json.loads((ROOT/"spec/instance.schema.json").read_text())
    enums=json.loads((ROOT/"spec/enums.json").read_text())
    assert schema["$defs"]["action"]["properties"]["type"]["enum"] == enums["action_types"]
    assert schema["$defs"]["connection"]["properties"]["kind"]["enum"] == enums["connection_kinds"]


def test_malformed_certificate_has_named_error():
    instance=case("01_missing_metadata_link")
    certificate=make_certificate(instance,exact_oracle(instance))
    del certificate["optimality"]
    with pytest.raises(ValidationError,match="CERTIFICATE_FORMAT"):
        verify_certificate(instance,certificate)
