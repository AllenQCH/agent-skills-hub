# BlueKing task detail + man-hour via opencli

Session notes from operating BlueKing task pages and the man-hour plugin with an authenticated opencli Chrome session.

## User workflow correction to preserve

When Allen explicitly says to use `opencli`, do not pivot to browser tools or speculate from non-shared login state. Verify the opencli session first, reconnect it if needed, then act and report only what was actually observed.

## OpenCLI reconnection pattern that worked

If `opencli doctor` reports daemon OK but extension not connected, and Chrome plus the OpenCLI extension are already installed, opening the extension popup page in Chrome re-established the bridge:

```bash
open -a 'Google Chrome' 'chrome-extension://ildkmabpimmkaediidaifkhjpohdnifk/popup.html'
opencli doctor
```

Observed result after opening the popup: doctor changed from `Extension: not connected` to `Extension: connected (v1.0.20)`.

## Task detail URL pitfall

For task detail pages, the `vteam` route worked reliably:

```text
https://devops-bk.heyteago.com/vteam/<projectId>/twTask/IssueDetail?vmode=table&id=<issueId>
```

The `console/.../twTask/IssueDetail` form produced a broken page / service-exception response in this session, while the plain `vteam/.../twTask/IssueDetail` route opened the real task detail.

## "我创建" task list API shape

The task list accepted the current filter body directly. After selecting `我创建`, the component state showed:

```json
[{"name":"relation","value":["CREATED"]}]
```

Posting that body to the TASK table endpoint returned the current user's created tasks:

```text
POST /ms/vteam/api/user/issue/<projectId>/table/TASK?num=1&size=100&remember=true
Body: [{"name":"relation","value":["CREATED"]}]
```

Useful fields per row under `property`:
- `id.value`
- `number.displayValue`
- `title.displayValue`
- `state.displayValue`
- `operator_user.displayValue`
- `estimate_start_time.displayValue`
- `estimate_end_time.displayValue`

## Updating task deadline directly

The task end-date field can be updated through the dynamic-field endpoint using the end-date field id:

- field label: `预计结束时间`
- field id observed: `32593c53f5ca48efa593eb9dac5a14f4`

Request pattern:

```text
PUT /ms/vteam/api/user/instance_value/<projectId>
Body: {"issueId":"<taskIssueId>","fieldId":"32593c53f5ca48efa593eb9dac5a14f4","value":"YYYY-MM-DD"}
```

Success shape observed:

```json
{"code":0,"data":true,"status":0}
```

## Man-hour plugin API shape

The task detail page loads a `man-hour-510` Vue component. The visible dialog validation may depend on a rendered form ref, but the underlying plugin API can be called directly once authenticated.

Plugin endpoint:

```text
POST /ms/teamworkplugin/api/user/plugin/projects/<projectId>/plugins/man-hour/versions/5.1.0?issueId=<taskIssueId>
Body: {"param":"<JSON string>"}
```

### Get records

```json
{"method":"GET_MAN_HOUR_RECORD"}
```

Wrap it as:

```json
{"param":"{\"method\":\"GET_MAN_HOUR_RECORD\"}"}
```

### Add a man-hour record

Payload inside `param`:

```json
{
  "method":"ADD_MAN_HOUR_RECORD",
  "manHour":{
    "jobContent":"物料缺失税收编码税率导致可开票订单修复并推送红蓝票",
    "jobDate":"2026-06-24",
    "manHour":8,
    "surplusManHour":null
  }
}
```

Observed success shape:

```json
{"code":0,"data":{"result":true},"status":0}
```

After submitting, re-query `GET_MAN_HOUR_RECORD` and verify:
- `hoursUsed`
- `surplusManHour`
- a new entry in `records[]`

## Remaining-hours rule from plugin implementation

The plugin form supports two modes for remaining hours:
- automatic calculation via `surplusManHour = null`
- manual override via a numeric value

For ordinary daily filling, use auto-calculation unless Allen explicitly wants a manual remaining-hours number.
