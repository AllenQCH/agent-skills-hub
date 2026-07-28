#!/usr/bin/env python3
"""Create a lightweight Acceptance QA Agent scaffold in a project workspace.

Usage:
    python create_acceptance_qa_scaffold.py [output_dir]

Default output_dir: .qa-agent
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


TEST_PLAN = """# Acceptance QA Test Plan

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
"""

REPORT = """# Acceptance QA Report

## 1. Executive Summary

- Requirement / feature:
- Test environment:
- Execution date:
- Tester / agent:
- Final recommendation: **Pass / Conditional pass / Do not release / Blocked**

## 2. Result Overview

| Metric | Count |
|---|---:|
| Total cases | 0 |
| Passed | 0 |
| Failed | 0 |
| Blocked | 0 |
| Not run | 0 |

## 3. Scope Tested

- 

## 4. Scope Not Tested / Limitations

- 

## 5. Findings

| ID | Severity | Category | Title | Status | Owner |
|---|---|---|---|---|---|
| BUG-001 | High | Functional |  | Open |  |

### BUG-001 — Title

- Severity:
- Category:
- Related case:
- URL / endpoint:
- Steps to reproduce:
  1. 
- Expected:
- Actual:
- Evidence:
- Console / API errors:
- Suggested fix direction:

## 6. Requirement Clarifications

| ID | Question | Impact | Recommendation |
|---|---|---|---|
| Q-001 |  |  |  |

## 7. Automation Added

| File | Case IDs | Command | Result |
|---|---|---|---|
| .qa-agent/tests/e2e/acceptance.spec.ts |  | npx playwright test .qa-agent/tests/e2e | Not run |
| .qa-agent/tests/api/test_acceptance.py |  | python -m pytest .qa-agent/tests/api -q | Not run |

## 8. Release Gate Decision

### Recommendation

**Pass / Conditional pass / Do not release / Blocked**

### Reasoning

- 

### Required Before Release

- 

### Suggested Follow-ups

- 
"""

PLAYWRIGHT = """import { test, expect } from '@playwright/test';

const BASE_URL = process.env.ACCEPTANCE_BASE_URL || 'http://localhost:3000';

test.describe('Acceptance QA', () => {
  test('TC-001 core happy path works', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.locator('body')).toBeVisible();
  });
});
"""

PYTEST_API = '''"""Acceptance QA API tests."""

import os
import requests

BASE_URL = os.environ.get("ACCEPTANCE_API_BASE_URL", "http://localhost:8000")


def test_tc_003_api_smoke():
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    assert response.status_code in {200, 204}
'''


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".qa-agent")
    for subdir in [
        "tests/e2e",
        "tests/api",
        "evidence/screenshots",
        "evidence/traces",
        "evidence/logs",
        "reports",
    ]:
        (root / subdir).mkdir(parents=True, exist_ok=True)

    write_if_missing(root / "README.md", "# Acceptance QA Agent\n\nMap → Automate → Run workspace.\n")
    write_if_missing(root / "requirements.md", "# Requirement Baseline\n\nPaste or summarize the source requirement here.\n")
    write_if_missing(root / "test-plan.md", TEST_PLAN)
    write_if_missing(root / "reports" / "acceptance-report.md", REPORT)
    write_if_missing(root / "tests" / "e2e" / "acceptance.spec.ts", PLAYWRIGHT)
    write_if_missing(root / "tests" / "api" / "test_acceptance.py", PYTEST_API)

    cases_path = root / "test-cases.csv"
    if not cases_path.exists():
        with cases_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Case ID",
                "Requirement ID",
                "Priority",
                "Type",
                "Title",
                "Preconditions",
                "Steps",
                "Expected Result",
                "Automation Target",
                "Status",
                "Evidence Path",
                "Notes",
            ])
            writer.writerow([
                "TC-001",
                "AC-001",
                "P0",
                "happy",
                "Core happy path works",
                "Given ...",
                "1. Open ...\n2. Do ...\n3. Submit ...",
                "Then ...",
                "playwright",
                "todo",
                "",
                "",
            ])
            writer.writerow([
                "TC-002",
                "AC-001",
                "P0",
                "negative",
                "Invalid input is rejected",
                "Given ...",
                "1. Open ...\n2. Enter invalid ...\n3. Submit",
                "Validation error is shown and data is not saved",
                "playwright",
                "todo",
                "",
                "",
            ])
            writer.writerow([
                "TC-003",
                "AC-002",
                "P0",
                "permission",
                "Unauthorized role cannot perform action",
                "Given user role ...",
                "1. Login as ...\n2. Open ...\n3. Attempt ...",
                "Action is blocked with safe message; no data mutation",
                "api",
                "todo",
                "",
                "",
            ])

    print(f"Acceptance QA scaffold created at {root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
