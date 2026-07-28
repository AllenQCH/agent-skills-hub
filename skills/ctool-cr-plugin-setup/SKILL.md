---
name: ctool-cr-plugin-setup
description: Use when Allen needs to install, verify, operate, or reconfigure the Ctool Chrome extension and its 代码CR钉钉机器人 settings, especially for supply-chain project CR notifications. Prioritizes direct UI operation, safe secret handling, and explicit blocker communication. Do not use for tasks outside the named productivity app, document, spreadsheet, meeting, or workflow scope.
license: MIT
metadata:
  hermes:
    tags:
    - ctool
    - chrome-extension
    - ding-talk
    - cr
    - macos
    - gui-operation
    related_skills:
    - opencli-browser-webapp-exploration
    - dingtalk-webhook-send
---

# Ctool Chrome Extension + CR DingTalk Bot Setup

## Overview

This skill captures Allen's working Ctool setup flow on macOS: load the local Ctool Chrome extension, verify it is enabled, configure the “代码CR钉钉机器人” settings, and validate that CR notifications can be sent to the intended DingTalk group.

The key behavior expectation is: **operate directly when possible**. Do not spend a long time silently trying brittle workarounds. If blocked, state exactly which step is blocked, what evidence was observed, and what minimal user action is needed.

Never store or repeat DingTalk webhook/access_token/secret values in skill content, memory, summaries, or logs. Treat them as ephemeral credentials used only during the active configuration.

## When to Use

Use this skill when Allen asks about:

- Ctool / `ctool.app` / “蓝鲸插件更新工具”
- installing or loading the Ctool Chrome extension
- Chrome `chrome://extensions` loading unpacked extensions for Ctool
- configuring “代码CR钉钉机器人”
- supply-chain project CR notification setup
- redoing the previous Ctool plugin operation on another machine/session

Do not use this skill for generic Chrome extension debugging unless Ctool or CR notification setup is involved.

## Known Local Facts from Allen's Mac

| Item | Known value |
|---|---|
| Ctool app UI name | `蓝鲸插件更新工具 v1.0.3` |
| Local extension directory used successfully | `/Users/heytea/Applications/ctool_chrome` |
| Chrome extension name | `Ctool 程序开发常用工具` |
| Extension version observed | `2.3.3` |
| Extension ID observed | `bidkmiagcmjhnmimhifhellkbeoacgoi` |
| Relevant settings keys | `ctool.ding_talk_cr_access_token`, `ctool.ding_talk_cr_secret` |
| Ctool prompt text | `请先到右下角的设置-代码CR钉钉机器人` |
| Notification rule | Supply-chain projects must not skip CR; CR notifications are sent to the current work group. |

These values are useful starting points, but always verify live state before acting because extension IDs, paths, and profiles can change.

## Safe Operating Rules

1. **No secret persistence.** Do not write real webhook tokens or secrets into memories, skills, summaries, screenshots captions, or final answers.
2. **Prefer UI operation over LevelDB editing.** Chrome LocalStorage is LevelDB-backed and brittle to modify while Chrome is running. Use the extension/settings UI unless a controlled script path is proven.
3. **Communicate blockers early.** If a GUI click, selector, file picker, permission prompt, or missing credential blocks progress for more than a few attempts, report the exact blocker.
4. **Verify with real evidence.** Do not claim setup is complete until extension state and robot send result are verified.
5. **Do not ask for manual steps when the agent can reasonably operate the UI.** Only ask for user help for OS permission prompts, OAuth/SSO, captchas, password prompts, or physical device actions.

## Workflow

### 1. Confirm Ctool app and extension directory

Check whether Ctool is running and whether the known extension path exists:

```bash
pgrep -fl 'ctool|Ctool|蓝鲸插件'
python3 - <<'PY'
from pathlib import Path
p = Path('/Users/heytea/Applications/ctool_chrome')
print('exists=', p.exists())
print('manifest=', (p/'manifest.json').exists())
if (p/'manifest.json').exists():
    print((p/'manifest.json').read_text()[:1000])
PY
```

If the known path is missing, search likely locations for a Ctool `manifest.json` without dumping unrelated files:

```bash
python3 - <<'PY'
from pathlib import Path
roots = [Path.home()/'Applications', Path.home()/'Downloads', Path.home()/'Documents', Path('/Applications')]
for root in roots:
    if not root.exists():
        continue
    for mf in root.rglob('manifest.json'):
        try:
            txt = mf.read_text(errors='ignore')
        except Exception:
            continue
        if 'Ctool' in txt or 'ctool' in txt or '程序开发常用工具' in txt:
            print(mf.parent)
PY
```

### 2. Load or verify Chrome extension

Open Chrome extensions:

```bash
open -a 'Google Chrome' 'chrome://extensions/'
```

Then verify in the UI:

- Developer mode is enabled.
- `Ctool 程序开发常用工具` is present and enabled.
- If missing, click **加载未打包的扩展程序 / Load unpacked** and select the directory containing `manifest.json`, usually:

```text
/Users/heytea/Applications/ctool_chrome
```

If GUI automation is available, operate the Chrome UI directly. If the file picker is blocked by macOS permission, focus, or multi-monitor coordinate issues, say exactly: “卡在 Chrome 文件选择器/按钮点击/系统权限弹窗”，not a vague “不行”.

### 3. Verify extension details

Expected details after loading:

| Field | Expected |
|---|---|
| Name | `Ctool 程序开发常用工具` |
| Version | around `2.3.3` |
| Enabled | yes |
| Source directory | `/Users/heytea/Applications/ctool_chrome` or another verified manifest directory |

If possible, inspect Chrome extension preferences or UI to confirm the extension ID. Do not rely on stale notes only.

### 4. Configure 代码CR钉钉机器人

Open the Ctool extension UI. The setting is normally reached from the lower-right settings/gear area:

```text
右下角设置 → 代码CR钉钉机器人
```

Fill these two fields:

| Field | Source |
|---|---|
| `access_token` | Extract from DingTalk webhook URL query parameter `access_token=...` |
| `secret` | DingTalk robot signing secret, usually starts with `SEC` |

If only a full webhook URL is provided, parse only the token into the Ctool field. Do not paste the entire webhook into an `access_token`-only field unless the UI explicitly asks for webhook URL.

### 5. Verify persisted Ctool settings

After saving, verify via UI or extension storage that both settings exist and look structurally valid without exposing values:

| Key | Safe validation |
|---|---|
| `ctool.ding_talk_cr_access_token` | non-empty; expected length around 64 |
| `ctool.ding_talk_cr_secret` | non-empty; starts with `SEC` |

Do not print the real values. Report only lengths/prefix shape.

### 6. Send a test notification

If the UI has a test button, use it. Otherwise use the DingTalk webhook send workflow with the active ephemeral credentials and a harmless test message.

Expected successful DingTalk response:

```json
{"errcode":0,"errmsg":"ok"}
```

Only report success after receiving this response or seeing the message in the target group.

## Fallbacks

### If Chrome LocalStorage direct write is tempting

Avoid this as the first path. Previous attempt hit LevelDB/Python binding issues on macOS:

- `plyvel` failed due to LevelDB dynamic library symbol mismatch.
- `leveldb` Python package failed to build under Python 3.14.

Use Ctool UI instead unless there is a tested local script and Chrome is safely closed.

### If extension is loaded but settings do not save

1. Reopen Ctool extension UI.
2. Confirm the settings panel is the CR robot panel, not a different DingTalk or notification panel.
3. Save again.
4. Reload extension from `chrome://extensions`.
5. Reopen Ctool and verify values structurally.
6. Send test message.

### If UI automation cannot click reliably

Provide a precise blocker statement:

```text
当前卡在：Chrome/Ctool 的 <具体控件> 无法通过自动化稳定点击。
已确认：<证据，例如扩展已启用、按钮可见、选择器未弹出>。
需要你做的最小动作：<例如点开齿轮设置面板/批准系统权限>。
我会继续完成后续字段填写和验证。
```

Do not simply ask Allen to redo the whole operation.

## Communication Template for Blockers

Use this format if blocked:

```markdown
## 当前卡点
卡在：<具体步骤>。

## 已确认事实
- <事实 1>
- <事实 2>

## 不能继续的原因
<具体原因：权限弹窗 / 找不到 manifest / 文件选择器无法定位 / 缺少 token 等>

## 需要你做的最小动作
<只列一个最小动作>。

## 我会继续做
<用户完成后我继续的动作>。
```

## Verification Checklist

- [ ] Ctool app or extension source directory verified live.
- [ ] Extension directory contains `manifest.json`.
- [ ] Chrome extension page shows `Ctool 程序开发常用工具`.
- [ ] Extension is enabled.
- [ ] CR robot settings panel located.
- [ ] `access_token` filled without exposing value.
- [ ] `secret` filled without exposing value.
- [ ] Settings persist after save/reopen/reload.
- [ ] DingTalk robot test returns `errcode: 0, errmsg: ok` or message is visible in target group.
- [ ] Final response reports concrete verification evidence and any remaining risk.
