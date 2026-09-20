from __future__ import annotations

from pathlib import Path

import fitz

PDF = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\rendered_application_enhanced_word\application_enhanced.pdf")
OUT_DIR = PDF.parent

doc = fitz.open(str(PDF))
for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
    out = OUT_DIR / f"page-{i}.png"
    pix.save(str(out))
    print(out)
print(f"pages={doc.page_count}")
