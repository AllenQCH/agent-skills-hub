---
name: hermes-yahoo-finance-mcp-setup
description: 'Use when the user needs the hermes yahoo finance mcp setup workflow: Configure Yahoo Finance MCP as a native Hermes tool source for US stock research, verify tool discovery, and avoid common setup pitfalls. Do not use for non-Hermes agent work or unrelated application/product tasks.'
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - MCP
    - finance
    - stocks
    - yahoo-finance
    - Hermes
    related_skills:
    - native-mcp
---

# Hermes Yahoo Finance MCP Setup

Use this when the user wants Hermes to gain built-in US stock research tools via an MCP server backed by Yahoo Finance.

## What this gives Hermes
After setup and restart, Hermes should discover tools similar to:
- `mcp_yahoo_finance_get_ticker_info`
- `mcp_yahoo_finance_get_ticker_news`
- `mcp_yahoo_finance_search`
- `mcp_yahoo_finance_get_top_entities`
- `mcp_yahoo_finance_get_price_history`
- `mcp_yahoo_finance_ticker_option_chain`
- `mcp_yahoo_finance_ticker_earning`

## When to use
- User wants a practical US-stock toolset inside Hermes
- Prefer quick integration over building a custom stock skill first
- Want price history, news, ticker lookup, options chain, and earnings tools

## Prerequisites
- Hermes repo/workdir available
- `uvx` installed and on PATH
- Node is optional for this server, but `uv`/`uvx` is required
- Hermes Python environment available (usually `source venv/bin/activate`)

## Important findings / pitfalls
1. **Hermes native MCP discovery happens at startup**
   - Adding the config is not enough
   - You must restart the Hermes process before the MCP tools appear in conversations

2. **Do not assume `pip` exists on PATH after activating venv**
   - In this environment, `pip` was missing but `python -m pip` worked
   - Prefer:
     ```bash
     source venv/bin/activate
     python -m pip install mcp
     ```
   - Avoid relying on bare `pip install mcp`

3. **Verify the server independently before blaming Hermes**
   - `uvx yahoo-finance-server --help` confirms the package resolves and installs
   - A direct MCP handshake using Python is the strongest verification

## Setup steps

### 1) Verify runtime tools
Run from the Hermes project root:
```bash
source venv/bin/activate
python -V
which python
uv --version
```
Optionally verify the server package resolves:
```bash
uvx yahoo-finance-server --help
```

### 2) Install MCP into Hermes' Python environment
```bash
source venv/bin/activate
python -m pip install mcp
```
Confirm:
```bash
source venv/bin/activate
python - <<'PY'
import importlib.util
print('mcp', bool(importlib.util.find_spec('mcp')))
PY
```
Expected output:
```text
mcp True
```

### 3) Add Yahoo Finance MCP to `~/.hermes/config.yaml`
If `mcp_servers:` already exists, add a sibling entry. Example:
```yaml
mcp_servers:
  yahoo_finance:
    command: uvx
    args:
    - yahoo-finance-server
    timeout: 120
    connect_timeout: 60
```

If other MCP servers already exist, preserve them.

### 4) Verify direct MCP connectivity before restart
Use a real MCP client handshake from Hermes' venv:
```bash
source venv/bin/activate
python - <<'PY'
import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

async def main():
    server = StdioServerParameters(command='uvx', args=['yahoo-finance-server'])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print('TOOL_COUNT', len(tools.tools))
            for t in tools.tools:
                print(t.name)

asyncio.run(main())
PY
```

A successful run should list 7 tools such as:
- `get-ticker-info`
- `get-ticker-news`
- `search`
- `get-top-entities`
- `get-price-history`
- `ticker-option-chain`
- `ticker-earning`

### 5) Restart Hermes
This is required for native MCP auto-discovery. After restart, Hermes should register the tools with the `mcp_yahoo_finance_` prefix.

## Recommended user-facing explanation
Tell the user:
- setup is complete
- the server was directly verified
- Hermes must be restarted before the tools appear
- after restart they can ask for US stock price history, news, earnings, options, and ticker lookup naturally

## Good follow-up work
After the MCP integration works, consider building a higher-level Hermes skill for:
- single-stock research workflow
- earnings preview / recap workflow
- AI / semiconductor / server-chain stock screening
- news + price-action combined analysis

## Troubleshooting
### `pip: command not found`
Use:
```bash
source venv/bin/activate
python -m pip install mcp
```

### `mcp False` after install attempt
Check that you are using Hermes' venv Python:
```bash
source venv/bin/activate
which python
python - <<'PY'
import sys
print(sys.executable)
PY
```

### Config added but tools still missing
Hermes probably was not restarted. Native MCP discovery is startup-time only.

### `uvx yahoo-finance-server` installs but tools still fail
Run the direct MCP Python handshake above. If the handshake works, the issue is likely Hermes process restart/discovery rather than the server package itself.
