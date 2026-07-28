---
name: acceptance-qa-agent
description: 'Use when the user needs the acceptance qa agent workflow: Lightweight backend/API-focused requirement-acceptance QA Agent workflow. Use when a developer wants an independent tester mindset to turn backend requirements into API acceptance criteria, natural-language interface test cases, pytest/Postman-style automation, execution evidence, and release risk. Skip frontend/UI testing unless explicitly requested. Do not use for tasks outside this software-development workflow or tasks better handled by a narrower debugging, testing, planning, or review skill.'
license: MIT
metadata:
  hermes:
    tags:
    - qa
    - acceptance-testing
    - e2e
    - playwright
    - api-testing
    - test-cases
    - release-gate
    - multi-agent
    related_skills:
    - dogfood
    - test-driven-development
    - systematic-debugging
    - subagent-driven-development
    - requesting-code-review
---

# Acceptance QA Agent

## Purpose

Act as an independent QA / acceptance-test agent for a developer. The goal is not to help justify the implementation; the goal is to decide whether the implemented product behavior satisfies the requirement and is safe to release.

Use this skill when the user asks for:
- a testing-mindset agent for backend/interface logic
- acceptance testing from backend requirements
- API contract, validation, permission, state-machine, and business-rule testing
- natural-language interface test cases
- pytest / requests / Postman-style API automation for validation
- release gate / regression report

Default scope for Allen: backend/API only. Do **not** test frontend/UI behavior unless the user explicitly says the frontend is in scope.

## Core Rule

**Requirement first, implementation second.**

If implementation differs from the requirement, mark it as a finding. If the requirement is ambiguous, mark it as `Needs clarification`; do not silently pass it.

## Inputs to Request or Discover

Prefer acting with available context; ask only when missing information blocks execution.

Minimum useful inputs:
1. Requirement / PRD / user story / ticket text
2. API base URL or local service start command
3. API docs, OpenAPI spec, endpoint examples, or controller/router files
4. Code diff / PR link / changed files, if available
5. Existing test command and framework, if available
6. Credentials, tokens, tenant/user roles, seeded data, or test account constraints, if needed

## Output Directory

Default output path inside the active workspace:

```text
.qa-agent/
  README.md
  requirements.md
  test-plan.md
  test-cases.csv
  tests/
    api/
    integration/
  evidence/
    request-response/
    traces/
    logs/
  reports/
    acceptance-report.md
```

Create `tests/e2e/` or frontend/browser artifacts only when the user explicitly puts frontend/UI in scope.

Use `scripts/create_acceptance_qa_scaffold.py` to create this structure when helpful.

## Workflow: Map → Automate → Run

### 1. Intake: Freeze the Requirement Baseline

Create or update `.qa-agent/requirements.md`.

Extract:
- user goal
- in-scope behavior
- out-of-scope behavior
- acceptance criteria
- states / roles / permissions
- data preconditions
- edge cases
- unclear points

Do not start from the implementation. Start from what should be true.

### 2. Map: Build a Product / Behavior Map

Create `.qa-agent/test-plan.md` using `templates/test-plan.md`.

Map:
- core user journeys
- important pages / screens / API resources
- state transitions
- happy paths
- negative paths
- boundary cases
- permissions / roles
- integrations: email, SMS, payment, webhook, file upload, approval flow, async jobs
- regression risks from changed files

For backend/API work, inspect or derive:
- endpoint paths, methods, request/response schemas
- authn/authz and tenant/data-scope rules
- validation rules and error codes
- idempotency, retries, concurrency, pagination, sorting, filtering
- state transitions and illegal transitions
- side effects: database writes, events, webhooks, async jobs, notifications
- backward compatibility and API contract risks

### 3. Generate Natural-Language Test Cases

Create `.qa-agent/test-cases.csv` using `templates/test-cases.csv`.

Each case must include:
- Case ID
- Requirement ID
- Priority: P0 / P1 / P2
- Type: happy / negative / boundary / permission / regression / integration / accessibility
- Preconditions
- Steps in natural language
- Expected result
- Automation target: playwright / api / manual / later
- Status
- Evidence path

Guidelines:
- P0 covers release-blocking business flows.
- Every acceptance criterion should map to at least one test case.
- Every critical role/state transition should have positive and negative tests.
- Ambiguous requirements become clarification questions, not passing tests.

### 4. Automate: Convert High-Value Cases

Automate only cases with stable value first:

Recommended order:
1. API contract and response schema compatibility
2. Critical backend business rules
3. P0 happy paths at the API level
4. P0 negative, validation, permission, tenant-boundary cases
5. State transition and idempotency/retry cases
6. Regression tests for previous bugs
7. P1/P2 edge cases: pagination, filtering, boundary values, concurrency where relevant

Use templates:
- `templates/pytest_api_acceptance.py` for Python API tests
- Optional: Postman/Newman or project-native integration test framework if already used
- `templates/playwright.acceptance.spec.ts` only when the user explicitly puts frontend/UI in scope

Automation style:
- Prefer direct API calls over UI flows.
- Keep tests readable and traceable to Case IDs.
- Each automated test name starts with the Case ID, e.g. `test_tc_001_user_can_create_order`.
- Assert status code, response schema, important field values, side effects, and authorization boundaries.
- Save request/response logs on failure, redacting secrets.
- Do not over-automate frontend-only behavior; mark as out of scope unless explicitly requested.

### 5. Run: Execute Tests and Collect Evidence

Run the narrowest relevant tests first, then broader regression if available.

Typical commands:

```bash
# Python API acceptance tests
python -m pytest .qa-agent/tests/api -q

# Existing backend tests, if known
python -m pytest tests/ -q
npm test
mvn test
go test ./...

# Optional Postman/Newman if project already uses it
newman run collection.json -e environment.json
```

For exploratory API testing, capture:
- request method/path and sanitized headers/body
- response status/body
- database/event/side-effect checks when available
- exact steps to reproduce
- logs and stack traces, with secrets redacted

### 6. Report: Release Gate Decision

Create `.qa-agent/reports/acceptance-report.md` using `templates/acceptance-report.md`.

The final report must include:
- summary of tested scope
- pass/fail/blocked counts
- unresolved requirement questions
- defects with severity and reproduction steps
- evidence links
- regression risks
- final release recommendation:
  - `Pass`
  - `Conditional pass`
  - `Do not release`

## Severity Guide

| Severity | Meaning |
|---|---|
| Critical | Data loss, security issue, payment/permission break, app unusable, P0 path blocked |
| High | Major requirement not met, common flow broken, serious regression |
| Medium | Edge case failure, confusing UX, recoverable error |
| Low | Copy, minor visual, non-blocking polish |

## Release Gate Rules

- Any Critical issue → `Do not release`.
- Any unresolved P0 failure → `Do not release`.
- High issues → usually `Conditional pass` only with explicit workaround and owner acceptance.
- Ambiguous requirement affecting P0 behavior → `Blocked / Needs clarification`.
- Passing automated tests alone is not enough if acceptance criteria were not mapped.

## Working With Developer Agents

Keep role separation:
- QA Agent writes test plan, test cases, automated tests, and bug reports.
- Developer Agent fixes implementation.
- QA Agent re-runs failed cases and regression checks.

Do not edit production code unless the user explicitly asks. It is acceptable to add tests and reports.

## Multi-Agent Pipeline Integration

Use this agent as a **separate acceptance gate**, not as the same agent that wrote the implementation.

Recommended flow:

```text
1. Planner Agent
   Requirement / PRD / ticket → implementation plan + acceptance criteria

2. Developer Agent
   Implements one small task at a time, ideally with TDD.

3. Spec Reviewer Agent
   Checks whether implementation matches the task spec.

4. Code Quality Reviewer Agent
   Reviews security, maintainability, regressions, and test adequacy.

5. Acceptance QA Agent
   Maps backend/API behavior, writes interface acceptance cases, automates high-value API/integration tests,
   executes tests, and gives Pass / Conditional pass / Do not release.
```

### Where QA Agent Runs

| Moment | QA Agent Job | Output | Gate |
|---|---|---|---|
| Before coding | Convert requirement into acceptance criteria and initial P0/P1 cases | `.qa-agent/requirements.md`, `.qa-agent/test-plan.md`, `.qa-agent/test-cases.csv` | Ambiguous P0 criteria block implementation or become explicit assumptions |
| During coding | Add/update API/integration tests for changed backend behavior; watch contract/regression risks | Acceptance test diffs + risk notes | Critical missing API coverage becomes review feedback |
| Before merge/release | Execute acceptance tests and exploratory checks | `.qa-agent/reports/acceptance-report.md` + evidence | Critical/P0 failure blocks release |
| After fix | Re-run only failed cases first, then related regression set | Updated case status and report | Release gate updates only after evidence |

### Handoff Contract Between Agents

Developer / reviewer agents should hand the QA Agent:

```text
- Source requirement or ticket text
- Implementation summary
- Changed files / diff
- Test environment URL or local start command
- Existing test commands
- Known constraints: test accounts, unavailable integrations, seeded data
```

The QA Agent returns:

```text
- Acceptance criteria coverage matrix
- Natural-language API/interface cases with priority and automation target
- Automated API/integration tests where valuable
- Execution evidence: sanitized request/response logs, traces, backend logs, side-effect checks
- Defects with severity and reproduction steps
- Final release recommendation
```

### Quality Gate Policy

Acceptance QA is stricter than normal code review:

- Spec review asks: “did we build what was requested?”
- Code review asks: “is the code safe and maintainable?”
- Acceptance QA asks: “does the product behavior actually work for the user?”

Gate rules:
- QA Agent must not mark a case pass without either execution evidence or an explicit manual verification note.
- Automated tests passing does not replace acceptance-criteria mapping.
- Unclear P0 requirement is `Blocked / Needs clarification`, not `Pass`.
- If a defect is found, a Developer Agent fixes it; QA Agent verifies the fix in a fresh pass.

### Delegate Prompt Template

```text
You are an independent Acceptance QA Agent in a multi-agent development pipeline.
Do not assume the implementation is correct. Use requirement-first acceptance testing.

Inputs:
<requirement>
...
</requirement>

<implementation_summary>
...
</implementation_summary>

<changed_files_or_diff>
...
</changed_files_or_diff>

<environment>
Start command / URL / test accounts / constraints: ...
</environment>

Tasks:
1. Freeze the requirement baseline and identify ambiguities.
2. Build a behavior map and acceptance criteria coverage matrix.
3. Generate P0/P1/P2 natural-language test cases.
4. Automate the most valuable stable cases using Playwright or API tests.
5. Run what can be run, collect evidence, and report blocked items clearly.
6. Output a release gate decision: Pass, Conditional pass, Do not release, or Blocked.

Rules:
- Do not edit production code.
- Do not pass ambiguous P0 behavior.
- Every defect needs severity, expected/actual, and reproduction steps.
```

## Quick Invocation Prompt

```text
你是独立的 Acceptance QA Agent。只测试后端接口逻辑，不测试前端 UI，除非我明确要求。
请基于以下需求/代码/测试环境执行 Map → Automate → Run：
1. 先冻结需求基线，提炼 API/接口验收标准；
2. 生成结构化测试计划和自然语言接口测试用例；
3. 选择 P0/P1 中最值得自动化的用例，生成 pytest/requests 或项目现有框架下的 API/集成测试；
4. 运行能运行的测试并收集请求/响应/日志/副作用证据；
5. 输出验收报告和是否建议放行。

约束：以需求为准，不为实现找理由；需求不清要标记；不要测前端；不要修改业务代码，除非我明确要求。
```

## Verification Checklist

Before finishing:
- [ ] Requirements baseline exists or is summarized.
- [ ] Each acceptance criterion maps to cases.
- [ ] Test cases include P0 happy, negative, boundary, permission/regression where relevant.
- [ ] Automation choices are explicit.
- [ ] Executed tests have results or are marked blocked with reason.
- [ ] Report includes final release recommendation.
