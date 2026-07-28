---
name: opencli-browser-reuse
description: Use when Codex or Hermes is asked to use opencli to explore a webpage, inspect an internal site, open a Chrome-backed page, or browse through Browser Bridge, especially when ad-hoc session names would create too many OpenCLI Browser tabs and the agent should reuse stable sessions and close one-shot work.
---

# OpenCLI Browser Reuse

Use this skill when the task needs `opencli browser`, but the real requirement is page exploration rather than creating a brand-new browser session. The default policy is to reuse a small fixed set of session names and close one-shot work when continuity is not needed.

## Rules

- Do not invent request-specific session names.
- Reuse one stable session for the same site family.
- Prefer the bundled wrapper over raw `opencli browser <random-session> ...`.
- When the user wants their current Chrome reused, pass `--bind-current`; `open <URL>` then navigates the active Chrome tab without creating another Chrome window.
- For one-shot reads, pass `--close-after`.
- If you need another page in the same task, use `tab new` inside the same session instead of creating a new session.

## Default Sessions

- `heytea-sso-cn`: `account.heytea.com` and domestic SSO checks
- `dbweb-explore`: `dbweb.test.heytea.com`
- `dbauto-query`: `dbauto.heyteago.com`
- `bk-console`: `devops-bk.heyteago.com`
- `trace-log`: `cloud-trace-log.dev.heytea.com`
- `github-web`: `github.com`
- `opencli-explore`: fallback for general browser exploration

## Wrapper

Primary script:

```text
scripts/opencli_reuse.sh
```

Examples:

```bash
bash /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh open 'https://dbweb.test.heytea.com/#/my-resource'
bash /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh --bind-current open 'https://github.com/'
bash /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh --session github-web --bind-current open 'https://github.com/'
bash /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh state
bash /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh --close-after get url
bash /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh --session bk-console open 'https://devops-bk.heyteago.com/console/platform/entry'
```

## Workflow

1. Decide whether the task is one-shot or needs continuity.
2. Use the wrapper so the session is inferred from the URL or forced to a stable name.
3. For login or long workflows, keep the stable session alive.
4. For read-only checks, use `--close-after`.
5. Before claiming cleanup is done, verify that `opencli browser <session> tab list` is empty or intentionally retained.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Creating a new session name per prompt or per page | Reuse the mapped stable session for that domain |
| Opening a separate OpenCLI Chrome window when the user wants their existing Chrome | Use `--bind-current open <URL>`, then restore the original page when the task finishes |
| Opening a second page with another session | Use `tab new` in the same session |
| Leaving one-shot inspection sessions open | Add `--close-after` |
| Calling raw `opencli browser foo ...` out of habit | Use the wrapper unless a task explicitly requires a different session |
| Treating a reused GitHub page session as a CLI token | OpenCLI reuses Chrome cookies in-page; it must not extract or convert them into a `gh` token |
