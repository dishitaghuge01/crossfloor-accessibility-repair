"""Frozen 8 inputs x 3 methods x 2 fresh repetitions; 45/40 second budgets."""
import argparse,json
from pathlib import Path
import run_joint_network_study as driver

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();driver.METHODS=['both','locality','cp-sat']
    cases=json.loads((a.dataset/'dataset.json').read_text())['cases']
    driver.run(a.dataset.resolve(),a.output.resolve(),[c['instance_id'] for c in cases],45)
