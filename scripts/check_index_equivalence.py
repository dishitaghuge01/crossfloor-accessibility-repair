"""Untimed comparison of indexed and original recognition on frozen input corpora."""
import argparse,json
from pathlib import Path
from cfar.interface_recognition import recognize_physical_interface
from cfar.errors import ValidationError
from cfar.io import manifest,write_json

def run(roots,out):
 out.mkdir(exist_ok=False);rows=[]
 for root in roots:
  for name in sorted({r['instance_id'] for r in json.loads((root/'records.json').read_text())}):
   a=json.loads((root/name/'input.json').read_text());results=[]
   for index in [False,True]:
    try:r=recognize_physical_interface(a,profile=True,spatial_index=index);status='recognized'
    except ValidationError as e:r={'error_code':e.code};status='unsupported'
    results.append((status,r))
   assert results[0][0]==results[1][0],name
   fields=['error_code'] if results[0][0]=='unsupported' else ['cells','action_cells','units','components','anchors','parameters','geometry_conflicts','blocked']
   for key in fields:assert results[0][1].get(key)==results[1][1].get(key),(name,key)
   row=dict(instance_id=name,status=results[0][0],plain_counts=results[0][1].get('operation_counts'),indexed_counts=results[1][1].get('operation_counts'))
   write_json(out/root.name/name/'manifest.json',manifest(a,{'method':'untimed-index-equivalence','spatial_index':[False,True]},row['status'],0))
   write_json(out/root.name/name/'results.json',results)
   rows.append(row);write_json(out/'summary.json',rows)
 print('PASS',len(rows),'indexed recognition comparisons')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--evidence',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.evidence,a.output)
