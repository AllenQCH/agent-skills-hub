---
name: dws-auth-helper
description: Use when Codex needs DingTalk `dws` CLI authentication, hits `not_authenticated`, cannot read DingTalk docs/files/messages because `dws` is logged out, or must guide the user through `dws auth status`, `dws auth login`, and post-login retry. Also use when a task mentions DingTalk doc access, `dws auth`, device flow, scan login, or reusing `dws` login state.
---

# DWS Auth Helper

Use this skill when the DingTalk `dws` CLI is the blocker. This is separate from HeyTea unified SSO.

## Safety

- Treat `dws` auth as DingTalk OAuth, not HeyTea SSO.
- Do not print or persist access tokens in notes, skills, or logs.
- Always use `--format json` when the command supports it.
- Before starting an interactive login, state that the user may need to scan a DingTalk QR code or confirm device authorization.

## Commands

Check auth state:

```bash
dws auth status --format json
```

Start login:

```bash
dws auth login --format json
```

Force re-login:

```bash
dws auth login --force --format json
```

Post-login verification:

```bash
dws auth status --format json
```

## Workflow

1. Run `dws auth status --format json`.
2. If authenticated, continue the original `dws` command.
3. If not authenticated, tell the user the next step requires DingTalk device authorization.
4. Start `dws auth login --format json`.
5. Relay the QR code URL, device code, or confirmation prompt to the user without paraphrasing away required details.
6. After the user confirms completion, rerun `dws auth status --format json`.
7. If authenticated, retry the original `dws` command exactly once.
8. If still not authenticated, report the exact failure and stop.

## Manual Confirmation Points

- The user may need to scan a DingTalk QR code.
- The user may need to confirm device authorization inside DingTalk.
- If DingTalk asks to choose an organization or account, the user must confirm the correct one.

## Common Mistakes

- Do not assume DingTalk desktop login automatically authenticates `dws`.
- Do not replace `dws auth login` with HeyTea `sso-login`.
- Do not keep retrying login in a loop.
