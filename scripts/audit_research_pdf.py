"""PDF structural QA; run using Python with pypdf installed (not solver timing)."""
import argparse
import json
import re
from pathlib import Path
from pypdf import PdfReader


def audit(folder):
    reader=PdfReader(folder/'master.pdf')
    seen=set();fonts={};forms=set();images=set()
    def key(ref):
        return str((ref.idnum,ref.generation)) if hasattr(ref,'idnum') else str(id(ref))
    def walk(ref):
        if not ref or key(ref) in seen:return
        seen.add(key(ref));res=ref.get_object()
        if res.get('/Font'):
            for fr in res['/Font'].get_object().values():
                font=fr.get_object();fd=font.get('/FontDescriptor')
                if not fd and font.get('/DescendantFonts'):
                    fd=font['/DescendantFonts'][0].get_object().get('/FontDescriptor')
                descriptor=fd.get_object() if fd else {}
                fonts[key(fr)]=dict(name=str(font.get('/BaseFont')),subtype=str(font.get('/Subtype')),
                    embedded=any(k in descriptor for k in ('/FontFile','/FontFile2','/FontFile3')))
        if res.get('/XObject'):
            for xr in res['/XObject'].get_object().values():
                x=xr.get_object()
                if x.get('/Subtype')=='/Form':forms.add(key(xr));walk(x.get('/Resources'))
                if x.get('/Subtype')=='/Image':images.add(key(xr))
    text=[]
    for page in reader.pages:
        walk(page.get('/Resources'));text.append(page.extract_text() or '')
        assert abs(float(page.mediabox.width)-612)<.1 and abs(float(page.mediabox.height)-792)<.1
    log=(folder/'master.log').read_text(errors='replace')
    tex=(folder/'master.tex').read_text()
    assert all(f['embedded'] and f['subtype']!='/Type3' for f in fonts.values())
    assert 'Overfull' not in log and not re.search(r'(?:Reference|Citation).*undefined',log)
    assert '??' not in '\n'.join(text)
    used=[]
    for keys in re.findall(r'\\cite\{([^}]+)\}',tex):
        for k in keys.split(','):
            if k not in used:used.append(k)
    assert used==re.findall(r'\\bibitem\{([^}]+)\}',tex),'References must follow first citation order'
    result=dict(pages=len(reader.pages),figures=len(re.findall(r'\\begin\{figure\*?\}',tex)),
        tables=len(re.findall(r'\\begin\{table\*?\}',tex)),font_objects=len(fonts),fonts=list(fonts.values()),
        all_fonts_embedded=True,type3_fonts=0,overfull_boxes=0,undefined_references=0,
        reference_order_verified=True,page_size='US Letter',form_objects=len(forms),raster_images=len(images),
        class_initialization_font_warnings=re.findall(r"LaTeX Font Warning: Font shape[^\n]+",log),
        visual_review='Required separately; structural checks do not certify layout')
    (folder/'pdf-qa.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('fonts','class_initialization_font_warnings')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path)
    audit(p.parse_args().folder)
