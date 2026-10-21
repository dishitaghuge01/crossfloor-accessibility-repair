import random
import pytest
from cfar.dp_owned_interface import solve_owned_interface
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.oracle import exact_oracle
from cfar.synthetic_shaft import make_shaft_instance


def label(r):
    return r['status'], r['cost'], r['selected']


@pytest.mark.parametrize('name',sorted(authored_interface_scenarios()))
def test_last_use_keeps_paid_effects_collisions_and_exact_ties(name):
    a=authored_interface_scenarios()[name]
    expected=label(exact_oracle(a))
    for compress in (False,True):
        for order in ('canonical','reverse'):
            result=solve_owned_interface(a,compress=compress,event_order=order,release_dead_cells=True,release_dead_vertices=True)
            assert label(result)==expected
            if result['status']=='optimal':assert result['reachability']['satisfied']


@pytest.mark.parametrize('seed',range(30))
def test_last_use_matches_exhaustive_shared_owner_random_catalogues(seed):
    rng=random.Random(seed);floors=rng.randint(1,4);n=rng.randint(1,7);p=rng.randint(1,2)
    intervals=[]
    for _ in range(n):
        left=rng.randrange(floors)
        intervals.append((left,rng.randrange(left,floors),rng.randint(1,p)))
    a=make_shaft_instance(floors,intervals,[rng.randrange(7)/4 for _ in range(n)],
        profiles=p,physical=True,asset_groups=[rng.randrange(3) for _ in range(n)])
    expected=label(exact_oracle(a))
    for compress in (False,True):
        assert label(solve_owned_interface(a,compress=compress,release_dead_cells=True,release_dead_vertices=True))==expected
