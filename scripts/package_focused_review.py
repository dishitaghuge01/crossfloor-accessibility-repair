"""Repackage frozen evidence with the corrected research-first manuscript."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from datetime import datetime,timezone


def digest(data):return hashlib.sha256(data).hexdigest()


def zip_entries(entries,target):
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for name,data in sorted(entries.items()):z.writestr(name,data)


def package(base_archive,focused,output,staging):
    if subprocess.check_output(['git','status','--porcelain'],text=True).strip():
        raise ValueError('commit reviewable revision before packaging')
    staging.mkdir(parents=True,exist_ok=False);output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(base_archive) as z:
        assert z.testzip() is None
        old={n:z.read(n) for n in z.namelist()}
    oldrelease=json.loads(old['release.json'])
    assert oldrelease['observations']==2286 and oldrelease['cad_observations']==12
    moved={'city_hall_admission.md','city_hall_documentary_protocol.md',
           'supplied_document_evidence_review.md','supplied_document_evidence.json',
           'marble_hill_evidence_screen.md','gap_assessment_completion.md',
           'user_cad_protocol.md','user_cad_results.md','building_evidence_search_guide.md',
           'REPRODUCE_DOCUMENTARY.md','REPRODUCE_GAP_ASSESSMENT.md','REPRODUCE_USER_CAD.md'}
    entries={};source={}
    existing_base=any(n.startswith('reproduction-base/') for n in old)
    for name,data in old.items():
        if name in {'content-sha256.json','release.json','README.md','source-code.zip',
                    'revised_delivery_report.md','revised_master_disposition.md'}:continue
        if name.startswith('paper/'):
            relative=name[len('paper/'):]
            if not existing_base and relative not in {'master.pdf','pdf-qa.json'}:
                entries['reproduction-base/'+relative]=data
                source['reproduction-base/'+relative]=data
            continue
        if name.startswith('reproduction-base/'):
            source[name]=data
        dest=name
        if name in moved or name.startswith(('evidence/city-hall-documentary/','evidence/user-cad-')):
            dest='supplementary-evidence/'+name
        entries[dest]=data
    for part,prefix in [('main','paper/'),('supplement','supplementary-evidence/paper/')]:
        for path in sorted((focused/part).rglob('*')):
            if not path.is_file() or 'preview' in path.parts:continue
            relative=path.relative_to(focused/part).as_posix()
            if relative in {'master.tex','master.pdf','IEEEtran.cls','pdf-qa.json'} or relative.startswith('figures/'):
                data=path.read_bytes();entries[prefix+relative]=data
                source[relative if part=='main' else 'supplementary-evidence/'+relative]=data
    for name in ['revised_delivery_report.md','revised_master_disposition.md','review_response.md']:
        entries[name]=(Path('docs')/name).read_bytes()
    entries['REPRODUCE_FOCUSED_REVIEW.md']=Path('paper/REPRODUCE_FOCUSED_REVIEW.md').read_bytes()
    entries['reporting-audit.json']=(focused/'reporting-audit.json').read_bytes()
    entries['supplementary-evidence/README.md']=Path('docs/supplementary_evidence/README.md').read_bytes()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    code=staging/'source-code.zip'
    subprocess.run(['git','archive','--format=zip','--output='+str(code.resolve()),'HEAD'],check=True)
    entries['source-code.zip']=code.read_bytes()
    metadata=dict(oldrelease)
    metadata.update(created_utc=datetime.now(timezone.utc).isoformat(),code_commit=commit,pdf_qa=json.loads((focused/'main/pdf-qa.json').read_text()),
        supplementary_pdf_qa=json.loads((focused/'supplement/pdf-qa.json').read_text()),
        main_observations=2274,supplementary_cad_observations=12,
        practical_advantage='not_established',building_optimization_difficulty='decision_simple_catalogues',
        reporting_audit_sha256=digest(entries['reporting-audit.json']),
        classification='Corrected research-first review manuscript; separate documentary/CAD supplement; practical advantage, difficult building optimization and literature priority not established.')
    entries['release.json']=(json.dumps(metadata,indent=2)+'\n').encode()
    entries['README.md']=b'''# Research-first review package

Read review_response.md and revised_delivery_report.md. paper/master.pdf is
the corrected main manuscript. Documentary admission studies and the small
CAD pilot are in supplementary-evidence/paper/master.pdf and its evidence
subtree. They do not establish difficult practical building optimization.

The main study has2274 observations; the separate CAD pilot has12. No new
benchmark was run for this revision. The original evidence is preserved.
See reporting-audit.json for corrected TableVIII cells/statuses and source
record hashes. Feasible greedy runs count as completed without optimality.
Read REPRODUCE_FOCUSED_REVIEW.md for the current artifact reproduction path.
reproduction-base/ is an archival source input,not the current manuscript.
Its staged wording/table is corrected by build_focused_master.py.
source-code.zip contains the current clean source snapshot.

No raw IFC,DWG,source PDF or private extracts are redistributed. Permission
for source-level CAD reconstruction must be obtained separately. Controlled
permissions/candidates/costs remain hypothetical. No practical advantage,
complete-construction priority,construction validation or acceptance is asserted.
'''
    entries['content-sha256.json']=(json.dumps({n:digest(d) for n,d in entries.items()},indent=2,sort_keys=True)+'\n').encode()
    source['REPRODUCE_FOCUSED_REVIEW.md']=entries['REPRODUCE_FOCUSED_REVIEW.md']
    source['reporting-audit.json']=entries['reporting-audit.json']
    full=output/'Crossfloor-Repair-Revised-Research-Package.zip'
    src=output/'Crossfloor-Repair-Revised-Paper-Source.zip'
    zip_entries(entries,full);zip_entries(source,src)
    generated=[full,src]
    for origin,name in [(focused/'main/master.pdf','Crossfloor-Repair-Revised-Master.pdf'),
                        (focused/'supplement/master.pdf','Crossfloor-Repair-Supplementary-Evidence.pdf'),
                        (Path('docs/review_response.md'),'review_response.md'),
                        (Path('docs/revised_delivery_report.md'),'revised_delivery_report.md'),
                        (Path('docs/revised_master_disposition.md'),'revised_master_disposition.md')]:
        target=output/name;target.write_bytes(origin.read_bytes());generated.append(target)
    release=output/'Crossfloor-Repair-Release.json';release.write_bytes(entries['release.json']);generated.append(release)
    (output/'Crossfloor-Repair-SHA256.json').write_text(json.dumps({p.name:digest(p.read_bytes()) for p in generated},indent=2)+'\n')
    print('Packaged corrected main and separate evidence supplement at',commit)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['base-archive','focused','output','staging']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();package(a.base_archive,a.focused,a.output,a.staging)
