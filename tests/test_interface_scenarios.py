import pytest

from cfar.certificates import make_certificate, verify_certificate
from cfar.interface_scenarios import EXPECTED_OPTIMA, authored_interface_scenarios
from cfar.oracle import exact_oracle


@pytest.mark.parametrize("name", sorted(EXPECTED_OPTIMA))
def test_physical_proof_probes_have_certified_expected_optima(name):
    instance = authored_interface_scenarios()[name]
    result = exact_oracle(instance)
    cost, selected = EXPECTED_OPTIMA[name]
    assert result["status"] == "optimal"
    assert (result["cost"], result["selected"]) == (cost, selected)
    assert result["delta_A"] == 0
    verify_certificate(instance, make_certificate(instance, result))
    records = {tuple(row["selected"]): row for row in result["ledger"]}
    if name == "shared_asset":
        assert records[("A001", "A002")]["error_code"] == "PORTAL_COLLISION"
    elif name == "partial_footprints":
        assert records[("A000", "A001")]["status"] == "feasible"
        assert records[("A000", "A002")]["error_code"] == "PORTAL_COLLISION"
    elif name == "unused_paid_geometry":
        assert records[("A000", "A002")]["error_code"] == "PORTAL_COLLISION"
    elif name == "separate_profiles":
        assert records[("A000",)]["status"] == "unsatisfied"
