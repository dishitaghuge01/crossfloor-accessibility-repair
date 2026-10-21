"""Construct and check nonoptimal feasibility controls, without optimization."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
from cfar.actions import apply_actions
from cfar.io import fingerprint, write_json
from cfar.obligations import verify_obligations
from audit_revised_evidence import paid_rectangles


def check(inputs, output):
    rows = []
    for path in sorted(inputs.glob('*.json')):
        a = json.loads(path.read_text())
        required = {o[k] for o in a['obligations'] for k in ('source', 'target')}
        catalog = {c['connection_id']: c for c in a['connections']}
        selected = [action['action_id'] for action in a['actions']
                    if action['action_id'].startswith('S')
                    and all({catalog[e['connection_id']]['u'], catalog[e['connection_id']]['v']}
                            <= required for e in action['effects'])]
        repair = apply_actions(a, selected)
        assert verify_obligations(repair['instance'], repair['active'])['satisfied']
        assert not any(x['delta'] for x in repair['adjacency'].values())
        cost = paid_rectangles(a, selected)
        assert cost == sum((Fraction(str(action['cost'])) for action in a['actions']
                            if action['action_id'] in selected), Fraction(0))
        rows.append(dict(case=path.stem,input_fingerprint=fingerprint(a),selected=selected,
                         cost=str(cost),satisfied=True,delta_A=0,paid_box_check=True))
    assert len(rows) == 15
    write_json(output,dict(classification='constructive feasibility controls; not optimality certificates or timed solver observations',
                           method='all individual segment purchases inside the declared potential root network',
                           checked=len(rows),cases=rows))
    print('Checked15 explicit nonoptimal feasibility witnesses; no optimizer run.')


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--instances',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();check(args.instances,args.output)
