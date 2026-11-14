from pathlib import Path
import json
import sys
import pymupdf

pdf=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2]).resolve()
out.mkdir(parents=True,exist_ok=True)
doc=pymupdf.open(pdf)
pages=[]
for n,page in enumerate(doc,1):
    p=out/f'page-{n:02d}.png'
    page.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6),alpha=False).save(p)
    text=page.get_text()
    (out/f'page-{n:02d}.txt').write_text(text,encoding='utf-8')
    bad=[]
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                if x0<0 or y0<0 or x1>page.rect.width+.1 or y1>page.rect.height+.1:
                    bad.append(span['text'])
    pages.append(dict(page=n,image=str(p),width_pt=page.rect.width,height_pt=page.rect.height,
                      off_page_text=bad,words=len(text.split()),text_start=text[:100]))
report=dict(pdf=str(pdf),pages=pages,page_count=len(doc))
(out/'render_report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
