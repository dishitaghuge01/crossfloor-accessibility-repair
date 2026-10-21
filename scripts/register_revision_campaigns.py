"""Canonical included/excluded campaign registry, including immutable history."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import zipfile

from cfar.io import fingerprint,write_json
import register_frozen_campaigns

ROOT=Path(__file__).resolve().parents[1]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    register_frozen_campaigns.main()
    def read(name):
        with (ROOT/'experiments'/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
    campaigns=read('campaign_registry.csv');instances=read('instance_registry.csv')
    for row in campaigns:
        row['record_path']='historical/frozen-research-package.zip!'+row['record_path']
        row['included_in_totals']='yes'
    def add(cid,folder,archive,role,case_metadata=None,default_case=None,included=True):
        rows=json.loads((folder/'records.json').read_text())
        protocol=json.loads((folder/'protocol.json').read_text())
        counts=Counter(r.get('instance_id') or r.get('case') or default_case for r in rows)
        revision=protocol.get('code_revision') or next((r.get('code_revision') or r.get('code_commit') for r in rows if r.get('code_revision') or r.get('code_commit')), 'not_reliably_recorded')
        campaigns.append(dict(campaign_id=cid,code_revision=revision,observations=len(rows),
            record_path=archive+'/records.json',record_sha256=digest(folder/'records.json'),role=role,
            unique_instance_ids=len(counts),included_in_totals='yes' if included else 'no'))
        if not included:return
        meta=case_metadata or {c['instance_id']:c for c in protocol.get('cases',[])}
        for iid,n in sorted(counts.items()):
            c=meta[iid]
            instances.append(dict(campaign_id=cid,instance_id=iid,input_fingerprint=c['input_fingerprint'],observations=n,
                source_building_id=c['source_building_id'],geometry_subset_id=c['geometry_subset_id'],
                catalogue_layout_id=c['catalogue_layout_id'],permission_pattern_id=c['permission_pattern_id'],
                conflict_pattern_id=c['conflict_pattern_id'],price_seed=c['price_seed'],solver_seed=0,
                repeat_index='see_per_run_record'))
    primary=ROOT/'runs/joint-network-complementary-final-2026-10-21'
    parameters=ROOT/'runs/parameter-final-2026-10-21'
    add('joint-primary',primary,'evidence/joint-primary','frozen_primary')
    add('parameters',parameters,'evidence/parameters','separate_structural')
    add('event-width-followup',ROOT/'runs/event-width-final-2026-10-21','evidence/event-width-followup','posthoc_event_width')
    diagnostic=ROOT/'runs/cp-stage-diagnostic-clean-2026-10-21'
    iid='clinic-network-48-s0'
    meta={iid:dict(source_building_id='clinic',geometry_subset_id='clinic-frozen-network-rooms',
        catalogue_layout_id='clinic-network-48',permission_pattern_id='identical',conflict_pattern_id='disjoint',
        price_seed=0,input_fingerprint=fingerprint(json.loads((diagnostic/'input.json').read_text())))}
    add('cp-stage-diagnostic',diagnostic,'evidence/cp-stage-diagnostic','posthoc_diagnostic',meta,iid)
    add('excluded-overlapping-cp',ROOT/'runs/cp-stage-diagnostic-2026-10-21',
        'excluded-development/overlapping-cp-diagnostic','excluded_development',default_case=iid,included=False)
    add('excluded-nested-demand',ROOT/'runs/joint-network-final-2026-10-21',
        'excluded-development/nested-demand-launch','excluded_development',included=False)
    frozen=ROOT/'runs/freeze-2026-10-21/Crossfloor-Repair-Revised-Research-Package.zip'
    with zipfile.ZipFile(frozen) as z:
        path='evidence/building-network-preliminary/records.json'
        rows=json.loads(z.read(path))
        campaigns.append(dict(campaign_id='excluded-unit-granularity-network',
            code_revision=next((r.get('code_commit') for r in rows if r.get('code_commit')),'see_archive'),
            observations=len(rows),record_path='historical/frozen-research-package.zip!'+path,
            record_sha256=hashlib.sha256(z.read(path)).hexdigest(),role='excluded_development',
            unique_instance_ids=len({r['case'] for r in rows}),included_in_totals='no'))
    control=ROOT/'runs/relevant-segment-controls-2026-10-21'
    cert=json.loads((control/'controls.json').read_text())
    first=json.loads(next(control.glob('*.manifest.json')).read_text())
    campaigns.append(dict(campaign_id='relevant-segment-controls',code_revision=first['git_revision'],
        observations=0,record_path='evidence/relevant-segment-controls/controls.json',record_sha256=digest(control/'controls.json'),
        role='untimed_constructive_controls',unique_instance_ids=len(cert['cases']),included_in_totals='no'))
    primary_meta={c['instance_id']:c for c in json.loads((primary/'protocol.json').read_text())['cases']}
    for c in cert['cases']:
        m=primary_meta[c['instance_id']]
        instances.append(dict(campaign_id='relevant-segment-controls',instance_id=c['instance_id'],input_fingerprint=c['input_fingerprint'],
            observations=0,**{k:m[k] for k in ('source_building_id','geometry_subset_id','catalogue_layout_id','permission_pattern_id','conflict_pattern_id','price_seed')},
            solver_seed='not_applicable',repeat_index='not_applicable'))
    generated=ROOT/'runs/joint-network-complementary-dataset-2026-10-21'
    dataset=json.loads((generated/'dataset.json').read_text())
    campaigns.append(dict(campaign_id='joint-generated-inputs',code_revision=json.loads((primary/'protocol.json').read_text())['code_revision'],
        observations=0,record_path='inputs/joint/dataset.json',record_sha256=digest(generated/'dataset.json'),
        role='input_generation_only',unique_instance_ids=len(dataset['cases']),included_in_totals='no'))
    for c in dataset['cases']:
        instances.append(dict(campaign_id='joint-generated-inputs',instance_id=c['instance_id'],input_fingerprint=c['input_fingerprint'],
            observations=0,**{k:c[k] for k in ('source_building_id','geometry_subset_id','catalogue_layout_id','permission_pattern_id','conflict_pattern_id','price_seed')},
            solver_seed='not_run',repeat_index='not_applicable'))
    total=sum(int(c['observations']) for c in campaigns if c['included_in_totals']=='yes')
    assert total==2777
    for name,rows in [('campaign_registry.csv',campaigns),('instance_registry.csv',instances)]:
        with (ROOT/'experiments'/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write_json(ROOT/'experiments/revision-campaign-manifest.json',dict(included_timed_observations=total,
        frozen_historical=2362,joint_primary=112,structural_parameters=276,posthoc_event_width=24,separate_cp_diagnostic=3,
        untimed_relevant_segment_controls=7,excluded_campaigns=[c for c in campaigns if c['role']=='excluded_development'],
        path_notation='archive.zip!member is a member of an immutable nested archive',
        campaign_registry_sha256=digest(ROOT/'experiments/campaign_registry.csv'),
        instance_registry_sha256=digest(ROOT/'experiments/instance_registry.csv')))
    print('Canonical included timed observations:',total)


if __name__=='__main__':main()
