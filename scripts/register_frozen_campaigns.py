"""Index the immutable pre-revision evidence without rewriting observations."""
import csv
import hashlib
import json
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGNS = [
    ('controlled', 'evidence/controlled/records.json', '25aa069c1d7430e0e0768a2c20289a415ad9f813'),
    ('building', 'evidence/building/records.json', '0a1f0e23facaaefe77ff1c1eeab5e82c7f5858e5'),
    ('followup', 'evidence/followup-ablations/records.json', '77a38447d04bda2239bacf214e51d38de6704ca2'),
    ('cad', 'supplementary-evidence/evidence/user-cad-evaluation/records.json', 'f6e1ea5e24d3d3d3afbe7b7970190587688afd7d'),
    ('network', 'evidence/building-network/records.json', 'f1e5d188738e53cdfe9f3532d036398e97e1d278'),
    ('network-extension', 'evidence/building-network-budget-extension/records.json', '7c2a3b2e48300d705da7d62ed426d4305012ff2d'),
]


def main():
    archive = ROOT / 'runs/freeze-2026-10-21/Crossfloor-Repair-Revised-Research-Package.zip'
    campaigns, instances = [], []
    with zipfile.ZipFile(archive) as z:
        for cid, path, rev in CAMPAIGNS:
            rows = json.loads(z.read(path))
            groups = defaultdict(list)
            for r in rows:
                iid = r.get('case') or r.get('instance_id') or r['variant']
                groups[iid].append(r)
            campaigns.append(dict(campaign_id=cid, code_revision=rev,
                observations=len(rows), record_path=path,
                record_sha256=hashlib.sha256(z.read(path)).hexdigest(),
                role='posthoc_budget' if 'extension' in cid else 'historical_frozen',
                unique_instance_ids=len(groups)))
            for iid, rs in sorted(groups.items()):
                r = rs[0]
                network = cid.startswith('network')
                instances.append(dict(campaign_id=cid, instance_id=iid,
                    input_fingerprint=r.get('input_fingerprint', r.get('instance_sha256', '')),
                    observations=len(rs),
                    source_building_id=iid.split('-')[0] if network else 'not_recorded',
                    geometry_subset_id='not_recorded',
                    catalogue_layout_id=iid.rsplit('-s', 1)[0] if network else iid,
                    permission_pattern_id='identical_profiles' if network else 'not_recorded',
                    conflict_pattern_id='disjoint_owners' if network else 'not_recorded',
                    price_seed=iid.rsplit('-s', 1)[-1] if network else 'not_recorded',
                    solver_seed='see_per_run_manifest', repeat_index='see_per_run_record'))
    assert sum(c['observations'] for c in campaigns) == 2362
    for name, rows in [('campaign_registry', campaigns), ('instance_registry', instances)]:
        with (ROOT / 'experiments' / f'{name}.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(f'Registered {len(campaigns)} campaigns, {len(instances)} campaign-instance pairs, 2362 observations')


if __name__ == '__main__':
    main()
