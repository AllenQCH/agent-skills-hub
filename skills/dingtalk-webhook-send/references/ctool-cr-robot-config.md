# Ctool 代码 CR 钉钉机器人配置

Use when configuring the Ctool Chrome extension (`Ctool 程序开发常用工具`) to send code-review notifications to a DingTalk custom robot.

## What Ctool expects

Ctool's settings page has a section named `代码CR钉钉机器人` with two fields:

- `access_token`: the value after `access_token=` in the DingTalk webhook URL, not the full webhook URL.
- `secret`: the DingTalk robot signing secret beginning with `SEC...`.

Ctool stores these as setting items named:

- `ding_talk_cr_access_token`
- `ding_talk_cr_secret`

Do not persist or echo the raw token/secret in memory, notes, logs, or final replies.

## Preferred workflow

1. Open Ctool in Chrome and go to the settings panel.
   - Ctool page can be opened directly with a Chrome extension URL if the extension ID is known.
   - The settings panel is reachable from the bottom-right gear icon.
2. In the `代码CR钉钉机器人` section, fill:
   - first field: access token only;
   - second field: signing secret.
3. Click/blur outside the fields so Ctool's `onChange` handlers save the values.
4. Verify visually that both fields are filled, without reading values aloud.
5. If safe and user-authorized, send a minimal test markdown message to the robot using the saved values or equivalent webhook-signing logic. Success criterion: DingTalk returns `{errcode:0, errmsg:"ok"}`.

## Useful source-code clues

If UI labels are unclear, search the unpacked extension for:

- `代码CR钉钉机器人`
- `ding_talk_cr_access_token`
- `ding_talk_cr_secret`
- `请先到右下角的设置-代码CR钉钉机器人`

Ctool may wrap settings under a `ctool.nv_setting` local-storage entry; however, direct LevelDB editing is a last resort. Prefer UI操作 first.

## Pitfalls

- Do not waste time downloading Ctool if the user says it is already installed locally; locate the existing unpacked extension directory and use Chrome UI.
- If automation cannot open/click the settings gear reliably, say exactly where you are blocked and ask the user to open the panel; do not keep silently trying unrelated low-level workarounds.
- When sending a test message, never print the full token, secret, timestamp signature, or full signed URL.
