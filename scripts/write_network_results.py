"""Write the concise evidence disposition from audited outcome summaries."""
import json
from pathlib import Path
from statistics import median


def write(summary,findings,target,extension=None):
 d=json.loads(summary.read_text());f=json.loads(findings.read_text());rows=d['methods']
 text='''# Building-network and event-lifetime results\n\nThis is new experimental work, not a relabeling of the earlier evidence.\nThe original2274 main observations and12 CAD observations stay frozen.\n\n## What changed\n\nOptional last-use cell/vertex forgetting uses the existing owned-interface\nDP. Cells expire after their last complete occupying unit; profile vertices\nexpire after their last incident action/baseline event. Physical ownership\nstill remains live throughout each complete unit, all paid effects remain,\nand vanished unanchored components still reject the state. Both flags default\noff. A compilation-local geometry cache is shared by every current method.\nThe worst-case theorem and priority qualification are unchanged.\n\nThe final code passes765 regression tests in72.93s. New tests compare exact\nlabels with exhaustive search and cached/uncached geometry outcomes.\n\n## Workload and independence units\n\nThe clinic uses253 retained original room projections across three original\nstoreys. Molio uses93 across eight. Five catalogue layouts, with three abstract\nprice seeds each, produce15 controlled inputs from TWO buildings. Do not\ncount them as15 buildings. The fixed70-observation campaign has rotated\nsix-method ordering (without reversing the primary pair), fresh processes,30-second parent deadlines and explicit\nrepetition roles. All manifests report clean revisionCOMMIT. See protocol\nand source/hash records in the package.\n\nUnlike the earlier two/three-action catalogues, the largest clinic input\nhas190 purchases,103 destinations,47 bundled purchases,102 active components\nafter baseline contraction and22 independent cycles. Molio's potential active\ngraph is sparser; eight source storeys do not by themselves make it hard.\nTwo route-profile layers have identical permissions/demands here, and the\nseparated grid does not create competing-owner overlaps. These limitations\nare explicit; semantic/owner-conflict tests remain separate evidence.\n\nAll baseline door annotations, profiles, reservations, connector designs,\npermissions and costs are hypothetical assumptions. Original room geometry\nand source identity are retained; verified construction data are not supplied.\nThis is building-derived controlled network evaluation, not validated actual\nbuilding repairs.\n\n## Measured outcomes\n\nFINDING\n\n| Source / columns,seed0 | Original DP | Lifetime DP | CP-SAT |\n| --- | --- | --- | --- |\n'''.replace('COMMIT',d['code_commit']).replace('FINDING',f['finding'])
 for name in sorted(n for n in d['structures'] if n.endswith('-s0')):
  vals=[]
  for method in ('uncompressed','lifetime-uncompressed','cp-sat'):
   r=next(r for r in rows if r['case']==name and r['method']==method)
   status=', '.join(str(v)+' '+k for k,v in r['statuses'].items())
   time=f"; completed median {r['seconds_median']:.3f}s" if r['seconds_median'] is not None else ''
   vals.append(status+time)
  text+='| '+name+' | '+' | '.join(vals)+' |\n'
 text+='''\nAll 15 inputs additionally have explicit, replay-checked nonoptimal segment
controls. Seed 0 costs are 342 for the 78-action clinic (exact DP optimum 267),
726 for the 190-action clinic, and 198 for the 152-action Molio case. These
checks establish feasibility under the declared model, not optimality or
construction validation; they are not extra timed solver observations.

Every returned selection is checked for paid rectangular overlap, original\natomic cost, required reachability and delta_A=0. Source room rings/IDs are\nchecked against the frozen inventories. Exact labels agree wherever more\nthan one method completes. Large results are not exhaustively certified.\n\nCP-SAT's exact count/ID tie stages can be expensive. The manuscript separately\nreports cost-stage and tie-stage search time. A faster complete pipeline or\na deadline win must not be represented as superiority at minimum-cost\noptimization. Single-run controls and price checks are labeled separately\nfrom three-repetition timing comparisons. Failures are retained in full.\n\n## What this does and does not settle\n\nThe implementation now has a demonstrated completion-range improvement over\nits original DP, and evaluation includes substantially larger active networks.\nGeneral superiority over CP-SAT, representative real-building performance,\nverified physical interventions and literature priority are not established.\nThe earlier15 unfavorable connectivity timings remain unchanged; weighted\nrank reduction is not credited for the new event-forgetting improvement.\nThe incomplete earlier clean campaign is retained as preliminary, without\nsplicing its timings into the final70 observations.\n'''
 if extension:
  e=json.loads(extension.read_text());text+='\n## Larger-budget boundary check\n\n'+e['finding']+'\n'
 for old,new in [('original2274','original 2274'),('and12','and 12'),('passes765','passes 765'),('in72.93','in 72.93'),('uses253','uses 253'),('uses93','uses 93'),('produce15','produce 15'),('as15','as 15'),('fixed70','fixed 70'),('processes,30','processes, 30'),('revisionf1','revision f1'),('has190','has 190'),(',103',', 103'),(',47',', 47'),(',102',', 102'),('and22','and 22'),('earlier15','earlier 15'),('final70','final 70'),('columns,seed0','columns, seed 0')]:text=text.replace(old,new)
 target.write_text(text)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser()
 for k in ('summary','findings','output'):p.add_argument('--'+k,type=Path,required=True)
 p.add_argument('--extension',type=Path);a=p.parse_args();write(a.summary,a.findings,a.output,a.extension)
