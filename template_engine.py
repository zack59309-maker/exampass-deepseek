"""模板引擎：生成漂亮的知识清单 HTML 和交互式测验 HTML。"""

import os
import json
import re

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
os.makedirs(TEMPLATES_DIR, exist_ok=True)


# ===== 知识清单 CSS =====
KNOWLEDGE_CSS = """
:root {
  --bg: #faf6f0;
  --ink: #2c2c2c;
  --ink-light: #888;
  --accent: #c0392b;
  --accent2: #2980b9;
  --border: #e0d8cc;
  --important-bg: #fff3cd;
  --important-border: #ffc107;
  --code-bg: #eee8d5;
  --font: 'Georgia', 'Noto Serif SC', serif;
}
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--ink);
  max-width: 900px;
  margin: 0 auto;
  padding: 20px 30px 60px;
  line-height: 1.8;
  font-size: 16px;
}
h1 { color: var(--ink); border-bottom: 3px solid var(--accent); padding-bottom: 8px; }
h2 { color: var(--ink); border-bottom: 1px solid var(--border); padding-bottom: 4px; margin-top: 2em; }
h3 { color: var(--accent2); margin-top: 1.5em; }
.toc { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 15px 20px; margin: 20px 0; }
.toc ul { list-style: none; padding-left: 0; }
.toc li { margin: 4px 0; }
.toc a { color: var(--accent2); text-decoration: none; }
.toc a:hover { text-decoration: underline; }
blockquote { border-left: 4px solid var(--accent); margin: 15px 0; padding: 10px 15px; background: #fefcf8; }
.important { background: var(--important-bg); border: 1px solid var(--important-border); border-radius: 6px; padding: 10px 15px; margin: 15px 0; }
.tag { display: inline-block; font-size: 12px; padding: 2px 8px; border-radius: 10px; margin-right: 6px; }
.tag-bikao { background: #e74c3c; color: #fff; }
.tag-zhangwo { background: #f39c12; color: #fff; }
.tag-pinchang { background: #3498db; color: #fff; }
.tag-lejie { background: #95a5a6; color: #fff; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; }
th, td { border: 1px solid var(--border); padding: 8px 12px; text-align: left; }
th { background: var(--border); font-weight: bold; }
code { background: var(--code-bg); padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }
@media print { body { background: #fff; } .toc { break-inside: avoid; } }
"""

# ===== 测验 CSS =====
TEST_CSS = """
:root {
  --bg: #faf6f0; --ink: #2c2c2c; --ink-light: #888;
  --correct: #27ae60; --wrong: #e74c3c; --border: #e0d8cc;
  --font: 'Georgia', 'Noto Serif SC', serif;
}
body { font-family: var(--font); background: var(--bg); color: var(--ink); max-width: 800px; margin: 0 auto; padding: 20px 30px 60px; }
h1 { border-bottom: 3px solid #c0392b; padding-bottom: 8px; }
.question-box { border: 1px solid var(--border); border-radius: 8px; padding: 15px 20px; margin: 15px 0; background: #fefcf8; }
.question-box.correct { border-color: var(--correct); background: #eafaf1; }
.question-box.wrong { border-color: var(--wrong); background: #fdedec; }
.options { margin: 10px 0; }
.option { display: block; padding: 8px 12px; margin: 4px 0; border: 1px solid var(--border); border-radius: 6px; cursor: pointer; }
.option:hover { background: #f0ebe3; }
.option.selected { background: #d5e8f0; border-color: #2980b9; }
.option.correct-answer { background: #d5f5e3; border-color: var(--correct); }
.option.wrong-answer { background: #fadbd8; border-color: var(--wrong); }
.explanation { margin-top: 10px; padding: 10px; border-radius: 6px; background: #fefcf8; border: 1px dashed var(--border); display: none; }
.explanation.show { display: block; }
#score-box { text-align: center; font-size: 2em; margin: 20px 0; }
.score-num { font-size: 1.5em; font-weight: bold; color: #c0392b; }
.grading-bar { text-align: center; margin: 20px 0; }
.grading-bar button { padding: 10px 30px; font-size: 1em; background: #c0392b; color: #fff; border: none; border-radius: 6px; cursor: pointer; }
.grading-bar button:hover { background: #a93226; }
.fill-input { border: none; border-bottom: 2px dashed #888; padding: 4px 8px; font-size: 1em; width: 200px; background: transparent; }
.fill-input.correct { border-bottom-color: var(--correct); }
.fill-input.wrong { border-bottom-color: var(--wrong); }
@media print { .no-print { display: none; } }
"""

# ===== 测验 JS =====
TEST_JS = """
const QUESTIONS = __QUESTIONS_PLACEHOLDER__;
const labels = __LABELS_PLACEHOLDER__;

function render() {
  const container = document.getElementById('questions-container');
  QUESTIONS.forEach((q, i) => {
    const div = document.createElement('div');
    div.className = 'question-box';
    div.id = 'q' + i;
    let html = '<p><strong>' + (i+1) + '. ' + q.question + '</strong> (' + q.points + '分)</p>';
    if (q.type === 'choice') {
      html += '<div class="options">';
      q.options.forEach((opt, j) => {
        html += '<label class="option" onclick="selectOption(' + i + ',' + j + ')">' +
          '<input type="radio" name="q' + i + '" value="' + j + '" style="display:none"> ' +
          String.fromCharCode(65 + j) + '. ' + opt + '</label>';
      });
      html += '</div>';
    } else if (q.type === 'fill') {
      html += '<p><input type="text" class="fill-input" id="fill' + i + '" placeholder="输入答案..."></p>';
    }
    html += '<div class="explanation" id="exp' + i + '">';
    if (q.explanation) html += '<p><strong>' + labels.explanation_label + '</strong>' + q.explanation + '</p>';
    if (q.pitfall) html += '<p><strong>' + labels.pitfall_label + '</strong>' + q.pitfall + '</p>';
    html += '</div></div>';
    div.innerHTML = html;
    container.appendChild(div);
  });
}

function selectOption(qIdx, optIdx) {
  const q = QUESTIONS[qIdx];
  const options = document.querySelectorAll('#q' + qIdx + ' .option');
  options.forEach((opt, j) => {
    opt.classList.toggle('selected', j === optIdx);
    const radio = opt.querySelector('input');
    if (radio) radio.checked = (j === optIdx);
  });
}

function gradeAll() {
  let total = 0, correct = 0;
  QUESTIONS.forEach((q, i) => {
    const box = document.getElementById('q' + i);
    box.classList.remove('correct', 'wrong');
    const exp = document.getElementById('exp' + i);
    let isCorrect = false;
    if (q.type === 'choice') {
      const selected = document.querySelector('#q' + i + ' input:checked');
      const val = selected ? parseInt(selected.value) : -1;
      isCorrect = (val === q.answer);
      document.querySelectorAll('#q' + i + ' .option').forEach((opt, j) => {
        opt.classList.remove('correct-answer', 'wrong-answer');
        if (j === q.answer) opt.classList.add('correct-answer');
        if (j === val && j !== q.answer) opt.classList.add('wrong-answer');
      });
    } else if (q.type === 'fill') {
      const input = document.getElementById('fill' + i);
      const ans = input.value.trim().toLowerCase();
      const expected = String(q.answer).toLowerCase();
      isCorrect = (ans === expected || ans.includes(expected) || expected.includes(ans));
      if (isCorrect) input.classList.add('correct'); else input.classList.add('wrong');
    }
    if (isCorrect) { correct++; total += q.points; box.classList.add('correct'); }
    else { box.classList.add('wrong'); }
    exp.classList.add('show');
  });
  document.getElementById('score-num').textContent = total + '/' + QUESTIONS.reduce((s,q) => s+q.points, 0);
  if (window.MathJax && MathJax.typesetPromise) {
    MathJax.typesetPromise();
  }
}

function resetAll() {
  QUESTIONS.forEach((q, i) => {
    const box = document.getElementById('q' + i);
    box.classList.remove('correct', 'wrong');
    document.getElementById('exp' + i).classList.remove('show');
    if (q.type === 'choice') {
      document.querySelectorAll('#q' + i + ' .option').forEach(opt => {
        opt.classList.remove('selected', 'correct-answer', 'wrong-answer');
        const radio = opt.querySelector('input');
        if (radio) radio.checked = false;
      });
    } else if (q.type === 'fill') {
      const input = document.getElementById('fill' + i);
      input.value = '';
      input.classList.remove('correct', 'wrong');
    }
  });
  document.getElementById('score-num').textContent = '0';
}

window.onload = function() {
  render();
  if (window.MathJax && MathJax.typesetPromise) {
    MathJax.typesetPromise();
  }
};
"""

TEST_LABELS = json.dumps({
  "page_title": "章节测验",
  "score_label": "得分",
  "grade_button": "提交批改",
  "reset_button": "重新作答",
  "explanation_label": "解析：",
  "pitfall_label": "常见陷阱：",
  "duration_prefix": "建议用时：",
  "duration_suffix": " 分钟"
})

# ===== 页面 HTML 模板 =====
PAGE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
__MATHJAX_CONFIG__
<style>
__CSS__
</style>
__MATHJAX_SCRIPT__
</head>
<body>
__BODY__
__EXTRA_JS__
</body>
</html>"""

MATHJAX_CONFIG = """<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true,
    packages: {'[+]': ['noerrors']}
  },
  options: {
    ignoreHtmlClass: 'no-mathjax',
    processHtmlClass: 'mathjax'
  },
  loader: {load: ['[tex]/noerrors']}
};
</script>"""
MATHJAX_SCRIPT = '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml-full.js"></script>'


def _build_page(title, body_html, css_extra='', js_extra=''):
    css = KNOWLEDGE_CSS + '\n' + css_extra
    return (PAGE_HTML
            .replace('__TITLE__', title)
            .replace('__MATHJAX_CONFIG__', MATHJAX_CONFIG)
            .replace('__MATHJAX_SCRIPT__', MATHJAX_SCRIPT)
            .replace('__CSS__', css)
            .replace('__BODY__', body_html)
            .replace('__EXTRA_JS__', js_extra))


def _auto_toc(body_html, title):
    """Auto-inject H1 title + TOC."""
    h1_html = f'<h1>{title}</h1>\n'
    toc_items = []
    def replace_heading(m):
        level = int(m.group(1))
        text = m.group(2).strip()
        clean = re.sub(r'<[^>]+>', '', text)
        anchor = 's' + str(abs(hash(clean)))[:8]
        toc_items.append({'level': level, 'text': clean, 'anchor': anchor})
        return f'<h{level} id="{anchor}">{text}</h{level}>'
    body_html = re.sub(r'<h([23])[^>]*?>(.+?)</h\1>', replace_heading, body_html, flags=re.DOTALL)
    if toc_items:
        toc = '<div class="toc">\n<h2>目录</h2>\n<ul>\n'
        for item in toc_items:
            indent = '  ' if item['level'] == 3 else ''
            toc += f'{indent}<li><a href="#{item["anchor"]}">{item["text"]}</a></li>\n'
        toc += '</ul>\n</div>\n'
    else:
        toc = ''
    return h1_html + toc + body_html


def save_knowledge_html(body_html, output_path, title):
    """生成知识清单 HTML 文件。"""
    body_html = _auto_toc(body_html, title)
    html = _build_page(title, body_html)
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def save_test(questions, output_path, title, duration_minutes=30):
    """生成交互式测验 HTML 文件。

    questions: [{type, points, question, options?, answer, explanation?, pitfall?}]
    """
    questions_json = json.dumps(questions, ensure_ascii=False)
    labels_json = TEST_LABELS

    js = (TEST_JS
          .replace('__QUESTIONS_PLACEHOLDER__', questions_json)
          .replace('__LABELS_PLACEHOLDER__', labels_json))
    js = '<script>\n' + js + '\n</script>'

    sub_html = f'<p style="text-align:center;color:var(--ink-light);font-size:0.95em">建议用时：{duration_minutes} 分钟</p>'
    body = '\n'.join([
        '<h1>' + title + '</h1>',
        '<h2 style="text-align:center">章节测验</h2>',
        sub_html,
        '<div id="score-box"><div class="score-num" id="score-num">0</div><div class="score-label">得分</div></div>',
        '<div id="questions-container"></div>',
        '<div class="grading-bar no-print">'
        '<button onclick="gradeAll()" id="grade-btn">提交批改</button>'
        ' <button onclick="resetAll()" id="reset-btn" style="margin-left:10px;background:#7f8c8d">重新作答</button>'
        '</div>',
    ])
    html = _build_page(title, body, css_extra=TEST_CSS, js_extra=js)
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
