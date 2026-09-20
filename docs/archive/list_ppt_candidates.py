from __future__ import annotations

from pathlib import Path

roots = [
    Path(r"D:\CDriveArchive\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件"),
    Path(r"C:\Users\jiang\Desktop\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件"),
    Path(r"C:\Users\jiang\quantum-tunneling-sim\submission_package"),
    Path(r"C:\Users\jiang\Downloads"),
]

seen: set[str] = set()
rows = []
for root in roots:
    if not root.exists():
        continue
    for p in root.rglob("*.ppt*"):
        key = str(p.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        st = p.stat()
        rows.append((st.st_mtime, st.st_size, str(p)))

from datetime import datetime

for mtime, size, path in sorted(rows, reverse=True):
    print(f"{datetime.fromtimestamp(mtime):%Y-%m-%d %H:%M:%S}\t{size/1024/1024:.2f} MB\t{path}")
