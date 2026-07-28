---
name: blueking-workhour-opencli
description: Use when 用户请求匹配此工作流：Use opencli to explore Allen's BlueKing/敏捷协同 task page, identify today's active tasks, and safely prepare work-hour filling without accidental submission. Do not use for tasks outside the named productivity app, document, spreadsheet, meeting, or workflow scope.
---

# BlueKing Workhour via opencli

Use when Allen asks to inspect or prepare daily work-hour filling in 蓝鲸 / 敏捷协同, especially `devops-bk.heyteago.com` task pages. Also use it when he drops a demand-detail link and wants you to create a related task and then immediately record same-day man-hours in the created task. Also use for Allen's weekly-report flow when DingTalk/DWS provides the report link and BlueKing provides 本周/下周 work content. When the request expands into a unified 蓝鲸 workflow covering demand creation, demand/service pipelines, demand-linked tasks, daily work-hour filling, and date-range work-hour reports, keep this skill as the class-level umbrella and follow `references/unified-demand-pipeline-task-workhour.md` rather than creating separate one-off skills for each step.

## Safety rule

Before creating any BlueKing demand-linked task, always show Allen and obtain explicit confirmation for these four items: **标题、任务类型、预计开始/结束日期、预估工时**. A request like “给这个需求加个任务” authorizes preparation and lookup only; it does not authorize inventing defaults and submitting. Do not execute `create-related-task --yes` until Allen confirms all four items. If a task was created prematurely, read back its live values and ask Allen to confirm or correct them before making any edits.

Do not submit work hours or change task status while only exploring. Once Allen has already provided/approved the exact target task, date (or default today), work content, and hours, treat that as authorization and submit directly; do not ask for an extra confirmation. Still verify success afterward. Status changes require the status-transition condition to be met and either clear prior authorization from Allen or an explicit request.

For **bulk task-plan changes** driven by a screenshot/spreadsheet, if Allen says “先给改造方案，再去实施”, the first pass is strictly read-only: inspect the live task set, reconcile it against the target plan, and present a per-task old→new table. Do not update fields or states in that pass. The plan must call out task consolidation, any task proposed for cancellation, title/date/hour changes, current vs target task counts, and total-hour delta. For merged-away tasks, prefer `取消` over physical deletion so history is preserved, but first check whether the task already has work-hour records; if it does, report the impact and wait for a decision rather than cancelling blindly.

## Workflow discipline for Allen

When Allen explicitly says to use `opencli`, use `opencli` as the primary execution path and do not infer state from other browser stacks. Verify the opencli session first, reconnect it if needed, then operate and report only actions/results you actually observed. Avoid speculative phrasing like “应该/可能/看起来” when the page state can be checked directly.

## Reporting discipline for Allen

- Evidence first: do not say a blocker is real until you have verified it in the actual tool/session you intend to use.
- For BlueKing/OpenCLI work, do not report login failure based on the generic browser tool; verify with OpenCLI against the user's real Chrome session first.
- If you are still checking or reconnecting tooling, say that explicitly instead of claiming the task is blocked.

## Known page/session

Reference: `references/blueking-demand-task-creation.md` captures the demand-detail → task-creation reconnaissance flow, relevant Vue components, and observed required fields.
Reference: `references/opencli-extension-reconnect.md` captures a verified reconnect pattern when Chrome is logged in but OpenCLI reports the Browser Bridge extension as disconnected.
Reference: `references/blueking-task-detail-and-field-update.md` captures a verified task-detail URL pitfall (`/console/.../twTask/IssueDetail` vs direct `/vteam/.../twTask/IssueDetail`) and the live `instance_value` API flow for editing task deadlines.
Reference: `references/blueking-task-and-manhour-opencli-notes.md` captures verified task-list filter payloads, deadline-update calls, and the direct man-hour plugin API for submitting/reading work-hour records.
Reference: `references/blueking-related-task-create-and-fill.md` captures the verified flow for opening a demand detail page, creating a related task from `AddIssueWin`, resolving required field values, and immediately filling same-day man-hours on the created task.
Reference: `references/blueking-status-transition-detail-quirk.md` captures a verified task-detail state-transition pitfall: after man-hours reach estimate, the detail page may still expose only the current state and empty `nextNodes`, so do not blindly POST status transitions.
Reference: `references/blueking-status-transition-verification.md` captures a verified follow-up rule: empty `nextNodes` only blocks safe automation, not necessarily the business transition itself; always verify the live page status plus `操作日志` before saying the transition failed.
Reference: `references/weekly-report-dws-blueking.md` captures Allen's weekly-report chain: use DWS to find the latest DingTalk report link from 陆建波, then use BlueKing/OpenCLI to collect 本周/下周 work content, with daemon-start diagnostics if OpenCLI fails before page access.
Reference: `references/allen-weekly-report-cli.md` captures the reusable Allen-specific weekly-report CLI integration under `/Users/heytea/Downloads/weekly-report-cli`, including the `weekly-report-allen` fast path, DWS sheet boolean flag pitfall, verification commands, and the API-first future route.
Reference: `references/unified-demand-pipeline-task-workhour.md` captures the reusable class-level architecture for combining demand creation, demand/service pipeline operations, demand-linked tasks, daily 8-hour filling, date-range work-hour aggregation, API/OpenAPI-first adapters, OpenCLI fallback, idempotency, dry-run, and read-back verification.
Reference: `references/bulk-task-plan-reconciliation.md` captures the plan-first workflow for reconciling an existing BlueKing task set against a new screenshot/spreadsheet plan, including semantic matching, task consolidation, cancel-vs-delete handling, total-hour checks, and post-write verification.

- opencli session used successfully: `bk-tw`
- URL pattern: `https://devops-bk.heyteago.com/console/vteam/b1af00/twTask`
- The actual app is often inside `#iframe-box`; JavaScript should use:
- Before page-specific debugging, run `opencli doctor` (and if needed `opencli daemon restart`) to verify the Browser Bridge extension is connected. Treat this as a prerequisite check, not as a permanent limitation of BlueKing automation.
- If Allen says he is already logged in, do not infer logout from the generic browser tool or from a stale opencli state. First verify the real OpenCLI/Chrome session. If the daemon is healthy but the extension is disconnected, use the reconnect pattern in `references/opencli-extension-reconnect.md`, then re-run `opencli doctor` before reporting any blocker.
- If `opencli browser <session> network` returns no entries on a visibly loaded BlueKing page, do not stop there. Fall back to in-page inspection: query `performance.getEntriesByType('resource')` from the iframe window to recover API/resource URLs, then inspect Vue components to locate the real create flow.
- For task detail pages, if `https://devops-bk.heyteago.com/console/vteam/<projectId>/twTask/IssueDetail?...` shows `服务异常，请稍候...` or `重新登录` despite a valid session, retry with the direct app URL `https://devops-bk.heyteago.com/vteam/<projectId>/twTask/IssueDetail?...` before concluding the login is invalid.
- For BlueKing demand/task creation pages built with Vue, inspect the component tree from `__vue__` roots that expose `$store`. The most useful targets found so far are `IssueHome`, `issueDetail`, and `AddIssueWin`.
- To discover whether a demand detail page can create a task, inspect component methods for verbs such as `createTask`, `createBug`, `createSonIssue`, and `addIssue`.
- To prepare a task creation payload before clicking submit, inspect `AddIssueWin.fields`; this reveals required fields and option values such as operator, task type, estimate start/end date, and estimated man-hours.
- If the live BlueKing page is temporarily unavailable but Allen gives demand descriptors (for example: business topic + 所属空间 + a related person such as 创建人/发布人/部署角色), do not stop at the missing browser path. Fall back to local evidence in this order:
  1. Search `~/.opencli/cache/browser-network/*.json` for demand title keywords / issue number / related person.
  2. Search the active workspace for `docs/bk/<需求号>.json` or similar exported demand metadata.
  3. From those local artifacts, verify at least: demand number, title, project/space name, and the related person field actually present in the artifact (`createUser`, `deployRole`, etc.).
  4. In the reply, explicitly say which field matched the user's clue instead of loosely claiming '创建人 matches' when the artifact only proves another role (for example `deployRole.name = 张柳`).

```js
const w = document.querySelector('#iframe-box')?.contentWindow || window;
const d = w.document;
```

## Identify candidate tasks

1. Get today's date from the system, do not guess:

```bash
date '+%Y-%m-%d %u %H:%M:%S %Z'
```

For weekly summaries, compute the current Monday-Sunday range from the date output. Example observed on Thu 2026-06-11: week range is `2026-06-08` through `2026-06-14`.

2. Clarify/obey the user's exact ownership wording:
   - If Allen says **“我的任务”** / “我本人的任务”: use the current user's own executable tasks — assignee/handler/owner (`经办人` / `负责人`, depending on table fields) is the current user, plus active status.
   - If Allen says **“我创建的任务”**: use the top tab/filter `我创建` and do **not** report tasks from the general list or other creators. The table may still show `经办人`; in this context the visible `经办人` is not the ownership criterion unless the user asks for assignee-owned tasks.
   - Filter statuses only if requested. For weekly created-task summaries, include all statuses unless Allen explicitly asks for `待处理/处理中` only.
   - If the visible table still contains unrelated people/tasks after selecting `我创建`, open the `筛选` panel and explicitly inspect/choose `创建人` / `经办人` fields before reporting.

3. Date containment rules:
   - For **today's fill candidates**: `预计开始时间 <= today <= 预计结束时间`.
   - For **this week's created-task summary** as Allen corrected: both `预计开始时间` and `预计结束时间` must be inside the current week range, not merely overlapping the week. Exclude rows where only one side is inside the week.

4. Extract visible table rows from the iframe. Useful fields in the task table:
   - 标题 / task key, e.g. `p35_15972`
   - 状态
   - 经办人
   - 预计开始时间
   - 预计结束时间

A robust inspection command:

```bash
opencli browser bk-tw eval '(()=>{const w=document.querySelector("#iframe-box")?.contentWindow||window; const d=w.document; return {href:w.location.href,text:d.body.innerText.slice(0,7000)};})()'
```

4. Candidate logic:
   - status is `待处理` or `处理中`
   - `预计开始时间 <= today <= 预计结束时间`

5. Report candidates in a table before doing any fill action.

## Workhour assistant panel / injected helper findings

The page may expose a native-looking `工时助手` button/panel, or a previously injected custom floating helper with DOM ids like:

- `heytea-blueking-timesheet-helper`
- `heytea-blueking-timesheet-toggle`

Prefer the direct opencli/DOM workflow over any custom floating helper. To remove/disable the injected helper without affecting the BlueKing app:

```bash
opencli browser bk-tw eval '(()=>{const w=document.querySelector("#iframe-box")?.contentWindow||window; const d=w.document; ["heytea-blueking-timesheet-helper","heytea-blueking-timesheet-toggle"].forEach(id=>d.getElementById(id)?.remove()); const st=d.createElement("style"); st.id="hide-heytea-blueking-timesheet-helper"; st.textContent="#heytea-blueking-timesheet-helper,#heytea-blueking-timesheet-toggle{display:none!important}"; d.documentElement.appendChild(st); return {hasToggle:!!d.getElementById("heytea-blueking-timesheet-toggle"), hiddenStyle:!!d.getElementById("hide-heytea-blueking-timesheet-helper")};})()'
```

Verify it is gone:

```bash
opencli browser bk-tw eval '(()=>{const w=document.querySelector("#iframe-box")?.contentWindow||window; const d=w.document; return {hasPlugin:!!d.getElementById("heytea-blueking-timesheet-helper")||!!d.getElementById("heytea-blueking-timesheet-toggle")};})()'
```

If a `工时助手` panel is present, it can be clicked for exploration only:

```bash
opencli browser bk-tw eval '(()=>{const w=document.querySelector("#iframe-box")?.contentWindow||window; const d=w.document; const btn=[...d.querySelectorAll("button")].find(b=>(b.innerText||"").trim()==="工时助手"); if(!btn) return "no workhour btn"; btn.click(); return {clicked:true,text:btn.innerText};})()'
```

Observed panel fields/buttons:
- `工作日期`
- `默认工时`
- `默认备注`
- `我的名字`
- `读取我的未完成任务`
- `批量提交工时`

Pitfalls:
- The helper may show tasks with `预估 0h`; do not rely on that alone to decide whether the task is complete. Verify task detail/pre-estimated hours and existing workhour total before changing status.
- The top-right keyword search input (`输入关键字回车搜索`) may accept a value but fail to refresh the table when manipulated via JS keyboard events. Do not treat a failed keyword-search refresh as proof the task does not exist; fall back to visible-row extraction, pagination, direct detail URLs if discoverable, or UI clicks.

## Local helper CLI discovered

A reusable opencli wrapper exists locally:

```bash
node /Users/heytea/Documents/new_tools/auto蓝鲸工时/blueking-opencli-workhour.mjs list --date YYYY-MM-DD
node /Users/heytea/Documents/new_tools/auto蓝鲸工时/blueking-opencli-workhour.mjs detail --issue p35_15972
node /Users/heytea/Documents/new_tools/auto蓝鲸工时/blueking-opencli-workhour.mjs submit --issue p35_15972 --hours 8 --content '工作内容' --date YYYY-MM-DD        # dry-run only
node /Users/heytea/Documents/new_tools/auto蓝鲸工时/blueking-opencli-workhour.mjs submit --issue p35_15972 --hours 8 --content '工作内容' --date YYYY-MM-DD --execute
```

The wrapper uses the `bk-tw` opencli browser session and direct in-page `fetch` calls. `submit` is dry-run unless `--execute` is passed. Before using `--execute`, make sure Allen has supplied/approved exact task, date, hours, and content.
- For simple single-field edits on an existing task (for example, moving `预计结束时间`), you do not have to reopen the full edit dialog first. Read the field id from live `detailData.property`, then use the verified `PUT /ms/vteam/api/user/instance_value/<projectId>` flow captured in `references/blueking-task-detail-and-field-update.md`, and finally re-fetch task detail to verify the new value.

Known current behavior: the local wrapper now provides an end-to-end OpenCLI work-hour flow:
- `list --date YYYY-MM-DD` returns unfinished date-matching tasks enriched with `hoursUsed`, `surplusManHour`, `progress`, and same-day records.
- `submit` without `--execute` performs a live dry-run including task resolution, current totals, duplicate detection, and the exact payload.
- `submit --execute` refuses an identical date+hours+content record, submits once, reads the created record back, and when cumulative hours reach the estimate, safely advances through actionable no-required-field nodes to `已完成`.
- All page-context API calls use the verified BlueKing host as a fallback when the OpenCLI-bound page has an opaque/`null` origin, so manual page rebinding is no longer required for these commands.
- If the page plugin dialog is awkward to drive but the user has already given exact task/date/hours/content, you can submit man-hour records through the authenticated teamwork-plugin API directly; payload shape and verification steps are documented in `references/blueking-task-and-manhour-opencli-notes.md`.
- OpenCLI pitfall: a healthy `opencli doctor` does not guarantee the bound page is usable. If `eval` shows `about:blank` or relative `fetch('/ms/...')` fails with `Failed to parse URL`, first reopen/bind the real BlueKing page, then use `w.location.origin + '/ms/...'` absolute URLs for in-page fetch calls instead of bare relative paths.
- Additional page-state recovery pattern observed live: even after reopening, the session may land on `https://devops-bk.heyteago.com/console/platform/entry` (top window, no iframe) instead of the task page. In that state, do not stop and do not claim the session is unusable. If `window.location.origin` is a real BlueKing origin, you can still call the authenticated teamwork-plugin and issue-detail APIs from the top window using `https://devops-bk.heyteago.com/...` absolute URLs; this was sufficient to submit and verify man-hour records successfully.
- Practical fast-path for Allen after he says he has logged in: reopen the BlueKing URL, accept that it may land on `/console/platform/entry`, then use the local wrapper to `list` candidate tasks first. Once Allen gives exact task/hours/content, run wrapper `submit` as dry-run to confirm the resolved issue/estimate, then execute the write via direct absolute-URL teamwork-plugin POST and immediately verify with `GET_MAN_HOUR_RECORD`. This avoids getting stuck on the visible page route while still keeping the operation grounded.
- Response-shape pitfall for man-hour verification: `GET_MAN_HOUR_RECORD` may return the payload under `json.data.result` rather than directly under `json.data`. Parsers should read `const result = json.data?.result || json.data || {}` before extracting `hoursUsed`, `surplusManHour`, and `records`, otherwise you can falsely conclude that today's records are empty right after a successful submission.
- Verification rule for same-day fills: do not assume there was no prior record today. After submission, read back `GET_MAN_HOUR_RECORD` filtered by `jobDate` and confirm the newly created record by `createdTime` / `id`, because multiple records can exist on the same task/date and progress may reach 100% after the new entry.

- If Allen asks for a demand-linked task to be created and, in the same instruction, also wants today's work-hour entry added afterward, treat it as a single authorized workflow. Only pause for genuinely missing required fields (for example, `预估工时(h)` if the template requires it and the user has not provided it). Once the missing field is supplied, continue through create -> verify -> add man-hour -> verify without asking for another confirmation in the middle.
- For demand-linked related-task creation, prefer inspecting the live `AddIssueWin.fields` payload over guessing form requirements from visible labels alone; it reveals the exact required fields, field ids, and option values needed for safe direct submission.
- When verifying the "我创建" task list API after creation, remember the response shape is `data.records.content`; do not incorrectly treat `data.records` as a flat array.

## Default selection workflow for Allen

When Allen says only “填写工时” / “填今天工时” without naming a task, do not ask him to restate the task first. Pull his unfinished candidate tasks and present them for selection.

Default candidate scope:
- tasks created by Allen himself (`创建人 = 戚呈辉` / current user id), unless he explicitly asks for another scope
- unfinished task statuses such as `待处理` / `处理中`
- prioritize tasks whose `预计开始时间 <= today <= 预计结束时间`
- show task key, title, status, estimated hours, used hours, remaining hours, and a suggested work-log sentence

Candidate enrichment is mandatory before asking Allen to choose:
1. Run the task-list query for today's date.
2. For every candidate, call `GET_MAN_HOUR_RECORD` and normalize `json.data?.result || json.data || {}`.
3. Include `estimateManHour`, `hoursUsed`, `surplusManHour`, progress, and any same-day records in the selection view.
4. If multiple candidates exist, ask Allen to select one or explicitly choose a split totaling 8 hours. Do not infer the target merely because one task has exactly 8 remaining hours.
5. If today's identical record already exists, mark it and do not offer it as a fresh submission without explaining the duplicate.

Only after Allen picks a task (or there is genuinely one unambiguous candidate), proceed to submission. Once he supplies the exact task, date, hours, and content, submit directly without a second confirmation, then read back the created record ID, cumulative hours, remaining hours, progress, and final task state.

## Filling workflow after Allen chooses a task

Only after Allen selects a task and gives/approves content:

1. Open the selected task detail.
2. Locate `工时信息`.
3. Read the existing records for the target date before writing. This is mandatory even when the user says “填 8 小时”: a same-day record may already exist from an earlier attempt.
4. Decide the operation from the live totals:
   - If no record exists for the target date, add the requested record.
   - If exactly one same-day record already has the requested hours, do **not** append another record. Treat a new work description as a request to edit/replace that existing record's content.
   - If same-day records already consume the requested hours in aggregate, do not add more; reconcile/edit the existing records or ask Allen how to split them.
   - If appending would make cumulative hours exceed the estimate, stop before writing and report the conflict.
5. For an existing same-day record, use the task detail UI's record-level edit action (`.record-handler` → `#bi-edit-manhour`) rather than submitting a second `ADD_MAN_HOUR_RECORD` payload. Preserve the existing 8-hour amount and date unless Allen explicitly asks to change them.
6. Fill or edit:
   - `工作内容`
   - `工时`
   - `实际工作日期` (defaults to today but may be changed)
7. Before clicking final `确定`, only ask for confirmation if Allen has not already authorized that exact submission. If the current message/workflow already makes the intent clear, submit directly.
8. After submitting, verify success by reading back the live record list/API and confirm the target date, hours, exact content, cumulative totals, remaining hours, progress, and task state.

### Same-day duplicate/replace pitfall

A dry-run that only checks for an *identical* date+hours+content record is not sufficient: a different description with the same date and hours can still be a duplicate. Always inspect all records for the target date first. In the common case where the previous entry should be corrected, edit the existing record and verify its `updateTime`/content rather than adding a new entry.

For Allen's usual “填今天工时” flow, if there is one unambiguous task and he provides the hours plus work content, proceed directly; do not make him repeat the task selection. Use the concise Chinese work description he supplied, preserving numbered items and domain acronyms such as `PDS`.

## Status transition rule

After submitting work hours, always re-query cumulative hours and compare them with the task's estimated hours.

Default rule for Allen:
- if `累计实际工时 < 预估工时`: keep the current task status unchanged;
- if `累计实际工时 >= 预估工时`: treat this as authorization to finish the task and move the status to `已完成`, then verify the final state.
- Guardrail learned in live use: authorization to finish is **not** authorization to guess transition payloads. If the detail page / state API does not surface actionable next-node metadata (for example, it only returns the current state and `nextNodes` stays empty), stop short of posting the transition blindly. Report that work hours are complete and the task is ready to finish, and only continue once the target node data is actually available.
- Verification pitfall learned in live use: if Allen says he already manually changed the status, or asks why a transition "failed", do not trust the earlier automation conclusion. Re-open the live task detail page, read the currently displayed `状态`, then open `操作日志` and verify whether the sequential transitions already succeeded. `nextNodes = []` only means the automation path lacked enough metadata; it does **not** prove BlueKing rejected the business transition.

Follow the allowed sequence:

`待处理 -> 处理中 -> 已完成`

Do not blindly jump over intermediate states in the API. If the current state is `待处理`, advance through the allowed transitions until the task reaches `已完成`; if the UI/API only allows one step at a time, execute the needed steps sequentially and verify after each step. Only stop short of `已完成` if the backend rejects the transition or returns unmet required fields, and then report the exact blocker.

Status API discovered from the app bundle:

```text
GET  /ms/vteam/api/user/issue_direction/{projectId}/{issueId}/state
GET  /ms/vteam/api/user/issue_direction/{projectId}/{issueId}
GET  /ms/vteam/api/user/issue_direction/{projectId}/{issueId}/{nextNodeId}
POST /ms/vteam/api/user/issue_direction/{projectId}/next
```

Important verified correction: for TASK status transitions, `GET /issue_direction/{projectId}/{issueId}` (without `/state`) can return actionable target nodes under `data.data[]`, while `/state` may only return users/roles and no nodes. Use `/state` for user/operator lookup if needed, but use the no-`/state` endpoint to discover valid next nodes.

Verified TASK state ids in project `b1af00`:
- `待处理` = `2ab768be9b814d4fb27d15fcd39ba799`
- `处理中` = `bdbb1506f1e04b76882eaf800cb9946a`
- `已完成` = `3a47f92694ea4d3bbf9b8a434db34be2`
- `取消` = `a393952764c2432a831d5759663cad7a`

The POST payload is produced by the status-box component and was verified live for `待处理 -> 处理中 -> 已完成` with no required fields:

```json
{
  "issueId": "<issue id>",
  "nextNodeId": "<target state node id>",
  "comment": {"atUser": [], "comment": ""},
  "directionFields": [],
  "operators": ["H003919"]
}
```

For Allen/current user, the operator id observed live is `H003919`. If operating for another user, derive it from the current task/user data instead of hard-coding.

Safe direct-flow checklist:
1. Read current state from `GET /ms/vteam/api/user/issue/{projectId}/{issueId}`.
2. Call `GET /ms/vteam/api/user/issue_direction/{projectId}/{issueId}` and confirm the desired target node appears with `operation: true` and `nodeFields` is empty or all required fields can be preserved.
3. POST `/ms/vteam/api/user/issue_direction/{projectId}/next` to `处理中` first; verify detail state became `处理中`.
4. POST the same endpoint to `已完成`; verify detail state became `已完成`.
5. Open `操作日志` and verify records such as `从[待处理]流转到[处理中]` and `从[处理中]流转到[已完成]`.

Do not hand-roll a status transition if the target node is not returned by `GET /issue_direction/{projectId}/{issueId}` or it contains required `nodeFields` you cannot safely fill.

## API/network findings

- The task table data is loaded by:

```text
POST https://devops-bk.heyteago.com/ms/vteam/api/user/issue/b1af00/table/TASK?num=1&size=100&remember=true
```

OpenCLI can inspect the cached response after table/filter loading:

```bash
opencli browser bk-tw network --detail 'POST devops-bk.heyteago.com/ms/vteam/api/user/issue/b1af00/table/TASK' --max-body 30000
```

Relevant response fields under each `data.records.content[].property`:
- `id.value` = issue id used by detail URL
- `number.displayValue` = task key, e.g. `p35_15972`
- `title.displayValue`
- `state.displayValue`
- `operator_user.displayValue`
- `estimate_start_time.displayValue`
- `estimate_end_time.displayValue`

Observed after filtering Allen/戚呈辉 active tasks: records may include future rows too; still apply the local date containment rule before reporting candidates.

### Verified list-filter payloads

For task-list reads, the POST body is the search-condition array. A reliable verified filter for **我创建** is:

```json
[{"name":"relation","value":["CREATED"]}]
```

This can be called directly in the page context:

```js
fetch('/ms/vteam/api/user/issue/b1af00/table/TASK?num=1&size=100&remember=true', {
  method: 'POST',
  credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify([{name:'relation', value:['CREATED']}])
})
```

Use this when Allen asks for "我创建的任务" bulk inspection or batch date adjustments.

### Verified dynamic-field update API

For editable dynamic fields such as `预计结束时间`, BlueKing uses:

```text
PUT /ms/vteam/api/user/instance_value/{projectId}
```

Payload shape:

```json
{
  "issueId": "<issue id>",
  "fieldId": "<field id>",
  "value": "<new value>"
}
```

Verified field id for `预计结束时间` in `智慧门店` task flow:
- `32593c53f5ca48efa593eb9dac5a14f4`

Example:

```json
{
  "issueId": "7e0cf36adb6b4bd18305695be687e5f6",
  "fieldId": "32593c53f5ca48efa593eb9dac5a14f4",
  "value": "2026-07-05"
}
```

Use this for one-by-one deadline adjustments after you have enumerated the target task IDs from the list API.

### Start/end date update ordering pitfall

BlueKing validates the date interval after **each individual field write**. When moving both dates forward, writing the new start first can fail with `预计开始时间不能大于预计结束时间` because the old end date is still present. Use an order that keeps every intermediate interval valid:
- moving the whole interval forward: update **end first, then start**;
- moving the whole interval backward: update **start first, then end**;
- mixed/overlapping changes: read the current values and choose the first write so `start <= end` remains true after each request.

A rejected first write does not prove partial success or failure. Re-fetch the task, apply the safe order, then independently verify both dates plus title, hours, state, and owner.

## OpenCLI session recovery pitfall

Do **not** stop at a first `opencli doctor` message that says the extension is disconnected, and do **not** tell Allen the task is blocked until you have retried actual OpenCLI recovery.

Verified recovery pattern when Chrome is already running and the OpenCLI extension is installed but not attached to the daemon:

1. Check `opencli doctor`.
2. If daemon is running but extension is disconnected, open the extension popup page in Chrome:
   ```bash
   open -a 'Google Chrome' 'chrome-extension://ildkmabpimmkaediidaifkhjpohdnifk/popup.html'
   ```
3. Re-run `opencli doctor`.
4. If it now shows `Extension: connected`, proceed with `opencli browser ...` normally.

Workflow rule for Allen: when he explicitly says to use OpenCLI, prefer **trying the recovery and re-checking live state** over speculating that the session is unavailable.

## User-style pitfall

Allen strongly prefers **verified statements over speculative blockers**. For BlueKing/OpenCLI tasks:
- do not say "cannot create" or "not logged in" unless you have just verified it in the live OpenCLI/Chrome path you intend to use;
- if one access path fails (for example headless browser or stale OpenCLI session), try the in-scope recovery path first and then report the verified result;
- when correcting previously shifted dates, compute the user's intended **final target** rather than blindly adding another offset on top of a prior intermediate adjustment.

## Useful DOM inspection snippets

List visible buttons, inputs, dialogs, and table-like elements:

```bash
opencli browser bk-tw eval '(()=>{const w=document.querySelector("#iframe-box")?.contentWindow||window; const d=w.document; const elems=[...d.querySelectorAll("button,input,textarea,[contenteditable=true],.bk-dialog,.bk-modal,.el-dialog,.bk-form,.bk-form-item,.bk-select,.bk-date-picker,.bk-table,.el-table")].map((e,i)=>{const r=e.getBoundingClientRect();return {i,tag:e.tagName,txt:(e.innerText||e.value||e.placeholder||e.getAttribute("title")||"").trim().slice(0,300),cls:String(e.className).slice(0,160),rect:{x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)},visible:r.width>0&&r.height>0&&getComputedStyle(e).visibility!=="hidden"};}).filter(x=>x.visible||x.txt); return {href:w.location.href,body:d.body.innerText.slice(-3000),elems};})()'
```

Inspect a specific row by task key:

```bash
opencli browser bk-tw eval '(()=>{const key="p35_15972"; const w=document.querySelector("#iframe-box")?.contentWindow||window; const d=w.document; const row=[...d.querySelectorAll("tr")].find(tr=>tr.innerText.includes(key)); if(!row) return "row not found"; return [...row.querySelectorAll("a,span,div,td")].map((e,i)=>({i,tag:e.tagName,txt:(e.innerText||e.textContent||"").trim().slice(0,160),cls:String(e.className).slice(0,160),href:e.href||e.getAttribute("href"),cursor:getComputedStyle(e).cursor}));})()'
```

## Output format

Prefer Chinese and table output for Allen. Default response structure is **结论 → 关键依据 → 建议/下一步**. Keep paragraphs focused; avoid long flat prose. Use a Markdown table when there are 3 or more comparable tasks, records, states, risks, or verification points. For troubleshooting, use **当前判断 → 已确认事实 → 根因/可能原因 → 下一步**. If Allen explicitly requests raw logs, full details, a transcript, pure code, SQL, curl, JSON, or another exact format, follow that format instead.

- First: date or week range used for filtering.
- Then: candidate task table.
- Include a `建议填写的工作内容` column when Allen asks to “找到其中我让你写的工作内容”. Derive it from the task title as a concise work-log sentence, e.g. title `磐石-手动插入税率编码的功能和审核通过的确认逻辑` -> `磐石税率编码手动插入功能开发，补充审核通过后的确认逻辑处理与联调验证`.
- Add an exclusion/notes table when useful, especially for rows excluded because only start or end date falls in the week.
- For a completed fill, report whether the action was an **新增** or an **编辑已有记录**, and include the verified date, hours, exact content, cumulative hours, remaining hours, progress, and final task state.
- Add a final note that no submission/status change was performed unless actually authorized and verified.
