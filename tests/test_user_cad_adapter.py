"""Extraction guards; no private CAD source required."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('user_cad_adapter', Path(__file__).resolve().parents[1]/'scripts/adapt_user_cad.py')
cad = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cad)


def test_nested_block_scale_rotation_and_basepoint():
    # The line starts one unit right of its block base. Scale x by two, rotate
    # 90 degrees, then place it at (10,20): the answer is (10,22), not (12,20).
    doc = {'OBJECTS': [
        dict(object='BLOCK_HEADER',handle=[0,1,1],name='*Model_Space',entities=[[0,1,2]]),
        dict(entity='INSERT',handle=[0,1,2],block_header=[0,1,3],ins_pt=[10,20,0],scale=[2,3,1],rotation=cad.math.pi/2),
        dict(object='BLOCK_HEADER',handle=[0,1,3],base_pt=[5,5,0],entities=[[0,1,4]]),
        dict(entity='LINE',handle=[0,1,4],start=[6,5,0],end=[6,6,0])
    ]}
    result = cad.flatten(doc)
    assert result[0]['points'][0] == pytest.approx([10,22])
    assert result[0]['points'][1] == pytest.approx([7,22])
    assert result[0]['insert_path'] == [2]


def test_external_reference_is_not_silently_omitted():
    doc = {'OBJECTS': [
        dict(object='BLOCK_HEADER',handle=[0,1,1],name='*Model_Space',entities=[[0,1,2]]),
        dict(entity='INSERT',handle=[0,1,2],block_header=[0,1,3]),
        dict(object='BLOCK_HEADER',handle=[0,1,3],blkisxref=1)
    ]}
    with pytest.raises(ValueError, match='external block'):
        cad.flatten(doc)


def test_wrong_source_rejected_before_output(tmp_path):
    source=tmp_path/'different.dwg';source.write_bytes(b'AC1018not-the-provided-drawing')
    with pytest.raises(ValueError, match='fingerprint'):
        cad.build(source,tmp_path/'absent.json',tmp_path/'output')
    assert not (tmp_path/'output').exists()
