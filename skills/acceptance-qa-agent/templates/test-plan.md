# Acceptance QA Test Plan

## 1. Requirement Baseline

- Source requirement:
- Version / date:
- Owner:
- Test environment:

## 2. User Goal

> What real user/business outcome must work?

## 3. Scope

### In Scope

- 

### Out of Scope

- 

## 4. Acceptance Criteria

| Req ID | Acceptance Criterion | Notes / Ambiguity |
|---|---|---|
| AC-001 |  |  |

## 5. Behavior Map

### Core Journeys

| Journey ID | User / Role | Entry Point | Goal | Expected End State | Priority |
|---|---|---|---|---|---|
| J-001 |  |  |  |  | P0 |

### States and Transitions

| State | Trigger | Expected Transition | Invalid Transition / Error |
|---|---|---|---|
|  |  |  |  |

### Data / Preconditions

| Data Set | Purpose | Setup Method | Cleanup |
|---|---|---|---|
|  |  |  |  |

## 6. Risk Map

| Risk | Why It Matters | Mitigation / Test Focus | Priority |
|---|---|---|---|
| Permission mismatch | Users may access or modify data incorrectly | Positive + negative role tests | P0 |

## 7. Automation Strategy

| Layer | What to Cover | Tool | Notes |
|---|---|---|---|
| API | Contracts, validation, permissions, business rules | pytest / request | Fast and stable |
| E2E | Critical user journeys | Playwright | Browser-visible acceptance |
| Manual | Exploratory, visual nuance, third-party constraints | Human/Agent checklist | Evidence screenshots |

## 8. Clarification Questions

| ID | Question | Impact if Unanswered | Owner | Status |
|---|---|---|---|---|
| Q-001 |  |  |  | Open |

## 9. Exit Criteria

- [ ] All P0 cases passed or explicitly waived by owner.
- [ ] No Critical defects remain open.
- [ ] High defects have workaround and owner acceptance if conditional pass.
- [ ] Regression risk has been assessed.
- [ ] Acceptance report contains final release recommendation.
