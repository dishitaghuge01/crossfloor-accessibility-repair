"""Re-evaluate existing semantic controls using the revised oracle certificates."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from cfar.certificates import verify_certificate
from cfar.io import manifest,write_json
from run_semantic_controls import control


def run(evidence,output):
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip():raise ValueError('commit source first')
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('fresh output required')
    rows=[]
    for name,mode in [('shared_asset','graph-only'),('shared_asset','no-owner-reuse'),('atomic_bundle','per-effect-price'),('unused_paid_geometry','graph-only')]:
        source=evidence/name
        instance=json.loads((source/'input.json').read_text())
        payload=json.loads((source/'oracle-0.json').read_text())
        certificate=json.loads((source/'oracle-0.certificate.json').read_text())
        if not verify_certificate(instance,certificate)['valid']:raise ValueError('baseline certificate failed')
        result=control(instance,payload['result'],mode)
        target=output/(name+'-'+mode)
        write_json(target/'input.json',instance);write_json(target/'result.json',result);write_json(target/'baseline-certificate.json',certificate)
        settings=dict(method='deliberate_semantic_control_v1',control=mode,
            source_oracle_sha256=hashlib.sha256((source/'oracle-0.json').read_bytes()).hexdigest(),
            source_certificate_sha256=hashlib.sha256((source/'oracle-0.certificate.json').read_bytes()).hexdigest(),
            runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        write_json(target/'manifest.json',manifest(instance,settings,result['status'],0));rows.append(dict(case=name,**result))
    write_json(output/'summary.json',rows)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.evidence,a.output)
