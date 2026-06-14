from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\ppt_fusion")
OUT = ROOT / "image2_assets"
OUT.mkdir(parents=True, exist_ok=True)


def slide_png(preview_dir: str, n: int) -> Path:
    folder = ROOT / preview_dir
    candidates = []
    for p in folder.glob("*.PNG"):
        digits = "".join(ch for ch in p.stem if ch.isdigit())
        if digits and int(digits) == n:
            candidates.append(p)
    if not candidates:
        raise FileNotFoundError(f"{preview_dir} slide {n}")
    return candidates[0]


selection = [
    ("preview_a", 1),
    ("preview_a", 2),
    ("preview_a", 3),
    ("preview_a", 4),
    ("preview_a", 5),
    ("preview_a", 6),
    ("preview_a", 7),
    ("preview_b", 8),
    ("preview_b", 9),
    ("preview_b", 10),
    ("preview_b", 11),
    ("preview_a", 9),
]

for idx, (folder, slide_no) in enumerate(selection, start=1):
    src = slide_png(folder, slide_no)
    dst = OUT / f"slide{idx:02d}.png"
    shutil.copy2(src, dst)
    with Image.open(dst) as im:
        print(f"{idx:02d}\t{folder}:{slide_no}\t{im.size[0]}x{im.size[1]}\t{dst}")
