# ExamPass Assistant — DeepSeek 驱动版

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)]()
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)

**把课件（PPT/Word/PDF）一键变成知识清单 + 交互式测验。**

> 基于 [ExamPass-Assistant](https://github.com/WUBING2023/ExamPass-Assistant) 的 DeepSeek 移植版。原项目用 Claude 驱动，此版本改为 DeepSeek API，同样免费、高效。
>
> 适用于：期末复习、章节自测、课堂练习生成。

---

## 功能

| 输入 | 输出 |
|------|------|
| PPTX / DOCX / PDF | 📖 **知识清单** — 结构化复习笔记，带数学公式、目录、重点标注 |
| 支持单文件或整个文件夹 | 📝 **交互式测验** — 在线做题，一键批改，看解析 |

---

## 快速开始

### 1. 安装

```bash
git clone https://github.com/zack59309-maker/exampass-deepseek.git
cd exampass-deepseek
pip install -r requirements.txt
```

### 2. 设置 API Key

```bash
export DEEPSEEK_API_KEY='你的key'
```

### 3. 运行

```bash
# 处理文件夹下所有课件
python exampass.py /path/to/course/folder

# 处理单个文件
python exampass.py /path/to/lecture.pptx
```

生成的文件和课件在同一目录下：
- `*_knowledge.html` — 知识清单
- `*_test.html` — 交互式测验（用浏览器打开即可做题）

---

## 示例

输入一个 PPTX 文件 → 得到两个 HTML 文件：

**知识清单页面：**
- 自动生成目录
- 双色高亮（重点/普通）
- ⭐ 标注重要程度
- LaTeX 数学公式支持
- Ctrl+P 可直接打印为 PDF

**测验页面：**
- 选择题点击作答
- 填空填输入
- 一键批改 + 显示得分
- 每题解析 + 常见陷阱说明

---

## 项目结构

```
exampass-deepseek/
├── exampass.py          # 主入口：提取 → 调 AI → 生成 HTML
├── extractor.py         # 文件内容提取（PPTX/DOCX/PDF）
├── template_engine.py   # HTML 模板引擎
├── requirements.txt     # Python 依赖
├── LICENSE
└── README.md
```

## 技术依赖

- **提取**：python-pptx / python-docx / pymupdf / pdfplumber
- **AI**：DeepSeek API（deepseek-chat 模型）
- **前端**：纯 HTML + CSS + JS，零外部依赖（MathJax 从 CDN 加载）

## License

CC BY-NC 4.0 — 可自由使用和修改，禁止商业用途。
