"""Regenerate CSV/Markdown summaries from saved measurements and manifests."""
import argparse
import csv
import json
from pathlib import Path
from statistics import median


def summarize(output):
    rows = []
    for folder in sorted(output.iterdir()):
        if not folder.is_dir():
            continue
        for method in ('recognition', 'compressed', 'uncompressed', 'oracle'):
            paths = sorted(folder.glob(f'{method}-[0-9]*.json'))
            paths = [p for p in paths if '.manifest.' not in p.name]
            if not paths:
                continue
            values = [json.loads(p.read_text(encoding='utf-8')) for p in paths]
            manifests = [json.loads(p.with_suffix('.manifest.json').read_text(encoding='utf-8')) for p in paths]
            if any(m['git_dirty'] for m in manifests):
                raise ValueError('dirty-revision evidence')
            result = values[0].get('result', {})
            stats = result.get('statistics', {})
            parameters = result.get('parameters', {})
            times = [v['elapsed_seconds'] for v in values if 'elapsed_seconds' in v]
            rows.append(dict(case=folder.name, method=method, category=manifests[0]['settings']['category'],
                samples=len(values), statuses=','.join(sorted({v['status'] for v in values})),
                median_seconds=median(times) if len(times) == len(values) else '',
                cost=result.get('cost', ''), selected=json.dumps(result.get('selected', [])),
                peak_raw=stats.get('peak_raw_states', ''), peak_retained=stats.get('peak_retained_states', ''),
                rows_removed=stats.get('representative_rows_removed', ''),
                parameters=json.dumps(parameters, sort_keys=True), revision=manifests[0]['git_revision']))
    if not rows:
        raise ValueError('no saved measurements')
    with (output/'summary.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = ['# Controlled benchmark summary', '',
        'Median worker wall time. DP includes its internal recognition and repair replay. Separate recognition timings are not subtracted. Oracle certificate replay is outside its timed solve.', '',
        '| Case | Method | Status | n | Seconds | Cost | Raw | Retained | Removed |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        seconds = f"{r['median_seconds']:.6f}" if r['median_seconds'] != '' else '—'
        lines.append(f"| {r['case']} | {r['method']} | {r['statuses']} | {r['samples']} | {seconds} | {r['cost']} | {r['peak_raw']} | {r['peak_retained']} | {r['rows_removed']} |")
    lines += ['', 'Authored fixed-2D inputs; no public-building evidence or established literature priority. Timeout/limit/unsupported statuses are not infeasibility. Dense cases use a cost-one analytical bound; only small oracle cases have exhaustive replay certificates.', '']
    (output/'summary.md').write_text('\n'.join(lines), encoding='utf-8')
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    summarize(parser.parse_args().output)
