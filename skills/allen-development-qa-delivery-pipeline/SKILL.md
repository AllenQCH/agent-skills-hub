---
name: allen-development-qa-delivery-pipeline
description: Use when 用户请求匹配此工作流：Allen 默认的 workspace-based multi-agent 开发需求交付编排：workspace→Codex/multi-agent 路由→开发迭代→具体需求→目标文件夹，然后执行规则串行、开发并行、验收串行、交付流水线。适用于一个需求跨服务/仓库/接口，需要 Developer Agent 实现、独立 Acceptance QA Agent 把关、CI 流水线和提测文档后才算完成. Do not use for tasks outside this software-development workflow or tasks better handled by a narrower debugging, testing, planning, or review skill.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - development-workflow
    - multi-agent
    - qa-gate
    - ci
    - delivery
    - test-submission
    related_skills:
    - acceptance-qa-agent
    - subagent-driven-development
    - test-driven-development
    - requesting-code-review
    - systematic-debugging
---

# Allen Development QA Delivery Pipeline

## Purpose

This document records Allen's multi-agent development orchestration, not a user-facing trigger phrase. Do not tell Allen to invoke this skill manually. Use it as internal procedural memory when coordinating work.

Allen's actual working shape is not “manual skill invocation”. It is workspace-based multi-agent orchestration:

```text
workspace → Codex / multi-agent routing → development iteration → specific requirement → target folder → workflow execution
```

When Allen gives a development task, first route within the workspace/iteration/requirement/folder context, then run the workflow. Do not frame this as Allen needing to name or trigger a skill.

This is Allen's default workflow:

```text
规则串行 → 开发并行 → 验收串行 → 交付流水线
Serial Planning → Parallel Implementation → Serial Acceptance → Delivery Pipeline
```

A requirement is **not done** when code is written. It is done only after QA Gate, commit/push, CI pipeline, test-submission documentation, real-evidence acceptance, release observation (when release is in scope), and closeout learning are complete. Production/pre-production release remains a human-confirmed action unless Allen explicitly delegates it.

## Definition of Done

```text
Done =
  Requirement baseline clear
  + Implementation complete
  + Reviewer has no blocking issue
  + Acceptance QA Gate passed
  + Commit complete
  + Push complete
  + CI / pipeline passed
  + Test-submission document created
  + Final delivery summary confirmed
```

## Core Rules

1. **规则串行**: planning and contracts must be unified before implementation.
2. **开发并行**: after rules are clear, split by repo/service and run developer subagents in parallel when useful.
3. **验收串行**: main agent must integrate, review, and run independent QA Gate before delivery.
4. **交付流水线**: only after QA Gate passes, commit, push, observe CI, fix failures, and create test-submission documentation.
5. Developer Agent can say `implementation complete`, but cannot say `requirement complete`.
6. Acceptance QA Agent must be independent and requirement-first.
7. If code changes after QA Gate because of review or CI failure, rerun impacted QA cases before final delivery.
8. Do not push/commit unless the user has provided enough repo context and it is safe for the current task.

## Requirement Link Intake — 飞书控制面 × 本地 Multi-Agent 执行面

**Implementation standard:** this workflow is not considered implemented merely because a Skill, prompt, plan, or diagram exists. Inspect Allen's actual local Multi-Agent runtime source of truth, add/register the required Agent and deterministic execution entry, update the routing/contracts, and verify runtime loading plus dry-run/tests. The Feishu group is the control plane; the registered local Codex Multi-Agent is the execution plane.

For the concrete architecture, binding schema, verification checklist, and pitfalls, read `references/feishu-control-plane-local-codex-execution.md`.

When Allen provides a requirement URL and asks to start collaboration:

1. Read the accessible requirement source and extract demand id/title, region, module, expected behavior and acceptance clues.
2. Create or reuse one Feishu group per canonical requirement URL using the registered local operator:

```bash
python3 ~/.codex/agents/operator/scripts/tool_lark_requirement_group_operator.py \
  --demand-url '<url>' \
  --title '<requirement title>' \
  --region '<cn|intl>' \
  --module '<module>' \
  --role '<development role>' \
  --primary-workspace '<absolute path>' \
  --execute
```

3. Treat the Feishu group as the **communication and human-confirmation control plane**. Treat Allen's registered local Codex four-layer multi-agent framework (`control -> stage -> tool -> gate`) as the **execution plane**.
4. Persist/reuse the binding in `~/.codex/state/lark-requirement-groups.json`: requirement URL/demand id -> `chat_id`, role, primary workspace and prompt file.
5. Continue clarification and design confirmation in the group. Group creation must not silently start Codex or mutate repositories.
6. After `gate_design_confirmed`, route the bound prompt/workspace into the local Codex workflow. Preserve `stage_test_runner` and `gate_test_passed` before commit/push/pipeline.
7. OpenSpec, repositories and reproducible verification evidence remain the durable source of truth; chat history is context and audit trail, not a replacement for implementation artifacts.

## Phase 0 — 上下文快照 / Context Snapshot

Before clarification or planning, collect only the stage-relevant facts instead of dumping everything into one prompt:

- Current requirement materials: ticket/PRD, comments, user additions, linked documents.
- Long-term business knowledge: stable rules, system boundaries, codemap, prior confirmed decisions.
- Code facts: repository rules, current implementation, interfaces, configs, dependencies.
- Runtime evidence when relevant: logs, metrics, environment/config state.

Store demand-specific artifacts on the requirement branch/workspace; do **not** promote raw process material directly into long-term knowledge. Missing or conflicting fact sources are a blocking condition and must be surfaced before implementation.

Expected output: a traceable context snapshot stating source, freshness, conflicts, and unknowns.

## Phase A — 规则串行 / Serial Planning

The main agent performs this phase serially. Do not parallelize until contracts and boundaries are clear.

### Steps

1. Confirm requirement and goal.
2. Identify in-scope and out-of-scope behavior.
3. Inspect repo/service structure and relevant project rules.
4. Identify impacted repositories, services, APIs, jobs, DB tables, configs, and integrations.
5. Create or summarize requirement baseline / OpenSpec if applicable.
6. Define acceptance criteria.
7. Design QA strategy and P0/P1/P2 test focus.
8. Apply interface-change gate:
   - endpoint/method changes
   - request/response schema changes
   - auth/permission changes
   - backward compatibility risks
   - downstream consumers
9. Create Diff Plan by repo/service.
10. Confirm branch strategy.
11. Generate task packages for Developer Agents.

### Outputs

Use project-native docs if available. Otherwise create or summarize:

```text
.requirement/requirements.md
.requirement/acceptance-criteria.md
.requirement/test-strategy.md
.requirement/diff-plan.md
.requirement/agent-task-packages.md
```

If a project already uses OpenSpec, follow OpenSpec instead of inventing another format.

## Phase B — 开发并行 / Parallel Implementation

After Phase A is stable, spawn Developer Agents by service/repo/module when the work can be isolated.

### Developer Agent Task Package

Each Developer Agent receives:

```text
- Requirement baseline
- This service/repo scope
- Allowed files / forbidden files
- Interface contract and dependencies
- Required tests
- Local verification command
- Output format
```

### Developer Agent Responsibilities

Each Developer Agent:

1. Reads local repo rules.
2. Locates relevant code.
3. Writes or updates tests where appropriate.
4. Implements the scoped change.
5. Runs narrow local verification.
6. Reports changed files, test results, assumptions, and risks.

Developer Agent final wording:

```text
Implementation complete for <service/repo>; waiting for integration and QA Gate.
```

Never:

```text
Requirement complete.
```

## Phase C — 验收串行 / Serial Acceptance

The main agent returns to a serial integration role.

### Steps

1. Collect all Developer Agent outputs.
2. Inspect unified diff across repos/services.
3. Run code quality review or Reviewer Agent:
   - security
   - maintainability
   - regression risk
   - duplicated logic
   - contract mismatch
4. Run Acceptance QA Agent using `acceptance-qa-agent` workflow:
   - requirement-first behavior map
   - acceptance criteria coverage matrix
   - natural-language test cases
   - automate high-value API/integration cases
   - execute tests where possible
   - collect evidence
   - give release gate decision
5. If QA finds defects, send back to Developer Agent, then rerun impacted QA cases.

### QA Gate Outcomes

```text
Pass
Conditional Pass
Do Not Release
Blocked / Needs Clarification
```

### Gate Policy

- Critical issue → Do Not Release.
- P0 failure → Do Not Release.
- Ambiguous P0 behavior → Blocked / Needs Clarification.
- High issue → usually Conditional Pass only with explicit workaround and owner acceptance.
- Automated tests passing is not enough without acceptance-criteria mapping.

## Phase D — 交付流水线 / Delivery Pipeline

Only start this phase after QA Gate is `Pass` or an explicitly accepted `Conditional Pass`.

### D1. Pre-commit Check

Before commit:

```bash
git status
git diff --stat
git diff
```

Check:

- no unrelated files
- no secrets/tokens/log dumps
- no accidental generated files
- test/QA report included if appropriate
- QA Gate result is recorded

### D2. Commit

Use structured commit message:

```text
feat(scope): requirement summary

- change 1
- change 2
- tests/QA coverage
- QA Gate: Pass

Refs: <ticket/link>
```

For fixes:

```text
fix(scope): issue summary
```

### D3. Push

Push the feature branch:

```bash
git push origin <branch>
```

For multi-repo work, push by repo. Parallel push/CI observation is acceptable, but final integration remains serial.

### D4. CI / Pipeline Observation

Observe CI pipelines concurrently where useful.

Each CI observer should report:

```text
- repo/service
- branch/commit
- pipeline URL
- status
- failed job, if any
- relevant logs
- likely cause
- suggested fix
```

If CI fails:

1. Classify cause: code / test / env / dependency / flaky.
2. Fix through Developer Agent or main agent.
3. Rerun targeted tests.
4. Rerun impacted QA cases if code changed.
5. Commit/push again.
6. Observe pipeline again.

### D5. Test-submission Document

After CI passes, create a test-submission document. Use project-native location if defined. Otherwise create:

```text
.delivery/test-submission.md
```

Template:

```markdown
# 提测文档

## 一、需求背景
- 需求链接：
- 需求目标：

## 二、变更范围
- 仓库/服务：
- 接口：
- 数据表：
- 配置项：
- 定时任务/消息：

## 三、实现说明
- 核心改动：
- 兼容性说明：
- 风险点：

## 四、测试范围
- 单测：
- 集成测试：
- 接口验收：
- 回归测试：

## 五、QA Gate 结果
- 结论：
- 测试用例数量：
- 通过：
- 失败：
- 阻塞：
- 证据链接：

## 六、影响面
- 用户角色：
- 业务场景：
- 上下游依赖：
- 是否需要灰度：

## 七、部署说明
- 分支：
- Commit：
- CI 链接：
- 配置变更：
- 数据变更：
- 回滚方案：

## 八、待关注事项
- 已知限制：
- 需要人工验证：
- 上线后监控点：
```

## Phase E — Final Delivery Summary

Final response to Allen should include:

```text
- Requirement summary
- Changed repos/files
- Tests run and results
- QA Gate decision
- Commit hash(es)
- Branch(es)
- CI/pipeline status and links
- Test-submission document path/link
- Remaining risks or manual checks
```

## Phase F — 真实验收、发布观察与结项学习

### F1. Real-evidence Acceptance

Unit tests and CI are necessary but not sufficient. Map every acceptance criterion to readable evidence:

- positive case
- negative/boundary case
- regression case
- API/integration response when available
- logs/metrics/config state when relevant

Write evidence to the requirement workspace (for example `.requirement/verification.md` or the project-native equivalent). If an independent environment exists, deploy the feature branch there first. Shared pre-production or production deployment requires a human gate.

### F2. Release Observation

When release is in scope, prepare risk, rollback, configuration and monitoring checklists. After the human-confirmed release, re-read logs/metrics/business behavior during the observation window. A successful deployment is not yet a completed requirement if post-release evidence is missing.

### F3. Closeout Distillation

Generate a closeout record that separates:

| Category | Destination | Rule |
|---|---|---|
| Stable business/system knowledge | long-term wiki/codemap candidate | promote only after review |
| Repeated agent/process failure | skill/prompt/tooling improvement candidate | require evidence and verification |
| One-off implementation/debug material | requirement archive/raw log | never pollute long-term memory |

Human feedback from requirement clarification, plan review, code review and acceptance must remain traceable in the native ticket/PR/review system whenever possible. After closeout, improve the relevant skill when the workflow exposed a repeatable gap.

### F4. Delivery Metrics

Track enough metadata to evaluate whether the Agent is improving rather than merely changing:

- human intervention count and review rounds
- requirement/plan rework rate
- first-pass acceptance rate
- CI/release failures and rollbacks
- cross-platform synchronization loss/blockers

## Quick Invocation Prompt

```text
按 Allen 的开发需求交付工作流执行：规则串行、开发并行、验收串行、交付流水线。

要求：
1. 先冻结需求和验收标准，不要直接写代码。
2. 生成 Diff Plan 和测试策略。
3. 可并行时按服务/仓库派 Developer Agent 实现。
4. Developer Agent 完成后，主 Agent 串行汇总 diff。
5. 使用独立 Acceptance QA Agent 做 QA Gate，基于需求而不是实现验收。
6. QA Gate 不通过则修复并重跑受影响用例。
7. QA Gate 通过后再 commit、push、观察 CI。
8. CI 失败则修复、重新验证、重新 push。
9. CI 通过后创建提测文档。
10. 最终输出交付摘要。
```

## Verification Checklist

Before declaring completion:

- [ ] Requirement baseline exists or is summarized.
- [ ] Acceptance criteria are explicit.
- [ ] Diff Plan is clear.
- [ ] Implementation is complete by repo/service.
- [ ] Code review has no blocking findings.
- [ ] Acceptance QA Gate is Pass or accepted Conditional Pass.
- [ ] Relevant tests have execution evidence.
- [ ] Commit is created.
- [ ] Branch is pushed.
- [ ] CI/pipeline status is checked and passed or documented.
- [ ] Test-submission document exists.
- [ ] Final delivery summary is provided.
