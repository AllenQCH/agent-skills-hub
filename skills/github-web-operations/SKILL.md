---
name: github-web-operations
description: Operate GitHub repositories through the user's existing Chrome session for repository creation, settings changes, file uploads, commits, visibility checks, and browser-confirmed actions. Use when GitHub is already logged in in Chrome, OpenCLI or browser reuse is requested, gh is unauthenticated, web confirmation is required, or a GitHub web workflow must avoid repeated login and token confusion.
---

# GitHub Web Operations

Use the existing Chrome login as the default GitHub authorization surface. Treat browser session reuse and GitHub CLI authentication as separate capabilities.

## Route The Operation

1. Identify the exact owner/repository, action, local file paths, target repository paths, and expected final state.
2. Read `~/.codex/agents/operator/tool_github_web_operator.toml` for the governed boundary when operating directly.
3. Run `gh auth status` only as a capability probe.
4. Use `gh` only when it is already authenticated and the requested action is supported cleanly.
5. When `gh` is unauthenticated and Chrome is already logged in, continue through Chrome/OpenCLI. Do not start `gh auth login` unless the user explicitly asks for terminal GitHub access or terminal `push`.

OpenCLI reuses the browser's authenticated page session. It does not obtain, convert, print, or persist a GitHub token from Chrome.

## Reuse The Current Chrome

Use stable session `github-web`. Do not create a separate Chrome window or a request-specific session.

```bash
opencli browser github-web bind
opencli browser github-web get url
bash /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/opencli-browser-reuse/scripts/opencli_reuse.sh \
  --session github-web open 'https://github.com/<owner>/<repo>'
```

Record the original URL before navigation. At closeout, restore it and unbind:

```bash
opencli browser github-web open '<original-url>'
opencli browser github-web unbind
```

Use the Chrome plugin for stable DOM interactions when available. Use Computer Use only for native macOS dialogs or Chrome internal settings that the browser surface cannot operate.

## Handle Authorization Correctly

- A visible logged-in GitHub profile proves browser authorization for web actions.
- An unauthenticated `gh` status does not invalidate the Chrome login.
- Never extract cookies, session values, access tokens, or browser profile data.
- If GitHub itself shows password, passkey, 2FA, CAPTCHA, sudo-mode, or device confirmation, pause at that page and state the exact user action required.
- Do not ask for a second confirmation when the user already approved the exact external action and the target did not change.

## Upload Files

1. Confirm the local files exist and record size/hash for release artifacts.
2. Open the exact GitHub upload URL for the target directory.
3. Prefer the browser file chooser with absolute paths.
4. If file selection fails with `Not allowed`, inspect the ChatGPT Chrome extension's `Allow access to file URLs` setting. Changing that permission and restarting Chrome requires explicit user approval.
5. After the permission is enabled, retry the browser file chooser before falling back to the native macOS picker.
6. Wait for uploads to settle, then verify the visible upload list contains each expected filename exactly once.
7. Remove accidental duplicates before committing.
8. Fill an explicit commit summary and commit only after the list is exact.

For native picker fallback, use `Command+Shift+G`, enter the absolute file path, select it, and confirm with the enabled `Open` button. Re-read the page after each file because GitHub's upload list may update asynchronously.

## Verify External Changes

Use the narrowest authoritative evidence:

- Repository creation/settings: final GitHub page showing owner, repository, visibility, or setting value.
- File upload: final commit page or repository tree showing the exact paths and commit summary.
- Public repository: unauthenticated GitHub page/API or raw URL when network access is available.
- Binary release artifact: download the published file and compare `shasum -a 256` with the local pre-upload hash.

If command-line access to GitHub is reset or unavailable but the browser page is authoritative, use the browser evidence and report the network limitation separately. Do not retry unrelated auth flows.

## Clean Up

- Restore the original user URL.
- Unbind `github-web`.
- Close only agent-created temporary tabs/groups.
- Never close or navigate unrelated user tabs.
- Keep the final repository page open only when it is useful to the user.

## Output Contract

Report:

- `target_repo`
- `requested_action`
- `browser_auth_state`
- `gh_auth_state`
- `execution_path` as `gh` or `opencli-web`
- `manual_pause_reason` when applicable
- `final_state`
- `verification_evidence`
- `cleanup_state`

When used through the tool framework, also report `selected_operator`, `public_capability`, `implementation_path`, `invocation_mode`, and `invocation_proof`.
