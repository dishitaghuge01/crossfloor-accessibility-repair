"""Append new frozen network evidence and the refreshed manuscript to the release."""
import argparse,hashlib,json,subprocess,zipfile
from datetime import datetime,timezone
from pathlib import Path

def digest(b):return hashlib.sha256(b).hexdigest()
def makezip(entries,path):
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for n,d in sorted(entries.items()):z.writestr(n,d)

def package(base,paper,evidence,dataset,summary,audits,extension,preliminary,output,staging):
 assert not subprocess.check_output(['git','status','--porcelain'],text=True).strip()
 staging.mkdir(parents=True,exist_ok=False)
 with zipfile.ZipFile(base) as z:
  assert z.testzip() is None;entries={n:z.read(n) for n in z.namelist()}
 old=json.loads(entries['release.json']);assert old['observations']==2286
 source={}
 for name in list(entries):
  if name.startswith('paper/'):
   rel=name[6:]
   if rel not in ('master.pdf','pdf-qa.json'):
    entries['network-reproduction-base/'+rel]=entries[name]
    source['network-reproduction-base/'+rel]=entries[name]
   del entries[name]
 for p in paper.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(paper).as_posix()
  if rel in ('master.tex','master.pdf','IEEEtran.cls','pdf-qa.json','network-section.tex','network-findings.json') or rel.startswith('figures/'):
   entries['paper/'+rel]=p.read_bytes();source[rel]=p.read_bytes()
 for p in evidence.rglob('*.json'):
  entries['evidence/building-network/'+p.relative_to(evidence).as_posix()]=p.read_bytes()
 for p in dataset.rglob('*.json'):
  entries['evidence/building-network-dataset/'+p.relative_to(dataset).as_posix()]=p.read_bytes()
 for name in ('clinic','molio'):
  entries['evidence/building-network-source-inventories/'+name+'.json']=(audits/(name+'.json')).read_bytes()
 for p in summary.rglob('*'):
  if p.is_file() and p.suffix in ('.json','.pdf','.png'):
   entries['evidence/building-network-summary/'+p.relative_to(summary).as_posix()]=p.read_bytes()
 for p in extension.rglob('*.json'):
  entries['evidence/building-network-budget-extension/'+p.relative_to(extension).as_posix()]=p.read_bytes()
 for p in preliminary.rglob('*.json'):
  entries['evidence/building-network-preliminary/'+p.relative_to(preliminary).as_posix()]=p.read_bytes()
 for name in ('network_study_results.md','network_study_protocol.md','event_lifetime_correctness.md','review_response.md','revised_delivery_report.md','revised_master_disposition.md'):
  entries[name]=(Path('docs')/name).read_bytes()
 entries['REPRODUCE_NETWORK_STUDY.md']=Path('paper/REPRODUCE_NETWORK_STUDY.md').read_bytes()
 source['REPRODUCE_NETWORK_STUDY.md']=entries['REPRODUCE_NETWORK_STUDY.md']
 entries['README.md']=b'''# Current research package: building-network / event-lifetime study

Start with network_study_results.md and REPRODUCE_NETWORK_STUDY.md.
paper/master.pdf is the current detailed master. The documentary/CAD evidence
supplement remains supplementary-evidence/paper/master.pdf. Earlier negative
results remain frozen. The new study has70 primary plus6 separate larger-budget observations on15 price variants,
five catalogue layouts and TWO source buildings; do not count15 buildings.
Geometry, profiles, candidate permissions and prices have distinct evidence
status. All network interventions/prices/access are hypothetical. No actual
building construction repair or broad algorithmic superiority is certified.

network-reproduction-base/ is the previous19-page main source, used ONLY as
an input to build_network_master.py. reproduction-base/ is the earlier
combined source used for the prior reporting revision. Neither is current.
All raw/source IFC,DWG/PDF and private extracts remain excluded. The shared
geometry memoization benefits every current method. Measurement revision and
current source snapshot revision are separately recorded in release.json.
'''
 archive=staging/'source-code.zip'
 subprocess.run(['git','archive','--format=zip','--output='+str(archive.resolve()),'HEAD'],check=True)
 entries['source-code-pre-network.zip']=entries['source-code.zip']
 entries['source-code.zip']=archive.read_bytes()
 s=json.loads((summary/'summary.json').read_text());ext=json.loads((summary/'extension-summary.json').read_text());qa=json.loads((paper/'pdf-qa.json').read_text())
 old['historical_gap_assessment']=old.pop('gap_assessment')
 old.update(earlier_building_inputs=8,building_inputs=23,network_constructive_feasibility_checks=15,
  main_figures=20,supplementary_figures=2,created_utc=datetime.now(timezone.utc).isoformat(),
  code_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  network_measurement_revision=s['code_commit'],network_extension_revision=ext['code_commit'],observations=2362,main_observations=2350,
  previous_observations=2286,network_observations=76,network_core_observations=70,network_extension_observations=6,network_source_buildings=2,
  network_catalogue_layouts=5,network_price_variants=15,pdf_qa=qa,
  independently_checked_returned_selections=1949+s['returned_selections_checked']+ext['returned_selections_checked'],
  independent_oracle_certificates=62,
  practical_advantage='bounded DP completion gain; see paired CP-SAT comparison; no general superiority',
  building_optimization_difficulty='expanded controlled networks, up to190 actions/103 destinations/22 cycles; unverified intervention assumptions',
  classification='Detailed research master with separate new building-network study; hypothetical interventions; priority and actual-building repair validation unconfirmed.')
 entries['release.json']=(json.dumps(old,indent=2)+'\n').encode()
 entries['content-sha256.json']=(json.dumps({n:digest(d) for n,d in entries.items() if n!='content-sha256.json'},indent=2,sort_keys=True)+'\n').encode()
 full=output/'Crossfloor-Repair-Revised-Research-Package.zip';src=output/'Crossfloor-Repair-Revised-Paper-Source.zip'
 # Keep the existing evidence supplement available in the paper source archive.
 for n,d in entries.items():
  if n.startswith('supplementary-evidence/paper/'):
   source['supplementary-evidence/'+n[len('supplementary-evidence/paper/'):]]=d
 makezip(entries,full);makezip(source,src)
 targets=[full,src]
 for data,name in [(entries['paper/master.pdf'],'Crossfloor-Repair-Revised-Master.pdf'),
                   (entries['release.json'],'Crossfloor-Repair-Release.json'),
                   (entries['network_study_results.md'],'network_study_results.md')]:
  p=output/name;p.write_bytes(data);targets.append(p)
 for name in ('review_response.md','revised_delivery_report.md','revised_master_disposition.md'):
  p=output/name;p.write_bytes(entries[name]);targets.append(p)
 # Preserve independently delivered supplementary PDF and its integrity entry.
 targets.append(output/'Crossfloor-Repair-Supplementary-Evidence.pdf')
 (output/'Crossfloor-Repair-SHA256.json').write_text(json.dumps({p.name:digest(p.read_bytes()) for p in targets},indent=2)+'\n')
 print('Packaged',old['observations'],'observations; current source',old['code_commit'])

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for key in ('base','paper','evidence','dataset','summary','audits','extension','preliminary','output','staging'):p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();package(a.base,a.paper,a.evidence,a.dataset,a.summary,a.audits,a.extension,a.preliminary,a.output,a.staging)
