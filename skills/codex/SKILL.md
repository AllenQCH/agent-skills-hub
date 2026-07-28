---
name: codex
description: 'Use when the user needs the codex workflow: Delegate coding tasks to OpenAI Codex CLI agent. Use for building features, refactoring, PR reviews, and batch issue fixing. Requires the codex CLI and a git repository. Do not use for ordinary direct execution that does not need an autonomous agent, CLI delegate, migration, or Hermes runtime workflow.'
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - Coding-Agent
    - Codex
    - OpenAI
    - Code-Review
    - Refactoring
    related_skills:
    - claude-code
    - hermes-agent
---

# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- OpenAI API key configured
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

## One-Shot Tasks

```
terminal(command="codex exec 'Add dark mode toggle to settings'", workdir="~/project", pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send input if Codex asks a question
process(action="submit", session_id="<id>", data="yes")

# Kill if needed
process(action="kill", session_id="<id>")
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `exec` for one-shots** — `codex exec "prompt"` runs and exits cleanly
4. **`--full-auto` for building** — auto-approves changes within the sandbox
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once for batch work

## Global AGENTS.md guidance for Allen

Reference: `references/agents-md-guidance.md` captures the current Codex AGENTS.md discovery model, public `agents.md` convention, openai/codex repository patterns, and recommended layering for Allen's local setup.

When Allen wants Codex to be less sycophantic and more evidence-driven, use `templates/anti-sycophancy-AGENTS.md` as the starter content for `~/.codex/AGENTS.md`, but keep the global file short and stable. It should contain durable working agreements only:
- action/confirmation boundaries such as Green/Yellow/Red;
- evidence-first engineering and real verification commands;
- smallest safe change / no unnecessary dependencies;
- rational collaboration and anti-sycophancy rules;
- Allen's Chinese, conclusion-first, table-friendly response format.

Do **not** keep every project/company workflow in global `~/.codex/AGENTS.md`. Prefer layering:
- `~/.codex/AGENTS.md` = stable personal working agreement;
- `~/.codex/AGENTS.override.md` = temporary strong override;
- `~/.codex/agents/docs/` = multi-agent registry, tool matrix, workflow docs;
- project-level `AGENTS.md` = concrete build/test/security/branch/PR rules.

Keep this as a Codex/AGENTS template, not a Hermes `pre_llm_call` plugin, to avoid per-turn prompt pollution.

## Hermes → Codex runtime integration

When the goal is **Hermes using the user's Codex CLI/runtime** (rather than running Codex as a one-off terminal agent), prefer Hermes' built-in Codex app-server runtime:

```bash
# Prereqs: Hermes provider is openai-codex/openai and codex >= 0.125 is installed
codex --version
codex app-server --help

# In Hermes CLI/gateway slash command:
/codex-runtime on          # persists model.openai_runtime=codex_app_server
/codex-runtime auto        # switch back to Hermes' default runtime
```

Equivalent config:

```yaml
model:
  provider: openai-codex
  api_mode: codex_responses
  openai_runtime: codex_app_server
```

What this does: new OpenAI/Codex Hermes sessions hand each turn to `codex app-server` over stdio, so terminal/file/patch/sandboxing run inside Codex. Hermes migrates configured MCP servers and registers a Hermes-tools MCP callback into `~/.codex/config.toml` so Codex can still access selected Hermes tools (web/browser/vision/image/skills/kanban; not full in-loop tools such as delegate_task/memory/session_search/todo).

Important distinction: `hermes acp` is Hermes acting as an ACP server for editors (Zed/VS Code/JetBrains). It is not the path for Hermes to call Codex. Hermes' generic ACP subprocess client currently targets GitHub Copilot CLI via `copilot --acp --stdio`; OpenAI Codex CLI exposes `codex app-server --stdio`, not `--acp --stdio`.

After enabling `codex_app_server`, start a new Hermes session (`/reset` in gateway, new CLI process, or gateway restart if needed); existing cached agents keep the old runtime to preserve prompt cache.

## A2A option for Hermes ↔ Codex peer messaging

When Allen specifically asks whether **A2A / Agent2Agent** can make Hermes and Codex talk to each other, answer yes but classify it as a higher-level peer-agent protocol, not a replacement for MCP. Use current GitHub evidence before recommending implementation:

- Official protocol: `a2aproject/A2A` — Agent Card discovery at `/.well-known/agent-card.json`, HTTP(S), JSON-RPC/REST/gRPC bindings, `message:send`, `message:stream`, tasks, artifacts, SSE/push. A2A is for agent-to-agent collaboration; MCP is for agent-to-tool calls.
- Codex wrapper examples: `MyPrototypeWhat/codex-a2a` exposes Codex through `@openai/codex-sdk` as an A2A server (JSON-RPC + REST endpoints, streaming Codex events, thread cache). `ricelines/codex-a2a` fronts `codex app-server` and maps A2A `contextId`/`taskId` to Codex thread/turn state.
- Hermes wrapper examples: `asimons81/hermes-a2a-bridge` is a local-first Hermes A2A bridge/plugin using `hermes chat -q {prompt}` by default, with `hermes a2a init/card/serve/send/stream/doctor`; it exposes `/.well-known/agent-card.json`, `/message:send`, `/message:stream`, `/tasks`, and bearer auth. It explicitly says it is a thin HTTP+JSON subset, not full A2A compliance. Check whether the local Hermes install actually has `hermes a2a --help` before assuming the plugin is installed.
- Topology recommendation: for long-running stateful peer collaboration, run both sides as A2A servers behind local-only ports/tunnel/HMAC/bearer tokens, and let each side use MCP internally for tools. For immediate low-risk implementation in stock Hermes/Codex, MCP bridge remains faster because both runtimes already ship MCP surfaces.

## Hermes ↔ Codex peer messaging via MCP

When Allen asks how Hermes and Codex can send messages to each other, distinguish three integration modes:

1. **Hermes calls Codex as an MCP tool**: add Codex CLI's MCP server to Hermes with `hermes mcp add codex --preset codex` (equivalent to command `codex`, args `["mcp-server"]`). After a new Hermes session/reset, Hermes gets MCP tools equivalent to Codex's `codex` and `codex-reply`: start a Codex thread with a `prompt` plus optional `cwd`, `model`, `sandbox`, `approval-policy`; continue with `threadId` + `prompt`.
2. **Codex calls Hermes messaging bridge**: add Hermes as an MCP server in Codex with `codex mcp add hermes -- hermes mcp serve` (or TOML `[mcp_servers.hermes] command="hermes" args=["mcp","serve"]`). Codex can then use Hermes bridge tools such as `conversations_list`, `messages_read`, `events_wait`, `messages_send`, `channels_list`, and approval tools to read/send platform conversation messages.
3. **Hermes hands its whole turn to Codex runtime**: `/codex-runtime on` uses `codex app-server` internally. This is not peer chat; Codex owns the loop and Hermes projects Codex events back into Hermes history. Use when the goal is Hermes running on Codex's shell/patch/sandbox runtime, not when you need two independent agents to converse.

Security/defaults: prefer `workspace-write` + `on-request`, keep thread/session IDs in messages, avoid recursive Hermes→Codex→Hermes loops, and verify `codex --version`, `codex mcp-server --help`, `codex app-server --help`, `hermes mcp --help` before changing config. Codex app-server protocol is JSON-RPC over JSONL stdio: `initialize` → `initialized` → `thread/start` → `turn/start` → stream `item/*`/`turn/completed`; use Hermes' wrapper unless building a custom bridge.

## Windows desktop app and offline installer

When the user asks for the **Codex Windows desktop app**, do not substitute a Codex CLI release asset. Resolve the requested artifact before downloading:

- **Codex CLI**: GitHub release binaries such as `codex-x86_64-pc-windows-msvc.exe.zip`.
- **Online desktop installer/bootstrapper**: a small EXE that downloads the application during installation; only use when the user explicitly accepts an online installer.
- **Complete offline desktop package**: the signed Microsoft Store package, normally named `OpenAI.Codex_<version>_x64__<publisher>.msix`; use this when the user wants to copy it to another Windows machine and install directly.

For the offline package, use Microsoft Store product ID `9PLM9XGG6VKS`, select the correct architecture (normally `x64` unless the user says ARM64), require the final payload URL to be on a Microsoft delivery domain such as `*.delivery.mp.microsoft.com`, verify the Store-provided hash, and compute a local SHA-256. Do not claim a local `MEDIA:/...` reference was uploaded to Feishu; verify the actual destination message/file record.

Before downloading a several-hundred-MB package, check the destination channel's file-size path. If a normal message upload is too small, prefer a supported large-file/Drive or authenticated desktop-client path. Do not silently replace the requested offline package with a smaller bootstrapper. See `references/windows-desktop-offline-package.md` for the verified Store-resolution and delivery workflow.

## Codex Desktop architecture and loading-order inspection

When the user asks about Codex Desktop folder structure, startup order, config precedence, or how AGENTS/skills/plugins/MCP are loaded, perform a read-only, evidence-backed inspection rather than relying on remembered paths.

Key rules:

1. Locate the installed app by bundle identity and live process metadata; branding may change and the bundle may not be named `Codex.app`.
2. Separate the App Bundle, Chromium user-data directory, `$CODEX_HOME`, and project-level configuration/instructions.
3. Trace the Electron entry from `Info.plist` → `app.asar/package.json` → early bootstrap → main startup, then cross-check against child processes.
4. Identify the exact bundled `codex app-server` command and treat it as the likely backend boundary only after source/process verification.
5. Inspect SQLite schemas and directory sizes without dumping private rows, cookies, prompt history, authentication data, or provider secrets.
6. Explain config precedence, AGENTS discovery, skill progressive disclosure, and plugin reconciliation as separate loading systems.
7. Extract/format ASAR code only in a temporary directory, write the requested report to the destination, and scan the final artifact for accidental secrets.
8. Never recommend deleting `~/.codex` or the whole Chromium profile as the first fix; preserve sessions, skills, config, and continuity-critical state.

Detailed procedure: `references/desktop-app-architecture-inspection.md`.

## Global AGENTS.md behavior template

When Allen asks to make Codex less sycophantic or more rational, use `templates/anti-sycophancy-AGENTS.md` as the starter content for `~/.codex/AGENTS.md` or a project-level `AGENTS.md`.

Key rules in that template:
- Treat user confidence and preferred framing as context, not evidence.
- Push back on wrong, risky, or unverified premises without manufacturing disagreement.
- Base coding conclusions on repo evidence: files, diffs, tests, logs, docs, and conventions.
- Report actual verification commands and results; never claim success without evidence.
- Preserve Allen's preferred Chinese, conclusion-first, table-friendly response format, while avoiding unnecessary headings for tiny answers.

Use the optional strong-pushback block only for review/planning/architecture/debugging contexts; do not enable it globally if the user wants normal execution efficiency.

## Skill catalog / context-budget management

When Allen asks about Codex skills becoming too many, or company skills bloating context through `name + description` listings, use `references/skill-catalog-budget-management.md` before recommending changes. Key pattern: keep a tiny always-loaded skill router / capability index, select top-K skills by workspace/profile/usage, and load full `SKILL.md` only after a match. Do not solve large catalogs only by raising context limits.

## Troubleshooting

- If `codex` fails immediately with an error like `Missing optional dependency @openai/codex-darwin-x64`, the npm install is incomplete or the packaged runtime for the current platform was not installed. Reinstall Codex with `npm install -g @openai/codex@latest` (or install the matching release binary / Homebrew cask) before debugging higher-level features. If npm hits `ENOTEMPTY` while renaming `@openai/codex`, remove the broken package/temp dirs under the same npm prefix (for Hermes-managed Node: `~/.hermes/node/lib/node_modules/@openai/codex`, `~/.hermes/node/lib/node_modules/@openai/.codex-*`, `~/.hermes/node/bin/codex`, `~/.hermes/node/bin/.codex-*`) and reinstall.
- When checking availability of newer CLI-only features such as `/goal`, verify both the installed version and whether the local install is runnable first; a broken runtime can look like a missing feature.
