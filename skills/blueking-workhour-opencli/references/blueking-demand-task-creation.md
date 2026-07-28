# BlueKing demand -> task creation reconnaissance

Session finding captured from exploring BlueKing demand detail pages with opencli.

## Target page pattern
- Demand detail URL example:
  `https://devops-bk.heyteago.com/console/vteam/yc9e25/twDemand/IssueDetail?vmode=table&id=<issueId>`
- Inner app URL example after iframe load:
  `https://devops-bk.heyteago.com/vteam/yc9e25/twDemand/IssueDetail?vmode=table&id=<issueId>`

## Useful API/resource clues recovered from iframe `performance` entries
- `https://devops-bk.heyteago.com/ms/vteam/api/user/issue/yc9e25/table/TASK?num=1&size=100&remember=true`
- `https://devops-bk.heyteago.com/ms/vteam/api/user/project_switch/yc9e25/hidden`

These were found even when `opencli browser <session> network` returned `count: 0`.

## Vue components that matter
From the iframe component tree (`__vue__` root with `$store`):

- `IssueHome`
  - refs include `addIssue`
  - methods include `addIssue`, `createOtherIssue`
- `issueDetail`
  - methods include `createTask`, `createBug`, `createSonIssue`, `copyIssue`, `dispatchDemand`
  - `issueId` on the inspected page matched the demand id
- `AddIssueWin`
  - exposes `fields`, `issue`, `issueTypeList`, `typeMenu`, `priorityMenu`
  - can be inspected before submission to learn required fields

## Task creation dialog fields observed
On a task-creation dialog opened from demand detail, required fields included:
- 经办人 (`operator_user`, type `USER`)
- 任务类型 (`SELECT`)
- 预计开始时间 (`estimate_start_time`, type `DATE`)
- 预计结束时间 (`estimate_end_time`, type `DATE`)
- 预估工时(h) (`estimate_man_hour`, type `NUMERICAL`)

Observed task type options included:
- 需求会议/需求消化
- 技术方案设计
- 代码开发
- 研发自测
- 跟测

## Notes
- Demand detail pages can expose `haveTask: true` while still allowing task creation flows via component methods.
- Use this reference to prepare field/value extraction before attempting automation that clicks or submits the dialog.
