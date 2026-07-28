# Codex Desktop Architecture Inspection

Use this reference when the user asks how Codex Desktop is packaged, where its state lives, what starts first, or how configuration/instructions/plugins are loaded.

## Goal

Produce an evidence-backed architecture report without modifying the app or exposing credentials, prompt history, cookies, or private session contents.

## 1. Locate by bundle identity, not display name

The desktop product may be renamed or branded differently while retaining a Codex bundle identifier and internal resources. Do not assume `/Applications/Codex.app` exists.

Check candidates using Spotlight metadata and inspect `Info.plist` for:

- `CFBundleIdentifier`
- `CFBundleExecutable`
- `CFBundleDisplayName`
- `CFBundleShortVersionString`
- `CFBundleVersion`
- URL schemes
- Electron ASAR integrity metadata

Also inspect live process command lines. A process can retain an executable path from an older/replaced app bundle, so distinguish the currently installed bundle from residual long-running processes.

## 2. Separate the four storage layers

Describe these independently:

1. **App Bundle** — Electron/Chromium framework, `app.asar`, native modules, bundled Codex binary, bundled plugins, updater.
2. **Chromium user data** — typically under `~/Library/Application Support/<product>`; cookies, browser partitions, cache, local storage, Crashpad.
3. **Codex Home** — `$CODEX_HOME` or default `~/.codex`; config, sessions, SQLite state, agents, skills, plugins, logs, hooks, temporary runtime data.
4. **Project layer** — project `.codex/config.toml`, `AGENTS.md`, `.agents/skills`, source tree and trust state.

Never recommend deleting an entire layer as an initial troubleshooting step. Preserve continuity-critical config, sessions, skills, and state; archive before cleanup.

## 3. Inspect Electron entry and startup chain

For an Electron build:

1. Read `Contents/Info.plist` and identify the executable.
2. Read `Contents/Resources/app.asar/package.json` and record `main`.
3. List `.vite/build/` or equivalent entry chunks.
4. Extract the ASAR to a temporary directory only.
5. Format/minify-reverse only the relevant bootstrap/main chunks in the temp directory.
6. Trace explicit imports and startup markers such as:
   - early bootstrap
   - open-file/open-url queue
   - single-instance lock
   - `app.whenReady()`
   - protocol registration
   - shell-environment hydration
   - data migrations
   - app-server connection
   - settings initialization
   - plugin reconcile
   - `ensureWindow()` / renderer load
   - pending deep-link flush
7. Cross-check source order against `ps` parent/child relationships and startup timestamps.

Do not infer exact ordering from process timestamps alone; timestamp resolution can place several dependent processes in the same second.

## 4. Identify the core backend boundary

Look for the bundled `codex` binary and the exact child-process arguments used by the desktop main process. Codex Desktop commonly uses Electron as the UI/coordinator and a bundled `codex app-server` as the agent backend over stdio or another local transport.

Verify which side owns:

- config merging
- agent runtime
- approvals and sandbox
- threads/sessions
- SQLite persistence
- skills/plugins/MCP
- dynamic tools and subagents

Use binary help output and app source evidence rather than guessing.

## 5. Inspect persistent databases safely

Use table names and schemas, not user rows, to explain data ownership. Useful safe probes include:

- SQLite `.tables`
- `.schema <table>`
- `PRAGMA quick_check` when appropriate

Avoid dumping conversation text, prompts, tokens, cookies, authentication records, or private workspace metadata into the report.

When measuring disk usage, distinguish allocated disk usage (`du`) from logical file sizes. Temporary directories may contain sparse files, locks, staging copies, or active runtime artifacts.

## 6. Explain configuration and instruction precedence separately

### Configuration

Verify against the installed CLI help and current official docs. Typical precedence, highest first:

1. CLI flags / `--config`
2. Trusted project `.codex/config.toml` layers, project root toward CWD, closest wins
3. selected profile file
4. user `$CODEX_HOME/config.toml`
5. system config
6. built-in defaults

Do not copy private provider URLs, tokens, environment values, or project paths into a distributable report unless the user explicitly requests them.

### AGENTS guidance

Explain global discovery separately from project discovery:

- Global: prefer `AGENTS.override.md`, otherwise `AGENTS.md`, first non-empty file.
- Project: walk from project root toward CWD; at each directory choose at most one applicable instruction file, with override/fallback rules.
- More specific nested guidance appears later and overrides broader guidance.
- Direct system/developer/user instructions remain higher priority.

### Skills

Describe progressive disclosure:

1. metadata for discovery
2. load `SKILL.md` when selected
3. read references/assets or run scripts only when needed

Distinguish authored skill sources from plugin caches, system compatibility directories, and marketplace staging copies.

## 7. Plugin loading model

Trace the complete path rather than listing folders only:

```text
App-bundled marketplace snapshot
  -> Codex Home staging/cache
  -> config enabled/disabled state
  -> app-server discovery
  -> desktop reconcile/cache invalidation
  -> renderer-visible plugin/skill state
```

Check whether startup waits for pending plugin reconciliation before showing the main window; if so, document it as part of the critical startup path.

## 8. Reporting format

A useful report should contain:

- one-paragraph conclusion
- installed identity/version table
- app bundle tree
- Codex Home and Chromium data trees
- verified startup sequence
- config precedence
- AGENTS/skills/plugins/MCP loading model
- disk hotspots and safe maintenance notes
- evidence sources and caveats

Write the report to the requested destination, verify UTF-8 readability and file size, and search the output for accidental secrets before delivery.
