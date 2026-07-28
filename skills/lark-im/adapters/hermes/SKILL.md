---
name: lark-im
description: Use when 用户请求匹配此工作流：飞书即时通讯：收发消息和管理群聊。发送和回复消息、搜索聊天记录、管理群聊成员、上传下载图片和文件、管理表情回复。当用户需要发消息、查看或搜索聊天记录、下载聊天中的文件、查看群成员时使用. Do not use for non-Lark/Feishu tasks or adjacent Lark operations covered by a narrower lark-* skill.
metadata:
  requires:
    bins:
    - lark-cli
  cliHelp: lark-cli im --help
---

# im (v1)

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../../../lark-shared/SKILL.md)，其中包含认证、权限处理**

## Core Concepts

- **Message**: A single message in a chat, identified by `message_id` (om_xxx). Supports types: text, post, image, file, audio, video, sticker, interactive (card), share_chat, share_user, merge_forward, etc.
- **Chat**: A group chat or P2P conversation, identified by `chat_id` (oc_xxx).
- **Thread**: A reply thread under a message, identified by `thread_id` (om_xxx or omt_xxx).
- **Reaction**: An emoji reaction on a message.

## Resource Relationships

```
Chat (oc_xxx)
├── Message (om_xxx)
│   ├── Thread (reply thread)
│   ├── Reaction (emoji)
│   └── Resource (image / file / video / audio)
└── Member (user / bot)
```

## Important Notes

### Identity and Token Mapping

- `--as user` means **user identity** and uses `user_access_token`. Calls run as the authorized end user, so permissions depend on both the app scopes and that user's own access to the target chat/message/resource.
- `--as bot` means **bot identity** and uses `tenant_access_token`. Calls run as the app bot, so behavior depends on the bot's membership, app visibility, availability range, and bot-specific scopes.
- If an IM API says it supports both `user` and `bot`, the token type changes who the operator is. The same API can succeed with one identity and fail with the other because owner/admin status, chat membership, tenant boundary, or app availability are checked against the current caller.

### Sender Name Resolution with Bot Identity

When using bot identity (`--as bot`) to fetch messages (e.g. `+chat-messages-list`, `+threads-messages-list`, `+messages-mget`), sender names may not be resolved (shown as open_id instead of display name). This happens when the bot cannot access the user's contact info.

**Root cause**: The bot's app visibility settings do not include the message sender, so the contact API returns no name.

**Solution**: Check the app's visibility settings in the Lark Developer Console — ensure the app's visible range covers the users whose names need to be resolved. Alternatively, use `--as user` to fetch messages with user identity, which typically has broader contact access.

### Card Messages (Interactive)

Card messages (`interactive` type) are not yet supported for compact conversion in event subscriptions. The raw event data will be returned instead, with a hint printed to stderr.

### Sending to an Existing Group by Name

When the user asks to send knowledge/materials to a named group, do **not** reuse a stale or guessed `oc_xxx` chat ID. If `+messages-send` returns `api_error code 230001` / `invalid receive_id`, resolve the current chat ID first:

```bash
lark-cli im +chat-search --as user --query '<group name>' --page-size 20
```

Then send with bot identity to the returned `chat_id`:

```bash
lark-cli im +messages-send --as bot --chat-id '<oc_xxx>' --markdown "$(python3 - <<'PY'
from pathlib import Path
print(Path('/tmp/message.md').read_text())
PY
)"
```

Notes:
- `+messages-send` is bot-only, but `+chat-search --as user` can find groups visible to the authorized user.
- If the group was just created or there are duplicate names, search by exact name and verify the returned `name` before sending.
- For long Markdown, write the message to a temp `.md` file first, then shell-substitute from Python to avoid quoting and newline issues.

### File delivery means a real uploaded file

When the user says “把 package/文件发进群里”, a local path or `MEDIA:/absolute/path` rendered as text is not completion. Use an actual Feishu upload/send path and verify by reading the target chat back. Required success evidence:

- send operation returns `ok: true` and a `message_id`; and
- chat history contains a new `msg_type=file` message whose filename matches the artifact.

Before selecting an artifact, preserve the user's packaging requirement: a small online bootstrapper is not a substitute for a complete offline installer, and a CLI archive is not a desktop app. Do not rename or re-label a different artifact to look compliant.

For large files, check the live upload limit before promising direct attachment delivery. If the package is too large, prefer a supported large-file Drive or user desktop-client upload. If neither is currently available, explain the verified limit and ask the user to choose between a cloud-download delivery and explicit split parts; do not flood a group with many parts without agreement. See `references/feishu-artifact-delivery-verification.md`.

### User-identity direct send via raw API

If the goal is to send a normal text message as the logged-in user rather than as the bot, note two constraints:

1. `im +messages-send` is a bot-oriented shortcut, so user-identity direct send may require raw API.
2. Before attempting raw API, check user scopes first. The official `im/v1/messages` API requires **both** `im:message` and `im:message.send_as_user` for user-identity send.

Recommended sequence:
- `lark-cli auth check --scope "im:message"`
- `lark-cli auth check --scope "im:message.send_as_user"`
- If either is missing, run `lark-cli auth login --scope "..."` for the missing scope(s), then re-check.
- Only then try `lark-cli api POST /open-apis/im/v1/messages --as user ...`
- After sending, always re-read chat history to confirm the new text actually appeared.

Reference: `references/lark-im-user-send-scopes.md`

### P2P send fallback when bot availability blocks delivery

For private chats, do **not** assume nickname/contact search will find the right target, and do **not** assume a previously successful bot send pattern will generalize to every P2P.

When all of the following happen:
- `contact +search-user` or `im +chat-search` cannot find the target by nickname / remark name,
- `+messages-send --as bot --user-id ...` fails with bot availability errors such as `230013 Bot has NO availability to this user`, or
- `+messages-send --as bot --chat-id ...` fails with `230002 Bot/User can NOT be out of the chat`,

use this fallback:
1. Search message history to recover the real P2P `chat_id` instead of guessing; older contact-application cards and prior P2P messages are strong evidence.
2. Verify the recovered `chat_id` with `im +chat-messages-list --as user --chat-id <oc_xxx> --page-size 5` so you don't confuse the user's maintenance chat with the actual friend's P2P. Treat a chat as suspicious if recent traffic is mostly the bot talking to the user rather than believable human dialogue from the target friend.
3. On macOS, if API delivery is still blocked, use the Feishu desktop client GUI fallback: open the chat via `lark://client/chat/open?openChatId=<oc_xxx>`, bring Feishu frontmost, then send the file through Finder copy/paste into the chat.
4. If an inline explanatory text is required but GUI text input focus is flaky, generate a small `README.txt` companion file and send that instead of claiming the note was sent.
5. Re-check the target chat with `+chat-messages-list` and confirm the new `file` message appears with the expected filename before telling the user it was sent.

Reference: `references/lark-im-p2p-fallback-macos.md`

## Shortcuts（推荐优先使用）

If the user provides a nickname/screenshot for a Feishu friend and `contact +search-user` returns no result, do **not** stop there. A durable fallback is:

1. Search historical messages with user identity to locate the existing P2P thread:

```bash
lark-cli im +messages-search --as user --query '<nickname or unique text>' --page-size 10
```

2. From the matched result, extract the P2P `chat_id` (`oc_xxx`) and the partner `open_id` if present.
3. Prefer sending via the existing **P2P `chat_id`**:

```bash
cd /tmp
lark-cli im +messages-send --as bot --chat-id '<oc_xxx>' --file './artifact.json'
```

Important pitfalls:
- `+messages-send --user-id <open_id>` can fail with `api_error code 230013` / `Bot has NO availability to this user` even when an existing P2P chat is searchable.
- In that case, retry with the known **`--chat-id`** from historical search results; this can succeed where `--user-id` fails.
- For file sends, `--file` must be a **relative path inside the working directory**; `cd` into the artifact directory first or use `workdir` so `./filename` is accepted.
- If the contact name only exists in a screenshot, use local OCR first (for example macOS Vision OCR) to recover the exact nickname before running `+messages-search`.

## Shortcuts（推荐优先使用）

Shortcut 是对常用操作的高级封装（`lark-cli im +<verb> [flags]`）。有 Shortcut 的操作优先使用。

| Shortcut | 说明 |
|----------|------|
| [`+chat-create`](references/lark-im-chat-create.md) | Create a group chat with bot identity; bot-only; creates private/public chats, invites users/bots, optionally sets bot manager |
| [`+chat-messages-list`](references/lark-im-chat-messages-list.md) | List messages in a chat or P2P conversation; user/bot; accepts --chat-id or --user-id, resolves P2P chat_id, supports time range/sort/pagination |
| [`+chat-search`](references/lark-im-chat-search.md) | Search visible group chats by keyword and/or member open_ids (e.g. look up chat_id by group name); user/bot; supports member/type filters, sorting, and pagination |
| [`+chat-update`](references/lark-im-chat-update.md) | Update group chat name or description; user/bot; updates a chat's name or description |
| [`+messages-mget`](references/lark-im-messages-mget.md) | Batch get messages by IDs; user/bot; fetches up to 50 om_ message IDs, formats sender names, expands thread replies |
| [`+messages-reply`](references/lark-im-messages-reply.md) | Reply to a message (supports thread replies) with bot identity; bot-only; supports text/markdown/post/media replies, reply-in-thread, idempotency key |
| [`+messages-resources-download`](references/lark-im-messages-resources-download.md) | Download images/files from a message; user/bot; downloads image/file resources by message-id and file-key to a safe relative output path |
| [`+messages-search`](references/lark-im-messages-search.md) | Search messages across chats (supports keyword, sender, time range filters) with user identity; user-only; filters by chat/sender/attachment/time, enriches results via mget and chats batch_query |
| [`+messages-send`](references/lark-im-messages-send.md) | Send a message to a chat or direct message with bot identity; bot-only; sends to chat-id or user-id with text/markdown/post/media, supports idempotency key |
| [`+threads-messages-list`](references/lark-im-threads-messages-list.md) | List messages in a thread; user/bot; accepts om_/omt_ input, resolves message IDs to thread_id, supports sort/pagination |

## API Resources

```bash
lark-cli schema im.<resource>.<method>   # 调用 API 前必须先查看参数结构
lark-cli im <resource> <method> [flags] # 调用 API
```

> **重要**：使用原生 API 时，必须先运行 `schema` 查看 `--data` / `--params` 参数结构，不要猜测字段格式。

### chats

  - `create` — 创建群。Identity: `bot` only (`tenant_access_token`).
  - `get` — 获取群信息。Identity: supports `user` and `bot`; the caller must be in the target chat to get full details, and must belong to the same tenant for internal chats.
  - `link` — 获取群分享链接。Identity: supports `user` and `bot`; the caller must be in the target chat, must be an owner or admin when chat sharing is restricted to owners/admins, and must belong to the same tenant for internal chats.
  - `list` — 获取用户或机器人所在的群列表。Identity: supports `user` and `bot`.
  - `update` — 更新群信息。Identity: supports `user` and `bot`.

### chat.members

  - `create` — 将用户或机器人拉入群聊。Identity: supports `user` and `bot`; the caller must be in the target chat; for `bot` calls, added users must be within the app's availability; for internal chats the operator must belong to the same tenant; if only owners/admins can add members, the caller must be an owner/admin, or a chat-creator bot with `im:chat:operate_as_owner`.
  - `get` — 获取群成员列表。Identity: supports `user` and `bot`; the caller must be in the target chat and must belong to the same tenant for internal chats.

### messages

  - `delete` — 撤回消息。Identity: supports `user` and `bot`; for `bot` calls, the bot must be in the chat to revoke group messages; to revoke another user's group message, the bot must be the owner, an admin, or the creator; for user P2P recalls, the target user must be within the bot's availability.
  - `forward` — 转发消息。Identity: `bot` only (`tenant_access_token`).
  - `merge_forward` — 合并转发消息。Identity: `bot` only (`tenant_access_token`).
  - `read_users` — 查询消息已读信息。Identity: `bot` only (`tenant_access_token`); the bot must be in the chat, and can only query read status for messages it sent within the last 7 days.

### reactions

  - `batch_query` — 批量获取消息表情。Identity: supports `user` and `bot`.[Must-read](references/lark-im-reactions.md)
  - `create` — 添加消息表情回复。Identity: supports `user` and `bot`; the caller must be in the conversation that contains the message.[Must-read](references/lark-im-reactions.md)
  - `delete` — 删除消息表情回复。Identity: supports `user` and `bot`; the caller must be in the conversation that contains the message, and can only delete reactions added by itself.[Must-read](references/lark-im-reactions.md)
  - `list` — 获取消息表情回复。Identity: supports `user` and `bot`; the caller must be in the conversation that contains the message.[Must-read](references/lark-im-reactions.md)

### images

  - `create` — 上传图片。Identity: `bot` only (`tenant_access_token`).

### pins

  - `create` — Pin 消息。Identity: supports `user` and `bot`.
  - `delete` — 移除 Pin 消息。Identity: supports `user` and `bot`.
  - `list` — 获取群内 Pin 消息。Identity: supports `user` and `bot`.

## 权限表

| 方法 | 所需 scope |
|------|-----------|
| `chats.create` | `im:chat:create` |
| `chats.get` | `im:chat:read` |
| `chats.link` | `im:chat:read` |
| `chats.list` | `im:chat:read` |
| `chats.update` | `im:chat:update` |
| `chat.members.create` | `im:chat.members:write_only` |
| `chat.members.get` | `im:chat.members:read` |
| `messages.delete` | `im:message:recall` |
| `messages.forward` | `im:message` |
| `messages.merge_forward` | `im:message` |
| `messages.read_users` | `im:message:readonly` |
| `reactions.batch_query` | `im:message.reactions:read` |
| `reactions.create` | `im:message.reactions:write_only` |
| `reactions.delete` | `im:message.reactions:write_only` |
| `reactions.list` | `im:message.reactions:read` |
| `images.create` | `im:resource` |
| `pins.create` | `im:message.pins:write_only` |
| `pins.delete` | `im:message.pins:write_only` |
| `pins.list` | `im:message.pins:read` |
