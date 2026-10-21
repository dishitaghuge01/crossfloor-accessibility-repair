"""Local review-package assembly after PDF QA and a clean final commit."""
import argparse,hashlib,json,shutil,subprocess,zipfile
from datetime import datetime,timezone
from pathlib import Path


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def zip_tree(folder,target):
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as archive:
        for p in sorted(folder.rglob('*')):
            if p.is_file():archive.write(p,p.relative_to(folder).as_posix())


def package(paper,output,staging,qa):
    root=Path.cwd()
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip():raise ValueError('commit final source before packaging')
    staging.mkdir(parents=True,exist_ok=True)
    if any(staging.iterdir()):raise ValueError('fresh release staging required')
    output.mkdir(parents=True,exist_ok=True)
    review=staging/'review-package';review.mkdir()
    paper_target=review/'paper';paper_target.mkdir()
    for filename in ['master.tex','IEEEtran.cls','master.pdf','master-provenance.json','summary.csv','followup-summary.csv','followup-provenance.json','base-master.tex','pre-documentary-master.tex','documentary-provenance.json']:
        shutil.copy2(paper/filename,paper_target/filename)
    gap_assessment = (paper/'gap-assessment-provenance.json').exists()
    if gap_assessment:
        for filename in ['pre-gap-master.tex','gap-assessment-provenance.json']:
            shutil.copy2(paper/filename,paper_target/filename)
        shutil.copy2(root/'paper/REPRODUCE_GAP_ASSESSMENT.md',review/'REPRODUCE_GAP_ASSESSMENT.md')
        for filename in ['generic_state_comparison.md','marble_hill_evidence_screen.md','gap_assessment_completion.md']:
            shutil.copy2(root/'docs'/filename,review/filename)
    cad_pilot = (paper/'cad-provenance.json').exists()
    if cad_pilot:
        for filename in ['pre-cad-master.tex','cad-provenance.json','cad-wall-underlay.json']:
            shutil.copy2(paper/filename,paper_target/filename)
        shutil.copy2(root/'paper/REPRODUCE_USER_CAD.md',review/'REPRODUCE_USER_CAD.md')
        for filename in ['user_cad_protocol.md','user_cad_results.md']:
            shutil.copy2(root/'docs'/filename,review/filename)
    shutil.copytree(paper/'figures',paper_target/'figures')
    shutil.copy2(qa,paper_target/'pdf-qa.json')
    for name in ['REPRODUCE_REVISED.md','REPRODUCE_FOLLOWUP.md','REPRODUCE_DOCUMENTARY.md']:
        shutil.copy2(root/'paper'/name,review/name)
    for name in ['revised_master_disposition.md','supported_contribution_boundary.md','revised_evaluation_protocol.md','revised_checkpoint_results.md','revised_delivery_report.md','followup_results.md','followup_protocol.md','followup_priority_check.md','continued_priority_assessment.md','building_evidence_search_guide.md','supplied_document_evidence_review.md','supplied_document_evidence.json','city_hall_admission.md','city_hall_documentary_protocol.md']:
        shutil.copy2(root/'docs'/name,review/name)
    code=review/'source-code.zip'
    subprocess.run(['git','archive','--format=zip','--output='+str(code.resolve()),'HEAD'],check=True)
    evidence=review/'evidence';evidence.mkdir()
    for source,name in [('runs/revised-controlled-portable','controlled'),('runs/revised-building-portable','building'),
                        ('runs/revised-building-dataset','source-dataset'),('runs/revised-semantic-controls','semantic-controls'),
                        ('runs/revised-geometry-profile','geometry-profile'),('runs/revised-license-audit','source-licences'),('runs/followup-ablations-isolated','followup-ablations'),('runs/followup-index-equivalence','index-equivalence'),('runs/followup-cli-smoke','cli-smoke')]:
        shutil.copytree(root/source,evidence/name)
    documentary=evidence/'city-hall-documentary';documentary.mkdir()
    for name in ['scalar-records.json','plan-audit.json','item-headings.json','admission.json']:
        shutil.copy2(root/'runs/city-hall-documentary-final'/name,documentary/name)
    if cad_pilot:
        cad_data=evidence/'user-cad-dataset';cad_data.mkdir()
        for filename in ['source-audit.json','dataset-manifest.json']:
            shutil.copy2(root/'runs/user-cad-dataset'/filename,cad_data/filename)
        for directory in ['instances','recognition']:
            shutil.copytree(root/'runs/user-cad-dataset'/directory,cad_data/directory)
        shutil.copytree(root/'runs/user-cad-evaluation',evidence/'user-cad-evaluation')
    shutil.copy2(root/'requirements-documentary.lock.txt',review/'requirements-documentary.lock.txt')
    inventory=evidence/'source-inventory'/'audits';inventory.mkdir(parents=True)
    for source in (root/'runs/revised-source-audit/audits').glob('*.json'):
        if not source.name.endswith(('-reference.json','-selection.json')):shutil.copy2(source,inventory/source.name)
    shutil.copy2(root/'runs/revised-source-audit/provenance.json',inventory.parent/'provenance.json')
    shutil.copy2(root/'runs/revised-release-tests.txt',review/'regression-log.txt')
    shutil.copy2(root/'runs/followup-release-tests.txt',review/'followup-regression-initial.txt')
    shutil.copy2(root/'runs/followup-temp-recheck-corrected.txt',review/'followup-regression-corrected.txt')
    shutil.copy2(root/'requirements-release.lock.txt',review/'requirements-release.lock.txt')
    ca=json.loads((evidence/'controlled/audit.json').read_text());ba=json.loads((evidence/'building/audit.json').read_text())
    fa=json.loads((evidence/'followup-ablations/audit.json').read_text())
    da=json.loads((documentary/'admission.json').read_text())
    metadata=dict(created_utc=datetime.now(timezone.utc).isoformat(),code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        authored_commit=ca['code_commit'],building_commit=ba['code_commit'],observations=ca['records']+ba['records']+fa['records'],original_observations=ca['records']+ba['records'],followup_observations=fa['records'],followup_code_commit=fa['code_commit'],independently_checked_returned_selections=ca['replayed_solutions']+ba['replayed_solutions']+fa['independent_solution_checks'],
        authored_recipes=ca['instances'],represented_authored_models=ca['represented_model_classes'],building_inputs=ba['instances'],
        independent_oracle_certificates=ca['certificate_replays']+ba['certificate_replays'],
        documentary_scalar_entries=da['scalar_rows'],documentary_priced_rows_checked=da['priced_rows_checked'],documentary_extraction_commit=da['manifest']['git_revision'],new_documentary_physical_instances=0,
        pdf_qa=json.loads(qa.read_text()),classification='Detailed IEEE-format advisor-review master; source-derived controlled experiments use hypothetical annotations; literature priority/independent human proof review remain open; no submission or push.')
    (review/'release.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    if gap_assessment:
        metadata.update(gap_assessment=json.loads((paper/'gap-assessment-provenance.json').read_text()),
                        literature_priority='unconfirmed', actual_building_validation='not_established')
        (review/'release.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    if cad_pilot:
        cad=json.loads((evidence/'user-cad-evaluation/audit.json').read_text())
        metadata.update(cad_observations=cad['observations'],cad_code_commit=cad['git_revision'],
                        cad_catalogue_variants=4,cad_room_pair_models=1,
                        cad_classification='permission-backed CAD-derived controlled experiment; hypothetical interventions')
        metadata['observations']+=cad['observations']
        metadata['independently_checked_returned_selections']+=cad['independent_paid_rectangle_checks']
        metadata['independent_oracle_certificates']+=cad['independently_reenumerated_oracle_certificates']
        (review/'release.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    readme='''# Cross-floor repair revised review package

Read revised_delivery_report.md, followup_results.md, city_hall_admission.md and revised_master_disposition.md first. The additional 180 observations are separate from the frozen original campaign.
The compiled paper and standalone source are in paper/. Unzip source-code.zip
into a fresh folder to inspect/reproduce code. The evidence/ directory contains
all reported raw/normalized results, independent certificates, source inventories,
source/derived-input fingerprints, licence notices and experimental assumptions.
Raw IFCs and excluded timing pilots are intentionally omitted. The pinned
downloader restores source files; all benchmark annotations/permissions/costs
remain hypothetical controlled assumptions, not actual-building repair evidence. Documentary historical prices are separate; no new physical instance is admitted. Source PDFs, drawings and private extracted wording are excluded. See REPRODUCE_DOCUMENTARY.md.

For offline evidence audits from the extracted source-code root:

```text
python -m pip install -r ../requirements-release.lock.txt
python -m pip install -e . --no-deps
python scripts/audit_revised_evidence.py ../evidence/controlled
python scripts/audit_revised_evidence.py ../evidence/building
```

Adjust relative paths to your extraction layout. The full regeneration commands
are in REPRODUCE_REVISED.md. For reanalysis with the supplied frozen inputs use
--controlled ../evidence/controlled --building ../evidence/building,
--source-audit ../evidence/source-dataset/two-storey,
--three-audit ../evidence/source-dataset/three-storey,
--controls ../evidence/semantic-controls and
--geometry-profile ../evidence/geometry-profile. Generate fresh figures before
running the manuscript builder. Paper/master.tex also compiles directly with its
local IEEEtran.cls and figures/. Follow actual venue/authorship rules later.
No priority certificate, human proof approval or acceptance guarantee is asserted.
'''
    if gap_assessment:
        readme += '\nAppendix G and the related-work resource comparison are regenerated by REPRODUCE_GAP_ASSESSMENT.md after the documentary stage. Read gap_assessment_completion.md for source-access limits. Priority remains unconfirmed and actual-building validation is not established. That assessment stage added no new timed observations or physical inputs.\n'
    if cad_pilot:
        readme += '\nAppendix H adds a separate12-observation CAD pilot at a pinned clean revision. Delivered totals are2286 observations,1949 returned-selection checks and62 independently replayed oracle certificates. Read user_cad_results.md and REPRODUCE_USER_CAD.md. Raw DWG/decoded/private extracts are excluded; anonymized derived inputs and cropped plotting segments are supplied for review. Source-level reconstruction requires authorized access to the original DWG. Intervention slots/profiles/elevations/costs remain experimental, not verified actual-building repair data.\n'
    (review/'README.md').write_text(readme,encoding='utf-8')
    files={p.relative_to(review).as_posix():sha(p) for p in review.rglob('*') if p.is_file()}
    (review/'content-sha256.json').write_text(json.dumps(files,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    pdf=output/'Crossfloor-Repair-Revised-Master.pdf';shutil.copy2(paper/'master.pdf',pdf)
    source_zip=output/'Crossfloor-Repair-Revised-Paper-Source.zip';zip_tree(paper_target,source_zip)
    full_zip=output/'Crossfloor-Repair-Revised-Research-Package.zip';zip_tree(review,full_zip)
    for name in ['revised_master_disposition.md','revised_delivery_report.md','followup_results.md','city_hall_admission.md']:
        shutil.copy2(root/'docs'/name,output/name)
    shutil.copy2(review/'release.json',output/'Crossfloor-Repair-Release.json')
    hashes={p.name:sha(p) for p in [pdf,source_zip,full_zip,output/'revised_master_disposition.md',output/'revised_delivery_report.md',output/'Crossfloor-Repair-Release.json',output/'followup_results.md',output/'city_hall_admission.md']}
    (output/'Crossfloor-Repair-SHA256.json').write_text(json.dumps(hashes,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(metadata,indent=2));print('PACKAGE',full_zip,full_zip.stat().st_size,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for key in ['paper','output','staging','qa']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();package(a.paper,a.output,a.staging,a.qa)
