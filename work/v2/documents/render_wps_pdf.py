import json
from pathlib import Path

import pymupdf

pdf_path = Path(__file__).parent / "preview" / "tables_v2.pdf"
output_dir = pdf_path.parent / "wps_render"
output_dir.mkdir(parents=True, exist_ok=True)
for old in output_dir.iterdir():
    if old.is_file() and (old.name.startswith("page-") and old.suffix in {".png", ".txt"}):
        old.unlink()
document = pymupdf.open(pdf_path)
pages = []
for index, page in enumerate(document, start=1):
    image_path = output_dir / f"page-{index:02d}.png"
    page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False).save(image_path)
    page_text = page.get_text()
    (output_dir / f"page-{index:02d}.txt").write_text(page_text, encoding="utf-8")
    pages.append({
        "page": index,
        "image": str(image_path.resolve()),
        "text_start": page_text[:180].replace("\n", " | "),
        "width_pt": page.rect.width,
        "height_pt": page.rect.height,
    })

report = {"pdf": str(pdf_path.resolve()), "page_count": len(document), "pages": pages}
(output_dir / "render_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=True))
