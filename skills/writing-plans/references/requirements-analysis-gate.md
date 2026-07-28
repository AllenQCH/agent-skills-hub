# Requirements Analysis Gate for Coding Agents

Use this before implementation when a feature, bug fix, API change, refactor, workflow, or automation request is not trivially specified.

## Goal

Prevent the agent from jumping from a vague request directly to code. Produce a compact, evidence-backed requirement brief with explicit assumptions, open questions, acceptance criteria, and readiness score.

## Phase 1 — Neutral restatement

Separate the user's proposed solution from the underlying requirement.

Capture:
- Problem: pain or gap being solved
- Goal: desired outcome after the change
- Users / actors
- Trigger / entry point
- Scope and non-goals
- Constraints: technical, product, operational, security, compatibility

## Phase 2 — Completeness scan

Check only categories that materially affect correctness or implementation:

| Category | What to check |
|---|---|
| Functional behavior | States, transitions, happy path, alternative path |
| Data | Entities, fields, ownership, validation, defaults, retention |
| Permissions | Who can/cannot act, mid-flow access changes |
| API/contracts | Inputs, outputs, errors, status codes, events, schemas |
| UI/UX | Loading, empty, error, disabled, success states |
| Edge cases | Null, empty, duplicate, stale, deleted, partial, large, invalid data |
| Timing/concurrency | Retries, timeouts, races, simultaneous edits, ordering |
| Integrations | Upstream/downstream systems and failure modes |
| Migration/compatibility | Existing data/config/API behavior and rollback |
| Observability | Logs, metrics, audit trails, alerts, debugging hooks |
| Security/privacy | Abuse, sensitive data, secrets, authN/authZ, compliance |
| Performance/reliability | Latency, throughput, availability, rate limits |
| Testing | How each requirement can be verified |
| Rollout | Feature flag, gradual rollout, rollback, manual ops |

## Phase 3 — Clarification rules

Ask clarification only if the answer would materially change architecture, data model, API contract, security/permissions, user-visible behavior, test design, rollout, compatibility, or operational risk.

- Ask at most 5 questions.
- Prefer multiple choice with a recommended option.
- If a reasonable default exists, proceed with an explicit `[ASSUMPTION]` instead of blocking.

Question format:

```md
## Question N: <topic>

**Why this matters:** <implementation or validation impact>

**Recommended:** Option <X> — <short reason>

| Option | Meaning | Impact |
|---|---|---|
| A | ... | ... |
| B | ... | ... |
| C | ... | ... |

You can reply with the option letter, accept the recommendation, or provide a short custom answer.
```

## Phase 4 — Readiness scoring

| Dimension | Weight | Score | What to check |
|---|---:|---:|---|
| Completeness | 20% | 0-10 | Core behavior, scope, actors, data, constraints |
| Clarity | 15% | 0-10 | No ambiguity likely to cause wrong implementation |
| Testability | 15% | 0-10 | Verifiable acceptance criteria |
| Feasibility | 10% | 0-10 | Achievable within visible constraints |
| Edge cases | 10% | 0-10 | Important null/boundary/error/concurrency cases |
| Integration impact | 10% | 0-10 | Modules, APIs, repos, dependencies understood |
| Security/privacy/compliance | 10% | 0-10 | Auth, data protection, abuse, audit concerns |
| Rollout/operations | 10% | 0-10 | Migration, compatibility, rollback, observability |

Decision rule:
- `>= 8`: ready to plan and implement.
- `6–7.9`: proceed only with explicit assumptions and risk notes.
- `< 6`: do not implement yet; return blocking questions and missing information.

## Output: Requirement Brief

```md
## Requirement Brief

### 1. Requirement Summary
- What:
- Who:
- Why:
- Where:

### 2. In Scope
- ...

### 3. Out of Scope
- ...

### 4. Assumptions
- [ASSUMPTION-1] ...

### 5. Open Questions
- [Q1] ...

### 6. Functional Requirements
- FR-001: The system must ...
  - Acceptance: Given ..., when ..., then ...

### 7. Non-Functional Requirements
- NFR-001: ...

### 8. Edge Cases
| Case | Expected behavior | Covered by |
|---|---|---|

### 9. Integration / Code Impact
| Area / file / API | Expected change | Risk |
|---|---|---|

### 10. Test Plan
| Requirement | Test type | Verification command or method |
|---|---|---|

### 11. Readiness Score
- Score:
- Verdict:
- Blocking issues:
```

## Hard rules

- Do not invent missing business rules.
- Do not silently expand scope.
- Do not bury assumptions.
- Do not treat vague adjectives like “fast”, “simple”, “robust”, “secure”, or “user-friendly” as requirements unless quantified or clarified.
- Do not start coding if permissions, data ownership, API contract, or migration behavior is materially ambiguous.
- If implementation proceeds under assumptions, label them clearly and make the smallest reversible change.
