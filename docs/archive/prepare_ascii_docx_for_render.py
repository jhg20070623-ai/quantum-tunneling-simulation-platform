from __future__ import annotations

import shutil
from pathlib import Path

SRC = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\outputs\量子隧穿虚拟仿真实验平台_项目申请书_四项内容强化版.docx")
OUT_DIR = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\rendered_application_enhanced_word")
DST = OUT_DIR / "application_enhanced.docx"
OUT_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy2(SRC, DST)
print(DST)
