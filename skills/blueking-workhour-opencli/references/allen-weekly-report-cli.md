# Allen 专用周报 CLI 整合记录

Use this as the reusable pattern when Allen asks to make weekly-report filling faster or asks to “用 dws 填周报”.

## Target repo / package

Path observed in session:

```text
/Users/heytea/Downloads/weekly-report-cli
```

The coworker package already contained a generic `weekly-report` CLI. The Allen-specific integration added two practical routes:

```bash
# Current recommended route: DWS + OpenCLI, works without bk-rush
./bin/weekly-report-allen publish --dry-run
./bin/weekly-report-allen publish --yes

# Future route: API-first collector from coworker package, needs bk-rush
./bin/weekly-report-api-allen publish --dry-run
```

## Current recommended flow: `weekly-report-allen`

Implemented entrypoint:

```text
bin/weekly-report-allen
```

Implementation file:

```text
tools/weekly_report/allen_fast_cli.py
```

Behavior:

1. Search DingTalk messages via DWS for keyword `周报`.
2. Select latest `alidocs.dingtalk.com/spreadsheetv2/...` link from sender `陆建波`.
3. Use OpenCLI session `bk-tw` to open/verify BlueKing task page if needed.
4. From the BlueKing page context, call authenticated APIs for `b1af00` created TASK rows and man-hour records.
5. Build three weekly report columns:
   - 本周工作
   - 下周计划
   - 已安排但尚未进入开发的需求
6. Locate `戚呈辉` row with DWS sheet find.
7. Update `B{row}:D{row}` only when `--yes` is passed; default is preview/dry-run.

Important command patterns:

```bash
# Preview this week using latest DingTalk link
./bin/weekly-report-allen publish --dry-run

# Preview fixed week and fixed sheet link
./bin/weekly-report-allen publish \
  --week-start 2026-07-06 \
  --week-end 2026-07-10 \
  --sheet-node 'https://alidocs.dingtalk.com/spreadsheetv2/.../edit?...' \
  --dry-run

# Write after preview looks correct
./bin/weekly-report-allen publish --yes
```

## DWS sheet pitfall fixed

For `dws sheet find`, boolean-like flags must be passed with explicit values, otherwise the CLI can treat the next flag (`--format`) as the value and error with `unknown command "json"`.

Correct:

```bash
dws sheet find \
  --node '<full spreadsheet URL>' \
  --sheet-id '人员维度' \
  --find '戚呈辉' \
  --match-entire-cell true \
  --format json
```

Wrong:

```bash
dws sheet find ... --match-entire-cell --format json
```

## Package fixes that made it runnable

These are durable adaptation patterns for downloaded Python CLI packages:

- Remove macOS quarantine when executable shell wrappers fail with `/usr/bin/env: bad interpreter: Operation not permitted`:

```bash
xattr -dr com.apple.quarantine /Users/heytea/Downloads/weekly-report-cli
```

- Add package markers to avoid a third-party installed `tools` package shadowing local imports:

```text
tools/__init__.py
tools/weekly_report/__init__.py
tools/blueking/__init__.py
```

- Make `bk-rush` imports lazy/guarded in `tools/blueking/bk_cli.py` so unit tests and non-BlueKing code can run even when `~/.skills-manager/skills/bk-rush` is absent. When actual API-first BlueKing access is used, raise a clear setup error explaining `BK_RUSH_SKILL_DIR` / bk-rush is required.

- Install Python deps for original package path when needed:

```bash
python3 -m pip install -r requirements.txt
```

## Verification commands

```bash
cd /Users/heytea/Downloads/weekly-report-cli
python3 -m unittest discover -s tools/weekly_report/tests -p 'test_*.py'
./bin/weekly-report-allen publish --dry-run --week-start 2026-07-06 --week-end 2026-07-10
```

Observed after integration:

```text
Ran 18 tests ... OK
```

Dry-run summary shape to verify:

```json
{
  "status": "preview",
  "sheet": {"row": 11, "range": "B11:D11"},
  "blueking": {"rows": [...]}
}
```

## Speed lesson

The 8-minute manual orchestration was dominated by repeated discovery and page/session checks. The dedicated CLI converts the task to a cached/configured pipeline and reached ~15 seconds in dry-run when the BlueKing OpenCLI page was usable.

Long-term fastest route remains the coworker package's API-first mode (`weekly-report-api-allen`) once bk-rush/Chrome-cookie access is configured, because it avoids OpenCLI page loading and supports concurrent enrichment/history snapshots.
