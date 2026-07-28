# BlueKing status transition detail-page quirk

Observed on 2026-07-07 while handling task `p35_17070` after work-hour submission reached the estimated 20h.

## Verified state before transition attempt
- Task detail URL worked: `https://devops-bk.heyteago.com/vteam/b1af00/twTask/IssueDetail?vmode=table&id=c4334c11e9a5409e8a823d9ff5174db7`
- Task state shown on page: `待处理`
- Estimated hours: `20.00`
- Man-hour plugin readback after submission:
  - `hoursUsed = 20`
  - `surplusManHour = 0`

## What the detail page exposed
From the `issueDetail` component, `detailData.property.state` provided the current state field:

```json
{
  "id": "109757585",
  "label": "状态",
  "name": "state",
  "displayValue": "待处理",
  "value": "2ab768be9b814d4fb27d15fcd39ba799"
}
```

A page component with methods like `changeState`, `submitData`, `cancel` prepared this form data after calling `changeState()`:

```json
{
  "issueId": "c4334c11e9a5409e8a823d9ff5174db7",
  "nextNodeId": "2ab768be9b814d4fb27d15fcd39ba799",
  "operators": ["H003919"],
  "comment": "",
  "directionFields": [],
  "nextNodeName": "待处理"
}
```

Important: this was only the CURRENT state, not a discovered target state.

## What the state API returned
Calling:

```text
GET /ms/vteam/api/user/issue_direction/b1af00/c4334c11e9a5409e8a823d9ff5174db7/state
```

returned only top-level keys like:
- `users`
- `roles`

It did **not** expose actionable next-node metadata in this session.

## Practical lesson
Do not blindly POST `/ms/vteam/api/user/issue_direction/{projectId}/next` just because cumulative hours reached or exceeded the estimate.

Before attempting auto-completion, verify that you have at least one of:
1. explicit next-node metadata from the live page or API, or
2. a populated transition form produced by the page that clearly identifies the target node beyond the current state.

If the detail route only yields the current state id/name and empty `nextNodes`, stop short of auto-transition, report that work hours are complete and the task is ready to finish, and avoid speculative status writes.

## Safe reporting pattern
- Confirm man-hour submission success.
- Confirm cumulative hours reached estimate.
- Say the task is ready for completion.
- Only claim status transition success after reading back the task state from BlueKing.
