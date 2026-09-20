from __future__ import annotations

from pathlib import Path

roots = [
    Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\outputs"),
    Path(r"D:\CDriveArchive\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件"),
    Path(r"C:\Users\jiang\Desktop\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件"),
    Path(r"C:\Users\jiang\quantum-tunneling-sim\submission_package"),
    Path(r"C:\Users\jiang\Downloads"),
]

terms = ("承诺", "诚信", "声明", "项目申请书", "申报书", "设计报告", "介绍视频", "源码", "程序源码")

for root in roots:
    if not root.exists():
        continue
    print(f"\n# {root}")
    hits = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(t in p.name for t in terms):
            hits.append(p)
    for p in sorted(hits, key=lambda x: (x.name, str(x)))[:120]:
        st = p.stat()
        print(f"{st.st_size/1024/1024:7.2f} MB\t{p}")
