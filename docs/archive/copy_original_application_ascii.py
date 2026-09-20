from __future__ import annotations

import shutil
from pathlib import Path

SRC = Path(r"D:\CDriveArchive\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件\量子隧穿虚拟仿真实验平台_项目申请书_最终上传版.docx")
OUT_DIR = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\rendered_original_application_word")
DST = OUT_DIR / "original_application.docx"
OUT_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(SRC, DST)
print(DST)
