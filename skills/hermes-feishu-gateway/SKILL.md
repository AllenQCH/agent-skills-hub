---
name: hermes-feishu-gateway
description: 'Use when the user needs the hermes feishu gateway workflow: Configure Hermes Agent Feishu/Lark gateway on macOS using an existing lark-cli app setup, including recovering the app secret from lark-cli''s encrypted local storage when it is not visible in config output. Do not use for non-Hermes agent work or unrelated application/product tasks.'
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - hermes
    - feishu
    - lark
    - gateway
    - macos
    - lark-cli
    related_skills:
    - hermes-agent
    - lark-shared
---

# Hermes Feishu Gateway via existing lark-cli setup

Use this when the user wants Hermes connected to Feishu/Lark in the same practical style they previously used in OpenClaw, especially on macOS where `lark-cli` is already configured but Hermes is not.

## When to use

Trigger this skill when all or most are true:
- Hermes needs Feishu/Lark chat access
- `lark-cli` is already configured on the machine
- The user wants an OpenClaw-like setup (WebSocket transport, DM open, group allowlist, mention-gated behavior)
- `lark-cli config show` masks or hides the app secret

## Target behavior

Match the old practical behavior as closely as Hermes supports:
- WebSocket transport
- Direct messages usable
- Group chats restricted by allowlist
- Group messages require explicit @mention

Notes:
- In Hermes Feishu adapter, group @mention gating is built in.
- DM openness is effectively the adapter's normal behavior; there is no separate `dmPolicy` knob matching old OpenClaw config.

## Root-cause findings that matter

1. Hermes Feishu gateway is activated from env vars like `FEISHU_APP_ID` and `FEISHU_APP_SECRET`.
2. `lark-cli auth status` is useful for user/bot identity state, but not enough for app secret recovery.
3. `~/.lark-cli/config.json` may store `appSecret` as a reference object like:
   - `{ "source": "keychain", "id": "appsecret:cli_xxx" }`
4. On macOS, current `lark-cli` stores the actual encrypted secret at:
   - `~/Library/Application Support/lark-cli/appsecret_cli_xxx.enc`
5. The decryption key is indirectly stored in macOS Keychain under:
   - service: `lark-cli`
   - account: `master.key`
6. `security find-generic-password -s lark-cli -a master.key -w` returns a string prefixed with `go-keyring-base64:` and the payload is base64-encoded twice before yielding the 32-byte AES key.
7. The encrypted `.enc` file uses AES-GCM:
   - first 12 bytes = nonce
   - remainder = ciphertext+tag
8. A very common misdiagnosis: changing the agent's answer format, memory, or prompt does **not** reproduce the polished Feishu "status card / thinking / completed / tool summary" look by itself. That visual effect comes from an extra rendering layer (for example a Feishu streaming-card/sidecar integration), not from plain gateway text formatting.
9. Current Hermes Feishu adapter normally sends standard `text` / `post` messages for ordinary replies; interactive cards are used only for specific flows (for example approval buttons). So if a coworker shows a much richer Feishu UI, first verify whether a separate card/sidecar package or runtime hook is installed before claiming the style has been "synced".
10. If the source contains `HERMES_FEISHU_CARD_*` patch blocks in `gateway/run.py` / `cron/scheduler.py`, that is only the hook surface. The renderer still requires an importable package such as `hermes_feishu_card.hook_runtime`; if `importlib.util.find_spec("hermes_feishu_card")` returns `None`, the card UI will not activate and Hermes will fall back to native text/post replies.
11. Feishu topic/group-thread messages can silently lose the card when the card hook tries to `reply_to` the original message: the adapter intentionally avoids falling back to a top-level group message when `metadata.thread_id` exists, so the hook returns `False` and native text is sent. Fix in `hermes_feishu_card.hook_runtime._get_or_create_state`: compute metadata before storing state, and if `metadata.get("thread_id")`, set `reply_to = None` so `_send_raw_message()` creates directly into the `thread_id`.
12. For durability, also make `_send_or_update()` retry as a top-level Feishu `interactive` card when threaded interactive-card send still fails. This preserves card UX instead of falling through to native Markdown text, even if Feishu rejects cards in a topic/thread. Log the retry at warning level.
13. Because gateway code changes cannot be hot-reloaded inside the running gateway process, a macOS launchd watchdog can be used outside the gateway: `~/Library/LaunchAgents/ai.hermes.feishu-card-watchdog.plist` running `~/.hermes/scripts/hermes_feishu_card_watchdog.py`. It should restart the gateway only when card hook source/venv mtime is newer than the running gateway process start time, with a rate limit to avoid restart loops.
14. Feishu reply readability has two separate layers:
    - Content discipline: use Allen's response-formatting skill for conclusion-first, short sections, and tables for 3+ comparable items.
    - Gateway display noise: tune `display.platforms.feishu` rather than changing global CLI defaults.
15. Upstream Hermes Feishu does not currently provide a universal “standard answer card” for normal replies. Ordinary final responses go through `FeishuAdapter.send()`, which chooses Feishu `text` or `post`; `interactive` cards are mainly for card actions, update confirmations, and command approvals. Do not promise card-like normal replies unless a separate renderer/hook is installed and verified.
16. Markdown tables are a special Feishu case: Hermes forces table-looking content to `text` because Feishu `post`/`md` can render markdown tables poorly or blank. This is a reason to keep tables compact and readable as raw Markdown in Feishu.

See `references/feishu-response-readability.md` for the GitHub/source-derived notes and recommended Feishu display override.

## Safe workflow

### 1. Inspect current state

Run:
```bash
hermes config path
hermes gateway status
hermes config check
lark-cli auth status
lark-cli config show
```

Check these first:
- Whether gateway already runs
- Whether Feishu env vars already exist in `~/.hermes/.env`
- Whether Hermes venv has `lark_oapi`

Useful verification:
```bash
/Users/heytea/.hermes/hermes-agent/venv/bin/python3 - <<'PY'
try:
    import lark_oapi
    print('lark_oapi_ok')
except Exception as e:
    print('missing', e)
PY
```

### 2. Back up Hermes config before edits

Always back up:
- `~/.hermes/.env`
- `~/.hermes/config.yaml`

### 3. Recover app credentials from lark-cli

Read `~/.lark-cli/config.json` and locate the first app entry.
Expect fields like:
- `appId`
- `brand`
- `appSecret` reference object

If `appSecret` is keychain-backed, derive the encrypted file path by replacing `:` with `_` and appending `.enc` under:
- `~/Library/Application Support/lark-cli/`

Get the master key:
```bash
security find-generic-password -s lark-cli -a master.key -w
```

Important:
- Strip the `go-keyring-base64:` prefix if present
- Base64-decode once to get another base64 string
- Base64-decode again to get the 32-byte AES key

Then decrypt the `.enc` file with AES-GCM:
- nonce = first 12 bytes
- ciphertext = remaining bytes

Do not print the secret to terminal output.
Write it directly into `~/.hermes/.env`.

### 4. Write Hermes Feishu env vars

Ensure these exist in `~/.hermes/.env`:
```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=...
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_GROUP_POLICY=allowlist
```

If you know the intended user should be allowed in groups, also set:
```bash
FEISHU_ALLOWED_USERS=ou_xxx
```

A good source for that user open_id is:
```bash
lark-cli auth status
```

### 5. Write Hermes config.yaml platform block

Ensure `~/.hermes/config.yaml` contains a Feishu platform entry like:
```yaml
platforms:
  feishu:
    enabled: true
    extra:
      connection_mode: websocket
      default_group_policy: allowlist
      ws_reconnect_interval: 120
```

Why both env and config?
- Gateway enablement and credentials come from env
- OpenClaw-like per-platform behavior maps cleanly into platform config `extra`

### 6. Install missing Hermes Feishu dependency

Hermes may not have `pip` available inside its venv initially.
If needed:
```bash
/Users/heytea/.hermes/hermes-agent/venv/bin/python3 -m ensurepip --upgrade
/Users/heytea/.hermes/hermes-agent/venv/bin/python3 -m pip install 'hermes-agent[feishu]'
```

This should install `lark-oapi` and related pieces.

### 7. Restart and verify gateway

Start or restart:
```bash
hermes gateway run
```

Then verify:
```bash
hermes gateway status
```

Also verify config state:
```bash
python3 - <<'PY'
from pathlib import Path
import yaml
cfg = yaml.safe_load(Path('/Users/heytea/.hermes/config.yaml').read_text()) or {}
feishu = (((cfg.get('platforms') or {}).get('feishu') or {}))
extra = feishu.get('extra') or {}
print('feishu_enabled=', feishu.get('enabled'))
print('connection_mode=', extra.get('connection_mode'))
print('default_group_policy=', extra.get('default_group_policy'))
print('ws_reconnect_interval=', extra.get('ws_reconnect_interval'))
PY
```

And env presence without revealing values:
```bash
python3 - <<'PY'
from pathlib import Path
for line in Path('/Users/heytea/.hermes/.env').read_text().splitlines():
    if '=' in line and line.split('=',1)[0].startswith('FEISHU_'):
        print(line.split('=',1)[0])
PY
```

## Verification checklist

Success means all of these are true:
- `hermes gateway status` shows running
- `lark_oapi` imports successfully in Hermes venv
- `~/.hermes/.env` contains Feishu keys
- `config.yaml` has `platforms.feishu.enabled: true`
- User can DM the bot
- User can @mention the bot in an allowed group

## Pitfalls

### 1. `lark-cli auth status` may show expired user token
That does not necessarily block bot-based Feishu gateway chat.
It only matters for user-identity operations in `lark-cli`.

### 2. `python` may not exist
Use `python3` on macOS shell checks.

### 3. Hermes venv may lack `pip`
Use `python3 -m ensurepip --upgrade` first.

### 4. `security` output is not raw key bytes
For `master.key`, current output is effectively double-base64 wrapped with a `go-keyring-base64:` prefix.
Do not use it directly as the AES key.

### 5. Avoid leaking secrets
Never echo `FEISHU_APP_SECRET` or decrypted values into the chat response.
Edit files directly.

### 6. Old OpenClaw settings do not map 1:1
- `dmPolicy = open` -> DM behavior is just normal Feishu adapter handling
- `requireMention = true` -> group mention gating is built into Hermes Feishu adapter
- `groupPolicy = allowlist` -> map to `FEISHU_GROUP_POLICY=allowlist` and/or `default_group_policy: allowlist`

### 7. Config files can be correct while the running gateway process is wrong
A real failure mode on macOS: `~/.hermes/.env` contains `FEISHU_ALLOWED_USERS`, but the already-running `hermes gateway run` process was started before that env existed or before it was reloaded.

Symptoms:
- DMs or group mentions are received in `~/.hermes/logs/gateway.log`
- then the log shows `Unauthorized user: ... on feishu`
- in groups, Hermes silently ignores the message
- startup log may show `No user allowlists configured`

Important implication:
- checking only `~/.hermes/.env` and `~/.hermes/config.yaml` is not enough
- you must verify the live process environment or restart the gateway cleanly

Useful checks:
```bash
read_file ~/.hermes/logs/gateway.log
```
Look for:
- `Unauthorized user:`
- `No user allowlists configured`

Check the live process command/env:
```bash
hermes gateway status
ps eww -p <gateway_python_pid>
```
Confirm `FEISHU_ALLOWED_USERS` is actually present in the running process.

### 8. Prefer a clean background restart when troubleshooting gateway env loading
A foreground `hermes gateway restart` can be confusing in agent sessions because the command may stay attached, hit a tool timeout, or later stop when the session is torn down.

A more reliable troubleshooting sequence is:
```bash
hermes gateway stop
hermes gateway run   # start in background if your tool/session supports it
hermes gateway status
```

On macOS launchd setups, `hermes gateway status` may also report:
- `Service definition is stale relative to the current Hermes install`

In that case, refresh the service definition with:
```bash
hermes gateway start
hermes gateway status
```

Then verify:
- `gateway.log` no longer prints `No user allowlists configured`
- the process env includes `FEISHU_ALLOWED_USERS`
- a fresh DM or group mention no longer logs `Unauthorized user`

## Context bloat / prompt pollution troubleshooting

When Allen reports that Hermes Feishu replies show repeated instructions, hidden memory blocks, or context bloat, consult `references/context-bloat-and-prompt-injection.md`.

Default mitigation learned from Allen's Feishu setup: do not put the same response-format/personality rules in both `agent.system_prompt` and a `pre_llm_call` plugin. In Hermes, `pre_llm_call` context is appended to the current user message for that API call, so duplicate formatting plugins can waste tokens and make replies look prompt-polluted. Prefer one canonical location; for Allen's default response style, keep `agent.system_prompt` and disable the duplicate formatting plugin.

## Troubleshooting: bot can send DMs but does not answer in groups

If the bot can send outbound Feishu messages, but ignores group `@mentions`, check in this order:

1. `hermes gateway status`
2. `~/.hermes/logs/gateway.log` for inbound Feishu events
3. `~/.hermes/logs/gateway.log` for `Unauthorized user:` warnings
4. process env with `ps eww -p <pid>` to confirm `FEISHU_ALLOWED_USERS`
5. confirm bot identity settings are present in env (`FEISHU_BOT_NAME`, optionally `FEISHU_BOT_OPEN_ID` / `FEISHU_BOT_USER_ID`)
6. restart gateway cleanly and re-test

A successful fix is indicated by:
- inbound group or DM messages appearing in the log
- no `Unauthorized user` warning for that sender
- Hermes replying after the re-test

### New failure mode: group mention visually appears blue, but Hermes still ignores it

A real-world failure mode on Feishu group chats:
- the user types something like `@openclaw叫笨笨 你能看到我吗`
- Feishu UI visually renders it like a mention
- but the inbound event may arrive with missing or degraded `mentions` metadata
- Hermes then fails mention gating before the message reaches the agent

Symptoms:
- DMs work fine
- group messages seem to be sent normally
- no reply appears in the group
- logs may show no usable bot mention match even though the UI looked correct
- startup may also show:
  - `Unable to hydrate bot identity from application info...`

Recommended mitigation order:

1. Set at least:
```bash
FEISHU_BOT_NAME=<the exact visible bot/group mention name>
```
Example from a working fix:
```bash
FEISHU_BOT_NAME=openclaw叫笨笨
```

2. If available, also set stable IDs:
```bash
FEISHU_BOT_OPEN_ID=ou_xxx
FEISHU_BOT_USER_ID=u_xxx
```

3. If you control Hermes code, add a fallback in group mention gating:
- first try SDK `mentions`
- then parsed post-content mention IDs
- finally fall back to matching `normalized.text_content` against `FEISHU_BOT_NAME`

The successful fallback pattern added in `gateway/platforms/feishu.py` was:
- keep allowlist/group-policy checks first
- accept `@_all`
- accept when SDK mentions match configured bot identity
- accept when parsed post `mentioned_ids` match configured bot identity
- accept when plain text still contains `@<bot_name>` and metadata is missing

4. Add regression tests for all three paths:
- SDK mention metadata path
- parsed post-content mention path
- plain-text fallback path when `mentions=[]`

Practical verification:
- ensure `~/.hermes/.env` includes `FEISHU_BOT_NAME`
- run Feishu adapter tests after patching
- restart gateway
- send a fresh group message like:
  - `@openclaw叫笨笨 你能看到我吗`

### Practical note on gateway restart behavior

On macOS with launchd-managed Hermes gateway, `hermes gateway restart` or `hermes gateway start && hermes gateway status` may print success but still return as an interrupted/attached command in agent sessions.

Important: when the agent is currently running inside the gateway process (for example from Feishu), Hermes may explicitly block `hermes gateway stop/start/restart` because stopping the launchd service would kill the running gateway and its child command before completion. Treat that as a real self-protection blocker, not a config failure. Apply/verify config changes first, then either:
- ask the user to run the restart from a separate local shell, or
- schedule an external supervisor outside the gateway process if one already exists.

When restarting from a separate shell, use:
```bash
hermes gateway status
hermes gateway stop
hermes gateway start
hermes gateway status
```
Then confirm:
- a live PID exists
- `LastExitStatus = 0`
- the updated env/config is loaded
- a fresh DM/group re-test succeeds


New practical finding:
- Some Feishu group messages visually show a blue `@mention`, but the inbound event may not carry usable mention metadata for Hermes.
- If the bot name is known, setting `FEISHU_BOT_NAME=<display name>` gives Hermes a better chance to recognize the group message as targeting the bot.
- In the Hermes codebase, a robust fallback is to accept the message when normalized text content contains `@<bot_name>` even if `message.mentions` is empty and post-style `mentioned_ids` are absent.
- The corresponding code path is in `gateway/platforms/feishu.py` inside `_should_accept_group_message()` and a helper like `_text_mentions_bot()`.
- Add regression coverage in `tests/gateway/test_feishu.py` for:
  - a text message whose content includes `@<bot_name>` but has no mention metadata → should be accepted
  - a text message mentioning a different bot name → should still be rejected

A successful fix is indicated by:
- inbound group or DM messages appearing in the log
- no `Unauthorized user` warning for that sender
- Hermes replying after the re-test

## Re-login note for user features
If the user later wants personal-resource operations through `lark-cli` (calendar, docs, tasks as the user), they may need:
```bash
lark-cli auth login
```

## Minimal implementation script outline

Use Hermes venv Python if you need AES-GCM available. Core outline:
1. Read `~/.lark-cli/config.json`
2. Resolve encrypted secret file path
3. Fetch `master.key` from macOS Keychain
4. Decode twice after removing `go-keyring-base64:`
5. AES-GCM decrypt app secret
6. Update `~/.hermes/.env`
7. Update `~/.hermes/config.yaml`
8. Install `hermes-agent[feishu]` if `lark_oapi` missing
9. Start gateway and verify
