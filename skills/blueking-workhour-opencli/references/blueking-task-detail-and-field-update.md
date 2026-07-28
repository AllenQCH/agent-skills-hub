# BlueKing task detail / field-update notes

Captured from live opencli work on BlueKing `devops-bk.heyteago.com`.

## OpenCLI connection recovery when Chrome is already running

Symptom:
- `opencli doctor` shows daemon OK but `Extension: not connected`
- Chrome is running and the OpenCLI extension is installed in the active Chrome profile

Working recovery used in session:
1. Verify Chrome is running and the OpenCLI extension exists in the active profile (`Default/Extensions/ildkmabpimmkaediidaifkhjpohdnifk/...`).
2. Open the extension popup page in Chrome:
   - `open -a 'Google Chrome' 'chrome-extension://ildkmabpimmkaediidaifkhjpohdnifk/popup.html'`
3. Re-run `opencli doctor`
4. Expected result: `Extension: connected (v1.0.20)` and a connected profile id is listed.

Interpretation:
- Do not assume the user is logged out or that opencli is unavailable just because the first `opencli doctor` says the extension is not connected.
- First recover the bridge and verify with `opencli doctor`.

## Demand detail vs task detail URL patterns

Confirmed working demand detail:
- `https://devops-bk.heyteago.com/console/vteam/<projectId>/twDemand/demand/IssueDetail?vmode=table&id=<issueId>`

For task detail, the direct **vteam** URL worked reliably in-session:
- `https://devops-bk.heyteago.com/vteam/<projectId>/twTask/IssueDetail?vmode=table&id=<issueId>`

Observed pitfall:
- The `console/.../twTask/IssueDetail` path returned `服务异常，请稍候... / 重新登录` in this session even though the user was logged in.
- When that happens, try the direct `/vteam/.../twTask/IssueDetail` URL before assuming login failure.

## Updating a single editable task field via API

Confirmed API path from live task-date edit:
- `PUT /ms/vteam/api/user/instance_value/<projectId>`

Payload shape:
```json
{
  "issueId": "<task issue id>",
  "fieldId": "<dynamic field id>",
  "value": "<new value>"
}
```

Example used successfully to move a task deadline:
```json
{
  "issueId": "7e0cf36adb6b4bd18305695be687e5f6",
  "fieldId": "32593c53f5ca48efa593eb9dac5a14f4",
  "value": "2026-07-04"
}
```

Success response observed:
```json
{
  "status": 0,
  "code": 0,
  "data": true
}
```

## Field IDs confirmed on task `p35_15974`

From task detail `detailData.property`:
- `estimate_start_time.fieldId = 0806a668bfbf42a298196d41eab58265`
- `estimate_end_time.fieldId = 32593c53f5ca48efa593eb9dac5a14f4`

Use live page data to re-read field ids before writing; do not hardcode globally unless verified for the same project/template.

## Multi-field date update ordering

BlueKing validates each `instance_value` update immediately against the other currently stored date. When moving a task window forward and the new start date is later than the old end date, updating start first fails with `预计开始时间不能大于预计结束时间`.

Safe ordering:
- Moving the whole window forward: update **end date first**, then start date.
- Moving the whole window backward: update **start date first**, then end date.
- Update estimated hours after both dates, then re-fetch the full task detail and verify all fields together.

## Verification pattern after field update

After the PUT succeeds, re-fetch task detail:
- `GET /ms/vteam/api/user/issue/<projectId>/<issueId>`

Verify the returned property value/displayValue changed as expected before reporting success.

## User-facing reporting lesson

For BlueKing/opencli work, report only what was actually verified in the browser/API. Avoid speculative statements like "you may be logged out" before checking the live opencli/Chrome state.