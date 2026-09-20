from __future__ import annotations

import sys
from pathlib import Path


DOCX = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\outputs\量子隧穿虚拟仿真实验平台_项目申请书_四项内容强化版.docx")
OUT_DIR = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\rendered_application_enhanced_word")
PDF = OUT_DIR / "application_enhanced.pdf"


def export_pdf_with_word() -> None:
    import win32com.client  # type: ignore

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(str(DOCX), ReadOnly=True)
        doc.ExportAsFixedFormat(str(PDF), 17)
    finally:
        if doc is not None:
            doc.Close(False)
        word.Quit()


def rasterize_pdf() -> int:
    import fitz  # type: ignore

    pdf_doc = fitz.open(str(PDF))
    for i, page in enumerate(pdf_doc, start=1):
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        pix.save(str(OUT_DIR / f"page-{i}.png"))
    return pdf_doc.page_count


def main() -> int:
    export_pdf_with_word()
    pages = rasterize_pdf()
    print(f"pdf={PDF}")
    print(f"pages={pages}")
    print(f"png_dir={OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
