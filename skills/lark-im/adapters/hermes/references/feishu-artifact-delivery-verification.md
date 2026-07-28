# Feishu artifact delivery verification

## Goal

Ensure “send this package/file to the group” results in a real downloadable Feishu artifact, not a local-path message or an unverified send attempt.

## Group workflow

1. Resolve the group by exact name with user identity; do not reuse a guessed chat ID.
2. Verify the matched `name` and save its `chat_id`.
3. Confirm the local artifact is the requested class (desktop app vs CLI, offline package vs bootstrapper), architecture, and complete size/hash.
4. Send using `lark-cli im +messages-send --as bot --chat-id <id> --file ./relative-file` from the artifact directory.
5. Read the recent chat with user identity.
6. Declare success only when the expected filename appears in a `msg_type=file` record; report the message ID.

## Large-file decision path

- Probe/inspect the live message-upload limit before committing to an attachment route.
- A local CLI pre-check and the server can enforce different ceilings; treat the server response as authoritative for that route.
- If IM upload is too small, try a supported Drive large-file flow or the logged-in desktop client.
- For GUI fallback, first confirm the clipboard contains a file object, not merely text. On macOS, `clipboard info` should show an alias/file representation; plain UTF text indicates the copy step failed.
- After GUI send, confirm actual upload activity or read the group back. Keystrokes completing without network/message evidence are not success.
- If large-file routes require a new scope, request the minimum scope and place the authorization URL in the chat when the user cannot access a locally opened browser.
- Only use byte-split parts after explaining the number of files and obtaining agreement. Supply a deterministic rebuild script plus whole-file hash.

## Common correction pattern

If the user rejects an artifact:

1. Stop sending variants immediately.
2. Restate the exact distinction they corrected.
3. Resolve the correct upstream artifact before downloading.
4. Verify packaging and destination upload separately.
5. Remove “downloaded locally” and “sent to chat” ambiguity from the final report.
