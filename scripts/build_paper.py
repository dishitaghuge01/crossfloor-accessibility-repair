"""Build a standalone manuscript from saved benchmark manifests; no fabricated rows."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import median
from cfar.io import fingerprint, write_json


def read_case(root, name):
    folder = root/name
    instance = json.loads((folder/'input.json').read_text())
    values = {}
    signatures = []
    for method in ('recognition', 'compressed', 'uncompressed', 'oracle'):
        samples = []
        for p in sorted(folder.glob(f'{method}-[0-9].json')):
            m = json.loads(p.with_suffix('.manifest.json').read_text())
            v = json.loads(p.read_text())
            if m['git_dirty'] or m['input_fingerprint'] != fingerprint(instance) or m['solver_status'] != v['status']:
                raise ValueError('manifest mismatch: '+str(p))
            if method != 'recognition' and v['status'] in ('optimal', 'infeasible'):
                r = v['result']
                signatures.append((r['status'], r['cost'], r['selected']))
                if method == 'oracle' and not v['verification']['valid']:
                    raise ValueError('invalid saved certificate')
                if r['status'] == 'optimal' and method != 'oracle':
                    if not r['reachability']['satisfied'] or any(a['delta'] != 0 for a in r['adjacency'].values()):
                        raise ValueError('strict replay mismatch')
            samples.append(v)
        if samples:
            values[method] = samples
    if signatures and any(s != signatures[0] for s in signatures):
        raise ValueError('exact status/cost/original-ID disagreement: '+name)
    return values


def timing(samples):
    return median(v['elapsed_seconds'] for v in samples)


def tables(root, building=False):
    names = sorted(p.name for p in root.iterdir() if p.is_dir()) if building else [
        'dense-8','dense-32','dense-64','dense-128','owners-2','owners-4','owners-8','owners-16','cyclic','rooms']
    lines = [r'\begin{center}\small', r'\begin{tabular}{lrrrrrl}', r'\toprule',
        r'Case & Rec. (s) & Comp. (s) & Full (s) & Raw & Kept & Cost/IDs \\', r'\midrule']
    for name in names:
        values = read_case(root, name)
        r = values['compressed'][0]['result'];stats=r['statistics']
        label = name.replace('duplex-', '').replace('owners-', 'h=').replace('dense-', 'n=')
        cost = r['cost'] if r['cost'] is not None else 'infeasible'
        ids = ','.join(r['selected'] or [])
        lines.append(f"{label} & {timing(values['recognition']):.4f} & {timing(values['compressed']):.4f} & {timing(values['uncompressed']):.4f} & {stats['peak_raw_states']} & {stats['peak_retained_states']} & {cost} {ids} " + r'\\')
    lines += [r'\bottomrule\end{tabular}', r'\end{center}',
        'Three timing samples per recognition/DP mode; medians in seconds. Comp./Full mean compressed/uncompressed end-to-end DP. Limits and all remaining cases are preserved in the complete CSV summary.']
    return '\n'.join(lines)


def chart(root):
    names = ['dense-8','dense-32','dense-64','dense-128']
    lines = [r'\begin{center}', r'\setlength{\unitlength}{1mm}', r'\begin{picture}(145,58)',
        r'\put(10,10){\vector(1,0){127}}', r'\put(10,10){\vector(0,1){44}}',
        r'\put(0,51){8 s}', r'\put(0,10){0}', r'\put(25,53){Dense catalogue: recognition and compressed end-to-end}']
    for i, name in enumerate(names):
        v=read_case(root,name);x=20+30*i
        for dx,method in [(0,'recognition'),(8,'compressed')]:
            height=timing(v[method])*5
            lines.append(f'\\put({x+dx},10){{\\rule{{6mm}}{{{height:.3f}mm}}}}')
        lines.append(f'\\put({x},4){{{name[6:]}}}')
    lines += [r'\end{picture}', 'Within each pair: recognition first, compressed end-to-end second. Candidates on horizontal axis. Independent timings; no subtraction.', r'\end{center}']
    return '\n'.join(lines)


def build(controlled, building, output, demo):
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('choose a fresh empty manuscript directory')
    # Audit every saved case, including operational failures excluded from compact tables.
    for root in (controlled, building):
        for folder in root.iterdir():
            if folder.is_dir():read_case(root, folder.name)
    demo_summary = json.loads((demo/'summary.json').read_text())
    if (demo_summary['before_satisfied'],demo_summary['after_satisfied'],demo_summary['cost'],demo_summary['delta_A'],demo_summary['certificate_valid']) != (1,4,'3',0,True):
        raise ValueError('motivating demo mismatch')
    before = json.loads((demo/'before.json').read_text())
    after = json.loads((demo/'result.json').read_text())['reachability']
    demo_lines = [r'\begin{center}\begin{tabular}{lll}\toprule', r'Obligation & Before & After \\', r'\midrule']
    for oid,path in sorted(before['paths'].items()):
        demo_lines.append(f"{oid} & {'satisfied' if path else 'unmet'} & {'satisfied' if after['paths'][oid] else 'unmet'} " + r'\\')
    demo_lines += [r'\bottomrule\end{tabular}\end{center}', 'Motivating authored before/after case: complete action A costs three; adjacency change is zero.']
    template = Path(__file__).resolve().parents[1]/'paper/manuscript.template.tex'
    text = template.read_text(encoding='utf-8').replace('@@CONTROLLED_TABLE@@',tables(controlled)+'\n'+chart(controlled)).replace('@@BUILDING_TABLE@@',tables(building,True)).replace('@@DEMO_TABLE@@','\n'.join(demo_lines))
    (output/'manuscript.tex').write_text(text,encoding='utf-8')
    provenance = dict(template_sha256=hashlib.sha256(template.read_bytes()).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), inputs={})
    for root in (controlled,building,demo):
        for p in sorted(root.rglob('*.json')):
            provenance['inputs'][str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
    write_json(output/'paper-provenance.json',provenance)
    return output/'manuscript.tex'


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--controlled',type=Path,required=True)
    parser.add_argument('--building',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--demo',type=Path,required=True)
    args=parser.parse_args()
    print(build(args.controlled,args.building,args.output,args.demo))
