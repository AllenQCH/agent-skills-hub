---
name: bug-killer
description: Bug analysis and repair workflow for the HeyTea internal stack. Use when Codex needs to investigate an HHT bug, trace logs, inspect release sheets, clone a HeyTea repo, implement a minimal fix, verify the result, or follow the bug-killer analyst/fixer/verifier workflow from the local package at /Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer.
---

# Bug Killer

Use this skill as the Codex-native entry point for the local bug-killer package.

## Source Of Truth

The original materials live at:

`/Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer`

Do not rewrite that package by default. Reuse it as the source of truth unless the user asks to migrate or edit it.

## What This Skill Provides

This skill gives Codex a stable entry in `~/.codex/skills` and tells it how to use the existing local materials:

- workflow docs in `agents/*.md`
- domain skills in `skills/*/SKILL.md`
- executable helper scripts in `skills/*/scripts/*`

## Workflow

1. Read the top-level source README when the user asks about the overall bug-killer flow.
2. Pick the matching role doc from the source `agents/` folder only when needed:
   - `bug-analyst.md`
   - `bug-fixer.md`
   - `bug-verifier.md`
   - `java-code-review.md`
   - `java-security-review.md`
   - `release-publisher.md`
3. Pick the matching source skill only when the task needs it:
   - `hht-bug`
   - `trace-log`
   - `heytea-git`
   - `sso-login`
   - `apollo-config-test`
   - `bk-pipeline`
   - `dbweb-test`
4. Run the source script directly instead of rewriting it when an existing script already does the job.
5. Save any task outputs in the current worktree or task directory, not inside the shared source package, unless the user explicitly asks to edit the package.

## Important Paths

- source package: `/Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer`
- source agents: `/Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer/agents`
- source skills: `/Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer/skills`

See `references/source-map.md` for the full path map.

## Execution Rules

- Prefer reading the smallest relevant file instead of loading the whole package.
- Treat the source scripts as the canonical implementation.
- If a required dependency is missing, install or configure only what is necessary for the specific skill being used.
- If the user wants Codex-native restructuring, create or update files under `/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bug-killer` and keep the original package untouched unless instructed otherwise.

## Common Commands

Examples below use the source package directly.

### HHT bug query

```bash
python3 /Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer/skills/hht-bug/scripts/fetch_bugs.py --list-projects
```

### Trace log search

```bash
node /Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer/skills/trace-log/scripts/search.js '{"query":"trace:\"<trace_id>\"","env":"intl-test","timeRange":"3d","analyze":true}'
```

### Clone repo helper

```bash
python3 /Users/heytea/Documents/myHeytea/code/tool_file/agent/bug-killer/skills/heytea-git/scripts/clone_repo.py --help
```

## When The User Asks To "Run bug-killer"

Clarify the concrete entry task if it is not explicit, then execute the smallest matching flow:

- "查 bug" -> use `hht-bug`
- "查 trace" -> use `trace-log`
- "拉代码" -> use `heytea-git`
- "分析根因" -> read `bug-analyst.md` and the needed source skills
- "修复并验证" -> follow `bug-fixer.md` then `bug-verifier.md`
