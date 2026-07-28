---
name: dingtalk-to-glm-knowledge-base
description: Use when 用户请求匹配此工作流：Import documents shared in a DingTalk group into Allen's GLM/智谱 knowledge base by extracting share links, capturing readable text with authenticated browser state, converting to Markdown, and uploading through the BigModel console. Do not use for tasks outside the named productivity app, document, spreadsheet, meeting, or workflow scope.
---

# When to use

Use this skill when Allen asks to move DingTalk group-shared docs into his GLM/智谱 knowledge base (also called 智谱知识库 / 智谱RAG / GLM RAG), especially when the source is a DingTalk group and the destination should be a named knowledge base such as `hey_share`.

Typical triggers:
- “把这个钉钉群里的分享文档放到 glm 知识库”
- “把群里分享的文档全部导入智谱知识库”
- “给这个钉钉群做一个 RAG 知识库”

# Outcome

Produce a real imported knowledge base, not a plan:
1. identify the target DingTalk group;
2. enumerate the shared docs/messages;
3. extract readable text into local `.md` files;
4. create or reuse the target GLM knowledge base;
5. upload the files;
6. verify import status in the console.

# Prerequisites

- DingTalk access is already authenticated in the available MCP/DWS tools.
- Browser cookies for `alidocs.dingtalk.com` and `bigmodel.cn` exist locally so Playwright/browser-cookie3 can reuse an already logged-in session.
- User gave a concrete group name and target knowledge-base name, or there is an obvious default.

# Recommended workflow

## 1) Locate the DingTalk group

Use DingTalk chat search first to get the exact group `openConversationId`.
Then inspect recent/history messages and/or search group messages for `alidocs.dingtalk.com` links.

Important: do not assume only the latest 50 messages contain all shared docs. Start with message search by keyword/domain when possible.

## 2) Extract share links and normalize them

Collect all relevant DingTalk doc links from group messages.
For each item, preserve:
- label shown in chat;
- original URL;
- if available, title / og:title / document name;
- any obvious file/document type.

Store a local manifest while processing so upload verification can later be compared against source count.

## 3) Prefer reliable source capture/download

Pitfall: DingTalk `doc_download` / `drive_download` may fail even when chat access works; one observed error is `PERMISSION_DENIED - 此MCP已被企业管理员禁用` for the drive MCP.

If chat messages expose DingTalk file IDs / dentry UUIDs for PDFs or Markdown files:
1. Open `https://alidocs.dingtalk.com/i/nodes/<dentryUuid>?corpId=<corpId>` in Playwright with local `dingtalk.com` / `alidocs.dingtalk.com` cookies.
2. Wait for redirect to `https://alidocs.dingtalk.com/uni-preview?...&cloudSpaceDentryId=<objectid>&cloudSpaceSpaceId=<spaceid>&version=<version>&dentryUuid=<uuid>&fileId=<objectid>`.
3. Download the original binary with authenticated cookies from:
   `https://space.dingtalk.com/attachment/mdown?bizid=<spaceid>&objectid=<cloudSpaceDentryId>&version=<version>&operate=download`
4. Verify with `file`, file size, and hashes.

For online docs where binary download is unavailable, fallback:
- reuse authenticated browser cookies;
- open each doc in Playwright or another browser automation path;
- capture `document.title`, `og:title`, and `body.inner_text()`;
- convert to compact Markdown snapshots.

For each output file:
- filename should be based on the clean document title;
- content should include source URL and captured title metadata at the top;
- save under a dedicated working folder such as `~/Downloads/<kb_name>_docs/`.

## 4) Create or reuse the target GLM knowledge base in the BigModel console

Open `https://bigmodel.cn/console/appcenter_v1/knowledge` with the user’s authenticated browser state.

If the target KB does not exist:
- create it with the requested name;
- a short description helps unblock creation when the dialog expects more than just a name.

Known UI pitfall:
- the page may show invite / notice / marketing dialogs that intercept clicks;
- remove or dismiss blocking overlays before clicking `Create New Knowledge Base` or upload actions.

## 5) Upload local Markdown files through the console

Use the KB detail page’s `Upload Knowledge` flow.
Supported practical path from this session: upload `.md` files through the local-document tab.

Suggested sequence:
- set files on the hidden `input[type=file]`;
- wait for all uploads to register in the file list;
- click `Next Step`;
- click `Configuration Complete`.

## 6) Verify with real page state

Do not stop after upload requests fire.
Verify on the knowledge-base detail page that:
- the files appear in the table;
- pagination was checked if there are more than 10 files;
- each file status shows success/completion (e.g. `数据完成`).

Report back with:
- KB name;
- KB id if visible;
- local folder path;
- imported file count;
- any caveats (e.g. text snapshot import vs raw original binary).

# Pitfalls

- Raw DingTalk download tools may expose metadata but not produce a directly reusable file for KB ingestion; be ready to pivot to authenticated page-text capture.
- BigModel console APIs may require in-page authorization headers; direct cookie-only HTTP calls can fail even when the browser page works. Prefer browser automation and page-state verification over standalone API scraping.
- The BigModel page can contain multiple `Create` buttons; target the dialog-scoped button, not the page-level `Create New Knowledge Base` button.
- Marketing/invite popups can block clicks on both KB creation and upload dialogs.
- Verification must include page 2 when the uploaded set exceeds the first-page table size.

# Files

See `references/playwright-upload-notes.md` for the concrete browser/UI quirks and verification pattern observed in a successful DingTalk→GLM import session.

# Response style for Allen

Keep the final report compact and practical:
- first: whether the import finished;
- then: KB name / KB id / file count / local path;
- then: one short caveat if the import used text snapshots instead of native original files.
