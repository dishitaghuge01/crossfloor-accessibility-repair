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
    staging=root/('runs/focused-revision-package-'+revision[:10])
    staging.mkdir(parents=True,exist_ok=False)
    subprocess.run(['git','archive','--format=zip','--output='+str(staging/'source-code.zip'),revision],cwd=root,check=True)
    protocol=json.loads((campaign/'protocol.json').read_text())
    subprocess.run(['git','archive','--format=zip','--output='+str(staging/'measured-joint-source.zip'),protocol['code_revision']],cwd=root,check=True)
    frontier_protocol=json.loads((root/'runs/local-band-final-2026-10-22/protocol.json').read_text())
    subprocess.run(['git','archive','--format=zip','--output='+str(staging/'measured-frontier-source.zip'),frontier_protocol['code_revision']],cwd=root,check=True)
    kernel=json.loads((summary/'summary.json').read_text())['kernel_fingerprints']
    assert kernel==json.loads((root/'runs/event-width-summary-2026-10-21/summary.json').read_text())['kernel_fingerprints']
    with zipfile.ZipFile(staging/'measured-kernel-bytes.zip','w',zipfile.ZIP_DEFLATED) as z:
        paths=list((root/'src/cfar').glob('*.py'))+[root/'spec/instance.schema.json',root/'spec/enums.json']
        assert {p.name for p in paths}==set(kernel)
        for p in paths:
            assert sha(p)==kernel[p.name],p.name
            z.write(p,p.relative_to(root).as_posix())
        z.writestr('source_fingerprints.json',json.dumps(kernel,indent=2)+'\n')
    shutil.copy2(paper/'master.pdf',output/'Crossfloor-Repair-Revised-Master.pdf')
    with zipfile.ZipFile(output/'Crossfloor-Repair-Revised-Paper-Source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(paper.rglob('*')):
            if p.is_file() and (p.name in ('master.tex','IEEEtran.cls') or p.parent.name=='figures'):
                z.write(p,p.relative_to(paper).as_posix())
    benchmark=output/'Crossfloor-Intervention-Benchmark.zip'
    input_sources=[('joint','joint-network-complementary-dataset-2026-10-21'),
        ('parameters','parameter-dataset-2026-10-21'),('event-width','event-width-inputs-2026-10-21'),
        ('matched','matched-permissions-inputs-2026-10-22'),('local-bands','local-band-final-inputs-2026-10-22'),
        ('private-bays','private-bay-final-inputs-2026-10-22')]
    inputs={}
    with zipfile.ZipFile(benchmark,'w',zipfile.ZIP_DEFLATED) as z:
        z.write(staging/'source-code.zip','source-code.zip')
        z.write(root/'docs/INTERVENTION_BENCHMARK.md','README.md')
        addtree(z,root/'runs/frontier-certificates-2026-10-22','validation/static-certificates')
        addtree(z,root/'runs/local-band-references-2026-10-22','validation/local-band-references')
        for name in ('transient_frontier_theorem.md','local_band_subclass.md','frontier_scaling_protocol.md','frontier_scaling_results.md'):
            z.write(root/'docs'/name,'docs/'+name)
        for name,folder in input_sources:
            addtree(z,root/'runs'/folder,'inputs/'+name)
            for f in (root/'runs'/folder/'instances').glob('*.json'):
                from cfar.io import fingerprint
                inputs['inputs/'+name+'/instances/'+f.name]=fingerprint(json.loads(f.read_text()))
        assert len(inputs)==55
        z.writestr('INPUT_MANIFEST.json',json.dumps(dict(instance_files=len(inputs),
            distinct_canonical_fingerprints=len(set(inputs.values())),instances=inputs,
            scope='Controlled authored/building-derived annotations; no verified construction catalogue or prices'),indent=2)+'\n')
    # Reopen the finalized directory before reading Windows-written members.
    with zipfile.ZipFile(benchmark,'a',zipfile.ZIP_DEFLATED) as z:
        hashes={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
        z.writestr('CONTENTS.sha256.json',json.dumps(hashes,indent=2)+'\n')
        assert z.testzip() is None
    research=output/'Crossfloor-Repair-Revised-Research-Package.zip'
    with zipfile.ZipFile(research,'w',zipfile.ZIP_DEFLATED) as z:
        z.write(staging/'source-code.zip','source-code.zip')
        z.write(staging/'measured-joint-source.zip','measured-joint-source.zip')
        z.write(staging/'measured-frontier-source.zip','measured-frontier-source.zip')
        z.write(benchmark,'intervention-benchmark.zip')
        z.write(staging/'measured-kernel-bytes.zip','measured-kernel-bytes.zip')
        z.write(output/'Crossfloor-Repair-Revised-Paper-Source.zip','paper-source.zip')
        z.write(paper/'master.pdf','paper/master.pdf')
        if (paper/'pdf-qa.json').exists():z.write(paper/'pdf-qa.json','paper/pdf-qa.json')
        addtree(z,campaign,'evidence/joint-primary')
        addtree(z,summary,'evidence/joint-summary')
        addtree(z,root/'runs/joint-network-complementary-dataset-2026-10-21','inputs/joint')
        addtree(z,parameters,'inputs/parameters')
        addtree(z,parameter_campaign,'evidence/parameters')
        addtree(z,root/'runs/parameter-summary-2026-10-21','evidence/parameter-summary')
        addtree(z,root/'runs/event-width-inputs-2026-10-21','inputs/event-width-followup')
        addtree(z,root/'runs/event-width-final-2026-10-21','evidence/event-width-followup')
        addtree(z,root/'runs/event-width-summary-2026-10-21','evidence/event-width-summary')
        addtree(z,root/'runs/matched-permissions-inputs-2026-10-22','inputs/matched-permissions')
        addtree(z,root/'runs/matched-permissions-final-2026-10-22','evidence/matched-permissions')
        addtree(z,root/'runs/matched-permissions-summary-2026-10-22','evidence/matched-permissions-summary')
        addtree(z,root/'runs/local-band-final-2026-10-22','evidence/local-band-scaling')
        addtree(z,root/'runs/private-bay-final-2026-10-22','evidence/private-bay-scaling')
        addtree(z,root/'runs/local-band-summary-2026-10-22','evidence/local-band-summary')
        addtree(z,root/'runs/private-bay-summary-2026-10-22','evidence/private-bay-summary')
        addtree(z,root/'runs/frontier-scaling-summary-2026-10-22','evidence/frontier-scaling-summary')
        addtree(z,root/'runs/frontier-certificates-2026-10-22','evidence/frontier-certificates')
        addtree(z,root/'runs/local-band-references-2026-10-22','evidence/local-band-references')
        addtree(z,root/'runs/local-band-final-inputs-2026-10-22','inputs/local-bands')
        addtree(z,root/'runs/private-bay-final-inputs-2026-10-22','inputs/private-bays')
        z.write(root/'runs/frontier-hardware-2026-10-22.json','evidence/frontier-hardware.json')
        z.write(root/'runs/frontier-memory-2026-10-22.json','evidence/frontier-memory.json')
        for p in (root/'runs').glob('local-band*pilot*'):
            if p.is_dir():addtree(z,p,'excluded-development/frontier-pilots/'+p.name)
            elif p.is_file():z.write(p,'excluded-development/frontier-pilots/'+p.name)
        addtree(z,root/'runs/relevant-segment-controls-2026-10-21','evidence/relevant-segment-controls')
        addtree(z,root/'runs/building-network-dataset','reproduction-base-network')
        addtree(z,root/'runs/cp-stage-diagnostic-clean-2026-10-21','evidence/cp-stage-diagnostic')
        addtree(z,root/'runs/cp-stage-diagnostic-2026-10-21','excluded-development/overlapping-cp-diagnostic')
        addtree(z,root/'runs/joint-network-final-2026-10-21','excluded-development/nested-demand-launch')
        z.write(root/'runs/greedy-profile-2026-10-21.json','excluded-development/greedy-replay-profile.json')
        # Preserve historical data as an immutable nested release. Never pool
        # its revisions with the current primary study in a single timing table.
        freeze=root/'runs/freeze-2026-10-21'
        z.write(freeze/'Crossfloor-Repair-Revised-Research-Package.zip','historical/frozen-research-package.zip')
        z.write(freeze/'Crossfloor-Repair-Revised-Master.pdf','historical/pre-revision-master.pdf')
        z.write(freeze/'Crossfloor-Repair-Supplementary-Evidence.pdf','supplementary/documentary-evidence.pdf')
        addtree(z,root/'experiments','registries')
        for name in ('contribution_claims.md','closest_work_matrix.md','experiment_protocol.md','manuscript_change_log.md',
            'event_schedule_specification.md','asynchronous_retirement_example.md','joint_network_protocol.md',
            'cp_stage_diagnostic_results.md','baseline_revision_notes.md','parameter_study_protocol.md',
            'revision_completion.md','review_refinement_2026-10-22.md','transient_frontier_theorem.md',
            'local_band_subclass.md','frontier_scaling_protocol.md','frontier_scaling_results.md','INTERVENTION_BENCHMARK.md',
            'modern_connectivity_comparison.md','generic_state_comparison.md'):
            z.write(root/'docs'/name,'docs/'+name)
        z.write(root/'paper/REPRODUCE_FOCUSED_REVISION.md','REPRODUCE.md')
        z.write(root/'runs/artifact-reproduction-2026-10-21.json','artifact-reproduction.json')
        reproduction=json.loads((root/'runs/artifact-reproduction-2026-10-21.json').read_text())
        z.write(root/'runs'/reproduction['source_archive'],'verified-reporting-source.zip')
        z.write(root/'runs/revision-2026-10-21-figures/asynchronous-retirement.pdf','explanatory-figures/asynchronous-retirement.pdf')
        for p in ('master.tex','IEEEtran.cls'):
            z.write(root/'runs/network-paper-final'/p,'reproduction-base/'+p)
        for p in (root/'runs/network-paper-final/figures').glob('*.pdf'):
            z.write(p,'reproduction-base/figures/'+p.name)
    with zipfile.ZipFile(research,'a',zipfile.ZIP_DEFLATED) as z:
        contents={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()}
        z.writestr('CONTENTS.sha256.json',json.dumps(contents,indent=2)+'\n')
        assert z.testzip() is None
        assert not any(n.lower().endswith(('.ifc','.dwg')) for n in z.namelist())
    release=dict(reporting_revision=revision,joint_measured_revision=protocol['code_revision'],frontier_measured_revision=frontier_protocol['code_revision'],
        historical_observations=2362,joint_primary_observations=len(json.loads((campaign/'records.json').read_text())),
        separate_cp_diagnostic_observations=3,parameter_observations=len(json.loads((parameter_campaign/'records.json').read_text())),
        event_width_followup_observations=24,matched_permission_observations=8,local_band_scaling_observations=36,
        private_bay_scaling_observations=24,included_timed_observations=2845,untimed_relevant_segment_controls=7,
        untimed_independent_local_band_checks=9,untimed_static_frontier_certificates=13,
        manuscript=json.loads((paper/'pdf-qa.json').read_text()),
        scope='Authored and building-derived controlled experiments, hypothetical interventions/permissions/abstract costs; actual-building intervention validation not established; priority over applicable generic methods unconfirmed',
        artifacts={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in (
            output/'Crossfloor-Repair-Revised-Master.pdf',output/'Crossfloor-Repair-Revised-Paper-Source.zip',research,benchmark)})
    (output/'Crossfloor-Repair-Release.json').write_text(json.dumps(release,indent=2)+'\n')
    hashes={p.name:sha(p) for p in (output/'Crossfloor-Repair-Revised-Master.pdf',output/'Crossfloor-Repair-Revised-Paper-Source.zip',research,benchmark,output/'Crossfloor-Repair-Release.json')}
    (output/'Crossfloor-Repair-SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('root','paper','summary','campaign','parameters','parameter-campaign','output'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();package(a.root,a.paper,a.summary,a.campaign,a.parameters,a.parameter_campaign,a.output)
