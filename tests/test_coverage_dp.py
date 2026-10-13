import random
from copy import deepcopy

import pytest

from cfar.certificates import make_certificate, verify_certificate
from cfar.dp_coverage import recognize_bundle_star, solve_bundle_star
from cfar.errors import ValidationError
from cfar.oracle import exact_oracle
from cfar.synthetic_star import make_star_instance


def test_overlap_is_idempotent_and_charged_once_per_action():
    instance=make_star_instance(3,[[0,1],[1,2]],[2,3])
    result=exact_oracle(instance)
    assert result["selected"] == ["A000","A001"]
    assert result["cost"] == "5"
    assert solve_bundle_star(instance)["cost"] == "5"
    assert verify_certificate(instance,make_certificate(instance,result))["valid"]


@pytest.mark.parametrize("seed",range(24))
def test_dp_matches_oracle_on_controlled_variations(seed):
    rng=random.Random(seed)
    m=rng.randint(1,5); k=rng.randint(0,8)
    subsets=[[i for i in range(m) if rng.random()<0.45] for _ in range(k)]
    costs=[rng.randint(0,6) for _ in range(k)]
    instance=make_star_instance(m,subsets,costs)
    original=deepcopy(instance)
    oracle=exact_oracle(instance)
    dp=solve_bundle_star(instance)
    assert (dp["status"],dp["selected"],dp["cost"]) == (oracle["status"],oracle["selected"],oracle["cost"])
    assert dp["states"] <= 2**m
    assert instance == original


def test_reject_scope_and_parameter_guard():
    instance=make_star_instance(2,[[0],[1]],[1,1])
    instance["actions"][0]["requires"]=["A001"]
    with pytest.raises(ValidationError,match="STAR_SCOPE"):
        recognize_bundle_star(instance)
    instance["actions"][0]["requires"]=[]
    with pytest.raises(ValidationError,match="TERMINAL_LIMIT"):
        solve_bundle_star(instance,max_terminals=1)


def test_many_actions_few_terminals_without_enumeration(monkeypatch):
    def forbidden(*args,**kwargs):
        raise AssertionError("oracle must not be called by structural DP")
    monkeypatch.setattr("cfar.oracle.exact_oracle",forbidden)
    instance=make_star_instance(3,[[0],[1],[2]]+[[0,1,2]]*37,[2,2,2]+[5]*37)
    result=solve_bundle_star(instance)
    assert result["cost"] == "5" and result["selected"] == ["A003"]
    assert result["states"] <= 8


def test_discrete_cost_comparison_does_not_round_large_integers():
    instance=make_star_instance(2,[[0],[1],[0,1]],[10**30,2,10**30+1])
    for result in (exact_oracle(instance),solve_bundle_star(instance)):
        assert result["selected"] == ["A002"]
        assert result["cost"] == str(10**30+1)
