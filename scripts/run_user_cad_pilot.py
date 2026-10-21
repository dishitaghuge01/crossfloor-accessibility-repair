"""Twelve isolated observations using the frozen revised-evaluation worker."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from cfar.io import fingerprint, manifest, write_json
from cfar.certificates import verify_certificate
from audit_revised_evidence import paid_rectangles


def run(dataset, output):
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip():
        raise ValueError('commit source before measurement')
    dm=json.loads((dataset/'dataset-manifest.json').read_text())
    if dm['git_dirty']:
        raise ValueError('regenerate dataset at clean revision')
    output.mkdir(parents=True,exist_ok=False)
    expected={'bundle':('optimal','3',['A']), 'separate':('optimal','4',['B','C']),
              'infeasible':('infeasible',None,None), 'single':('optimal','4',['D'])}
    rows=[];checks=0;certs=0
    for name in expected:
        source=dataset/'instances'/f'{name}.json'
        instance=json.loads(source.read_text());folder=output/name;folder.mkdir()
        write_json(folder/'input.json',instance)
        for method in ['compressed','uncompressed','oracle']:
            target=folder/f'{method}.json'
            completed=subprocess.run([sys.executable,'scripts/run_revised_evaluation.py','--worker',
                str(folder/'input.json'),method,str(target),'30'],capture_output=True,text=True,timeout=45)
            if completed.returncode:
                raise RuntimeError(completed.stderr)
            record=json.loads(target.read_text());result=record['result']
            label=(record['status'],result.get('cost'),result.get('selected'))
            if label!=expected[name]:
                raise ValueError(f'predeclared label mismatch: {name}/{method}/{label}')
            if result.get('selected') is not None:
                assert paid_rectangles(instance,result['selected'])==Fraction(result['cost'])
                assert record['replay']['satisfied'] and record['replay']['delta_A']==0
                checks+=1
            if method=='oracle':
                certificate=json.loads(target.with_suffix('.certificate.json').read_text())
                assert verify_certificate(instance,certificate,max_actions=8)['valid']
                certs+=1
            write_json(folder/f'{method}.manifest.json',manifest(instance,dict(
                method=method,repetitions=1,parent_seconds=45,worker_budget=30,
                classification='CAD-derived controlled input pilot; no speedup inference',
                source_sha256=dm['settings']['source_sha256'],dataset_manifest_sha256=hashlib.sha256(
                    (dataset/'dataset-manifest.json').read_bytes()).hexdigest()),record['status'],0))
            rows.append(dict(variant=name,method=method,input_fingerprint=fingerprint(instance),
                             raw_record=target.relative_to(output).as_posix(),**record))
        print(name,expected[name],flush=True)
    write_json(output/'records.json',rows)
    write_json(output/'audit.json',dict(observations=len(rows),optimal=sum(r['status']=='optimal' for r in rows),
        infeasible=sum(r['status']=='infeasible' for r in rows),independent_paid_rectangle_checks=checks,
        independently_reenumerated_oracle_certificates=certs,
        exact_label_agreement=True,seed=0,classification='ONE room-pair model;four catalogue variants',
        git_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        git_dirty=False,prior_frozen_observations=2274,new_observations=12))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['dataset','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();run(a.dataset,a.output)
