"""Semantic controls are deliberate invalid simplifications, not repair baselines."""
import argparse
from decimal import Decimal
import hashlib
from itertools import combinations
import json
from pathlib import Path

from cfar.actions import apply_actions
from cfar.errors import ValidationError
from cfar.interface_recognition import recognize_physical_interface
from cfar.io import fingerprint, manifest, write_json
from cfar.objective import action_cost, exact_product, exact_sum
from cfar.obligations import verify_obligations
from cfar.oracle import enumerate_action_subsets
from cfar.validation import baseline_active


def control(instance, oracle, mode):
    actions = {a['action_id']:a for a in instance['actions']}
    feasible = {tuple(row['selected']) for row in oracle['ledger'] if row['status']=='feasible'}
    recognized = recognize_physical_interface(instance)
    best = None
    for selected in enumerate_action_subsets(list(actions)):
        if mode == 'graph-only':
            active = baseline_active(instance)
            for aid in selected:
                for effect in actions[aid]['effects']:
                    cid = effect['connection_id']
                    active[cid] = sorted(set(active.get(cid,[])) | set(effect['permitted_profiles']))
            if not verify_obligations(instance,active)['satisfied']:
                continue
        else:
            if tuple(selected) not in feasible:
                continue
            if mode == 'no-owner-reuse' and any(set(recognized['action_cells'][a]) & set(recognized['action_cells'][b]) for a,b in combinations(selected,2)):
                continue
        objective = action_cost(instance,selected)
        if mode == 'per-effect-price':
            objective = exact_sum(exact_product(Decimal(str(actions[a]['cost'])),Decimal(len(actions[a]['effects']))) for a in selected)
        key=(objective,len(selected),tuple(selected))
        if best is None or key<best:best=key
    if best is None:
        return dict(status='control-infeasible',mode=mode)
    selected=list(best[2])
    try:
        repair=apply_actions(instance,selected)
        physical_valid=verify_obligations(instance,repair['active'])['satisfied']
        error=None
    except ValidationError as e:
        physical_valid=False;error=e.code
    return dict(status='control-optimum',mode=mode,control_objective=str(best[0]),original_cost=str(action_cost(instance,selected)),
        selected=selected,full_model_valid=physical_valid,full_model_error=error,
        strict_cost=oracle['cost'],strict_selected=oracle['selected'],
        interpretation='Deliberate semantic simplification; not an alternative valid repair baseline.')


def run(evidence,output):
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('choose a fresh empty directory')
    rows=[]
    for name,mode in [('shared_asset','graph-only'),('shared_asset','no-owner-reuse'),('atomic_bundle','per-effect-price'),('unused_paid_geometry','graph-only')]:
        source=evidence/name
        instance=json.loads((source/'input.json').read_text())
        payload=json.loads((source/'oracle-0.json').read_text())
        source_manifest=json.loads((source/'oracle-0.manifest.json').read_text())
        assert source_manifest['input_fingerprint']==fingerprint(instance) and not source_manifest['git_dirty']
        assert payload['verification']['valid']
        result=control(instance,payload['result'],mode)
        folder=output/(name+'-'+mode)
        write_json(folder/'input.json',instance);write_json(folder/'result.json',result)
        settings=dict(method='deliberate_semantic_control_v1',control=mode,variant='SCFAR',
            baseline_manifest_sha256=hashlib.sha256((source/'oracle-0.manifest.json').read_bytes()).hexdigest(),
            baseline_certificate_sha256=hashlib.sha256((source/'oracle-0.json').read_bytes()).hexdigest(),
            baseline_revision=source_manifest['git_revision'],runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            scope='not a valid repair optimizer comparison; no runtime comparison',timeout=None)
        write_json(folder/'manifest.json',manifest(instance,settings,result['status'],seed=0))
        rows.append(dict(case=name,**result))
    write_json(output/'summary.json',rows)
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--evidence',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(run(args.evidence,args.output))
