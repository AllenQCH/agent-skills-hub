---
name: release-workflow
description: Generate test-release documents and locate or open CI/CD pipelines for development handoff. Use when the user asks for 提测文档, 提测说明, 测试交付, release notes for testing, open pipeline, 打开流水线, 查流水线, 构建流水线, 部署流水线, or wants to prepare a branch/service for test verification.
---

# Release Workflow

## Scope

Use this skill for the handoff stage after or during development:

- Generate a test-release document from requirement, branch, commits, changes, verification, risk, rollback, and test scope.
- Locate or open a CI/CD pipeline from project, service, branch, environment, or known URL mapping.

Do not create merge requests, approve releases, merge to main branches, or trigger destructive deployments unless the user explicitly asks and project rules allow it.

## Workflow

1. Identify the target project, service, branch, environment, and release intent.
   Classify changed repositories with the project stack manifest. Only repositories whose remote action is `service_deploy` belong in the test-delivery service list; Maven dependencies whose remote action is `artifact_publish` belong in dependency/build notes and must not receive a demand service-pipeline row.
2. Gather evidence from deterministic sources when available: `git status`, `git branch --show-current`, `git log`, `git diff --stat`, test/build command outputs, OpenSpec, issue text, or user-provided notes.
3. For test-release docs, use `assets/templates/test-release-doc.md` or run `scripts/render_test_doc.py`.
4. For pipelines, read `references/pipeline-map.json` first. If no mapping exists, search project docs/config for CI URLs or ask for the pipeline entry URL.
5. Preserve uncertainty. Use `待确认` rather than inventing requirement IDs, owners, environments, URLs, or verification results.
6. When writing to Obsidian, follow `obsidian-note-writing` and link back to related project or skill notes.

## Test-Release Document Requirements

A release handoff document should include:

- Requirement / ticket / background
- Target service(s)
- Dependency artifacts required by those services, kept separate from the target service list
- Branch and commit range
- Change summary
- Impact scope
- Verification performed
- Test focus
- Risk and rollback
- Configuration / data / migration notes
- Pipeline or deployment links
- Open questions

## Pipeline Rules

- Prefer an exact URL mapping from `references/pipeline-map.json`.
- If a mapping has URL template variables, substitute only known values such as `{branch}`, `{service}`, `{env}`.
- If project/service mapping is missing, do not guess. Ask for the pipeline platform or URL.
- Opening a pipeline is navigation, not deployment. Do not trigger builds or deploys unless explicitly requested.

## Resources

- `assets/templates/test-release-doc.md`: Markdown template for 提测文档.
- `references/pipeline-map.json`: editable mapping of project/service/environment to pipeline URLs.
- `scripts/render_test_doc.py`: render a test-release document from JSON input.
- `scripts/open_pipeline.py`: resolve and open a pipeline URL from the mapping.
