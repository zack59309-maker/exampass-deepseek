#!/usr/bin/env python3
"""
ExamPass Assistant — DeepSeek 驱动版
====================================
用法：
  python exampass.py /path/to/course/folder
  python exampass.py /path/to/lecture.pptx

输出：知识清单 (*_knowledge.html) + 交互式测验 (*_test.html)
"""

import os
import sys
import json
import glob
import re
import time

from extractor import extract_file, merge_texts
from template_engine import save_knowledge_html, save_test

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
DEEPSEEK_MODEL = 'deepseek-chat'
API_MAX_RETRIES = 3
API_RETRY_DELAY = 2


def call_deepseek(system_prompt, user_prompt, max_tokens=4096):
    """调用 DeepSeek API，带重试逻辑。"""
    import requests
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': DEEPSEEK_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        'max_tokens': max_tokens,
        'temperature': 0.3
    }

    last_error = None
    for attempt in range(1, API_MAX_RETRIES + 1):
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers,
                                     json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            last_error = e
            if attempt < API_MAX_RETRIES:
                wait = API_RETRY_DELAY * (2 ** (attempt - 1))
                print(f"  ⚠ API 调用失败（第 {attempt} 次），{wait}s 后重试...")
                time.sleep(wait)
            else:
                print(f"  ❌ API 调用失败（已重试 {API_MAX_RETRIES} 次）: {e}")
                raise


def _cleanup_latex(html_text):
    """清理 AI 输出中常见的 LaTeX 格式问题。"""
    # 1. 将 \(...\) 替换为 $...$
    html_text = re.sub(r'\\\((.*?)\\\)', r'$\1$', html_text)
    # 2. 将 \[...\] 替换为 $$...$$
    html_text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', html_text)
    # 3. 去掉 LaTeX 命令中多余的空格: \frac{...} {..} -> \frac{...}{..}
    html_text = re.sub(r'\\([a-zA-Z]+)\s*\{', r'\\\1{', html_text)
    # 4. 修复常见的 HTML 实体转义
    html_text = html_text.replace('&gt;', '>').replace('&lt;', '<')
    # 5. 去掉空行中的多余空白
    html_text = re.sub(r'\n\s*\n', '\n', html_text)
    return html_text


def generate_knowledge(text, title):
    """调用 DeepSeek 生成知识清单。"""
    system_prompt = """你是一位资深的大学课程辅导专家。请根据课程资料生成一份**期末考试复习知识清单**。

## 输出要求
1. **核心知识点** — 定义、定理、公式、关键概念
2. **重点解题方法** — 解题步骤、技巧、常见陷阱
3. **考试高频考点** — 用 ⭐ 标注重要程度（⭐了解 ⭐⭐掌握 ⭐⭐⭐必考）

## LaTeX 公式规则（重要）
- **必须**使用标准 LaTeX 语法：行内用 `$...$`，独立公式用 `$$...$$`
- 不要在公式内使用中文或全角符号
- 示例：`$f(x) = \\int_{a}^{b} x^2 \\, dx$`  ✅
- 示例：`$$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$`  ✅
- 不要使用 `\(...\)` 或 `\[...\]` 格式
- 不要在 LaTeX 命令和花括号之间加多余空格

## 格式要求
- 使用 <h2>、<h3> 标题，不要用 markdown
- 表格用 <table><tr><th><td>
- 重要内容用 <div class="important"> 包裹
- 关键概念用 <strong> 加粗
- 所有纯文本内容直接写，不要用 HTML 转义字符代替中文"""

    # 截断防止超长，使用普通字符串拼接避免 f-string 花括号冲突
    text_truncated = text[:8000] if len(text) > 8000 else text
    user_prompt = ("请分析以下课程资料，生成期末复习知识清单。\n\n"
                   "课程名称：" + title + "\n\n"
                   "资料内容：\n" + text_truncated + "\n\n"
                   "请输出完整的 HTML 内容（body 内部分）。")

    print("  → 调用 DeepSeek 生成知识清单...")
    result = call_deepseek(system_prompt, user_prompt, max_tokens=4096)
    result = _cleanup_latex(result)
    return result


def generate_test(text, title):
    """调用 DeepSeek 生成测验题目。"""
    system_prompt = """你是一位大学课程命题专家。请根据课程资料生成一套**章节测试题**。

## 题型配比
- 选择题（约60%）：4个选项，考察概念理解和辨析
- 填空题（约20%）：挖空关键词或数值
- 简答题（约20%）：考察解题方法应用

## 质量要求
- 题目之间相互独立
- 覆盖核心知识点
- 难度梯度：60%基础 + 30%提高 + 10%综合
- 每道题标注分值

## 输出格式
输出 JSON 数组，每道题格式如下：
{{
  "type": "choice" 或 "fill",
  "points": 2,
  "question": "题目内容（支持 LaTeX: $...$）",
  "options": ["A选项", "B选项", "C选项", "D选项"],  // 仅选择题
  "answer": 0,  // 选择题：正确选项索引(0开始)；填空题：答案字符串
  "explanation": "解析内容",
  "pitfall": "常见陷阱（可选）"
}}
只输出 JSON 数组，不要加其他内容。"""

    text_truncated = text[:6000] if len(text) > 6000 else text
    user_prompt = ("请根据以下课程资料生成 8-12 道测试题。\n\n"
                   "课程名称：" + title + "\n\n"
                   "资料内容：\n" + text_truncated)

    print("  → 调用 DeepSeek 生成测验题目...")
    result = call_deepseek(system_prompt, user_prompt, max_tokens=4096)

    # 尝试解析 JSON
    # 找到 [] 包围的部分
    match = re.search(r'\[.*?\]', result, re.DOTALL)
    if match:
        try:
            questions = json.loads(match.group())
            return questions
        except json.JSONDecodeError:
            pass

    # 如果解析失败，尝试在 ```json ... ``` 中找
    match = re.search(r'```(?:json)?\s*\n(.*?)\n```', result, re.DOTALL)
    if match:
        try:
            questions = json.loads(match.group(1))
            return questions
        except json.JSONDecodeError:
            pass

    print("  ⚠ 无法解析 AI 返回的测验题目，使用备用题目")
    return _fallback_questions()


def _fallback_questions():
    """备用题目（API 失败时使用）。"""
    return [
        {"type": "choice", "points": 2,
         "question": "以下哪个是机器学习中的监督学习算法？",
         "options": ["K-Means", "KNN", "PCA", "Apriori"],
         "answer": 1,
         "explanation": "KNN（K近邻）是监督学习算法，需要标注数据训练。"},
        {"type": "choice", "points": 2,
         "question": "以下哪个指标用于分类问题评估？",
         "options": ["RMSE", "MAE", "F1-Score", "R-Squared"],
         "answer": 2,
         "explanation": "F1-Score 是分类问题的常用评估指标。"},
    ]


def process_file(filepath):
    """处理单个文件。"""
    filename = os.path.basename(filepath)
    name_no_ext = os.path.splitext(filename)[0]
    folder = os.path.dirname(filepath) or '.'
    title = name_no_ext

    print(f"\n📄 处理: {filename}")
    text = extract_file(filepath)
    print(f"   提取文本: {len(text)} 字符")

    # 生成知识清单
    knowledge_html = generate_knowledge(text, title)
    knowledge_path = os.path.join(folder, f"{name_no_ext}_knowledge.html")
    save_knowledge_html(knowledge_html, knowledge_path, title)
    print(f"   ✅ 知识清单: {knowledge_path}")

    # 生成测验
    questions = generate_test(text, title)
    test_path = os.path.join(folder, f"{name_no_ext}_test.html")
    save_test(questions, test_path, title)
    print(f"   ✅ 测验题目: {test_path} ({len(questions)} 题)")


def process_folder(folder):
    """处理文件夹下所有支持的文档。"""
    supported = []
    for ext in ('*.pptx', '*.docx', '*.pdf', '*.PPTX', '*.DOCX', '*.PDF'):
        supported.extend(glob.glob(os.path.join(folder, ext)))

    if not supported:
        print(f"❌ 在 {folder} 中没有找到 PPTX/DOCX/PDF 文件")
        return

    print(f"\n📁 找到 {len(supported)} 个文件在 {folder}")
    for fpath in sorted(supported):
        process_file(fpath)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if not DEEPSEEK_API_KEY:
        print("❌ 请设置环境变量 DEEPSEEK_API_KEY")
        print("   export DEEPSEEK_API_KEY='你的key'")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isfile(target):
        process_file(target)
    elif os.path.isdir(target):
        process_folder(target)
    else:
        print(f"❌ 找不到: {target}")
        sys.exit(1)

    print("\n✅ 全部完成！")


if __name__ == '__main__':
    main()
