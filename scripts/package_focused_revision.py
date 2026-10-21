"""Package current manuscript plus explicitly separate frozen campaign history."""
import argparse,hashlib,json,shutil,subprocess,zipfile
from pathlib import Path


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def addtree(z,folder,prefix):
    for p in sorted(folder.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            z.write(p,prefix+'/'+p.relative_to(folder).as_posix())


def package(root,paper,summary,campaign,parameters,parameter_campaign,output):
    output.mkdir(parents=True,exist_ok=True)
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True).strip()
    staging=root/'runs/focused-revision-package-staging'
    staging.mkdir(parents=True,exist_ok=False)
    subprocess.run(['git','archive','--format=zip','--output='+str(staging/'source-code.zip'),revision],cwd=root,check=True)
    protocol=json.loads((campaign/'protocol.json').read_text())
    subprocess.run(['git','archive','--format=zip','--output='+str(staging/'measured-joint-source.zip'),protocol['code_revision']],cwd=root,check=True)
    shutil.copy2(paper/'master.pdf',output/'Crossfloor-Repair-Revised-Master.pdf')
    with zipfile.ZipFile(output/'Crossfloor-Repair-Revised-Paper-Source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(paper.rglob('*')):
            if p.is_file() and (p.name in ('master.tex','IEEEtran.cls') or p.parent.name=='figures'):
                z.write(p,p.relative_to(paper).as_posix())
    research=output/'Crossfloor-Repair-Revised-Research-Package.zip'
    with zipfile.ZipFile(research,'w',zipfile.ZIP_DEFLATED) as z:
        z.write(staging/'source-code.zip','source-code.zip')
        z.write(staging/'measured-joint-source.zip','measured-joint-source.zip')
        z.write(output/'Crossfloor-Repair-Revised-Paper-Source.zip','paper-source.zip')
        z.write(paper/'master.pdf','paper/master.pdf')
        addtree(z,campaign,'evidence/joint-primary')
        addtree(z,summary,'evidence/joint-summary')
        addtree(z,root/'runs/joint-network-complementary-dataset-2026-10-21','inputs/joint')
        addtree(z,parameters,'inputs/parameters')
        addtree(z,parameter_campaign,'evidence/parameters')
        addtree(z,root/'runs/cp-stage-diagnostic-clean-2026-10-21','evidence/cp-stage-diagnostic')
        # Preserve historical data as an immutable nested release. Never pool
        # its revisions with the current primary study in a single timing table.
        freeze=root/'runs/freeze-2026-10-21'
        z.write(freeze/'Crossfloor-Repair-Revised-Research-Package.zip','historical/frozen-research-package.zip')
        z.write(freeze/'Crossfloor-Repair-Revised-Master.pdf','historical/pre-revision-master.pdf')
        z.write(freeze/'Crossfloor-Repair-Supplementary-Evidence.pdf','supplementary/documentary-evidence.pdf')
        addtree(z,root/'experiments','registries')
        for name in ('contribution_claims.md','closest_work_matrix.md','experiment_protocol.md','manuscript_change_log.md',
            'event_schedule_specification.md','asynchronous_retirement_example.md','joint_network_protocol.md',
            'cp_stage_diagnostic_results.md','baseline_revision_notes.md'):
            z.write(root/'docs'/name,'docs/'+name)
        for p in ('master.tex','IEEEtran.cls'):
            z.write(root/'runs/network-paper-final'/p,'reproduction-base/'+p)
        for p in (root/'runs/network-paper-final/figures').glob('*.pdf'):
            z.write(p,'reproduction-base/figures/'+p.name)
    with zipfile.ZipFile(research,'a',zipfile.ZIP_DEFLATED) as z:
        contents={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
        z.writestr('CONTENTS.sha256.json',json.dumps(contents,indent=2)+'\n')
        assert z.testzip() is None
        assert not any(n.lower().endswith(('.ifc','.dwg')) for n in z.namelist())
    release=dict(reporting_revision=revision,joint_measured_revision=protocol['code_revision'],
        historical_observations=2362,joint_primary_observations=len(json.loads((campaign/'records.json').read_text())),
        separate_cp_diagnostic_observations=3,parameter_observations=len(json.loads((parameter_campaign/'records.json').read_text())),
        scope='Building-derived controlled experiments, hypothetical interventions/permissions/abstract costs; actual-building intervention validation not established; priority unconfirmed',
        artifacts={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in (
            output/'Crossfloor-Repair-Revised-Master.pdf',output/'Crossfloor-Repair-Revised-Paper-Source.zip',research)})
    (output/'Crossfloor-Repair-Release.json').write_text(json.dumps(release,indent=2)+'\n')
    hashes={p.name:sha(p) for p in (output/'Crossfloor-Repair-Revised-Master.pdf',output/'Crossfloor-Repair-Revised-Paper-Source.zip',research,output/'Crossfloor-Repair-Release.json')}
    (output/'Crossfloor-Repair-SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('root','paper','summary','campaign','parameters','parameter-campaign','output'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();package(a.root,a.paper,a.summary,a.campaign,a.parameters,a.parameter_campaign,a.output)
