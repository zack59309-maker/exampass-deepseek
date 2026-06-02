# ExamPass Assistant — DeepSeek 驱动版

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)]()
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)

**把课件（PPT/Word/PDF）一键变成知识清单 + 交互式测验 HTML 页面。**  
基于 DeepSeek API（`deepseek-chat` 模型），自动提取课件文本 → 调用 AI 生成复习材料。

原项目 [ExamPass-Assistant](https://github.com/WUBING2023/ExamPass-Assistant) 用 Claude 驱动，此版本改为 DeepSeek API。

---

## 功能

| 输入 | 输出 |
|------|------|
| PPTX / DOCX / PDF | 📖 **知识清单** — 结构化复习笔记，含目录、重点标注、LaTeX 公式 |
| 支持单文件或整个文件夹 | 📝 **交互式测验** — 选填结合，一键批改，显示解析 |
| 从终端命令行运行 | 两个 HTML 文件，浏览器打开即用 |

---

## 快速开始

### 1. 克隆

```bash
git clone https://github.com/zack59309-maker/exampass-deepseek.git
cd exampass-deepseek
```

### 2. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 设置 API Key

```bash
export DEEPSEEK_API_KEY='sk-你的key'
```

> 没有 DeepSeek API key？[去平台注册](https://platform.deepseek.com/)，注册送 500 万 tokens。

### 4. 运行

```bash
# 处理一个文件夹下所有课件
python exampass.py /path/to/课件文件夹/

# 处理单个文件
python exampass.py /path/to/lecture.pptx
```

输出文件在课件同目录下，用浏览器打开即可查看：

- `*_knowledge.html` — 知识清单（带目录、可打印）
- `*_test.html` — 交互式测验（在线做题、批改、看解析）

---

## 输出示例

**知识清单页面：**
- 自动提取标题和层级 → 生成目录
- 双色高亮（重点 ⭐⭐⭐ / 普通）
- LaTeX 数学公式支持（由 MathJax 渲染）
- `Ctrl+P` 可直接打印为 PDF

**测验页面：**
- 选择题点击作答
- 填空题输入
- 一键批改 + 得分显示
- 每题解析 + 常见陷阱说明

---

## 项目结构

```
exampass-deepseek/
├── exampass.py          # 主入口：提取 → 调 AI → 生成 HTML
├── extractor.py         # PPTX/DOCX/PDF 文本提取
├── template_engine.py   # HTML 模板引擎（CSS + JS 模板）
├── requirements.txt     # Python 依赖
├── HERMES_SKILL.md      # 在 Hermes Agent 中作为 SKILL 使用
├── LICENSE
└── README.md
```

## Hermes Agent 用户

如果你在用 [Hermes Agent](https://hermes-agent.nousresearch.com/)，还可以直接把此功能作为 SKILL 加载，无需 DeepSeek API key：

```
/skill exampass-assistant
```

详见 [HERMES_SKILL.md](HERMES_SKILL.md)。

## 技术依赖

| 用途 | 库 |
|------|----|
| 提取 PPTX | `python-pptx` |
| 提取 DOCX | `python-docx` |
| 提取 PDF | `pymupdf` |
| AI 调用 | `requests` + DeepSeek API |
| 前端渲染 | 纯 HTML + CSS + JS，零外部依赖 |
| 公式渲染 | MathJax（从 CDN 加载） |

---

## 注意事项

- 需要 **DeepSeek API key**（环境变量 `DEEPSEEK_API_KEY`）
- 课件文本超过 8000 字符会自动截断（控制 API 费用）
- API 调用失败会自动重试 3 次
- 支持的格式：`.pptx` `.docx` `.pdf`
- 生成的知识清单/测验默认保存在课件所在目录

---

## License

CC BY-NC 4.0 — 可自由使用和修改，禁止商业用途。
