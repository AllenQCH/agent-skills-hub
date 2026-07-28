# OpenCLI extension reconnect pattern for BlueKing sessions

Observed durable workflow on macOS/Chrome when Allen says he is already logged in but `opencli doctor` reports `Browser Bridge extension not connected`.

## Symptoms
- `opencli doctor` shows:
  - `[OK] Daemon: running ...`
  - `[MISSING]` or `[FAIL] Extension: not connected`
- `opencli browser <session> ...` commands fail with `Browser Bridge extension not connected`
- Meanwhile the user's real Chrome may already have active BlueKing tabs and valid login state.

## Verified fix
1. Confirm Chrome is actually running.
2. Confirm the OpenCLI extension is installed in the active Chrome profile.
   - Observed extension id in this environment: `ildkmabpimmkaediidaifkhjpohdnifk`
3. Open the extension popup page in Chrome:
   - `chrome-extension://ildkmabpimmkaediidaifkhjpohdnifk/popup.html`
4. Re-run `opencli doctor`.
5. Proceed only after doctor reports the extension is connected.

## Why this matters
- Do not conclude "BlueKing login is unavailable" from a disconnected OpenCLI extension.
- Do not use the generic browser tool's login page as evidence about the user's real Chrome login state for OpenCLI work.
- For Allen specifically, evidence-first reporting matters: verify with OpenCLI/Chrome before saying a blocker is real.

## Reporting rule
Bad: "I can't continue; you're on the login page."
Good: "OpenCLI extension was disconnected; I reconnected it and then verified the live Chrome/BlueKing session before proceeding."