from itertools import combinations
import pytest
from cfar.geometry import joint_geometry
from cfar.errors import ValidationError
from cfar.interface_scenarios import authored_interface_scenarios
from cfar.validation import baseline_active


@pytest.mark.parametrize('name',sorted(authored_interface_scenarios()))
def test_compilation_local_cache_matches_uncached_paid_geometry(name):
    a=authored_interface_scenarios()[name];cache={}
    actions=a['actions']
    for count in range(min(3,len(actions))+1):
        for selected in combinations(actions,count):
            active=baseline_active(a)
            for action in selected:
                for e in action['effects']:
                    active[e['connection_id']]=sorted(set(active.get(e['connection_id'],[]))|set(e['permitted_profiles']))
            try:expected=joint_geometry(a,active)
            except ValidationError as error:
                with pytest.raises(ValidationError) as caught:joint_geometry(a,active,_fixed_cache=cache)
                assert caught.value.code==error.code
            else:assert joint_geometry(a,active,_fixed_cache=cache)==expected
