"""Separate counterbalanced structural campaign; never pool with buildings."""
import argparse
import json
from pathlib import Path
import run_joint_network_study as driver


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    driver.METHODS=list(driver.CONFIG)+['cp-sat']
    cases=json.loads((a.dataset/'dataset.json').read_text())['cases']
    driver.run(a.dataset.resolve(),a.output.resolve(),[c['instance_id'] for c in cases],30)
