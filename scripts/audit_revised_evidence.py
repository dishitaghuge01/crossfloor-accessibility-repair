"""Audit normalized evidence and independently check paid rectangle overlap/cost."""
from collections import Counter,defaultdict
from fractions import Fraction
import hashlib,json
from pathlib import Path


def paid_rectangles(instance,selected):
    """Independent box arithmetic; no solver, Shapely or apply_actions call."""
    catalog={c['connection_id']:c for c in instance['connections']}
    actions={a['action_id']:a for a in instance['actions']}
    floor={r['room_id']:f['floor_id'] for f in instance['floors'] for r in f['rooms']}
    paid=[];owners={}
    for aid in selected:
        for e in actions[aid]['effects']:
            c=catalog[e['connection_id']]
            for r in c['geometry'].get('footprints',[]):
                xs,ys=zip(*r['polygon'])
                bounds=(min(xs),min(ys),max(xs),max(ys))
                owner=c['geometry']['asset_id']
                signature=(c['kind'],Fraction(str(c['geometry']['width_m'])),tuple(sorted(c['physical_profiles'])),bounds)
                if owner in owners and owners[owner]!=signature:raise ValueError('independent owner consistency')
                owners[owner]=signature
                paid.append((floor[r['room_id']],owner,bounds))
    for i,(f,a,bounds) in enumerate(paid):
        for g,b,other in paid[i+1:]:
            if f!=g or a==b:continue
            area=max(0,min(bounds[2],other[2])-max(bounds[0],other[0]))*max(0,min(bounds[3],other[3])-max(bounds[1],other[1]))
            if area>1e-8:raise ValueError('independent paid-owner overlap')
    return sum((Fraction(str(actions[a]['cost'])) for a in selected),Fraction(0))


def audit(root, *, replay_certificates=True):
    from cfar.io import fingerprint
    rows=json.loads((root/'records.json').read_text())
    from jsonschema import Draft202012Validator
    schema=json.loads((Path(__file__).resolve().parents[1]/'spec/evaluation-records.schema.json').read_text())
    Draft202012Validator(schema).validate(rows)
    if (root/'portable-export.json').exists():
        export=json.loads((root/'portable-export.json').read_text())
        original=(root/'original-records.json').read_bytes()
        if hashlib.sha256(original).hexdigest()!=export['original_records_sha256']:raise ValueError('original records changed')
        before=json.loads(original)
        for a,b in zip(before,rows):
            if {k:v for k,v in a.items() if k not in {'raw_record','certificate_path'}}!={k:v for k,v in b.items() if k not in {'raw_record','certificate_path'}}:raise ValueError('measurement changed during normalization')
        if len(before)!=len(rows):raise ValueError('record omission during export')
    source_maps=set();commits=set();counts=Counter();solutions=0;certs=set();certificate_hashes={};certificate_replays=0
    expected={};model_groups=defaultdict(set)
    for row in rows:
        raw=root/row['raw_record'];payload=json.loads(raw.read_text());meta=json.loads(raw.with_suffix('.manifest.json').read_text())
        instance=json.loads((raw.parent/'input.json').read_text())
        model_groups[fingerprint({k:v for k,v in instance.items() if k not in {'building_id','description'}})].add(row['instance_id'])
        if meta['git_dirty'] or meta['input_fingerprint']!=fingerprint(instance) or row['instance_sha256']!=fingerprint(instance):
            raise ValueError('unclean or changed input evidence')
        if row['status']!=payload['status'] or meta['solver_status']!=row['status']:raise ValueError('status mismatch')
        result=payload.get('result',{})
        selection=result.get('selected')
        if selection is None:selection=result.get('incumbent',{}).get('selected')
        cost=result.get('cost') or result.get('incumbent',{}).get('cost')
        if row['selected_action_ids']!=selection or row['objective_cost']!=cost:raise ValueError('raw objective/selection mismatch')
        for record_key,raw_key in [('function_seconds','function_seconds'),('replay_seconds','replay_seconds'),('peak_memory_bytes','peak_memory_bytes')]:
            if row[record_key]!=payload.get(raw_key):raise ValueError('raw measurement mismatch')
        if row['code_commit']!=meta['git_revision']:raise ValueError('revision mismatch')
        commits.add(meta['git_revision']);source_maps.add(json.dumps(meta['source_fingerprints'],sort_keys=True))
        counts[(row['solver'],row['status'])]+=1
        selected=row['selected_action_ids']
        if selected is not None:
            cost=paid_rectangles(instance,selected)
            if cost!=Fraction(row['objective_cost']) or len(selected)!=row['objective_action_count']:raise ValueError('objective mismatch')
            if not row['replay']['satisfied'] or row['replay']['delta_A']:raise ValueError('missing full replay')
            solutions+=1
        if row['solver'] not in {'greedy','greedy-improved'} and row['status'] in {'optimal','infeasible'}:
            label=(row['status'],row['objective_cost'],selected)
            if row['instance_id'] in expected and expected[row['instance_id']]!=label:raise ValueError('exact disagreement')
            expected[row['instance_id']]=label
        if row['certificate_path']:
            certificate=root/Path(row['raw_record']).with_suffix('.certificate.json')
            if not certificate.exists():raise ValueError('missing certificate')
            certs.add(str(certificate))
            certificate_hashes[str(certificate.relative_to(root)).replace('\\','/')]=hashlib.sha256(certificate.read_bytes()).hexdigest()
            if replay_certificates:
                from cfar.certificates import verify_certificate
                if not verify_certificate(instance,json.loads(certificate.read_text()),max_actions=8)['valid']:raise ValueError('independent oracle certificate failed')
                certificate_replays+=1
    if len(commits)!=1 or len(source_maps)!=1:raise ValueError('mixed code revisions')
    return dict(records=len(rows),instances=len({r['instance_id'] for r in rows}),represented_model_classes=len(model_groups),duplicate_model_recipes=[sorted(names) for names in model_groups.values() if len(names)>1],
        code_commit=next(iter(commits)),replayed_solutions=solutions,oracle_certificates=len(certs),certificate_replays=certificate_replays,certificates_sha256=certificate_hashes,
        outcomes={m:dict((s,n) for (method,s),n in counts.items() if method==m) for m in sorted({m for m,s in counts})},
        records_sha256=hashlib.sha256((root/'records.json').read_bytes()).hexdigest())


if __name__=='__main__':
    import argparse
    from cfar.io import write_json
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args()
    result=audit(a.root);write_json(a.root/'audit.json',result);print(json.dumps(result,indent=2))
