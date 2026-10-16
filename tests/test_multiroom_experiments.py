"""Small hand-derived extraction fixture, independent of downloaded IFCs."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_multiroom_experiments import build_one
from extend_multiroom_storeys import extend
from cfar.dp_owned_interface import solve_owned_interface
from cfar.synthetic_star import rectangle


def source_fixture():
    rooms=[]
    specs=[('S',0,rectangle(0,0,4,4)),('L',0,rectangle(4,0,6,4)),
           ('T0',1,rectangle(0,0,2,4)),('T1',1,rectangle(2,0,4,4)),
           ('V0',2,rectangle(0,0,2,4)),('V1',2,rectangle(2,0,4,4))]
    for rid,floor,shape in specs:
        rooms.append(dict(global_id=rid,name=rid,storey_id=f'F{floor}',storey_elevation_m=3*floor,
            polygon=shape,area=(shape[1][0]-shape[0][0])*(shape[2][1]-shape[1][1]),eligible=True))
    return dict(provenance=dict(building='fixture',sha256='0'*64),spaces=rooms,background=[],
        storeys=[dict(global_id=f'F{i}',name=f'F{i}',elevation_m=3*i) for i in range(3)],
        counts=dict(spaces=6,eligible_spaces=6,storeys=3,stairs=0,transport=0))


def test_horizontal_choice_and_necessary_third_storey_preserve_source_rings():
    audit=source_fixture();original=deepcopy(audit)
    variants,selection=build_one(audit)
    assert audit==original
    assert selection['adjacency_edges_per_floor']==[1,1]
    assert solve_owned_interface(variants['horizontal'])['cost']=='1'
    assert solve_owned_interface(variants['restricted-horizontal'])['cost']=='4'
    three,report=extend(audit,variants['horizontal'])
    assert len(three['floors'])==3
    assert solve_owned_interface(three)['cost']=='3'
    by={r['global_id']:r['polygon'] for r in audit['spaces']}
    assert all(r['polygon']==by[r['room_id']] for f in three['floors'] for r in f['rooms'])
    # Without the third-storey physical action, its required destination is unreachable.
    three['actions']=[a for a in three['actions'] if a['action_id']!='A2']
    assert solve_owned_interface(three)['status']=='infeasible'


def test_empty_original_storey_prevents_skipped_storey_admission():
    audit=source_fixture()
    audit['spaces']=[r for r in audit['spaces'] if r['storey_id']!='F2']
    audit['storeys']=[audit['storeys'][0],dict(global_id='empty',name='empty',elevation_m=1.5),audit['storeys'][1]]
    with pytest.raises(ValueError,match='consecutive storeys'):build_one(audit)


def test_maximum_room_subset_beats_greedy_large_polygon_and_has_stable_ties():
    from source_room_selection import maximum_nonoverlap
    rooms=[dict(global_id='large',polygon=rectangle(0,0,4,4)),
           dict(global_id='small-a',polygon=rectangle(0,0,2,4)),
           dict(global_id='small-b',polygon=rectangle(2,0,4,4))]
    selected,excluded,stats=maximum_nonoverlap(rooms)
    assert [r['global_id'] for r in selected]==['small-a','small-b']
    assert stats['retained']==2 and len(excluded)==1
    same=[dict(global_id=i,polygon=rectangle(0,0,2,2)) for i in ['B','A']]
    assert [r['global_id'] for r in maximum_nonoverlap(same)[0]]==['A']
