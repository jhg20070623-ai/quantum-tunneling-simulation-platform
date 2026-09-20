from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026")
SRC = ROOT / "work" / "ppt_fusion" / "image2_fusion.pptx"
DST = ROOT / "outputs" / "量子隧穿虚拟仿真实验平台_展示PPT_image2融合版.pptx"
shutil.copy2(SRC, DST)
print(f"{DST.stat().st_size / 1024 / 1024:.2f} MB\t{DST}")
