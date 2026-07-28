# Gaia attendance calendar export via OpenCLI

Session-derived workflow for整理 Gaia Portal / WFM attendance calendar data over a long date range.

## When to use

Use when Allen asks to整理/导出 Gaia Portal 考勤 over a month or multi-month period, especially from `portal-hw.gaiaworkforce.com/#/`.

## Key discovery

The attendance calendar iframe may reject plain browser `fetch()` with `签名失败` because Gaia gateway requires nonce/time/signature headers. However, the frontend already has a signed Ajax wrapper exposed through the loaded webpack modules.

In the attendance calendar iframe (`card-attendanceCalendar`, commonly frame index 4 after opening the portal homepage), bootstrap webpack require and call Pandora Ajax instead of raw fetch:

```bash
opencli browser gaia-att eval --frame 4 '(()=>{window.webpackChunkwfm4_integration.push([[Math.random()],{},function(req){window.__wfm_req=req;}]); return {ok:!!window.__wfm_req, modules:Object.keys(window.__wfm_req?.m||{}).length};})()'

opencli browser gaia-att eval --frame 4 '(async()=>{const p=window.__wfm_req("ZffG"); const data=await p.ajax.loadable.get("/dashboard/attendance-calendar",{startDate:"2024-07-01",endDate:"2025-03-31"}); return {count:data.length, first:data[0]?.date,last:data.at(-1)?.date,sample:data.slice(0,2)};})()'
```

This returns an array of day objects such as:

```json
{
  "date": "2024-07-01",
  "dateType": 1,
  "shift": {
    "timeClassName": "职能标准班1 09:00-18:00",
    "cardList": [{"start":"09:59","end":"22:32"}]
  },
  "payCodeList": []
}
```

## Export pattern

1. Open and verify Gaia homepage:
   ```bash
   opencli browser gaia-att open 'https://portal-hw.gaiaworkforce.com/#/'
   opencli browser gaia-att state
   opencli browser gaia-att frames
   ```
2. Inspect the attendance frame. Look for `#/attendance/attendance-calendar`.
3. Use the webpack `ZffG` module Ajax wrapper to retrieve the desired range.
4. Save raw JSON to `/tmp/gaia_attendance_<range>.raw.json`.
5. Process into Excel/CSV with these sheets:
   - `总览`: overall counts
   - `月度汇总`: monthly workdays/rest days/punch days/missing punch/rest-day punch/pay-code hours
   - `明细`: one row per calendar day
   - `需关注记录`: filtered rows with missing punch, rest-day punch, pay-code/exception records, or other attention flags
6. Verify the output artifact by opening the workbook with `openpyxl` and checking sheet names plus expected row counts.

## Suggested metrics

- 自然日、工作日、休息日、节假日/其他
- 有打卡天数
- 工作日缺打卡
- 休息日有打卡
- 假勤/异常小时 and by-label detail, e.g. `调休假18.62h/14次`
- 打卡时长 >= 10h 天数
- 10点后且无假勤记录
- 月内最早上班 / 最晚下班

## Pitfalls

- Do not conclude the API is unavailable after raw fetch returns `签名失败`; use the app's own `p.ajax.loadable.get` signing wrapper.
- Frame indices can shift. Always run `opencli browser <session> frames` and identify the frame URL/name before hard-coding `--frame 4`.
- Long date ranges are accepted by `/dashboard/attendance-calendar`; no need to click month-by-month if the Ajax wrapper works.
- Treat the task as read-only unless the user explicitly asks to submit forms or modify Gaia data.
