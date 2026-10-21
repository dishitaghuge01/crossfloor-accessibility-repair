"""Frozen two-family scaling protocol; existing unmodified solver workers."""
import argparse,json
from pathlib import Path
import run_joint_network_study as driver


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--private-bays',action='store_true')
    a=p.parse_args();driver.METHODS=['floor','both','cp-sat'] if a.private_bays else ['both','cp-sat']
    cases=json.loads((a.dataset/'dataset.json').read_text())['cases']
    driver.run(a.dataset.resolve(),a.output.resolve(),[c['instance_id'] for c in cases],90)
