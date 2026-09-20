from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026")
WORK = ROOT / "work" / "ppt_fusion"
WORK.mkdir(parents=True, exist_ok=True)

folder = Path(r"D:\CDriveArchive\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件")
ppts = sorted(folder.glob("*.pptx"), key=lambda p: p.stat().st_size, reverse=True)
for p in ppts:
    print(f"FOUND {p.stat().st_size}\t{p.name!r}")

if len(ppts) < 2:
    raise SystemExit("Need at least two PPTX files")

src_a = ppts[0]
src_b = next((p for p in ppts if "展示PPT" in p.name or "可编辑" in p.name), ppts[1])

dst_a = WORK / "source_a_visual.pptx"
dst_b = WORK / "source_b_editable.pptx"
shutil.copy2(src_a, dst_a)
shutil.copy2(src_b, dst_b)

print(f"A_VISUAL={dst_a}")
print(f"B_EDITABLE={dst_b}")
