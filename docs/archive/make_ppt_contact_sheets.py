from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\ppt_fusion")


def make_sheet(src: Path, out: Path, label: str) -> None:
    imgs = sorted(src.glob("*.PNG"), key=lambda p: int("".join(ch for ch in p.stem if ch.isdigit()) or 0))
    if not imgs:
        imgs = sorted(src.glob("*.png"))
    thumbs = []
    for p in imgs:
        im = Image.open(p).convert("RGB")
        im.thumbnail((420, 236))
        canvas = Image.new("RGB", (440, 280), "white")
        canvas.paste(im, ((440 - im.width) // 2, 28))
        d = ImageDraw.Draw(canvas)
        d.text((12, 8), f"{label} {len(thumbs)+1}", fill=(0, 0, 0))
        thumbs.append(canvas)
    cols = 3
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 440, rows * 280), (238, 240, 244))
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * 440, (i // cols) * 280))
    sheet.save(out)
    print(out)


make_sheet(ROOT / "preview_a", ROOT / "contact_a_visual.png", "A")
make_sheet(ROOT / "preview_b", ROOT / "contact_b_editable.png", "B")
if (ROOT / "preview_fusion_v1").exists():
    make_sheet(ROOT / "preview_fusion_v1", ROOT / "contact_fusion_v1.png", "F")
if (ROOT / "preview_fusion_v2").exists():
    make_sheet(ROOT / "preview_fusion_v2", ROOT / "contact_fusion_v2.png", "F2")
if (ROOT / "preview_image2_fusion").exists():
    make_sheet(ROOT / "preview_image2_fusion", ROOT / "contact_image2_fusion.png", "I2")
if (ROOT / "preview_image2_unified_style").exists():
    make_sheet(ROOT / "preview_image2_unified_style", ROOT / "contact_image2_unified_style.png", "U")
