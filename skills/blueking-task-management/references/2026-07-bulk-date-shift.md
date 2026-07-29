# Session note: shifting Allen's unfinished BlueKing tasks by 5 days

## User request

Allen asked to keep `p35_17708` unchanged and shift every other unfinished task's start/end dates backward by 5 days.

## Verified result

Scope: BlueKing project `b1af00`, `operator_user = H003919` / 戚呈辉, unfinished states only.

- Active tasks before: 12
- Excluded unchanged: `p35_17708`
- Targets shifted: 11
- Verified successful: 11
- Work hours changed: no
- Task states changed: no

## Updated tasks

| Task | Old dates | New dates |
|---|---|---|
| `p35_17376` | 2026-07-20 ~ 2026-07-28 | 2026-07-25 ~ 2026-08-02 |
| `p35_17381` | 2026-07-20 ~ 2026-07-31 | 2026-07-25 ~ 2026-08-05 |
| `p35_17455` | 2026-07-21 ~ 2026-07-29 | 2026-07-26 ~ 2026-08-03 |
| `p35_17456` | 2026-07-21 ~ 2026-07-29 | 2026-07-26 ~ 2026-08-03 |
| `p35_17453` | 2026-07-23 ~ 2026-07-29 | 2026-07-28 ~ 2026-08-03 |
| `p35_17457` | 2026-07-30 ~ 2026-07-31 | 2026-08-04 ~ 2026-08-05 |
| `p35_17458` | 2026-08-03 ~ 2026-08-04 | 2026-08-08 ~ 2026-08-09 |
| `p35_17459` | 2026-08-05 ~ 2026-08-06 | 2026-08-10 ~ 2026-08-11 |
| `p35_17460` | 2026-08-07 ~ 2026-08-10 | 2026-08-12 ~ 2026-08-15 |
| `p35_17463` | 2026-08-17 ~ 2026-08-20 | 2026-08-22 ~ 2026-08-25 |
| `p35_17454` | 2026-08-24 ~ 2026-08-26 | 2026-08-29 ~ 2026-08-31 |

## Unchanged task

| Task | Dates |
|---|---|
| `p35_17708` | 2026-07-27 ~ 2026-07-28 |

## Implementation notes

- The general task-list API can return everyone in the project when no ownership filter is supplied.
- For Allen's unfinished executable tasks, `operator_user=H003919` was the verified ownership filter.
- The existing work-hour wrapper's `list --date` is good for daily work-hour candidates, but not sufficient for listing all unfinished tasks across dates.
- Date changes used `PUT /ms/vteam/api/user/instance_value/b1af00` and then re-read task detail.
- End-first order was used because the shift was forward; this avoided transient invalid intervals.
