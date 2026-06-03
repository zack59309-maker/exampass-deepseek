# 在 Hermes Agent 中作为 SKILL 使用

如果你在用 [Hermes Agent](https://hermes-agent.nousresearch.com/)，可以直接把这个功能加载为 SKILL，不需要配 DeepSeek API key（用你当前 Hermes 配置的模型即可）。

## 方法一：加载本地 SKILL

```bash
# 把仓库克隆到 Hermes skills 目录
git clone https://github.com/zack59309-maker/exampass-deepseek.git /tmp/exampass-deepseek
hermes skills install /tmp/exampass-deepseek/SKILL.md
```

然后在 Hermes 会话中：

```
/skill exampass-assistant
```

粘贴课件内容或提供文件路径，我直接帮你生成复习资料。

## 方法二：直接给 Hermes 发指令

不需要安装任何东西，在会话中直接说：

> "帮我把这份课件做成复习资料，生成知识清单 + 交互式测验"

## v1.1.0 修复内容

### LaTeX 公式显示修复
- **MathJax 配置修正** — 修复多层转义导致的公式渲染失败
- **后处理清理** — 自动将 `\(...\)`/`\[...\]` 转换为标准 `$...$`/`$$...$$`
- **AI Prompt 优化** — 明确要求标准 LaTeX 语法，给出正确示例
- **HTML 实体修复** — 自动处理 `&gt;` `&lt;` 等转义问题
- **模板 bug 修复** — 修复 `\n` 字面量导致 HTML 结构错乱
