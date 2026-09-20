from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\work\ppt_fusion")
OUT = ROOT / "restyled_a_theme"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
FONT_REG = r"C:\Windows\Fonts\SourceHanSansCN-Normal.ttf"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consolab.ttf"


def font(size: int, bold: bool = False, mono: bool = False):
    path = FONT_MONO if mono else (FONT_BOLD if bold else FONT_REG)
    return ImageFont.truetype(path, size)


F_TITLE = font(46, True)
F_SUB = font(22)
F_H = font(26, True)
F_BODY = font(22)
F_SMALL = font(18)
F_TINY = font(15)
F_NUM = font(26, True)
F_MONO = font(19, mono=True)

BG = (3, 16, 34)
PANEL = (7, 31, 58)
PANEL2 = (8, 39, 70)
CYAN = (0, 211, 255)
CYAN2 = (0, 148, 220)
TEXT = (229, 242, 255)
MUTED = (146, 171, 205)
YELLOW = (255, 205, 48)
GREEN = (61, 238, 144)
RED = (255, 91, 100)


def alpha_rect(base, box, color, outline=None, width=2, radius=10, alpha=190):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fill = (*color, alpha)
    if outline:
        d.rounded_rectangle(box, radius=radius, fill=fill, outline=(*outline, 220), width=width)
    else:
        d.rounded_rectangle(box, radius=radius, fill=fill)
    base.alpha_composite(layer)


def draw_bg(page_no: str, title: str, subtitle: str):
    im = Image.new("RGBA", (W, H), (*BG, 255))
    d = ImageDraw.Draw(im)

    # Subtle grid
    for x in range(0, W, 40):
        col = (10, 45, 78, 50) if x % 160 else (20, 82, 130, 80)
        d.line((x, 0, x, H), fill=col, width=1)
    for y in range(0, H, 40):
        col = (10, 45, 78, 42) if y % 160 else (20, 82, 130, 70)
        d.line((0, y, W, y), fill=col, width=1)

    # Dark overlay to keep text readable
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 110))
    im.alpha_composite(overlay)

    # glow bands
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-180, 820, 520, 1260), fill=(0, 180, 255, 42))
    gd.ellipse((690, 850, 1240, 1160), fill=(0, 180, 255, 34))
    gd.ellipse((1510, -160, 2120, 300), fill=(0, 110, 255, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(34))
    im.alpha_composite(glow)

    # top chrome and corner lines
    d = ImageDraw.Draw(im)
    d.line((26, 25, 120, 25, 145, 50, 300, 50), fill=(0, 156, 235, 180), width=2)
    d.line((W - 300, 50, W - 145, 50, W - 120, 25, W - 26, 25), fill=(0, 156, 235, 180), width=2)
    d.line((34, 1000, 310, 1000), fill=(0, 156, 235, 170), width=2)
    d.line((W - 310, 1000, W - 34, 1000), fill=(0, 156, 235, 170), width=2)
    d.line((72, 78, W - 72, 78), fill=(0, 156, 235, 110), width=1)

    # page number block
    d.polygon([(32, 86), (114, 86), (138, 110), (138, 150), (32, 150)], fill=(4, 46, 83), outline=CYAN)
    d.text((58, 102), page_no, fill=CYAN, font=F_NUM)

    d.text((155, 88), title, fill=TEXT, font=F_TITLE)
    if subtitle:
        d.text((155, 146), subtitle, fill=MUTED, font=F_SUB)
    d.text((1590, 88), "量子隧穿虚拟仿真实验平台", fill=(118, 158, 200), font=F_SMALL)
    return im


def crop(src: Path, box, size=None, boost=True):
    im = Image.open(src).convert("RGBA").crop(box)
    if size:
        im = im.resize(size, Image.LANCZOS)
    if boost:
        im = ImageEnhance.Contrast(im).enhance(1.08)
        im = ImageEnhance.Sharpness(im).enhance(1.15)
    return im


def paste_panel(base, image, box, label=None):
    x1, y1, x2, y2 = box
    alpha_rect(base, (x1 - 14, y1 - 14, x2 + 14, y2 + 14), (5, 28, 55), CYAN2, 2, 14, 220)
    if label:
        d = ImageDraw.Draw(base)
        d.rectangle((x1 - 14, y1 - 54, x1 + 250, y1 - 14), fill=(0, 194, 242), outline=CYAN)
        d.text((x1 + 2, y1 - 48), label, fill=(2, 14, 30), font=F_SMALL)
    base.alpha_composite(image, (x1, y1))


def wrap_text(draw, text, max_width, fnt):
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        if draw.textlength(test, font=fnt) <= max_width or not current:
            current = test
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def bullet(draw, x, y, text, width, color=TEXT, fnt=F_BODY, bullet_color=CYAN):
    draw.ellipse((x, y + 10, x + 8, y + 18), fill=bullet_color)
    lines = wrap_text(draw, text, width - 24, fnt)
    yy = y
    for i, line in enumerate(lines):
        draw.text((x + 22, yy), line, fill=color, font=fnt)
        yy += int(fnt.size * 1.38)
    return yy + 6


def metric_card(base, box, num, title, lines, accent=CYAN):
    x1, y1, x2, y2 = box
    alpha_rect(base, box, PANEL2, accent, 2, 13, 208)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((x1 + 22, y1 + 22, x1 + 86, y1 + 86), radius=8, fill=accent)
    d.text((x1 + 40, y1 + 35), num, fill=(2, 14, 30), font=F_NUM)
    d.text((x1 + 108, y1 + 28), title, fill=TEXT, font=F_H)
    yy = y1 + 76
    for line in lines:
        yy = bullet(d, x1 + 108, yy, line, x2 - x1 - 132, fnt=F_SMALL, bullet_color=accent)


def footer(base, text):
    d = ImageDraw.Draw(base)
    alpha_rect(base, (180, 930, 1740, 996), (8, 45, 82), CYAN, 2, 0, 210)
    tw = d.textlength(text, font=F_H)
    d.text(((W - tw) / 2, 947), text, fill=CYAN, font=F_H)


def slide08():
    im = draw_bg("08", "数据表与结果校验把“可看见”变成“可复核”", "参数、区间、概率、守恒条件同源输出")
    d = ImageDraw.Draw(im)
    src = ROOT / "preview_b" / "幻灯片8.PNG"
    table = crop(src, (125, 214, 1178, 706), (980, 456))
    paste_panel(im, table, (110, 270, 1090, 726), "实验数据表")
    metric_card(im, (1160, 250, 1805, 430), "01", "记录链条", [
        "E、V0、a、m 与区间判断同步记录",
        "透射概率 T、反射概率 R 并列展示",
        "经典预测与量子预测形成对照证据",
    ])
    metric_card(im, (1160, 470, 1805, 650), "02", "校验链条", [
        "T、R 限制在 [0,1] 物理区间",
        "|T+R-1| < 10^(-6) 作为守恒条件",
        "极限行为、参数趋势与教材公式交叉验证",
    ], accent=YELLOW)
    # validation strip
    alpha_rect(im, (1160, 700, 1805, 832), (4, 30, 54), GREEN, 2, 12, 210)
    d.text((1202, 726), "校验结果", fill=GREEN, font=F_H)
    d.text((1202, 775), "T + R = 1.00000000   守恒校验通过", fill=TEXT, font=F_BODY)
    footer(im, "面向教学：让学生看到“参数 - 数值 - 物理解释”的完整证据链")
    im.convert("RGB").save(OUT / "slide08.png")


def slide09():
    im = draw_bg("09", "自动实验报告与数据导出让学习闭环落地", "从操作记录到实验报告，形成可提交的学习产物")
    d = ImageDraw.Draw(im)
    src = ROOT / "preview_b" / "幻灯片9.PNG"
    report = crop(src, (235, 220, 1146, 880), (900, 650))
    paste_panel(im, report, (110, 260, 1010, 910), "Markdown 实验报告")
    export = crop(src, (1338, 222, 1780, 382), (390, 142))
    paste_panel(im, export, (1230, 250, 1620, 392), "导出按钮")
    metric_card(im, (1085, 430, 1805, 610), "A", "报告结构", [
        "实验目的、实验原理、模型与参数",
        "实验过程、结果分析、经典/量子对比",
        "结论与改进方向自动组织成文",
    ])
    metric_card(im, (1085, 655, 1805, 835), "B", "输出格式", [
        "JSON 保存当前参数与计算结果",
        "CSV 导出参数扫描曲线数据",
        "Markdown 生成可编辑实验报告",
    ], accent=YELLOW)
    footer(im, "报告不是附属功能，而是把虚拟实验转化为可评价成果")
    im.convert("RGB").save(OUT / "slide09.png")


def slide10():
    im = draw_bg("10", "教学说明与学习闭环支撑课堂演示和课后探究", "把“看动画”升级为“设参数、看图像、析规律、写报告”")
    d = ImageDraw.Draw(im)
    src = ROOT / "preview_b" / "幻灯片10.PNG"
    guide = crop(src, (218, 211, 1051, 775), (760, 515))
    paste_panel(im, guide, (125, 290, 885, 805), "内置教学说明")

    # Flow line
    xs = [1015, 1240, 1465, 1690]
    y = 430
    for i in range(len(xs) - 1):
        d.line((xs[i] + 85, y + 34, xs[i + 1] - 25, y + 34), fill=CYAN, width=4)
        d.polygon([(xs[i + 1] - 25, y + 24), (xs[i + 1] - 25, y + 44), (xs[i + 1] - 5, y + 34)], fill=CYAN)
    steps = [
        ("1", "设置参数", "提出假设"),
        ("2", "观察图像", "建立图像"),
        ("3", "分析曲线", "总结规律"),
        ("4", "生成报告", "复盘表达"),
    ]
    for x, (num, title, desc) in zip(xs, steps):
        alpha_rect(im, (x - 20, y - 30, x + 155, y + 170), (6, 36, 65), CYAN, 2, 16, 210)
        d.rounded_rectangle((x + 35, y - 6, x + 100, y + 58), radius=8, fill=CYAN)
        d.text((x + 58, y + 8), num, fill=(2, 14, 30), font=F_NUM)
        tw = d.textlength(title, font=F_H)
        d.text((x + (135 - tw) / 2, y + 82), title, fill=TEXT, font=F_H)
        tw2 = d.textlength(desc, font=F_SMALL)
        d.text((x + (135 - tw2) / 2, y + 124), desc, fill=MUTED, font=F_SMALL)

    alpha_rect(im, (1015, 700, 1805, 830), (4, 32, 58), YELLOW, 2, 12, 210)
    d.text((1050, 724), "适用场景", fill=YELLOW, font=F_H)
    yy = 772
    for txt in ["课堂演示：快速呈现隧穿核心现象", "课后探究：调参观察规律", "实验训练：数据记录与报告生成"]:
        yy = bullet(d, 1050, yy, txt, 710, fnt=F_SMALL, bullet_color=YELLOW)
    footer(im, "平台把“可教、可学、可复盘”整合成一条完整实验路径")
    im.convert("RGB").save(OUT / "slide10.png")


def slide11():
    im = draw_bg("11", "作品创新点与应用价值：可操作、可观察、可分析", "不是静态演示，而是可交互、可计算、可产出的虚拟仿真实验")
    d = ImageDraw.Draw(im)
    items = [
        ("参数可调", "E / V0 / a / m 实时调节，支持预设场景"),
        ("定量计算", "解析公式计算 T 与 R，避免黑箱模拟"),
        ("可视化展示", "V(x)、E 参考线与 |ψ(x)|² 同图显示"),
        ("经典/量子对比", "同一物理系统展示两种理论预测差异"),
        ("自动报告", "一键生成 Markdown 实验报告，支撑学习闭环"),
        ("低成本部署", "浏览器端运行，可本地预览或静态部署"),
    ]
    positions = [(100, 245), (690, 245), (1280, 245), (100, 520), (690, 520), (1280, 520)]
    for idx, ((title, body), (x, y)) in enumerate(zip(items, positions), start=1):
        accent = CYAN if idx not in (2, 5) else YELLOW
        alpha_rect(im, (x, y, x + 520, y + 220), (5, 31, 60), accent, 2, 15, 220)
        d.rounded_rectangle((x + 22, y + 28, x + 80, y + 86), radius=7, fill=accent)
        d.text((x + 40, y + 40), str(idx), fill=(2, 14, 30), font=F_NUM)
        d.text((x + 102, y + 30), title, fill=TEXT, font=F_H)
        lines = wrap_text(d, body, 378, F_BODY)
        yy = y + 94
        for line in lines:
            d.text((x + 102, yy), line, fill=MUTED, font=F_BODY)
            yy += 32

    alpha_rect(im, (230, 800, 1690, 900), (5, 36, 66), CYAN, 2, 10, 210)
    labels = [("课堂演示", "快速呈现核心现象"), ("自主探究", "调参观察规律"), ("报告训练", "生成可提交成果")]
    for i, (name, desc) in enumerate(labels):
        x = 330 + i * 460
        d.rounded_rectangle((x, 822, x + 58, 880), radius=8, fill=CYAN if i != 1 else YELLOW)
        d.text((x + 16, 834), str(i + 1), fill=(2, 14, 30), font=F_NUM)
        d.text((x + 78, 820), name, fill=TEXT, font=F_H)
        d.text((x + 78, 858), desc, fill=MUTED, font=F_SMALL)
    footer(im, "适用于大学物理、近现代物理、量子力学入门教学")
    im.convert("RGB").save(OUT / "slide11.png")


if __name__ == "__main__":
    slide08()
    slide09()
    slide10()
    slide11()
    for p in sorted(OUT.glob("slide*.png")):
        print(p)
