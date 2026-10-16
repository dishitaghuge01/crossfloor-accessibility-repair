"""Portable evidence export; measurements remain byte-traceable to original records."""
import argparse,hashlib,json,shutil
from pathlib import Path
from cfar.io import write_json


def export(source,output):
    if output.exists():raise ValueError('new output path required')
    shutil.copytree(source,output)
    original=(source/'records.json').read_bytes()
    (output/'original-records.json').write_bytes(original)
    records=json.loads(original)
    for r in records:
        r['raw_record']=r['raw_record'].replace('\\','/')
        if r['certificate_path']:
            r['certificate_path']=str(Path(r['raw_record']).with_suffix('.certificate.json')).replace('\\','/')
    write_json(output/'records.json',records)
    write_json(output/'portable-export.json',dict(original_records_sha256=hashlib.sha256(original).hexdigest(),
        normalized_records_sha256=hashlib.sha256((output/'records.json').read_bytes()).hexdigest(),
        changes='Only path separators and certificate paths normalized; original records retained byte-for-byte. No status, measurement, objective or selected-action value changed.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();export(a.source,a.output)
