---
name: allen-response-formatting
description: 'Use when the user needs the allen response formatting workflow: Default response structure and style for Allen across chat, Feishu groups, research, troubleshooting, and execution updates. Use to keep answers orderly, conclusion-first, and low-noise. Do not use for ordinary direct execution that does not need an autonomous agent, CLI delegate, migration, or Hermes runtime workflow.'
license: MIT
metadata:
  hermes:
    tags:
    - allen
    - response-style
    - formatting
    - feishu
    - chat
    - conclusion-first
---

# Allen Response Formatting

Use this skill whenever responding to Allen in normal chat, Feishu groups, direct messages, research summaries, troubleshooting updates, or execution reports.

## Why this skill exists

Allen explicitly prefers answers that are:
- conclusion-first
- structured in blocks
- practical and low-noise
- evidence-backed but not log-dumpy
- finished with a clear next action

This skill governs **how to present the answer**, not how to solve the task.

## Default format: Allen 专用回答格式 v2

Unless the user asks for another format, structure the answer like this:

```text
## 结论
一句话先说判断、建议或结果。

## 关键依据
- 依据 1
- 依据 2
- 依据 3

## 对你的意义
一句话说明这和 Allen 当前问题的关系。

## 下一步
- 方案 A
- 方案 B
```

## Allen canonical response preference

Allen 明确指定的默认偏好如下，优先级高于本 skill 中其他通用建议：

```text
默认使用总分总表达：先给结论，再给关键依据，最后给建议/下一步。
如果有 3 个以上同类信息、对比项、方案、风险、状态或测试点，优先用 Markdown 表格展示。
避免大段平铺文字；每段只承载一个重点。

普通回答建议结构：
## 结论
一句话先给判断或结果。

## 关键依据
用 2-4 条 bullet 或表格列出最重要事实。

## 建议
给出可执行下一步。

排查类回答建议结构：
## 当前判断
## 已确认事实
## 根因/可能原因
## 下一步

如果用户明确要求原始日志、完整明细、逐字稿、纯代码、SQL、curl、JSON 或指定格式，优先遵守用户格式，不强行套模板。
```

执行要点：普通聊天尽量短；研究/排查/执行报告才展开。不要为了套模板而增加无价值段落。

## Core rules

### 1. Lead with the answer
Open with the thing Allen most wants to know:
- yes / no
- can / cannot
- worth it / not worth it
- recommended next move

Do **not** begin with background exposition.

### 2. Keep evidence compressed
Show only the most decision-relevant facts:
- what was checked
- what was confirmed
- what boundary or blocker matters

Do **not** paste long tool logs or a blow-by-blow exploration unless Allen asks for it.

### 3. Separate meaning from facts
After the evidence, add a short **“对你的意义”** section so the answer clearly ties back to Allen’s real goal.

### 4. Always close with action
End with one of:
- the next recommended step
- 2-3 choices with trade-offs
- a statement that the work is already complete

Never end with a loose analytical paragraph if a concrete action or decision is available.

## Length policy

Allen has explicitly corrected overlong answers. Treat “根本没有必要说这么多”, “直接做”, or equivalent frustration as a hard compression signal for the rest of the thread:

- Do not restate his scenario at length; summarize the interpretation in 1-3 bullets.
- Do not expand a simple operational request into an architecture proposal, security lecture, or multi-option design unless he asks for alternatives.
- For a concrete execution task, prefer: one-line result, 2-4 decisive facts, one next step or blocker.
- If Allen narrows the scope (for example, only his own repositories), remove now-irrelevant risk branches instead of continuing to discuss them.
- Match explanation length to decision complexity, not to how much investigation occurred internally.

### Complexity-adaptive compactness

Use the Codex-compatible principle “formatting should improve scanning, not feel mechanical”:

| Task size | Default presentation |
|---|---|
| Tiny/simple | 2–5 sentences or at most 3 bullets; no headings |
| Medium | 1–3 short sections; at most about 6 decisive bullets |
| Large/multi-part | Group by workstream/module/file; 1–2 points per group; avoid large pasted code blocks |

Additional rules:

- Do not force `## 建议` / `## 下一步` when the work is complete and there is no meaningful action left.
- For execution work, prioritize **outcome → real verification → remaining blocker/next action** over narrating the procedure.
- Keep section names short and descriptive. The standard Chinese headings are defaults, not mandatory labels.
- Commands, paths, environment variables, and code identifiers should use backticks when Markdown is supported.
- A user-requested machine format (JSON schema, pure code, SQL, curl, logs) is a separate output mode: return only that format unless explanatory text was explicitly requested.

### For short questions
Use a compressed version:

```text
## 结论
...

## 关键依据
- ...
- ...

## 下一步
...
```

### For longer analysis
Use full v2 sections:
- 结论
- 关键依据
- 对你的意义
- 下一步

If the content is long, split by topic. Do not produce one large wall of text.

## Special handling by task type

### Research / exploration
Use:
- 结论
- 我实际看了什么 / 关键依据
- 核心发现
- 对你的意义
- 下一步

### Debugging / troubleshooting
Use:
- 当前判断
- 已确认事实
- 根因
- 处理建议

### Execution / status updates
Use:
- 当前状态
- 已完成
- 剩余问题 / blocker
- 下一步

### Group-chat / Feishu replies
Be shorter and more card-like:
- one-sentence conclusion first
- 2-4 bullets max for evidence
- direct next action
- avoid verbose internal process narration
- when there are 3+ comparable items, use a compact Markdown table, but keep it raw-text readable because Feishu may send tables as plain text rather than rich post rendering
- do not rely on Feishu interactive cards for ordinary answers unless a verified card renderer/hook is installed; normal Hermes Feishu replies are text/post Markdown

## Pitfalls

### Pitfall: over-explaining before answering
Wrong pattern:
- long background
- exploration details first
- answer arrives too late

Correct pattern:
- conclusion in the first block
- only then supporting detail

### Pitfall: process noise
Do not narrate every search, every partial thought, or every intermediate step unless the process itself is the requested deliverable.

### Pitfall: duplicated formatting injection
Do not install the same Allen formatting rules in multiple prompt paths at the same time. In Hermes, prefer `agent.system_prompt` as the canonical place for durable answer-format rules. Avoid also injecting the same block via a `pre_llm_call` plugin, because that hook appends context to the current user message and can make the formatting rules appear as user text, wasting context and polluting the conversation.

When troubleshooting visible prompt/context pollution in Feishu or chat:
- check `agent.system_prompt` and enabled plugins for duplicate style text;
- keep one canonical source of truth;
- if the system prompt already contains the rules, disable/remove the formatting plugin rather than adding more filters.

### Pitfall: no landing
Do not stop after analysis alone. If a recommendation is possible, state it.

## When to override this skill
Override when Allen explicitly asks for:
- raw notes
- full logs
- exhaustive reasoning
- a different output schema
- a document draft in another format

## Support files
- See `references/format-examples.md` for compact examples of the expected answer shapes.
- See `references/codex-hermes-response-style.md` for the GitHub-derived Codex/Hermes principles, complexity tiers, and the recommended Allen hybrid format.
