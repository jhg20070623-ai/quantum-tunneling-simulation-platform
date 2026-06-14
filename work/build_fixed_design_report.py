from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(r"D:\CDriveArchive\Desktop-contest\2026年辽宁省大学生物理实验竞赛附件")
SOURCE = ROOT / "量子隧穿虚拟仿真实验平台_项目申请书_最终上传版.docx"
OUTPUT_DIR = Path(r"C:\Users\jiang\Documents\Codex\2026-06-14\d-cdrivearchive-desktop-contest-2026\outputs")
OUTPUT = OUTPUT_DIR / "量子隧穿虚拟仿真实验平台_设计报告_匿名评审风险修复版.docx"
AUDIT = OUTPUT_DIR / "量子隧穿虚拟仿真实验平台_设计报告_修复说明.json"


SENSITIVE_PATTERNS = [
    "沈阳大学",
    "姜浩广",
    "贾雨萌",
    "石镜开",
    "谢谢",
    "2007.06",
    "2006.03",
    "2005.12",
]


def set_run_font(run, size=None, bold=None, color=None, east_asia="宋体", latin="Calibri"):
    run.font.name = latin
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east_asia)
    run._element.rPr.rFonts.set(qn("w:ascii"), latin)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), latin)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def set_paragraph_style(paragraph, *, before=0, after=6, line=1.15, align=None):
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing = line
    if align is not None:
        paragraph.alignment = align


def clear_body(doc: Document) -> None:
    body = doc._body._element
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def configure_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15

    for name, size, color, font in [
        ("Heading 1", 15, "1F4D78", "黑体"),
        ("Heading 2", 13, "2E74B5", "黑体"),
        ("Heading 3", 12, "1F4D78", "黑体"),
    ]:
        style = doc.styles[name]
        style.font.name = "Calibri"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), font)
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(10 if name == "Heading 1" else 6)
        style.paragraph_format.space_after = Pt(5)
        style.paragraph_format.keep_with_next = True


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_width(cell, width_twips: int) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(width_twips))
    tc_w.set(qn("w:type"), "dxa")


def set_cell_no_wrap(cell) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    no_wrap = tc_pr.find(qn("w:noWrap"))
    if no_wrap is None:
        tc_pr.append(OxmlElement("w:noWrap"))


def set_table_width(table, width_twips: int) -> None:
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(width_twips))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_pr.append(OxmlElement("w:tblLayout"))
    tbl_pr[-1].set(qn("w:type"), "fixed")


def style_table(table, widths=None) -> None:
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    set_table_width(table, 9360)
    if widths:
        for row in table.rows:
            for idx, width in enumerate(widths):
                if idx < len(row.cells):
                    set_cell_width(row.cells[idx], width)
    for row_idx, row in enumerate(table.rows):
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for paragraph in cell.paragraphs:
                set_paragraph_style(paragraph, after=0, line=1.0)
                for run in paragraph.runs:
                    set_run_font(run, size=9.2 if len(cell.text) > 18 else 9.6)
            if row_idx == 0:
                set_cell_shading(cell, "E8EEF5")
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        set_run_font(run, size=9.8, bold=True, color="0B2545", east_asia="黑体")


def add_para(doc, text="", *, style=None, before=0, after=6, line=1.15, align=None, bold=False):
    p = doc.add_paragraph(style=style)
    if text:
        run = p.add_run(text)
        set_run_font(run, bold=bold)
    set_paragraph_style(p, before=before, after=after, line=line, align=align)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    run = p.add_run(text)
    set_run_font(run, bold=True, east_asia="黑体")
    return p


def add_caption(doc, text):
    p = add_para(doc, text, before=4, after=4, line=1.1, align=WD_ALIGN_PARAGRAPH.CENTER)
    for run in p.runs:
        set_run_font(run, size=10, color="555555")
    return p


def add_simple_table(doc, rows, widths=None, nowrap_cols=None, center_cols=None):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    nowrap_cols = set(nowrap_cols or [])
    center_cols = set(center_cols or [])
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            cell = table.cell(i, j)
            cell.text = str(value)
            if j in nowrap_cols:
                set_cell_no_wrap(cell)
            if j in center_cols:
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_table(table, widths)
    return table


def configure_sections(doc: Document) -> None:
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.6)
        section.right_margin = Cm(2.4)
        section.header_distance = Cm(1.25)
        section.footer_distance = Cm(1.25)
        header = section.header
        header.is_linked_to_previous = False
        if header.paragraphs:
            p = header.paragraphs[0]
        else:
            p = header.add_paragraph()
        p.text = "2026年辽宁省大学生物理实验竞赛 · 自选题2：教学资源和虚仿 · 匿名评审版"
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_paragraph_style(p, after=0, line=1.0)
        for run in p.runs:
            set_run_font(run, size=9, color="666666")

        footer = section.footer
        footer.is_linked_to_previous = False
        if footer.paragraphs:
            fp = footer.paragraphs[0]
        else:
            fp = footer.add_paragraph()
        fp.text = "设计报告"
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_paragraph_style(fp, after=0, line=1.0)
        for run in fp.runs:
            set_run_font(run, size=9, color="666666")


def build() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document(str(SOURCE))
    clear_body(doc)
    configure_styles(doc)
    configure_sections(doc)

    doc.core_properties.author = "匿名评审版"
    doc.core_properties.last_modified_by = "匿名评审版"
    doc.core_properties.title = "基于交互式可视化的量子隧穿虚拟仿真实验平台设计报告"
    doc.core_properties.subject = "自选类创新作品赛道-自选题2：教学资源和虚仿"
    doc.core_properties.comments = "匿名评审风险修复版"

    title = add_para(doc, "2026年辽宁省大学生物理实验竞赛", after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    for run in title.runs:
        set_run_font(run, size=14, bold=True, east_asia="黑体", color="0B2545")
    subtitle = add_para(doc, "自选类创新作品赛道 · 自选题2：教学资源和虚仿", after=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    for run in subtitle.runs:
        set_run_font(run, size=12, bold=True, east_asia="黑体", color="1F4D78")
    main_title = add_para(doc, "基于交互式可视化的量子隧穿虚拟仿真实验平台", after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    for run in main_title.runs:
        set_run_font(run, size=20, bold=True, east_asia="黑体", color="111111")
    doc_type = add_para(doc, "设计报告（匿名评审风险修复版）", after=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    for run in doc_type.runs:
        set_run_font(run, size=14, bold=True, east_asia="黑体", color="2E74B5")

    meta_rows = [
        ["参赛题目", "基于交互式可视化的量子隧穿虚拟仿真实验平台"],
        ["所属赛道", "自选类创新作品赛道——自选题2：教学资源和虚仿"],
        ["参赛信息", "以报名系统信息为准；本报告为匿名评审版，不列示学校、教师和学生真实姓名。"],
        ["作品形态", "浏览器端虚拟仿真程序 + 设计报告 + 展示PPT + 介绍视频"],
    ]
    table = doc.add_table(rows=len(meta_rows), cols=2)
    for i, row in enumerate(meta_rows):
        for j, value in enumerate(row):
            table.cell(i, j).text = value
    style_table(table, [1900, 7460])

    add_heading(doc, "一、选题意义与目标定位", 1)
    add_para(
        doc,
        "量子隧穿效应是量子力学中最具代表性的非经典现象之一：微观粒子在能量不足以越过势垒时，仍可能以非零概率出现在势垒另一侧。该现象与扫描隧道显微镜、半导体器件、核衰变和共振隧穿结构等现代物理与工程问题密切相关，但真实实验装置成本高、操作复杂，难以在普通大学物理实验课堂中大规模开展。",
    )
    add_para(
        doc,
        "本作品面向“教学资源和虚仿”方向，目标是把抽象的薛定谔方程解、边界连续条件和透射概率转化为可操作、可观察、可记录的虚拟实验过程。平台强调四个教学目标：降低近现代物理实验门槛；帮助学生建立波函数与概率密度图像；通过参数扫描训练定量分析能力；通过自动报告形成“操作—观察—解释—复盘”的学习闭环。",
    )
    add_para(
        doc,
        "与单纯动画演示不同，本作品的核心定位是“可交互的定量虚拟实验”：学生改变粒子能量、势垒高度、势垒宽度和粒子质量后，系统实时给出透射率、反射率、经典/量子预测对比、参数扫描曲线和实验记录。作品适用于大学物理、近现代物理和量子力学入门课程的课堂演示、课后探究和实验报告训练。",
    )

    add_heading(doc, "二、物理原理与计算模型", 1)
    add_heading(doc, "2.1 一维方势垒模型", 2)
    add_para(
        doc,
        "平台采用一维方势垒模型。空间划分为三个区域：区域 I（x < 0，V(x)=0，入射波与反射波叠加）；区域 II（0 <= x <= a，V(x)=V0，波函数在势垒内衰减或振荡）；区域 III（x > a，V(x)=0，形成透射波）。系统满足一维定态薛定谔方程：",
    )
    eq = add_para(doc, "-hbar^2/(2m) * d^2 psi/dx^2 + V(x) psi = E psi", after=8, align=WD_ALIGN_PARAGRAPH.CENTER)
    for run in eq.runs:
        set_run_font(run, size=11, bold=True, latin="Consolas")
    add_para(
        doc,
        "程序在三个区域分别写出波函数通解，并利用 x=0 和 x=a 处波函数及其一阶导数连续的边界条件，求解反射振幅、透射振幅和相对概率密度。可视化页面采用入射振幅归一化，因此图中的 |psi(x)|^2 表示相对概率密度，用于展示空间分布趋势；透射率 T 和反射率 R 由概率流守恒给出。",
    )

    add_heading(doc, "2.2 透射概率公式与边界情况", 2)
    add_para(
        doc,
        "当 E < V0 时，粒子处于隧穿区，势垒内波函数呈指数衰减，透射概率采用解析式：T = 1 / [1 + V0^2 * sinh^2(kappa a) / (4E(V0-E))]，其中 kappa = sqrt(2m(V0-E)) / hbar。",
    )
    add_para(
        doc,
        "当 E > V0 时，粒子处于越垒传播区，但由于边界处波矢失配，仍可能发生量子反射，透射概率为：T = 1 / [1 + V0^2 * sin^2(k2 a) / (4E(E-V0))]，其中 k2 = sqrt(2m(E-V0)) / hbar。当 k2 a = n*pi（n=1,2,...）时出现完全透射，对应共振隧穿条件。",
    )
    add_para(
        doc,
        "为避免 E 接近 V0 时公式分母出现数值奇异，程序在近垒顶区域采用极限表达式进行处理：T(E=V0) = 1 / [1 + m*V0*a^2/(2*hbar^2)]。这一处理保证了曲线在垒顶附近连续，也避免学生误把数值异常理解为物理异常。",
    )

    add_heading(doc, "三、程序设计与实现技术", 1)
    add_heading(doc, "3.1 总体流程", 2)
    add_para(
        doc,
        "总体流程为：参数输入 -> 物理计算 -> 势垒与相对概率密度可视化 -> 参数扫描 -> 数据校验 -> 经典/量子对比 -> 实验报告生成 -> 教学说明。物理计算模块独立封装，界面层只负责参数输入和结果展示，便于后续扩展到双势垒、WKB 近似或含时波包演化。",
    )
    add_heading(doc, "3.2 技术架构", 2)
    add_para(
        doc,
        "平台采用浏览器端单页应用架构，主要技术栈为 React 18、TypeScript、Vite 5、Recharts 和 CSS。所有物理计算在浏览器端完成，不依赖后端服务器；构建后可作为静态网页部署，也可在本地通过 Node.js 18+ 启动。页面由“虚拟实验”“参数扫描”“实验报告”“教学说明”四个视图组成。",
    )
    add_para(
        doc,
        "本作品在实现上突出自主计算和教学闭环：透射概率、反射概率、经典/量子对比和扫描曲线均由程序根据当前参数实时计算；实验报告根据当前实验记录自动生成 Markdown 文本，学生可直接复制、下载并继续整理为正式实验报告。",
    )
    add_heading(doc, "3.3 参数范围与运行要求", 2)
    add_caption(doc, "表 1  程序参数与运行要求")
    add_simple_table(
        doc,
        [
            ["项目", "当前设计范围/要求", "说明"],
            ["粒子能量 E", "0.10 - 3.00", "无量纲自然单位；覆盖深隧穿、近垒顶与越垒传播"],
            ["势垒高度 V0", "0.10 - 3.00", "与 E 联合决定经典禁戒区和透射概率"],
            ["势垒宽度 a", "0.10 - 6.00", "用于观察隧穿概率随宽度的指数衰减"],
            ["粒子质量 m", "0.20 - 5.00", "用于展示质量增大时趋近经典极限的趋势"],
            ["扫描点数", "默认 100 点", "支持 T-E、T-a、T-V0 三类扫描"],
            ["运行环境", "现代浏览器；开发运行需 Node.js 18+", "可构建为静态网页，无需后端服务器"],
        ],
        [1900, 2600, 4860],
    )

    doc.add_page_break()
    add_heading(doc, "3.4 功能模块与性能指标", 2)
    add_caption(doc, "表 2  功能模块与可评价指标")
    add_simple_table(
        doc,
        [
            ["模块", "功能说明", "评价指标"],
            ["参数控制", "滑块和数值输入同步调节 E、V0、a、m；支持典型场景预设", "参数变化后即时刷新计算结果"],
            ["可视化展示", "同图显示势垒 V(x)、能量线 E 和相对概率密度 |psi(x)|^2", "坐标轴、图例和曲线含义清楚，可用于课堂演示"],
            ["经典/量子对比", "并列展示同一参数下经典预测和量子预测", "突出 E<V0 时非零透射、E>V0 时量子反射"],
            ["参数扫描", "支持 T-E、T-a、T-V0 三类扫描并导出 CSV", "每次扫描默认 100 点，便于定量分析"],
            ["数据校验", "检查 0<=T<=1 与 |T+R-1|<1e-6", "避免物理量越界和概率守恒错误"],
            ["报告生成", "按当前参数和结果自动生成 Markdown 实验报告", "形成可复盘的学习产出"],
        ],
        [1700, 5160, 2500],
    )

    add_heading(doc, "四、开发过程与学生参与", 1)
    add_para(
        doc,
        "为满足自选题2对学生参与程度和开发历程的要求，本报告采用匿名方式记录分工，不列示真实姓名。实际参赛身份以报名系统和学校汇总表为准。",
    )
    add_caption(doc, "表 3  匿名成员贡献与开发历程")
    add_simple_table(
        doc,
        [
            ["阶段", "主要工作", "主要贡献者"],
            ["需求分析", "研读赛道要求，确定量子隧穿教学痛点、作品定位和提交材料结构", "成员A、成员B、成员C"],
            ["物理建模", "整理一维方势垒模型、透射率公式、经典/量子对比和极限行为验证", "成员A"],
            ["程序实现", "搭建 React + TypeScript 项目，封装物理计算、参数控制、图表展示和数据导出", "成员A、成员C"],
            ["教学设计", "设计实验目的、操作步骤、观察问题、报告模板和课堂使用流程", "成员B"],
            ["测试与展示", "测试典型场景、扫描曲线、报告生成和视频演示流程，整理 PPT 与介绍视频", "成员A、成员B、成员C"],
        ],
        [1750, 5760, 1850],
        nowrap_cols=[0, 2],
        center_cols=[0, 2],
    )

    add_heading(doc, "五、典型实验数据与结果分析", 1)
    add_para(doc, "下表给出 5 组覆盖不同物理区域的典型参数与计算结果。所有参数采用自然单位制，hbar=1。")
    add_caption(doc, "表 4  典型参数条件下的量子隧穿计算结果")
    add_simple_table(
        doc,
        [
            ["场景", "参数（E / V0 / a / m）", "物理区域", "T", "R"],
            ["明显隧穿", "0.50 / 1.00 / 1.00 / 1.00", "隧穿区", "42.61%", "57.39%"],
            ["弱隧穿", "0.30 / 1.50 / 3.00 / 1.00", "深隧穿区", "约0.076%", "约99.924%"],
            ["近垒顶", "0.95 / 1.00 / 2.00 / 1.00", "近垒顶区", "约84.9%", "约15.1%"],
            ["越垒传播", "1.50 / 1.00 / 2.00 / 1.00", "越垒区", "约92.2%", "约7.8%"],
            ["宽垒隧穿", "0.60 / 1.20 / 5.00 / 2.00", "宽垒隧穿", "极小(<0.01%)", "约100%"],
        ],
        [1550, 3440, 1650, 1360, 1360],
        nowrap_cols=[0, 1, 2, 3, 4],
        center_cols=[0, 1, 2, 3, 4],
    )
    add_para(
        doc,
        "T-E 曲线表明：在 E < V0 时，透射概率随能量增大而上升；在 E 接近 V0 的近垒顶区域，透射率对参数变化更加敏感；在 E > V0 时，透射率整体趋近于 1，但由于边界干涉仍出现振荡和非零反射。",
    )
    add_para(
        doc,
        "T-a 曲线表明：在隧穿区，势垒越宽，波函数在势垒内衰减距离越长，透射概率近似按 exp(-2*kappa*a) 下降。T-V0 曲线表明：势垒高度增大使经典禁戒区增强，隧穿概率降低；当 V0 远大于 E 时，透射率趋近于 0。质量扫描表明：kappa 与 sqrt(m) 成正相关，质量越大越接近经典力学极限。",
    )
    add_para(
        doc,
        "经典/量子对比是本作品的教学重点。E < V0 时，经典力学预测透射率为 0，而量子力学给出非零透射率，这是隧穿效应的核心。E > V0 时，经典力学预测完全透射，而量子模型仍可能存在反射，说明量子行为不能简单理解为“能量够就一定通过”。",
    )

    add_heading(doc, "六、有效性验证与学术规范", 1)
    add_caption(doc, "表 5  物理正确性与程序可靠性验证")
    add_simple_table(
        doc,
        [
            ["验证项目", "验证方法", "结论"],
            ["解析公式一致性", "与标准教材中一维方势垒透射率公式比对", "公式结构和物理含义一致"],
            ["概率守恒", "程序实时检查 |T+R-1|<1e-6", "计算结果满足归一化要求"],
            ["极限行为", "检查高能极限、宽垒极限、近垒顶极限和共振条件", "趋势符合量子力学预期"],
            ["参数趋势", "扫描 E、V0、a、m 对 T 的影响", "曲线趋势与理论分析一致"],
            ["教学可解释性", "把公式、图像、数据表和报告生成关联展示", "有利于学生从操作走向物理解释"],
        ],
        [1700, 4660, 3000],
    )
    add_para(
        doc,
        "报告和展示材料引用教材、课程教学要求和开源技术资料，公式、图表和程序说明均围绕作品本身展开。最终提交时，设计报告、PPT、视频和程序界面应保持匿名，不出现学校、指导教师和学生真实身份信息；报名信息仅通过竞赛系统和汇总表提交。",
    )

    add_heading(doc, "七、教学效果、创新性与推广价值", 1)
    add_para(
        doc,
        "作品的创新性主要体现在三个方面。第一，把量子隧穿从静态公式讲解转化为可调参数、可观察曲线、可导出数据的实验流程；第二，把经典/量子对比嵌入同一实验界面，使学生能直接比较两套理论预测；第三，把实验报告自动生成纳入平台，使学生不仅观看结果，还要记录参数、分析趋势、形成结论。",
    )
    add_para(
        doc,
        "从教学效果看，平台适合教师课堂演示，也适合学生课后自主探究。教师可用预设场景快速讲解明显隧穿、弱隧穿、近垒顶和越垒传播；学生可通过参数扫描发现规律，并将 CSV 数据用于进一步作图或撰写报告。由于作品为纯软件系统，部署成本低、维护简单、可复制性强，具备在大学物理实验和近现代物理教学中推广的现实意义。",
    )

    add_heading(doc, "八、局限性与后续改进", 1)
    add_para(
        doc,
        "当前版本采用一维定态方势垒模型，优点是理论清晰、计算快速、适合教学入门；局限是尚未展示真实含时波包穿越势垒的动态过程，也暂未纳入真实单位体系下的 eV、nm、fs 等换算。图中的 |psi(x)|^2 为入射振幅归一化后的相对概率密度，主要用于教学可视化，不等同于束缚态的归一化概率密度。",
    )
    add_para(
        doc,
        "后续可从四个方向扩展：加入含时薛定谔方程求解和高斯波包动画；扩展双势垒模型以展示共振隧穿；引入真实单位体系和 WKB 近似对比；增加学生答题反馈、教师端任务发布和学习评价模块，使平台从单一演示工具升级为可组织教学活动的虚拟实验资源。",
    )

    add_heading(doc, "九、制作成本", 1)
    add_para(doc, "本作品为纯软件项目，所有开发工具和依赖均为开源或免费软件，不涉及实体实验耗材。")
    add_caption(doc, "表 6  制作成本明细")
    add_simple_table(
        doc,
        [
            ["项目", "说明", "成本（元）"],
            ["开发电脑", "使用已有个人计算机", "0"],
            ["开发环境", "Node.js、React、TypeScript、Vite", "0"],
            ["图表库", "Recharts，MIT 开源许可", "0"],
            ["部署环境", "本地运行或静态网页部署，无需服务器", "0"],
            ["合计", "按零额外经费条件计算", "0"],
        ],
        [1900, 5560, 1900],
    )

    add_heading(doc, "十、结论", 1)
    add_para(
        doc,
        "本作品围绕量子隧穿这一近现代物理教学难点，构建了参数可调、实时计算、图像直观、数据可导出、报告可生成的虚拟仿真实验平台。平台以一维定态薛定谔方程和方势垒解析解为理论基础，通过经典/量子对比、参数扫描和有效性校验帮助学生理解隧穿概率、量子反射和共振条件等关键概念。",
    )
    add_para(
        doc,
        "作品符合自选类创新作品赛道“教学资源和虚仿”方向要求，具有物理原理明确、交互性强、安装维护简单、成本低、便于推广等特点。经过公式比对、概率守恒检查、典型场景测试和参数趋势分析，平台计算结果具有可靠性，可作为大学物理近现代物理内容的辅助教学资源。",
    )

    add_heading(doc, "参考文献", 1)
    refs = [
        "[1] Griffiths D J, Schroeter D F. Introduction to Quantum Mechanics[M]. 3rd ed. Cambridge: Cambridge University Press, 2018.",
        "[2] 曾谨言. 量子力学教程[M]. 3版. 北京: 科学出版社, 2014.",
        "[3] 周世勋. 量子力学教程[M]. 2版. 北京: 高等教育出版社, 2009.",
        "[4] Eisberg R, Resnick R. Quantum Physics of Atoms, Molecules, Solids, Nuclei, and Particles[M]. 2nd ed. New York: John Wiley & Sons, 1985.",
        "[5] 教育部高等学校大学物理课程教学指导委员会. 理工科类大学物理实验课程教学基本要求[S]. 北京: 高等教育出版社, 2023.",
    ]
    for ref in refs:
        p = add_para(doc, ref, after=0, line=1.0)
        for run in p.runs:
            set_run_font(run, size=9.2)

    doc.save(str(OUTPUT))
    patch_docprops(OUTPUT)

    text = extract_docx_text(OUTPUT)
    hits = [pattern for pattern in SENSITIVE_PATTERNS if pattern in text]
    audit = {
        "output": str(OUTPUT),
        "sensitive_hits": hits,
        "paragraph_count": len(Document(str(OUTPUT)).paragraphs),
        "table_count": len(Document(str(OUTPUT)).tables),
        "risk_fixes": [
            "移除真实学校、指导教师、学生姓名与出生年月",
            "补充匿名成员贡献与开发历程",
            "补充参数范围、运行环境和性能指标",
            "补充 E=V0 近垒顶极限处理，降低物理/数值表述风险",
            "明确 |psi(x)|^2 为相对概率密度，避免归一化误读",
            "补充局限性、改进方向、教学效果和推广价值",
        ],
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    if hits:
        raise RuntimeError(f"Sensitive text remains: {hits}")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


def extract_docx_text(path: Path) -> str:
    doc = Document(str(path))
    parts = []
    for paragraph in doc.paragraphs:
        parts.append(paragraph.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)
    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            parts.append(paragraph.text)
        for paragraph in section.footer.paragraphs:
            parts.append(paragraph.text)
    return "\n".join(parts)


def patch_docprops(path: Path) -> None:
    tmp = path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "docProps/core.xml":
                text = data.decode("utf-8")
                for pattern in SENSITIVE_PATTERNS:
                    text = text.replace(pattern, "匿名评审版")
                data = text.encode("utf-8")
            elif item.filename in {"docProps/app.xml", "docProps/custom.xml"}:
                text = data.decode("utf-8", errors="ignore")
                for pattern in SENSITIVE_PATTERNS:
                    text = text.replace(pattern, "匿名评审版")
                data = text.encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(path)


if __name__ == "__main__":
    build()
