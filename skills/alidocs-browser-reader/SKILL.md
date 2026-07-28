---
name: alidocs-browser-reader
description: Use when Codex needs to read DingTalk or AliDocs pages through an existing local browser login instead of `dws` CLI auth, especially when `dws auth` is blocked, CLI permissions are unavailable, or a user provides an `alidocs.dingtalk.com` or `docs.dingtalk.com` URL. Also use when browser cookies already hold a valid DingTalk session and Codex must extract visible document text from a rendered preview frame.
---

# AliDocs Browser Reader

Use this skill to read DingTalk docs from an existing local Chrome session. This avoids `dws` CLI login entirely.

## Safety

- Do not print cookie values or persist browser secrets.
- Use local browser cookies only to render the target page and extract visible text.
- If the browser session is no longer valid, stop and ask the user to log into DingTalk in Chrome first.
- Prefer this skill for `alidocs.dingtalk.com` and `docs.dingtalk.com` URLs when CLI auth is blocked.

## Command

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/alidocs-browser-reader/scripts/read_alidocs.py '<alidocs-url>'
```

Optional length limit:

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/alidocs-browser-reader/scripts/read_alidocs.py '<alidocs-url>' --max-chars 12000
```

## Workflow

1. Use Chrome cookies from the local profile.
2. Launch headless Chrome via Playwright.
3. Inject DingTalk cookies into a fresh browser context.
4. Open the AliDocs page and wait for the preview frame to render.
5. Extract title, preview frame URL, and visible article text.
6. If article text is missing, report that the browser session exists but document content did not render.

## Failure Modes

- If imports are missing, install `browser-cookie3` or Playwright dependencies locally.
- If no DingTalk cookies are found, ask the user to log into DingTalk in Chrome.
- If the page redirects to login or shows only shell content, the browser session is stale.
- If the document opens but the preview frame text is empty, the page structure may have changed and the selector should be updated.
