# BlueKing work-hour fallback notes

Use when Allen explicitly asks to fill BlueKing/敏捷协同 work hours and the dedicated `blueking-workhour-opencli` skill is unavailable.

## Default policy for Allen

- First list Allen's executable unfinished tasks with `operator_user = H003919` and known active states.
- Fill work hours for the current date unless Allen specifies another date.
- Allen's preference: daily work hours should add up to 8h; if a task reaches its estimated hours, finish/close it and include the verified task link in the report.
- Do not create, delete, or edit unrelated tasks while filling work hours.
- Worklog submission is an external write. It is authorized only when Allen explicitly asks to fill/submit work hours.

## Known local helper

A local helper may exist at:

```bash
/Users/heytea/Downloads/weekly-report-cli/bin/bk
```

Useful commands:

```bash
# List executable unfinished tasks
./bin/bk task list \
  --project b1af00 \
  --size 100 \
  --no-default-relation \
  --filters-json '[{"name":"operator_user","value":["H003919"]},{"name":"state","value":["766ec13ac2ef482bb72ad9e9d6a1cd17","2ab768be9b814d4fb27d15fcd39ba799","bdbb1506f1e04b76882eaf800cb9946a"]}]' \
  --sort-by estimate_start_time \
  --order-by ASC \
  --no-remember

# Inspect one task's current man-hour state
./bin/bk worklog list --project b1af00 --id <taskIssueId>

# Add one worklog only
./bin/bk worklog add --project b1af00 --id <taskIssueId> \
  --hours <hours> \
  --work-date YYYY-MM-DD \
  --work-content '<content>'

# Add remaining worklog and transition to completed when appropriate
./bin/bk task finish --project b1af00 --id <taskIssueId> \
  --hours <hours> \
  --work-date YYYY-MM-DD \
  --work-content '<content>' \
  --target-state 已完成
```

## Authentication prerequisites

The helper's API-first mode expects BlueKing cookies via `bk-rush`; if unavailable, use the `sso-login` skill's `get_app_cookies('bk', 'cn')` or OpenCLI/Chrome login state.

If API calls redirect to `account.heytea.com` or return `用户权限验证失败`, do not invent task data. Ask Allen to complete SSO / DingTalk confirmation in Chrome, then retry and verify.

## Verification checklist

After writes:

1. Re-run `worklog list` for each changed task and confirm the new record exists with date/content/hours.
2. If finishing tasks, re-fetch task detail and confirm state is `已完成`.
3. Report a concise table: task number/title, hours added, final used/surplus hours, final state, link.
4. State explicitly that no unrelated task fields were changed.
