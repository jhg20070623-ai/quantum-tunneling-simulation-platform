from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026")
OUT = ROOT / "outputs"
PROJECT = Path(r"C:\Users\jiang\quantum-tunneling-sim")

DOCX = OUT / "量子隧穿虚拟仿真实验平台_项目申请书_四项内容强化版.docx"
PDF_WORK = ROOT / "work" / "rendered_application_enhanced_word" / "application_enhanced.pdf"
PDF_OUT = OUT / "量子隧穿虚拟仿真实验平台_项目申请书_四项内容强化版.pdf"
ZIP_OUT = OUT / "量子隧穿虚拟仿真实验平台_其他材料_源码运行说明截图.zip"

if PDF_WORK.exists():
    shutil.copy2(PDF_WORK, PDF_OUT)


def add_file(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    if path.exists() and path.is_file():
        zf.write(path, arcname)


def add_tree(zf: zipfile.ZipFile, base: Path, arcbase: str) -> None:
    if not base.exists():
        return
    for p in base.rglob("*"):
        if p.is_file():
            zf.write(p, str(Path(arcbase) / p.relative_to(base)))


source_zip = next((p for p in (PROJECT / "submission_package").rglob("*.zip") if "程序源码" in p.name), None)
run_doc = next((p for p in (PROJECT / "submission_package").rglob("程序运行说明.md")), None)
submit_readme = PROJECT / "submission_package" / "README_提交说明.md"
screens = next((p for p in (PROJECT / "submission_package").iterdir() if p.is_dir() and "截图" in p.name), None)

with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    add_file(zf, DOCX, "项目申请书_四项内容强化版.docx")
    if PDF_OUT.exists():
        add_file(zf, PDF_OUT, "项目申请书_四项内容强化版.pdf")
    if source_zip:
        add_file(zf, source_zip, f"程序源码/{source_zip.name}")
    if run_doc:
        add_file(zf, run_doc, "运行说明/程序运行说明.md")
    add_file(zf, submit_readme, "README_提交说明.md")
    add_tree(zf, PROJECT / "dist", "部署产物_dist")
    if screens:
        add_tree(zf, screens, "截图材料")

for p in [DOCX, PDF_OUT, ZIP_OUT]:
    if p.exists():
        print(f"{p.stat().st_size / 1024 / 1024:.2f} MB\t{p}")
