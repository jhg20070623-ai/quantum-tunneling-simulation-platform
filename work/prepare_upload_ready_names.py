from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026")
OUT = ROOT / "outputs"
READY = OUT / "upload_ready"
READY.mkdir(parents=True, exist_ok=True)

files = [
    (OUT / "量子隧穿虚拟仿真实验平台_介绍视频_720p_25fps_AAC48k.mp4", READY / "video_720p_25fps_aac48k.mp4"),
    (OUT / "量子隧穿虚拟仿真实验平台_项目申请书_四项内容强化版.pdf", READY / "project_book.pdf"),
    (OUT / "量子隧穿虚拟仿真实验平台_项目申请书_四项内容强化版.docx", READY / "project_book.docx"),
    (OUT / "量子隧穿虚拟仿真实验平台_其他材料_源码运行说明截图.zip", READY / "other_materials_source_dist_screenshots.zip"),
    (OUT / "量子隧穿虚拟仿真实验平台_展示PPT_image2统一风格版.pptx", READY / "presentation_image2_unified_style.pptx"),
]

for src, dst in files:
    if src.exists():
        shutil.copy2(src, dst)
        print(f"{dst.stat().st_size / 1024 / 1024:.2f} MB\t{dst}")
    else:
        print(f"MISSING\t{src}")
