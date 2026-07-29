---
name: blueking-task-management
description: 'Use when the user explicitly needs the blueking-task-management workflow: Manage BlueKing/敏捷协同 tasks through OpenCLI or verified API calls: list Allen''s tasks, inspect unfinished work, bulk adjust dates, and verify task-field changes without touching work hours or state unless explicitly requested.'
license: MIT
---

# BlueKing Task Management

Use this class-level skill for BlueKing / 敏捷协同 task-list and task-field operations, including task inspection, schedule fields, and fallback work-hour filling when no dedicated work-hour skill is available.

Prefer the existing `blueking-workhour-opencli` skill for work-hour submission if it exists. If it is missing or unavailable, this skill owns the fallback workflow: list Allen's unfinished tasks, choose the task according to Allen's daily work-hour preference, add man-hour records through the BlueKing man-hour plugin, then re-read and finish the task when estimated hours are full. Use this skill when the task is about **listing tasks, distinguishing ownership filters, changing task fields, bulk adjusting schedules, or fallback work-hour filling**.

Session-specific work-hour fallback notes live in `references/workhour-fallback.md`. Load them when `blueking-workhour-opencli` is unavailable or when using the local `weekly-report-cli` BlueKing helper.

## Safety

- Read-only listing and inspection can be done directly.
- Field changes such as expected start/end date require an explicit user instruction that identifies the scope and intended change.
- Do not submit work hours, change task state, cancel tasks, delete tasks, or edit titles unless the user explicitly asks for that specific action.
- After any write, re-fetch the task detail and report verified before/after values.

## Ownership filters

For Allen's normal wording:

| User wording | BlueKing filter |
|---|---|
| `我的任务` / `我未完成的任务` / executable tasks | `operator_user = H003919` |
| `我创建的任务` | `relation = CREATED` |

Do not confuse these two. `relation=CREATED` returns tasks created by Allen; it is not the same as current handler/operator ownership.

Verified incomplete state IDs in project `b1af00`:

```text
待处理 = 2ab768be9b814d4fb27d15fcd39ba799
处理中/observed active = 766ec13ac2ef482bb72ad9e9d6a1cd17
处理中/observed active = bdbb1506f1e04b76882eaf800cb9946a
```

## Daily work-hour filling fallback

Use this when Allen says `填一下工时` / `填今天工时` and no dedicated `blueking-workhour-opencli` skill is available.

## Read-only work-hour check

Use this when Allen asks `昨天的工时填了没有` / `看下某天工时填没填` / `查工时`.

1. Check the live date/time first and resolve relative dates such as `昨天` to `YYYY-MM-DD` in Asia/Shanghai.
2. This is read-only unless Allen explicitly asks to fill/submit. Do not add worklogs or transition states while checking.
3. Prefer checking all Allen executable tasks with `operator_user = H003919` and **no incomplete-state filter** when verifying a past date, because the task with yesterday's worklog may already be `已完成` and disappear from unfinished-only queries.
4. If the local `bk` helper cannot run because `bk-rush` is unavailable, reuse the existing BlueKing browser session with OpenCLI page-context `fetch(..., {credentials: 'include'})`; do not ask Allen to re-login if page-context API calls already return status 200.
5. For each fetched task, call the man-hour plugin `GET_MAN_HOUR_RECORD`, filter records by the target `jobDate`, sum `manHour`, and report: date, total hours, task number/title, work content, task state, used/surplus/progress.
6. Explicitly state that the check made no writes.

1. Check the current date with `date`; Allen's default is to fill the current workday to 8h.
2. Query Allen's executable unfinished tasks with `operator_user = H003919` and the incomplete states listed below; do **not** use `relation=CREATED` for this.
3. Re-read candidate task man-hour state through the BlueKing man-hour plugin:

```text
POST /ms/teamworkplugin/api/user/plugin/projects/<project>/plugins/man-hour/versions/5.1.0?issueId=<issueId>
body: {"param":"{\"method\":\"GET_MAN_HOUR_RECORD\"}"}
```

4. Choose the task by Allen's standing preference: fill 8h/day, prefer already-started/currently-due task with exactly enough remaining hours, and when estimated hours become full, finish the task automatically and include its link in the report.
5. Add worklog idempotently: if a record already exists for the same `jobDate` + `jobContent` + `manHour`, skip instead of duplicating.

```text
POST /ms/teamworkplugin/api/user/plugin/projects/<project>/plugins/man-hour/versions/5.1.0?issueId=<issueId>
body.param = {
  "method":"ADD_MAN_HOUR_RECORD",
  "manHour": {"jobContent":"<content>", "manHour":"8.0", "jobDate":"YYYY-MM-DD", "surplusManHour": null}
}
```

6. Re-read man-hour state and verify `hoursUsed`, `surplusManHour`, `progress`, and worklog records.
7. If the task's estimated hours are now full (`surplusManHour <= 0` or `hoursUsed >= estimateManHour`), finish it by walking workflow directions:
   - read `GET /ms/vteam/api/user/issue_direction/<project>/<issueId>`;
   - prefer flow `Backlog → 待处理 → 处理中 → 已完成`;
   - POST each transition to `/ms/vteam/api/user/issue_direction/<project>/next` with `operators: [H003919]`.
8. Re-query unfinished tasks to prove the completed task disappeared from Allen's unfinished list.

### OpenCLI/browser fallback when API cookie helpers fail

If `bk-rush` is missing or `sso-login` HTTP cookie refresh fails, do not stop if the user has a live BlueKing browser session. Open/bind `bk-tw` to `https://devops-bk.heyteago.com/console/vteam/b1af00/twTask`, then run `opencli browser bk-tw eval` with page-context `fetch(..., {credentials: 'include'})`. This reuses the browser login and can call the same BlueKing endpoints above without extracting cookies. Keep the JS deterministic and return JSON with before/action/final verification.

See `references/2026-07-workhour-opencli-fallback.md` for a compact example and pitfalls.

## Bulk unfinished task date shift

When Allen asks to shift all unfinished tasks by N days except some task keys:

1. Open/recover OpenCLI session `bk-tw` and load:
   `https://devops-bk.heyteago.com/console/vteam/b1af00/twTask`
2. Query unfinished tasks with:

```json
[
  {"name":"operator_user","value":["H003919"]},
  {"name":"state","value":[
    "766ec13ac2ef482bb72ad9e9d6a1cd17",
    "2ab768be9b814d4fb27d15fcd39ba799",
    "bdbb1506f1e04b76882eaf800cb9946a"
  ]}
]
```

Endpoint:

```text
POST /ms/vteam/api/user/issue/b1af00/table/TASK?num=1&size=500&remember=true
```

3. Exclude task keys the user says should remain unchanged.
4. For each target, re-fetch task detail:

```text
GET /ms/vteam/api/user/issue/b1af00/<issueId>
```

5. Read live field IDs when available. Verified fallback IDs:

```text
estimate_start_time = 0806a668bfbf42a298196d41eab58265
estimate_end_time   = 32593c53f5ca48efa593eb9dac5a14f4
```

6. Update dynamic fields through:

```text
PUT /ms/vteam/api/user/instance_value/b1af00
```

Payload:

```json
{"issueId":"<issueId>","fieldId":"<fieldId>","value":"YYYY-MM-DD"}
```

7. Preserve interval validity after each individual write:
   - moving both dates forward: update **end first**, then start;
   - moving both dates backward: update **start first**, then end.
8. Re-fetch every changed task and verify exact start/end values.
9. Re-query unfinished tasks and report the final schedule.

## Reporting format

Use Chinese and tables for Allen:

1. 结论: total targets, exclusions, verified count.
2. 已更新任务: task key, old start/end, new start/end, verification.
3. 保持不变: excluded task keys and dates.
4. 当前未完成任务时间表.

Explicitly state when no work hours or state transitions were changed.
