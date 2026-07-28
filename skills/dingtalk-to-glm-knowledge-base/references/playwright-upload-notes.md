# Playwright upload notes for DingTalk → GLM knowledge-base imports

This reference captures the durable parts of a successful import workflow.

## Source-side extraction pattern

- Group messages can contain many DingTalk doc-share URLs in different shapes:
  - `https://alidocs.dingtalk.com/i/nodes/...`
  - `https://alidocs.dingtalk.com/document/edit?...`
  - `https://alidocs.dingtalk.com/document/preview?...`
  - `https://alidocs.dingtalk.com/uni-preview?...`
- For KB ingestion, a text snapshot is often sufficient and more reliable than trying to pull the original online-doc binary.
- Captured fields worth preserving in the generated Markdown:
  - source chat label;
  - original URL;
  - HTML title;
  - `og:title` when available;
  - `body.inner_text()`.

Suggested front matter / header pattern:
- source label
- source URL
- page title
- og:title
- captured timestamp

## BigModel console quirks

### 1) Blocking overlays
The knowledge-base console may load invite/marketing/notice dialogs immediately. They can intercept pointer events and make normal Playwright `.click()` fail.

Durable lesson:
- if a visible button is inexplicably unclickable, inspect for `.v-modal`, `.el-dialog__wrapper`, invite dialogs, or notice dialogs;
- dismiss them if possible, or remove blocking overlays in page JS before continuing.

### 2) KB creation dialog
Observed working path:
- open KB list page;
- neutralize blocking overlays;
- trigger `Create New Knowledge Base`;
- fill KB name;
- if needed, also fill description;
- trigger the dialog-local `Create` button.

Reason this matters:
- the page may contain more than one `Create` button or similar labels, causing selector ambiguity.

### 3) Upload flow
Observed working path:
- enter the target KB detail page;
- click `Upload Knowledge` / `导入知识`;
- use the local-document tab;
- set multiple `.md` files on the hidden file input;
- wait until the file list shows all uploaded items;
- click `Next Step`;
- click `Configuration Complete`.

### 4) Verification
A successful upload is not enough. Verify the final table view.

Checks that worked well:
- refresh or revisit the KB detail page;
- inspect table rows on page 1;
- if pagination shows page 2, open page 2 as well;
- confirm each item shows a completed status such as `数据完成`.

## Why browser verification beats direct HTTP here

Direct cookie-based HTTP calls to BigModel document endpoints may still fail because the console sends an `Authorization` header generated in-page. Browser automation with the logged-in page is therefore the more reliable end-to-end path for creation, upload, and verification.

Durable takeaway:
- prefer browser-state verification over trying to reconstruct all console headers manually.
