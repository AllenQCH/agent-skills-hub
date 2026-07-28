# BlueKing demand detail → related task creation → same-day man-hour fill

Verified on `devops-bk.heyteago.com` with the authenticated `opencli` browser session.

## When this flow applies

Use when Allen drops a BlueKing demand-detail URL and says to create a task under that demand, optionally followed by same-day work-hour filling.

## Demand-detail page findings

Demand detail page used successfully:

```text
https://devops-bk.heyteago.com/console/vteam/<projectId>/twDemand/demand/IssueDetail?vmode=table&id=<demandId>
```

Observed working example:
- `projectId = yc9e25`
- demand id `e6195623e62d4438a30f1e59bd443b34`
- demand number `p45_7127`

Useful Vue targets from the iframe app tree:
- `issueDetail`
- `AddIssueWin`

The demand detail component exposed a callable `createTask` path that opened the related-task creation dialog.

## Related-task creation dialog

`AddIssueWin.fields` exposed the real required fields for this template:
- `经办人` (`fieldId = f29e34f0a0ad48a1a37f394135f9872f`, type `USER`)
- `任务类型` (`fieldId = f0481eab24094a3da81a85c062edb07c`, type `RADIO/SELECT` depending on UI wrapper)
- `预计开始时间` (`fieldId = 0806a668bfbf42a298196d41eab58265`)
- `预计结束时间` (`fieldId = 32593c53f5ca48efa593eb9dac5a14f4`)
- `预估工时(h)` (`fieldId = 642ef8e5e3d7424dbbb7b71b4f336d59`)

Template metadata was returned by:

```text
GET /ms/vteam/api/user/issue_template/<projectId>/b3daba4bc7ed4ad18bf31e030e98e0eb
```

Observed template name:
- `灵感之茶任务模板`

## Discovering task-type option values

Task-type options were fetched successfully from:

```text
GET /ms/vteam/api/user/issue_field_value/<projectId>/option/f0481eab24094a3da81a85c062edb07c?all=false&classify=TASK
```

Observed useful values:
- `代码开发` = `zrwFGCeXgR`
- `技术方案设计` = `tphrnMBv61`
- `研发自测` = `xDYigbmOV9`

## Handler / assignee lookup

The live field options in `经办人.values` exposed valid user ids. Observed example:
- `戚呈辉` = `H003919`

## Actual create API

The dialog submit eventually posted to:

```text
POST /ms/vteam/api/user/issue/<projectId>
```

Observed successful request characteristics:
- `relationIssue` carried the source demand id
- `typeClassify` became `TASK`
- `instanceValue` carried the required dynamic-field values

Observed successful response:
- task id `bb2c9fd8aa214fbaa74856394bed8bc1`
- task number `p45_7128`
- state `待处理`

## Verification after create

Reliable verification paths used successfully:

1. Open task detail using the direct app route:

```text
https://devops-bk.heyteago.com/vteam/<projectId>/twTask/IssueDetail?vmode=table&id=<taskId>
```

2. Confirm visible fields on the task detail page:
- 编号
- 经办人
- 任务类型
- 预计开始时间
- 预计结束时间
- 预估工时(h)

3. Optionally verify from the created-task list API:

```text
POST /ms/vteam/api/user/issue/<projectId>/table/TASK?num=1&size=100&remember=true
Body: [{"name":"relation","value":["CREATED"]}]
```

Note: the response shape is `data.records.content`, not a plain array.

## Console-vs-direct task route pitfall

For the newly created task, the `console/.../task/IssueDetail` route dropped to the project home page.
The direct route worked:

```text
https://devops-bk.heyteago.com/vteam/<projectId>/twTask/IssueDetail?vmode=table&id=<taskId>
```

## Same-day man-hour fast path

Once the exact task/date/hours/content are authorized, use the direct plugin API instead of struggling with the visible dialog.

### Read current records

```text
POST /ms/teamworkplugin/api/user/plugin/projects/<projectId>/plugins/man-hour/versions/5.1.0?issueId=<taskId>
Body: {"param":"{\"method\":\"GET_MAN_HOUR_RECORD\"}"}
```

Observed pre-fill result on the new task:
- `estimateManHour = 4`
- `hoursUsed = 0`
- `surplusManHour = 4`
- `records = []`

### Add record

```json
{
  "param": "{\"method\":\"ADD_MAN_HOUR_RECORD\",\"manHour\":{\"jobContent\":\"处理海外门店15笔待收货单的问题\",\"jobDate\":\"2026-07-02\",\"manHour\":4,\"surplusManHour\":null}}"
}
```

Observed success shape:

```json
{"status":0,"data":{"result":true},"code":0}
```

### Verify after add

Re-read `GET_MAN_HOUR_RECORD` and confirm:
- `hoursUsed = 4`
- `surplusManHour = 0`
- `progress = 100`
- a new record exists with:
  - `id = 81891`
  - `jobDate = 2026-07-02`
  - `jobContent = 处理海外门店15笔待收货单的问题`
  - `manHour = 4`

## Practical rule learned

If Allen gives only one missing required field (for example `预估工时`), ask only for that missing field, then perform both operations in one pass:
1. create the related task
2. verify the created task page/fields
3. add the requested same-day man-hour record
4. verify the post-fill totals

Do not stop after task creation if the user already asked for the work-hour entry too.

## Duplicate-create pitfall and recovery

- When setting `AddIssueWin.fields` programmatically before invoking `comfirm()`, keep numerical field values such as `预估工时(h)` as strings (for example `"16"`). Passing a JavaScript number can fail client-side with `TypeError: n.trim is not a function` before submission.
- Use exactly one submission path. Do **not** call the Vue `AddIssueWin.comfirm()` method and then click the visible `确定` button: the method call can create successfully while the dialog remains visible, so the subsequent click creates a duplicate.
- Prefer filling the component fields and clicking the visible `确定` button once. Then verify by querying the created-task list for the exact title and creation time before any retry.
- If an accidental duplicate is created, first try `DELETE /ms/vteam/api/user/issue/<projectId>/<issueId>`. The current user may lack delete permission even for a just-created task.
- When deletion is forbidden, query `GET /ms/vteam/api/user/issue_direction/<projectId>/<issueId>` and, only if the `取消` node is returned with `operation: true` and no required `nodeFields`, transition the duplicate to `取消` via `POST /ms/vteam/api/user/issue_direction/<projectId>/next`. Add an audit comment identifying the retained task number, then read both task details back to verify one remains active and the duplicate is cancelled.