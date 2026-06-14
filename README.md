# 量子隧穿虚拟仿真实验平台 (Quantum Tunneling Virtual Simulation Platform)

基于 Web 的量子隧穿效应虚拟仿真实验教学平台。

## 项目结构

```
├── work/                          # 源码与构建脚本
│   ├── quantum-tunneling-platform/  # 前端应用 (Vite + TypeScript)
│   ├── ppt_fusion/                  # 展示PPT制作
│   └── *.py, *.ps1                  # 构建/导出脚本
├── outputs/                       # 最终交付物
│   ├── upload_ready/              # 准备上传的最终文件
│   └── *.docx, *.pdf, *.pptx, *.zip  # 报告、申请书、展示材料
└── .gitignore
```

## 技术栈

- **前端**: Vite + TypeScript + React
- **测试**: Vitest
- **文档**: Python-docx, PowerPoint

## 快速开始

```bash
cd work/quantum-tunneling-platform
npm install
npm run dev
```
