# 2026-07 work-hour OpenCLI fallback

## When to use

Use this reference from `blueking-task-management` when Allen asks to fill BlueKing work hours but the normal API-cookie route is unavailable, for example:

- `bk-rush is not installed or not configured`;
- `sso-login` HTTP refresh reports expired SSO credentials;
- DWS/other unrelated auth state is unavailable but BlueKing is already open in Chrome.

Do not encode the transient failure as a permanent rule. The durable lesson is: if a live BlueKing page is logged in, OpenCLI page-context `fetch(..., {credentials: 'include'})` can perform the same verified API workflow.

## Stable browser session

Use the stable session name `bk-tw` and the task table URL:

```bash
opencli browser bk-tw open 'https://devops-bk.heyteago.com/console/vteam/b1af00/twTask'
opencli browser bk-tw wait time 5
opencli browser bk-tw state
```

If the page lands on SSO, ask Allen to complete login, then reopen the same BlueKing URL and verify the title is `蓝鲸DevOps平台`.

## List Allen's unfinished executable tasks

Run in page context:

```js
async () => {
  const filters = [
    {name: 'operator_user', value: ['H003919']},
    {name: 'state', value: [
      '766ec13ac2ef482bb72ad9e9d6a1cd17',
      '2ab768be9b814d4fb27d15fcd39ba799',
      'bdbb1506f1e04b76882eaf800cb9946a'
    ]}
  ];
  const res = await fetch('/ms/vteam/api/user/issue/b1af00/table/TASK?num=1&size=100&remember=false&sort_by=estimate_start_time&order_by=ASC', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    credentials: 'include',
    body: JSON.stringify(filters)
  });
  const data = await res.json();
  function d(p,k){ const v=p&&p[k]; return v ? (v.displayValue ?? v.value ?? null) : null; }
  function v(p,k){ const x=p&&p[k]; return x ? (x.value ?? null) : null; }
  return (data?.data?.records?.content || []).map(it => {
    const p = it.property || {};
    return {
      id: v(p,'id'),
      number: d(p,'number'),
      title: d(p,'title'),
      state: d(p,'state'),
      start: d(p,'estimate_start_time'),
      end: d(p,'estimate_end_time'),
      estimateHours: d(p,'estimate_man_hour'),
      operator: d(p,'operator_user'),
      url: location.origin + `/console/vteam/b1af00/twTask/IssueDetail?vmode=table&id=${v(p,'id')}`
    };
  });
}
```

## Man-hour plugin endpoints

All calls are page-context `fetch` with `credentials: 'include'`.

```text
POST /ms/teamworkplugin/api/user/plugin/projects/b1af00/plugins/man-hour/versions/5.1.0?issueId=<issueId>
```

Read:

```json
{"param":"{\"method\":\"GET_MAN_HOUR_RECORD\"}"}
```

Add:

```json
{
  "param": "{\"method\":\"ADD_MAN_HOUR_RECORD\",\"manHour\":{\"jobContent\":\"了解 diy配方模块的知识点\",\"manHour\":\"8.0\",\"jobDate\":\"2026-07-28\",\"surplusManHour\":null}}"
}
```

Normalize records by reading `jobDate`, `jobContent`, `manHour`, and `id`. Before adding, check for an exact duplicate on same date/content/hour.

## Finish task when estimated hours are full

After adding work hours, re-read man-hour state. If `hoursUsed >= estimateManHour` or `surplusManHour <= 0`, walk workflow directions:

```text
GET  /ms/vteam/api/user/issue_direction/b1af00/<issueId>
POST /ms/vteam/api/user/issue_direction/b1af00/next
```

Transition body:

```json
{
  "issueId": "<issueId>",
  "nextNodeId": "<direction.id>",
  "comment": {"atUser": [], "comment": ""},
  "directionFields": [],
  "operators": ["H003919"]
}
```

Prefer direction order: `Backlog → 待处理 → 处理中 → 已完成`. Stop when final state is `已完成`; detect loops.

## Report shape for Allen

Use a concise Chinese summary with tables:

1. 工时填写 row: task link, date, hours, content, result.
2. Verification row: before/after `hoursUsed`, `surplusHours`, `progress`, `state`.
3. Workflow row if transitioned, e.g. `待处理 → 处理中 → 已完成`.
4. Re-query unfinished tasks and state whether the completed task disappeared.

## Pitfalls

- Do not confuse `operator_user=H003919` with `relation=CREATED`.
- Do not report success until the final man-hour state and final issue state are re-read.
- Do not add duplicate worklog records; exact same date/content/hour should be skipped.
- If SSO login is required, ask Allen to finish the browser login. Once the browser page is authenticated, page-context fetch is usually enough; no need to extract cookies.
