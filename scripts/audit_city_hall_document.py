"""Pinned documentary admission audit. No room polygons or repairs are inferred."""
import argparse,hashlib,json,re,subprocess,sys,platform,importlib.metadata
from collections import Counter
from decimal import Decimal,InvalidOperation
from pathlib import Path

SOURCE_SHA256='31b125ed7371564f3c7e4254237464cac7bf9fc1ff68bb8c46dec556d9fcf3a1'
SOURCE_URL='https://santabarbaraca.gov/sites/default/files/documents/Government/Transition%20Plan%20Update%20Report/Technical%20Appendix%20A%20-%201%20City%20Hall%20and%20City%20Hall%20Annex.pdf'
UNITS={'JOB','LF','SF','EA','EACH','REF.','REF','SY','PAIR'}


def number(text, *, money=False):
    value=text.strip()
    if money:
        if not value.startswith('$'):return None
        value=value[1:]
    if not re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?',value):return None
    return Decimal(value.replace(',',''))



def scalar_row(cells):
    unit=cells['unit'].strip();q=number(cells['quantity']);u=number(cells['unit_cost'],money=True);t=number(cells['total_cost'],money=True)
    ref=unit.rstrip('.')=='REF'
    return dict(unit_type=unit,quantity=str(q) if q is not None else None,
        source_unit_cost=str(u) if u is not None else None,source_total_cost=str(t) if t is not None else None,
        accounting_role='reference_not_independent_action' if ref else 'priced_observation_not_admitted_action',
        independent_action_cost=None,quantity_price_matches_total=(q*u==t) if not ref and None not in (q,u,t) else None)


def extract(pdf,output):
    import pdfplumber
    digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest!=SOURCE_SHA256:raise ValueError('source hash changed; re-audit instead of silently parsing another revision')
    output.mkdir(parents=True,exist_ok=False)
    rows=[];plans=[];unrecognized=[];section=None;item=None;headings=[];private=[]
    with pdfplumber.open(pdf) as doc:
        assert len(doc.pages)==264
        for n,page in enumerate(doc.pages,1):
            if n in [44,119,197]:
                plans.append(dict(pdf_page=n,level={44:'first',119:'second',197:'basement'}[n],
                    page_points=[page.width,page.height],text_characters=len(page.chars),vector_lines=len(page.lines),vector_rectangles=len(page.rects),vector_curves=len(page.curves),
                    raster_images=[dict(pixel_dimensions=list(im['srcsize']),bits=im['bits']) for im in page.images],
                    metric_scale_verified=False,room_polygons_extracted=False,room_adjacency_verified=False,floor_elevations_verified=False))
            words=page.extract_words(extra_attrs=['fontname','size'])
            if not words:continue
            top=' '.join(page.crop((20,35,760,75)).extract_text().upper().split())
            local=next((s for s in ['FIRST FLOOR','SECOND FLOOR','BASEMENT','PUBLIC RIGHT-OF-WAY','SITE'] if s in top),None)
            anchors=[w for w in words if 554<=w['x0']<580 and 100<w['top']<530 and w['size']<9 and w['text'] in UNITS]
            if not anchors:continue
            if local!=section:section=local;item=None
            item_heads=sorted([w for w in words if 45<=w['x0']<70 and 100<w['top']<530 and w['size']>11.5 and w['text'].isdigit()],key=lambda w:w['top'])
            for head in item_heads:
                money=[w['text'] for w in words if w['x0']>620 and abs(w['top']-head['top'])<1 and w['text'].startswith('$')]
                headings.append(dict(pdf_page=n,section=section,item=head['text'],heading_amount=money))
            for i,anchor in enumerate(anchors):
                previous=[w for w in item_heads if w['top']<anchor['top']]
                if previous:item=previous[-1]['text']
                end=anchors[i+1]['top']-1 if i+1<len(anchors) else 530
                later=[w['top']-1 for w in item_heads if anchor['top']<w['top']<end]
                if later:end=min(later)
                band=[w for w in words if anchor['top']-1<=w['top']<end]
                # Currency/quantity entries occur on the unit's first line. Avoid a lower header's amount.
                line=[w for w in band if abs(w['top']-anchor['top'])<1]
                cells={key:' '.join(w['text'] for w in line if low<=w['x0']<high) for key,low,high in
                       [('quantity',530,554),('unit',554,584),('unit_cost',584,626),('total_cost',626,674)]}
                rec=dict(record_id=f'p{n:03}-r{i+1}',pdf_page=n,section=section,item=item,y_top_points=round(anchor['top'],3),**scalar_row(cells))
                rows.append(rec)
                private.append(dict(**rec,source_cells=cells,barrier=' '.join(w['text'] for w in band if 40<=w['x0']<141),
                                    existing=' '.join(w['text'] for w in band if 253<=w['x0']<346),recommendation=' '.join(w['text'] for w in band if 424<=w['x0']<530)))
            for w in words:
                if 554<=w['x0']<580 and 100<w['top']<530 and w['size']<9 and w['text'] not in UNITS:
                    unrecognized.append(dict(pdf_page=n,text=w['text']))
    elevator=[r for r in rows if r['section']=='FIRST FLOOR' and r['item']=='28']
    assert len(elevator)==8,(len(elevator),elevator)
    assert Counter(r['unit_type'] for r in elevator)=={'REF.':7,'JOB':1}
    job=next(r for r in elevator if r['unit_type']=='JOB')
    assert job['pdf_page']==113 and job['source_unit_cost']=='900000' and job['source_total_cost']=='900000' and job['quantity_price_matches_total']
    assert all(r['independent_action_cost'] is None for r in rows)
    assert all(r['section'] is not None and r['source_unit_cost'] is not None for r in rows)
    assert sum(r['quantity_price_matches_total'] is True for r in rows)==533
    mismatches=[r['record_id'] for r in rows if r['quantity_price_matches_total'] is False]
    report=dict(source_url=SOURCE_URL,source_sha256=digest,source_pages=264,
        extractor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        classification='historical_documentary_admission_audit_not_solver_evaluation',
        parser_scope='Scalar unit anchors on machine-readable table pages; no OCR, no complete-document row-recall claim; private source text not redistributed',
        scalar_rows=len(rows),priced_rows_checked=sum(r['quantity_price_matches_total'] is True for r in rows),reference_rows=sum(r['accounting_role']=='reference_not_independent_action' for r in rows),section_counts=dict(Counter(r['section'] for r in rows)),unit_counts=dict(Counter(r['unit_type'] for r in rows)),unrecognized_unit_band_tokens=unrecognized,
        quantity_price_mismatch_records=mismatches,
        plans=plans,elevator_item28=dict(records=[r['record_id'] for r in elevator],job_record=job['record_id'],reference_rows=7,source_job_estimate_usd='900000',
            grouping_rule='REF zero is an accounting reference, not evidence of an independent zero-cost action; no graph-edge price splitting'),
        admissions=dict(physical_solver_instances=0,validated_building_repairs=0,reason_codes=['RASTER_REFERENCE_PLANS_UNCALIBRATED','RESERVATIONS_UNVERIFIED','LOBBY_REMODEL_NOT_SHOWN_TO_PRESERVE_TOPOLOGY','EXISTING_ASSET_REMODEL_OUTSIDE_RECOGNIZER','CONSTRUCTION_PERMISSION_UNVERIFIED']),
        rights=dict(notice='GPPA copyright2007; introduction saysAll Rights Reserved',open_redistribution_license_verified=False,raw_pdf_and_drawings_distributed=False),
        historical_summary_discrepancy=dict(summary_pdf_page=10,first_floor_summary_usd='1144509',detail_header_pdf_page=61,first_floor_detail_header_usd='1144309',difference_usd='200',resolution='unresolved_source_difference'),
        manifest=dict(git_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),git_dirty=bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),python=sys.version,platform=platform.platform(),packages={name:importlib.metadata.version(name) for name in ['pdfplumber','pdfminer.six','Pillow']},seed=None,seed_reason='deterministic_document_extraction_no_random_generator',solver_status='not_run_not_admitted',source_price_basis='historical table14Apr2008, nominalUSD, not current installed quote'))
    for name,value in [('scalar-records.json',rows),('plan-audit.json',plans),('item-headings.json',headings),('admission.json',report)]:
        (output/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    # Kept under ignored runs only; never include this verbatim extraction in delivery packages.
    (output/'private-source-rows.json').write_text(json.dumps(private,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['scalar_rows','unit_counts','quantity_price_mismatch_records','admissions']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pdf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();extract(a.pdf,a.output)
