---
name: hermes-dingtalk-mcp-setup
description: 'Use when the user needs the hermes dingtalk mcp setup workflow: Configure DingTalk MCP for Hermes Agent using dws and @sputnicyoji/dingtalk-workspace-mcp, including prerequisites, config, auth, and verification. Do not use for non-Hermes agent work or unrelated application/product tasks.'
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - MCP
    - DingTalk
    - Hermes
    - dws
---

# Hermes DingTalk MCP Setup

Use this when the user wants Hermes Agent to access DingTalk via MCP, especially to send messages, manage chat/calendar/todo, or when `dws` exists but no DingTalk MCP is configured.

## Why this skill exists

In practice, DingTalk MCP setup for Hermes has a few non-obvious requirements:
- Hermes native MCP only loads servers present in `~/.hermes/config.yaml`
- Hermes must be restarted after adding `mcp_servers`
- The Hermes Python runtime needs the `mcp` package installed
- On this macOS setup, Hermes runs under a uv-managed Python 3.11, so plain `pip install mcp` may fail with `externally-managed-environment`
- `dws auth login` can still block actual message sending even after MCP is configured
- The `@sputnicyoji/dingtalk-workspace-mcp` package expects `dws >= 1.0.7`; older versions should be upgraded first

## Prerequisites

Verify these first:

```bash
hermes --version
python3.11 -c 'import importlib.util; print(importlib.util.find_spec("mcp") is not None)'
dws version
dws auth status --format json
npx --version
```

Expected:
- `hermes` available
- Python check prints `True` once MCP SDK is installed
- `dws` should be `>= v1.0.7`
- `npx` available

## Step 1: Upgrade/install dws if needed

If `dws version` is older than `v1.0.7`, upgrade it:

```bash
curl -fsSL https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.sh | sh
which dws && dws version
```

Observed working result on macOS:
- installer placed binary at `~/.local/bin/dws`
- upgraded from `v1.0.6` to `v1.0.10`

## Step 2: Add DingTalk MCP server to Hermes config

Edit `~/.hermes/config.yaml` and add:

```yaml
mcp_servers:
  dingtalk:
    command: "npx"
    args: ["-y", "@sputnicyoji/dingtalk-workspace-mcp"]
    timeout: 180
```

Safe insertion point: near other top-level config keys, e.g. before `_config_version`.

## Step 3: Verify the MCP package itself can launch

Before restarting Hermes, check the package resolves:

```bash
npx -y @sputnicyoji/dingtalk-workspace-mcp --version
```

Expected output seen in testing:

```bash
0.0.4
```

## Step 4: Install the Python MCP SDK for Hermes

Hermes native MCP discovery requires the Python `mcp` package.

### Important macOS/uv-managed Python note

On this setup, `python3.11 -m pip install --user mcp` failed with:
- `externally-managed-environment`

Working approach:

```bash
python3.11 -m pip install --user --break-system-packages mcp
```

If the install is slow, run it in the background and wait/poll.

## Step 5: Authenticate dws

Even with MCP configured, DingTalk actions will fail until `dws` is authenticated:

```bash
dws auth status --format json
dws auth login
```

If status returns:

```json
{"success": true, "authenticated": false, ...}
```

then the user still needs to finish the browser/device authorization flow.

## Step 6: Restart Hermes Agent

Hermes does not hot-reload MCP server config. Restart is required after:
- editing `~/.hermes/config.yaml`
- installing the Python `mcp` package

After restart, Hermes should discover tools from the configured DingTalk MCP server.

## Verification checklist

Run/check these in order:

```bash
dws version
dws auth status --format json
npx -y @sputnicyoji/dingtalk-workspace-mcp --version
python3.11 -c 'import importlib.util; print(importlib.util.find_spec("mcp") is not None)'
```

Then restart Hermes and verify MCP-backed DingTalk tools appear / are callable.

## Failure modes and fixes

### 1. `dws` not authenticated
Symptoms:
- `dws auth status --format json` shows `authenticated: false`
- DingTalk messaging/contact/chat operations fail

Fix:
```bash
dws auth login
```

### 2. MCP package missing in Hermes runtime
Symptoms:
- Hermes never loads configured MCP servers
- native MCP support appears inert

Fix:
```bash
python3.11 -m pip install --user --break-system-packages mcp
```

### 3. dws too old
Symptoms:
- package docs require newer dws
- MCP server may reject or behave incorrectly

Fix:
```bash
curl -fsSL https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.sh | sh
```

### 4. Config added but nothing changes
Cause:
- Hermes not restarted

Fix:
- restart Hermes Agent

## Recommended operator summary to the user

When setup is only partially complete, report status clearly:
- MCP config added
- package launch test passed
- current blocker is either `dws` auth, missing Python `mcp`, or pending Hermes restart
- avoid claiming DingTalk messaging works until all three are complete
