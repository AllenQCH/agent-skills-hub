---
name: trace-log-analysis
description: Use when investigating an internal log platform or exported logs by traceId and the goal is to reconstruct the request timeline, find the first failing hop, separate root cause from cascading noise, and produce a concise summary with evidence. Applies to browser-based log platforms, pasted raw logs, and traceId-driven incident triage where reading logs line by line is slow or error-prone.
---

# Trace Log Analysis

## Overview
Turn traceId-based log digging into a repeatable analysis workflow. Start from a traceId or raw log export, rebuild the cross-service chronology, isolate the earliest meaningful failure, and return a compact engineer-facing conclusion with evidence and next checks.

## Workflow

### 1. Stabilize the input

Collect the minimum context before analyzing:

- Exact `traceId`
- Environment or cluster if multiple environments exist
- Approximate request time if available
- Service name, interface name, or business action if known
- Raw text logs, export link, or platform search results

If the platform requires browser login, let the user log in with their own account first. Do not ask for passwords, OTP codes, or other credentials. Prefer raw text, copied log blocks, or exported files over screenshots.

If the user only provides a `traceId`, start there. Do not block unless the logs are truly inaccessible.

### 2. Query the logs deliberately

Use the exact `traceId` first. Do not start with fuzzy keywords unless the trace lookup fails.

When reading results:

- Sort chronologically
- Keep `timestamp`, `level`, `service`, `host/pod`, `thread`, `logger`, `message`, and stack traces when present
- Expand around the first and last hit if the platform truncates context
- Group by service if the result set is large

If the trace is missing, check these before concluding anything:

- Wrong environment
- Wrong time range
- Typo or partial traceId
- Sampling or trace propagation gaps
- Logs retained in another platform or index
- Browser log-console state/cache issues. For Tencent CLS, if a newly opened URL shows zero rows but the user's current tab or screenshot has rows, bind to the current visible tab and extract from it first, for example:
  `opencli --profile pk7rrjkq browser cls-current bind`
  `opencli --profile pk7rrjkq browser cls-current extract`

### 3. Reconstruct the request timeline

Build a simple sequence instead of reading lines in isolation.

Track these event types:

- Request entry
- Downstream call start
- Retry or fallback
- Timeout
- Exception
- Business rejection
- Final response

Deduplicate obvious retry spam, heartbeat noise, and repeated wrapper errors. If multiple services emit the same failure, keep the earliest useful one and mark later copies as propagation noise.

### 4. Identify the first meaningful anomaly

The most important rule: do not treat the last `ERROR` as the root cause by default.

Find the earliest event that actually explains the breakage:

- Explicit exception with stack
- Timeout at the first downstream dependency
- Circuit breaker open
- Connection failure
- SQL, Redis, MQ, or HTTP client error
- Business validation rejection with clear reason code

Treat later messages such as "调用失败", "业务异常", "请求失败", or global exception wrappers as symptoms unless they add new technical evidence.

If the earliest visible anomaly is still only a symptom, say so explicitly and list what evidence is missing.

### 5. Separate root cause from cascade

For each suspicious log line, classify it as one of:

- Root cause candidate
- Propagated symptom
- Recovery behavior
- Irrelevant noise

Useful heuristics:

- The first timeout is usually more important than the later rollback
- The first dependency failure is usually more important than the controller-level `500`
- Fallback logs often explain impact, not cause
- Repeated retries can hide the true first failing attempt
- Missing service hops may indicate trace propagation or logging gaps rather than healthy execution

### 6. Produce a standard output

Always return the analysis in this shape:

```markdown
## 结论
- 用一句话说明最可能的故障点和影响范围

## 关键链路
- `10:01:12.001` `gateway` 接收请求
- `10:01:12.140` `order-service` 调用 `inventory-service`
- `10:01:15.142` `inventory-service` 超时/抛错
- `10:01:15.210` `order-service` 包装异常并返回失败

## 第一异常点
- 服务：
- 时间：
- 日志特征：
- 为什么判断它是第一异常点：

## 证据
```log
[贴最关键的 3-10 行原始日志]
```

## 判断
- 最可能根因：
- 连带报错：
- 当前不确定性：

## 建议下一步
- 还需要补查哪些服务、指标、时间窗口或配置
```

If evidence is weak, say "当前只能定位到第一异常症状，不能确认根因" instead of overstating certainty.

## Quick Reference

Recommended order:

1. Search exact `traceId`
2. Sort by time
3. Build service timeline
4. Mark first anomaly
5. Distinguish root cause vs cascade
6. Quote minimal evidence
7. Give conclusion and next checks

Use this skill for requests like:

- "帮我根据这个 traceId 看下哪里报错"
- "登录日志平台后按 traceId 帮我梳理调用链"
- "这些 traceId 日志太长了，帮我给出结论和证据"
- "我贴一段日志，你帮我找第一异常点"

## Common Mistakes

- 从最后一条 `ERROR` 倒推根因，忽略更早的异常
- 看到控制器 `500` 就下结论，没有继续追下游服务
- 把 fallback、限流、熔断当成根因，而不是保护动作
- 忽略重试，导致把第二次失败看成第一次失败
- 混入多个环境或多个请求窗口的日志一起分析
- 只看截图，不要求原始文本日志
- 没有明确区分"证据"和"推断"

## Rationalization Table

| Excuse | Reality |
| --- | --- |
| "最后一条 `ERROR` 肯定就是根因" | 最后一条通常只是传播后的结果，优先看第一条有技术含量的异常。 |
| "有截图就够了" | 截图容易漏时间戳、堆栈和上下文，原始文本更可靠。 |
| "traceId 查不到说明系统没问题" | 更常见的是环境、时间窗、采样或 trace 传递缺失。 |
| "先给个很确定的结论再说" | 证据不足时应明确标注不确定性，而不是装作确定。 |

## Red Flags

- 你找不到第一异常点，只是在重复最后的报错摘要
- 你无法说明某条日志为什么是根因而不是传播噪音
- 你引用的证据没有时间顺序
- 你没有指出缺失的服务、日志或上下文
- 你的结论和原始日志证据对不上

## Extension Points

Keep the first version manual-analysis friendly.

If the platform later exposes stable APIs, export functions, saved query links, or browser automation hooks, extend this skill with deterministic tooling such as:

- `scripts/` for exported log normalization
- `references/` for platform query syntax and field semantics
- Browser automation only when the login flow and security policy make it safe and maintainable
