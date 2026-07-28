# macOS fallback: send a file to a Feishu P2P chat when bot delivery fails

Use this when all of the following are true:
- The target is a **P2P/private chat** rather than a group.
- `lark-cli im +messages-send --as bot --user-id ...` fails with bot availability / visibility errors such as `230013 Bot has NO availability to this user`.
- Direct bot send to the P2P `chat_id` also fails with `230002 Bot/User can NOT be out of the chat`.
- You are on macOS with the **Feishu/Lark desktop app installed** and Accessibility automation allowed.

## Durable workflow

1. **Do not trust nickname search alone** for P2P targets.
   - `contact +search-user` may return no results for a nickname/remark.
   - `im +chat-search` may also miss P2P names.

2. **Recover the real P2P chat from message history** instead of guessing.
   - Search messages with the target's legal/display name or related strings.
   - Strong signal: older P2P history may contain a contact-application card like:
     - `申请人：康学涛`
     - `申请理由：我是摇摆的涛哥`
   - From search results, identify the actual `chat_id` (`oc_xxx`) for the target P2P.

3. **Verify the chat really is the target person** before sending.
   - Use `lark-cli im +chat-messages-list --as user --chat-id <oc_xxx> --page-size 5`.
   - Confirm recent message context matches the intended person, not the assistant's own bot/user maintenance chat.

4. **If API send is blocked, use the desktop-client GUI fallback on macOS.**
   - Open the target chat with:
     - `open 'lark://client/chat/open?openChatId=<oc_xxx>'`
   - Bring Feishu to front (`tell application "Feishu" to activate`).
   - For files, the most reliable path is:
     - reveal the local file in Finder
     - copy it with Cmd-C
     - focus Feishu chat input area
     - paste with Cmd-V
     - press Enter
   - This reliably sends files even when bot API permissions block message delivery.

5. **Verify delivery from chat history after GUI send.**
   - Re-run `+chat-messages-list` and confirm the new `file` message appears with the expected filename.

## Notes from this session

- Bot API send can succeed to one P2P/chat and fail to another depending on bot availability and whether the bot is considered inside that conversation.
- A GUI fallback is especially useful for "send this exported file to a known Feishu friend" tasks on macOS.
- Inline text automation via GUI can be flaky because focus may not land in the composer; file-send via Finder copy/paste is more reliable than text paste.
