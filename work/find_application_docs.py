from __future__ import annotations

from pathlib import Path

roots = [
    Path(r"D:\CDriveArchive\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件"),
    Path(r"C:\Users\jiang\Desktop\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件"),
    Path(r"C:\Users\jiang\quantum-tunneling-sim"),
    Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\outputs"),
]

keywords = ("申报书", "申请书", "项目申请", "项目申报")
rows = []
for root in roots:
    if not root.exists():
        continue
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".docx", ".md", ".pdf"}:
            continue
        if any(k in path.name for k in keywords):
            st = path.stat()
            rows.append((st.st_mtime, st.st_size, str(path)))

for mtime, size, path in sorted(rows, reverse=True):
    from datetime import datetime

    print(f"{datetime.fromtimestamp(mtime):%Y-%m-%d %H:%M:%S}\t{size}\t{path}")
