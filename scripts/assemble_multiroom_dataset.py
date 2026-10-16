"""Assemble a provenance-audited two/three-storey controlled IFC dataset."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
from cfar.io import fingerprint,write_json
from build_multiroom_experiments import build as build_two
from extend_multiroom_storeys import build as build_three


def build(audit_root,output):
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip():raise ValueError('commit source before release extraction')
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('fresh output required')
    build_two(audit_root/'audits',output/'two-storey')
    build_three(audit_root/'audits',output/'two-storey',output/'three-storey')
    target=output/'instances';target.mkdir()
    inventory={p.stem:json.loads(p.read_text()) for p in (audit_root/'audits').glob('*.json') if not p.name.endswith(('-reference.json','-selection.json'))}
    generated={}
    for folder in ['two-storey','three-storey']:
        for p in sorted((output/folder/'instances').glob('*.json')):
            name=p.stem.split('-')[0];source=inventory[name];instance=json.loads(p.read_text())
            source_rooms={r['global_id']:r for r in source['spaces']};ranks={s['global_id']:i for i,s in enumerate(source['storeys'])}
            order=[ranks[f['floor_id']] for f in instance['floors']]
            if any(b!=a+1 for a,b in zip(order,order[1:])):raise ValueError('skipped original storey')
            for f in instance['floors']:
                for r in f['rooms']:
                    original=source_rooms[r['room_id']]
                    if r['polygon']!=original['polygon'] or f['floor_id']!=original['storey_id']:raise ValueError('source room altered')
            shutil.copy2(p,target/p.name)
            generated[p.name]=dict(instance_fingerprint=fingerprint(instance),source_building_id=name,source_sha256=source['provenance']['sha256'],
                rooms_per_floor=[len(f['rooms']) for f in instance['floors']],adjacency_per_floor=[len(f['adjacency_edges']) for f in instance['floors']])
    root=Path(__file__).resolve().parents[1]
    paths=[root/'scripts/public_building_controlled.py',root/'scripts/build_multiroom_experiments.py',root/'scripts/extend_multiroom_storeys.py',root/'scripts/source_room_selection.py',Path(__file__),root/'docs/public_ifc_sources.json']
    write_json(output/'dataset-manifest.json',dict(git_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        source_hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        source_inventory_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (audit_root/'audits').glob('*.json') if p.stem in inventory},
        generated=generated,seed=0,classification='building-derived controlled experiment; hypothetical doors, reservations, profiles, permissions and abstract costs; not validated actual-building repairs'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.audit,a.output)
