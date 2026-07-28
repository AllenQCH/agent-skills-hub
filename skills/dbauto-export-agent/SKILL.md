---
name: dbauto-export-agent
description: Use when Codex needs to launch or operate the local dbauto export workflow at /Users/heytea/Documents/new_tools/dbauto_export_tool, especially when the task requires starting the Python backend, preparing dbauto login in Chrome, reusing opencli Browser Bridge, or opening the export extension UI for bulk export work.
---

# DBAuto Export Agent

## Overview

Use this skill as the single entry point for the local dbauto export tool. Prefer the bundled wrapper script so future sessions do not need to rediscover how to start the backend, check login, or open the extension UI.

## Hard Rules

- When the user asks to "导出" dbauto data, stay on the dbauto export agent path end-to-end.
- Do not fall back to `dbauto-sql-query`, ad-hoc `opencli browser eval`, custom Python pagination, manual CSV stitching, or direct cookie-based export code unless the user explicitly asks to debug or replace the agent itself.
- Do not add extra `ORDER BY`, pagination strategy changes, or alternate query wrappers "for stability" unless the existing agent workflow has already been proven broken and the user explicitly approves agent-level debugging.
- Treat the mature workflow as:
  1. `run_dbauto_export_agent.sh` prepares backend, login, and UI.
  2. The local dbauto export tool performs the export.
  3. Codex only monitors readiness, task status, output path, and logs.
- If export fails, debug the existing agent workflow first. Fix the agent or its local toolchain; do not silently switch to a different export implementation.

## Workflow

1. Confirm the target environment: `bj`, `uswest`, or `sg`.
2. Run the bundled launcher wrapper.
3. If the launcher reports `LOGIN_REQUIRED`, complete the dbauto login in Chrome and rerun or wait for the polling flow to finish.
4. Once the launcher reports `RESULT=READY`, continue the export task in the extension UI or the local export service APIs that belong to the same toolchain.
5. For execution, keep using the export tool's own backend, task APIs, logs, and output files until completion.

## Commands

Full startup:

```bash
/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-export-agent/scripts/run_dbauto_export_agent.sh --env bj
```

Readiness check only:

```bash
/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-export-agent/scripts/run_dbauto_export_agent.sh --env bj --status-only
```

Skip UI opening:

```bash
/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/dbauto-export-agent/scripts/run_dbauto_export_agent.sh --env bj --skip-ui
```

## Expected Behavior

The wrapper delegates to:

```text
/Users/heytea/Documents/new_tools/dbauto_export_tool/start-agent.sh
```

That launcher is responsible for:

- ensuring the local FastAPI backend is running
- verifying `opencli` Browser Bridge connectivity
- opening the matching dbauto environment in Chrome
- waiting for login if required
- opening the unpacked extension UI tab when installed

During export work, the expected runtime path is:

- browser / extension captures dbauto cookies
- local export backend creates a task
- exporter drains pages and writes the final file
- Codex watches `/tasks/{task_id}` and reports the output path

## Common Mistakes

| Mistake | Fix |
|---|---|
| Starting `start.sh` manually and forgetting the login/UI steps | Use the wrapper script instead |
| Assuming dbauto is logged in because Chrome is open | Run `--status-only` and check the launcher result |
| Forgetting Browser Bridge | Run `opencli doctor -v` if the launcher says opencli is not ready |
| Reimplementing cookie capture in the agent | Keep cookie capture in the existing Chrome extension |
| Replacing the export agent with custom pagination or `dbauto-sql-query` export logic | Stop and return to the local dbauto export workflow |
| Tweaking SQL semantics, such as adding `ORDER BY`, while "helping" the export | Keep the user's SQL unchanged unless the user explicitly asks for a SQL rewrite |

## Script

Primary script:

```text
scripts/run_dbauto_export_agent.sh
```
