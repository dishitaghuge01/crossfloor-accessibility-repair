"""Untimed geometry-operation counts; never enabled during timing workers."""
import argparse,dis,hashlib,inspect,json,sys
from pathlib import Path
from cfar.errors import ValidationError
from cfar.geometry import joint_geometry
from cfar.interface_recognition import recognize_physical_interface
from cfar.io import manifest,write_json


def count_recognition(instance):
    source,start=inspect.getsourcelines(joint_geometry)
    line=start+next(i for i,text in enumerate(source) if 'polygon(x["polygon"]).intersection' in text)
    instructions=[i for i in dis.get_instructions(joint_geometry) if i.positions.lineno==line]
    entry=min(instructions,key=lambda i:i.offset)
    if entry.argval!='require':raise RuntimeError('geometry operation locator changed; inspect counter')
    count=0
    def trace(frame,event,arg):
        nonlocal count
        if frame.f_code is not joint_geometry.__code__:return None
        if event=='line' and frame.f_lasti==entry.offset:count+=1
        return trace
    previous=sys.gettrace();sys.settrace(trace)
    try:
        recognized=recognize_physical_interface(instance)
        result=dict(status='recognized',physical_footprint_pair_intersection_tests=count,
            generated_cells=len(recognized['cells']),parameters=recognized['parameters'])
    except ValidationError as e:
        result=dict(status='unsupported',error_code=e.code,physical_footprint_pair_intersection_tests=count,generated_cells=None,parameters=None)
    finally:sys.settrace(previous)
    return result


def run(roots,output):
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('fresh output required')
    records=[]
    for root in roots:
        observations=json.loads((root/'records.json').read_text())
        for name in sorted({r['instance_id'] for r in observations}):
            instance=json.loads((root/name/'input.json').read_text());seed=next(r['seed'] for r in observations if r['instance_id']==name)
            result=count_recognition(instance);target=output/root.name/name
            write_json(target/'profile.json',result)
            write_json(target/'manifest.json',manifest(instance,dict(method='untimed_geometry_line_counter_v1',
                operation='different-owner physical-footprint intersection in joint_geometry, including active baseline portals; shared-owner reuse skips it',
                geometry_source_sha256=hashlib.sha256(Path(inspect.getsourcefile(joint_geometry)).read_bytes()).hexdigest(),
                runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),result['status'],seed))
            records.append(dict(experiment=root.name,instance_id=name,**result))
            write_json(output/'summary.json',records)
    print('Untimed geometry profiles:',len(records),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.evidence,a.output)
