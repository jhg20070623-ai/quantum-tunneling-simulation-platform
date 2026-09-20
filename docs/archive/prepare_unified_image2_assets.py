from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\ppt_fusion")
OUT = ROOT / "image2_unified_assets"
OUT.mkdir(parents=True, exist_ok=True)


def source_a(n: int) -> Path:
    for p in (ROOT / "preview_a").glob("*.PNG"):
        digits = "".join(ch for ch in p.stem if ch.isdigit())
        if digits and int(digits) == n:
            return p
    raise FileNotFoundError(n)


selection: list[Path] = [
    source_a(1),
    source_a(2),
    source_a(3),
    source_a(4),
    source_a(5),
    source_a(6),
    source_a(7),
    ROOT / "restyled_a_theme" / "slide08.png",
    ROOT / "restyled_a_theme" / "slide09.png",
    ROOT / "restyled_a_theme" / "slide10.png",
    ROOT / "restyled_a_theme" / "slide11.png",
    source_a(9),
]

for idx, src in enumerate(selection, start=1):
    dst = OUT / f"slide{idx:02d}.png"
    shutil.copy2(src, dst)
    with Image.open(dst) as im:
        print(f"{idx:02d}\t{im.size[0]}x{im.size[1]}\t{src.name} -> {dst}")
