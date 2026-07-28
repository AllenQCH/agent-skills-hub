# BlueKing status transition verification after manual/UI completion

Session lesson: when investigating whether a BlueKing task status transition "failed", do not rely only on the automation path that tried to fetch `nextNodes` from the detail-page status component.

## Verified live case

Task: `p35_17070`

Observed facts from the live task detail page:
- Current visible status on the page: `已完成`
- Operation log showed successful sequential transitions by the same user:
  - `2026-07-07 17:35:41` — `从[待处理]流转到[处理中]`
  - `2026-07-07 17:35:44` — `从[处理中]流转到[已完成]`

This proved the business transition succeeded even though an earlier automation inspection had concluded the detail component was blocked because:
- `formData.nextNodeId` still reflected the current state node
- `nextNodes` came back empty
- the component did not surface actionable next-node metadata for safe POST construction

## Durable workflow lesson

When Allen asks why a transition "failed" or says he manually changed it himself:

1. Re-open the actual task detail page in the live OpenCLI/Chrome session.
2. Read the currently displayed status from the page.
3. Click/open `操作日志` and extract transition records.
4. Only then conclude whether the transition truly failed, partially succeeded, or actually completed manually.

## Interpretation rule

- `nextNodes = []` or missing next-node metadata means **your automation path is not ready to submit safely**.
- It does **not** prove the task is non-transitionable or that the backend rejected the transition.
- If the page and logs show the state already changed, report that the task transition succeeded and that the blocker was only in the automation/introspection path.

## Reporting rule

Use wording like:
- `业务侧已成功流转；卡点在自动化没拿到下一状态节点数据。`

Avoid wording like:
- `蓝鲸流转失败`

unless you have verified an actual backend/UI rejection in the live page state or operation logs.

## Practical implication for future automation

Before attempting a direct status POST after work-hour completion:
- trigger/init the status panel,
- fetch actionable next-node/required-field data if available,
- but if metadata still looks incomplete, fall back to **state + operation-log verification** instead of overclaiming failure.
