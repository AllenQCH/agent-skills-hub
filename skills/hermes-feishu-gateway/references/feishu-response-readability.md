# Feishu response readability notes

Use this when Allen complains that Hermes replies in Feishu are hard to read, noisy, too stream-like, or not card-like enough.

## Core finding

Hermes Feishu has platform message adaptation, but normal final answers do **not** have a built-in standardized user-facing response format or universal interactive-card renderer.

Normal replies flow through `gateway/platforms/feishu.py`:

- `FeishuAdapter.send()` formats and chunks the response.
- `_build_outbound_payload()` chooses:
  - `text` when no Markdown hints are present;
  - `post` with `md` rows when Markdown hints are present;
  - `text` for Markdown-table-looking content, because Feishu `post`/`md` can render tables poorly or blank.
- If Feishu rejects an invalid `post` payload, Hermes falls back to plain text.
- `interactive` cards are used for specific flows such as dangerous command approval, update confirmation, and card action callbacks — not as the default normal-answer renderer.

## Practical diagnosis

If Feishu output feels unfriendly, separate the problem:

1. **Content shape** — solved with Allen response-formatting skill/prompt discipline.
2. **Gateway noise** — solved with Feishu-specific display config overrides.
3. **Rich card UI** — requires an additional Feishu card renderer/hook; do not claim it is present until verifying an importable renderer package and live behavior.

## Recommended Feishu display override

Prefer platform-specific overrides so CLI behavior is not degraded:

```yaml
display:
  platforms:
    feishu:
      streaming: false
      tool_progress: "new"        # use "off" if Allen wants no progress chatter
      tool_preview_length: 0
      interim_assistant_messages: false
      busy_ack_detail: false
      long_running_notifications: true
```

Why:

- `streaming: false` reduces fragmented Feishu bubbles/updates.
- `tool_progress: new` gives some progress signal for long tasks without showing every iteration. Use `off` for maximum cleanliness.
- `tool_preview_length: 0` prevents tool-call parameter previews from cluttering mobile chat.
- `interim_assistant_messages: false` keeps final-answer-first behavior.
- `busy_ack_detail: false` removes noisy iteration/detail counters.
- `long_running_notifications: true` keeps a minimal heartbeat for truly long work.

## Content style to pair with Feishu

For Allen, prefer:

```text
## 结论
一句话先给判断或结果。

## 关键依据
2-4 条 bullet；3 个以上同类信息用 Markdown 表格。

## 建议 / 下一步
给出可执行动作。
```

Troubleshooting:

```text
## 当前判断
## 已确认事实
## 根因/可能原因
## 下一步
```

Rules:

- Avoid large prose blocks; one paragraph = one point.
- Use compact Markdown tables for 3+ comparable items, but keep them raw-text readable because Feishu table rendering is not rich.
- If the user requests raw logs, SQL, curl, JSON, code, transcript, or another exact format, obey that format instead of forcing the template.

## Verification checklist after changing config

1. Back up `~/.hermes/config.yaml` before edits.
2. Apply only `display.platforms.feishu` overrides unless the user explicitly wants global changes.
3. Restart the gateway; display changes do not reliably affect already-running gateway processes.
4. Send a short Feishu DM and a longer tool-using request.
5. Confirm:
   - final answer arrives as one coherent reply/update;
   - no reasoning is shown;
   - no long tool previews are shown;
   - progress chatter is at the requested level (`new` or `off`).
