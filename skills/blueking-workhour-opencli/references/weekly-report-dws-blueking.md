# 周报：DWS 取钉钉链接 + BlueKing 汇总内容

Use this when Allen says “用 dws 填周报” and asks to copy/fill a weekly report based on a latest DingTalk/钉钉群 link plus BlueKing 本周/下周工作内容.

## Expected chain

1. **DWS first: locate the latest report link**
   - Use `dws`/DingTalk chat search or message list against the relevant group.
   - Search sender `陆建波` and recent messages mentioning `周报` / `周报链接` / report document keywords.
   - Extract the latest usable URL/document/report identifier from the message body.
   - Do not invent the group or link; if multiple candidate groups/messages appear, show the candidates and choose the newest exact match.
   - Do **not** start this workflow by listing `dws report template`; Allen's requested target is the latest report link from the group, and template discovery only belongs later if the link/artifact proves to be a DingTalk report template.
   - If Allen provides a fresh successful `dws auth status --format json` transcript but the agent shell returns `not_authenticated`, treat it as a context/HOME/profile mismatch to debug or bypass via Hermes DingTalk MCP tools, not as proof the user must login again.

2. **BlueKing second: gather work content**
   - Use OpenCLI against the real Chrome/BlueKing session, not a generic browser session.
   - For weekly content, compute the current Monday-Sunday range from system date.
   - Pull Allen-created or Allen-owned tasks according to the wording in the request; for weekly report content, prefer fields that describe actual work (`jobContent`, task detail, man-hour records) over task titles alone.
   - Split output into:
     - 本周已完成/进行中工作
     - 下周计划
     - 风险/阻塞（only if backed by task/man-hour evidence）

3. **Fill/submit only after target is known**
   - If the target is a DingTalk report template, use `dws report` commands and query template/detail before create/update.
   - If the target is an online spreadsheet link (`alidocs.dingtalk.com/spreadsheetv2/...`), use the DingTalk sheet commands rather than report-template commands:
     1. Pass the **full spreadsheet URL** to `dws sheet list --node '<url>' --format json`; do not pass only the short `dentryKey`/path token, because sheet APIs require a valid URL or 32-char node id.
     2. Read the candidate sheet/range with `dws sheet range read --node '<url>' --sheet-id <sheetId> --range 'A1:Z80' --format json`.
     3. Locate Allen/戚呈辉's row by reading column A, then update only the relevant cells (typically `B:D` for 本周工作/下周计划/已安排但尚未进入开发的需求) via `dws sheet range update`.
     4. Immediately re-read the exact row/range and verify the new cell values before reporting success.
   - If the target is an online document link, use the appropriate document/browser workflow and verify the write/readback.
   - Report exactly which artifact was filled and include the link/ID.

## Speed optimizations learned from `weekly-report-cli`

A coworker package at `/Users/heytea/Downloads/weekly-report-cli` shows a faster 1-2 minute design. Reuse these ideas when Allen asks for recurring weekly-report filling:

- Prefer an API-first BlueKing client that reads Chrome BlueKing cookies via `bk-rush`/`ChromeCookieClient`, instead of driving BlueKing through OpenCLI for every read. OpenCLI should be a fallback or optional `--with-gantt` enrichment, not the default path.
- Keep a local `config.local.json` containing owner name/job number, DingTalk sheet URL, sheet id, owner/start/end columns, category rules, projects, concurrency, and history lookback. Avoid rediscovering group/link/sheet layout every week when the target is stable.
- Locate the DingTalk row with `dws sheet find --match-entire-cell true` and then update exactly the owner row range, instead of reading a large `A1:Z80` range and manually scanning it. For DWS sheet boolean flags, always pass the explicit value (`true`/`false`); `--match-entire-cell --format json` can be parsed incorrectly.
- Enrich BlueKing task details/man-hour records in parallel (`ThreadPoolExecutor`, default around 8 workers), because each candidate requires multiple API calls: search/detail/relations/man-hour.
- Save JSON snapshots under `artifacts/weekly-report/` and use them to skip historical completed tasks and generate diffs/warnings. This cuts repeated enrich calls and avoids duplicating old completed work.
- Default week range should be current Monday-Friday for work reports, not Monday-Sunday, unless Allen explicitly asks otherwise.
- Preserve a dry-run/preview mode and require explicit `--yes` for sheet writes; after writing, still read back or return the DWS logId/range as verification.

Current downloaded package caveat: its shell entrypoints have macOS `com.apple.quarantine`, and Python imports may be shadowed by an installed `tools` package unless the project is packaged/fixed with `tools/__init__.py`; treat it as a design reference until adapted.

## OpenCLI prerequisite pitfall

When OpenCLI fails before opening BlueKing, distinguish daemon/bridge setup from BlueKing business failure:

```bash
opencli doctor -v
opencli browser bk-console state
# if hinted:
node /Users/heytea/.hermes/node/lib/node_modules/@jackwener/opencli/dist/src/daemon.js
```

If the direct daemon run shows `listen EPERM ... 127.0.0.1:19825`, the current sandbox cannot bind the local OpenCLI daemon port. The fix is to run/approve the daemon locally (`opencli daemon restart && opencli doctor -v`) rather than concluding that BlueKing cannot be read. Keep the user-facing wording concise: “OpenCLI daemon 没起来，第一错误是 19825 端口绑定被当前沙箱拒绝；需要本机终端/授权后继续。”

## Allen-facing response style

Allen is usually asking for completion, not a long diagnosis. Prefer:

- one-line status: `DWS 链接已找到 / BlueKing 已读取 / 已填入` or `卡在 OpenCLI daemon`
- compact evidence: command/status + exact first error or filled artifact ID/link
- next action: what permission or missing target is needed

Avoid repeating speculative explanations or switching away from the requested `dws + OpenCLI` path unless that path is actually verified unavailable.
