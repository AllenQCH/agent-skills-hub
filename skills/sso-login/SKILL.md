---
name: sso-login
description: Use when Codex needs HeyTea unified SSO login, internal account.heytea.com session checks, Browser Bridge based login refresh, or opencli-driven access to internal systems like dbauto and bk/BlueKing. Also use when an internal page asks for SSO login, session expires, opencli browser automation is required, or a task mentions SSO, account.heytea.com, dbauto, bk, BlueKing, TGC, SESSION, Browser Bridge, or cookie refresh.
---

# SSO Login

Use this skill to manage HeyTea SSO through `opencli` Browser Bridge instead of the old external Playwright wrapper. The opencli path is mandatory for HeyTea SSO checks; do not fall back to Playwright/browser-profile login scripts unless the user explicitly asks to debug legacy tooling.

Use `opencli-browser-reuse` for any browser-opening step so SSO checks reuse `heytea-sso-cn` instead of creating ad-hoc sessions.

## Safety

- Treat this skill as a credential/session helper.
- Do not print cookie values, TGC, SESSION, access tokens, or browser profile contents.
- Do not persist copied browser profiles, cookie databases, or token dumps inside this skill directory.
- Before opening a browser or requiring user scan/approval, state the platform, target system, and expected manual action.
- If a CLI reports its own OAuth login is missing, such as `dws auth login` or `lark-cli auth login`, follow that CLI's auth flow; do not assume HeyTea SSO can replace tool OAuth.

## Commands

Check domestic SSO status with `opencli`:

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/sso-login/scripts/sso_opencli.py --platform cn --status
```

Ensure domestic SSO session, opening browser guidance if needed:

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/sso-login/scripts/sso_opencli.py --platform cn
```

Force a fresh session check in a dedicated `opencli` session name:

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/sso-login/scripts/sso_opencli.py --platform cn --session heytea-sso-cn
```

Diagnose Browser Bridge connectivity first:

```bash
opencli doctor -v
```

## Platform Selection

- Use `cn` for domestic HeyTea systems, including `account.heytea.com`, `dbauto.heyteago.com`, and `devops-bk.heyteago.com`.
- Use `uswest` for US West internal systems.
- Use `sg` for Singapore/APAC internal systems.
- Use `test` for domestic test CAS systems such as `test-go-1-cas.heyteago.com` and `dbweb.test.heytea.com`.
- Use `test-intl` for overseas test CAS systems.
- Use `dev` for domestic development CAS systems.
- Read `references/platforms.md` only when selecting a non-`cn` platform or checking app support.

## Workflow

1. Run `opencli doctor` or the bundled script with `--status`.
2. If Browser Bridge is disconnected, stop and report that opencli itself is not ready yet; do not pretend the SSO session was checked.
3. If Browser Bridge is healthy, open the platform SSO page through the reuse wrapper or the bundled script, not a random raw session.
4. Determine login state by checking the current URL and page title; if the page is already past the SSO login screen, treat the SSO session as valid.
5. If still on the login page, tell the user what manual action is needed, then poll with `opencli browser <session> wait time 3` and `get url` until the page leaves the SSO login host or timeout expires.
6. After successful login, continue the original task; if timeout expires, report that login was not completed.

## Script

Primary script:

```text
scripts/sso_opencli.py
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Treating `opencli` installed as equivalent to browser-ready | Run `opencli doctor` and require Browser Bridge connectivity |
| Claiming SSO is valid without opening the SSO page | Use the script or `opencli browser ... open/get` flow |
| Assuming tool OAuth can be replaced by HeyTea SSO | Keep `dws`/`lark-cli` OAuth separate |
| Dumping raw cookies or tokens into logs | Only report status, URL/title transitions, and next actions |
