---
name: feishu-friend-send-macos-fallback
description: Use when you need to send a file or note to a Feishu friend and normal contact search / bot delivery is unreliable. Covers P2P chat recovery, API-first send, and macOS GUI fallback with verification. Do not use for tasks outside the named productivity app, document, spreadsheet, meeting, or workflow scope.
license: MIT
metadata:
  hermes:
    tags:
    - feishu
    - lark
    - im
    - p2p
    - file-send
    - macos
    - gui-fallback
    related_skills:
    - lark-im
    - lark-shared
---

# Send to a Feishu Friend from macOS (API first, GUI fallback)

## Overview

Use this skill when the goal is to send a file or short note to a specific Feishu friend, especially when the user identifies the target by nickname, remark name, or screenshot instead of a clean open_id.

This workflow assumes:
- `lark-cli` is available
- `--as user` can read/search chats
- `--as bot` may or may not be able to send to the target
- On macOS, Feishu/Lark desktop client is installed and GUI automation may be used as a fallback

The key lesson: **do not trust nickname search alone, and do not assume a recovered P2P chat is the right person until message history proves it.**

## When to Use

Use when:
- The user says “发给飞书好友 X” and gives a nickname / remark / screenshot
- `contact +search-user` returns nothing
- `+messages-send --as bot --user-id ...` fails with availability errors
- There is probably already an existing P2P chat, but it must be recovered and verified
- You need a reliable fallback on macOS when API delivery is blocked

Do not use for:
- Sending to a Feishu group by name (use `lark-im` group workflow)
- Large-scale broadcast / automation across many chats
- Cases where the user can simply provide the exact `chat_id` or `open_id`

## Fast Path

1. Confirm the artifact exists locally.
2. Try normal search:
   - `lark-cli contact +search-user --query '<name>' --as user`
   - `lark-cli im +chat-search --as user --query '<name>' --page-size 20`
3. If that fails, search messages for the nickname / a unique phrase from prior conversation:
   - `lark-cli im +messages-search --as user --query '<nickname or unique phrase>' --page-size 20`
4. Extract candidate P2P `chat_id` values.
5. Verify the candidate chat by reading the latest messages:
   - `lark-cli im +chat-messages-list --as user --chat-id '<oc_xxx>' --page-size 8`
6. Only after verification, try bot send by `chat_id`:
   - `cd /tmp && lark-cli im +messages-send --as bot --chat-id '<oc_xxx>' --file './artifact.json'`
7. If bot send fails because the bot is not in the chat, use macOS GUI fallback.
8. Re-read the target chat and confirm the expected file appears before telling the user it succeeded.

## Recovery Workflow in Detail

### A. Recover the real target chat

Preferred search order:

```bash
lark-cli im +messages-search --as user --query '<nickname>' --page-size 20
lark-cli im +messages-search --as user --query '<real name>' --page-size 20
```

If the user only provided a screenshot, OCR it first. On macOS, Vision OCR works well for small Feishu screenshots.

### B. Verify the recovered chat is actually the friend

Never assume a P2P `chat_id` is correct just because the nickname appears somewhere in search results.

Read the latest messages:

```bash
lark-cli im +chat-messages-list --as user --chat-id '<oc_xxx>' --page-size 8
```

Look for evidence such as:
- the friend's past messages in that thread
- the user's own past replies to that same person
- content that clearly belongs to that friend

### C. Red flags that you found the WRONG chat

Treat these as danger signs:
- the chat mainly contains the user's maintenance traffic with the bot
- recent messages are mostly the bot talking to the user
- message content is about agent debugging rather than the real friend's conversation
- there is no believable human dialogue from the target friend

If any of those appear, keep searching. Do **not** send yet.

## API Send Rules

### Send by `chat_id` first when possible

If a real P2P `chat_id` is known, prefer:

```bash
cd /tmp
lark-cli im +messages-send --as bot --chat-id '<oc_xxx>' --file './filename.ext'
```

Why:
- `--user-id` can fail with availability errors even when an existing P2P thread exists
- `--chat-id` can succeed in some cases where `--user-id` fails

### Relative file path requirement

For file sends, `--file` must be a relative path inside the working directory. Absolute paths like `/tmp/a.json` can be rejected.

Correct pattern:

```bash
cd /tmp
lark-cli im +messages-send --as bot --chat-id '<oc_xxx>' --file './a.json'
```

### Common API failure meanings

- `230013 Bot has NO availability to this user`
  - Bot cannot reach that user by `user-id`
- `230002 Bot/User can NOT be out of the chat`
  - Bot is not in that existing chat, so bot send-by-chat-id is blocked

When either blocks delivery, switch to GUI fallback on macOS.

## macOS GUI Fallback

### Preconditions

Check:

```bash
mdfind 'kMDItemCFBundleIdentifier == "com.bytedance.ee.lark" || kMDItemDisplayName == "飞书"'
osascript -e 'tell application "System Events" to return UI elements enabled'
```

Expected:
- Feishu/Lark desktop client exists
- UI scripting is enabled

### Open the exact chat

```bash
open 'lark://client/chat/open?openChatId=<oc_xxx>'
```

Then bring Feishu frontmost if needed.

### Most reliable file-send method found

For files, Finder copy/paste is more reliable than trying to drag with blind coordinates:

1. Reveal the file in Finder
2. Copy it (`Cmd+C`)
3. Open the target Feishu chat
4. Paste (`Cmd+V`)
5. Press Enter if required
6. Re-read the chat via `+chat-messages-list`

### Text-note fallback when inline text input is flaky

If GUI text entry is unstable because the input focus is unclear, create a short README `.txt` locally and send that file instead.

Example README content:
- what the main file is
- time range
- record count
- optional note that a Markdown/table summary can be provided later

This is often more reliable than trying to inject Chinese text into the Feishu compose box.

## Verification Checklist

Do not declare success until all are true:

- [ ] The target `chat_id` was verified from actual recent messages
- [ ] The correct artifact path exists locally
- [ ] If using API send, the command returned `ok: true`
- [ ] If using GUI fallback, `+chat-messages-list --as user --chat-id '<oc_xxx>'` shows a new `file` message with the expected filename
- [ ] If sending an explanation note, confirm that note also appears (either as text or README file)
- [ ] Final user report distinguishes between “sent the main file” and “sent the explanatory note”

## Common Pitfalls

1. **Confusing the user's bot-maintenance P2P with the actual friend's P2P.**
   Search hits can point to the wrong conversation. Always verify the latest messages before sending.

2. **Trusting nickname search too early.**
   Friend remark names often do not resolve via `contact +search-user`.

3. **Trying `--user-id` only.**
   `--user-id` can fail while a known P2P `chat_id` path might still work.

4. **Using absolute paths for `--file`.**
   Use a relative path from the working directory.

5. **Declaring success before reading the chat back.**
   Delivery is not real until the new file message appears in the target chat history.

6. **Assuming GUI text input succeeded just because automation ran.**
   Focus can be stolen by Terminal/Ghostty/Finder. Re-check the chat. If needed, send a README file instead of inline text.

## One-Shot Recipe

### Send a JSON export to a friend when only a nickname is known

1. OCR screenshot if needed to recover the displayed nickname.
2. Search messages with user identity for that nickname.
3. Gather candidate P2P chats.
4. Verify the correct chat by reading recent messages.
5. Try bot send by `chat_id` with relative file path.
6. If blocked by bot availability / membership, use macOS Feishu GUI fallback.
7. Re-read the chat and confirm the new file is present.
8. If explanatory text is required and inline text is flaky, generate and send `README.txt`.
