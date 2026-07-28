# Gaia WFM attendance and overtime export notes

Use this when Allen asks to整理/导出 Gaia Workforce (`portal-hw.gaiaworkforce.com` / `gateway-hw.gaiaworkforce.com`) 考勤、加班、请假、我的申请表单等数据.

## Attendance calendar export

The home dashboard attendance calendar iframe can expose the signed ajax client via webpack modules. In the `card-attendanceCalendar` / `dashboard.html#/attendance/attendance-calendar` frame:

```js
window.webpackChunkwfm4_integration.push([[Math.random()],{},req=>{window.__wfm_req=req;}]);
const pandora = window.__wfm_req('ZffG');
const data = await pandora.ajax.loadable.get('/dashboard/attendance-calendar', {
  startDate: '2024-05-13',
  endDate: '2026-06-30'
});
```

Direct browser `fetch('/wfm4integration-wfm4api/api/dashboard/attendance-calendar?...')` fails with `签名失败` unless signed headers are supplied. Prefer `pandora.ajax.loadable.get()` for normal in-frame reads.

Observed attendance row shape:

```json
{
  "date": "2026-06-30",
  "dateType": 1,
  "shift": {"timeClassName": "职能标准班1 09:00-18:00", "cardList": [{"start": "09:07", "end": "20:37"}]},
  "payCodeList": [{"label": "调休假", "startdtm": "09:00:00", "enddtm": "10:30:00", "payHours": "1.50"}]
}
```

Useful derived fields: 日期类型, 首次打卡, 末次打卡, 打卡时长, 假勤/异常明细, 工作日缺打卡, 休息日有打卡, `>=10h` / `>=12h` 打卡.

## Overtime/application list export

Open the self-application list:

```text
https://gateway-hw.gaiaworkforce.com/wfm4integration-wfm4api/app.html#/workflow/my-apply-form
```

Initialize webpack require if needed:

```js
window.webpackChunkwfm4_integration.push([[Math.random()],{},req=>{window.__wfm_req=req;}]);
```

The list table store can be found from module `I8/N`; it exposes `tableStore.dataUrl` and `tableStore.getSearchParams()`. A large page size returned all visible history in one request during this session:

```js
const ajax = window.__wfm_req('ZffG').ajax.clone();
const store = window.__wfm_req('I8/N').default;
const ts = store.tableStore;
const params = ts.getSearchParams();
params.pageNum = 1;
params.pageSize = 1000;
const list = await ajax.post(ts.dataUrl, params);
const overtimeForms = list.filter(x => x.formType === 'OT' || x.type === 'PROCESSOVERTIMEFORM' || String(x.number || '').startsWith('OT-'));
```

Observed list fields include `number`, `processInstanceId`, `formType`, `type`, `formKey`, `applyDate`, `endProcessTime`, `status`, `source`, `employeeId`, `name`, `applicantUnit`.

## Detail endpoint and signing workaround

Overtime detail data (加班日期、开始/结束时间、申请小时、说明、打卡记录) lives behind:

```text
GET /wfm4integration-wfm4api/api/common/workflow/detail/{processInstanceId}
```

Plain `fetch()` fails with `签名失败`. If `pandora.ajax.get()` hangs or is awkward in OpenCLI, reuse the frontend signing hook and then call `fetch()` yourself:

```js
const ajax = window.__wfm_req('ZffG').ajax.clone();
async function sign(method, params) {
  const n = {params: params || null, paramsInOptions: null, method, options: {}, processData: true};
  await ajax.processParamsAfter(n);
  return n.options.headers || {};
}
async function signedJson(url, method = 'GET', body) {
  const headers = await sign(method.toLowerCase(), body);
  if (method !== 'GET') headers['Content-Type'] = 'application/json';
  const r = await fetch(url, {method, credentials: 'include', headers, body: method === 'GET' ? undefined : JSON.stringify(body)});
  const j = await r.json();
  if (!r.ok || j.result === false) throw new Error((j && (j.message || j.errorMsg || j.reason)) || `HTTP ${r.status}`);
  return j.data;
}
const detail = await signedJson('/wfm4integration-wfm4api/api/common/workflow/detail/' + processInstanceId);
```

Observed detail shape:

```json
{
  "formNo": "OT-142606",
  "processStatus": "COMPLETED",
  "form": [{
    "scheduleDate": "2026-07-15",
    "startDate": "2026-07-15",
    "endDate": "2026-07-15",
    "startTime": "19:30",
    "endTime": "20:30",
    "typeLabel": "平时加班",
    "hours": "1.0",
    "monthOverTimeHours": "2.0",
    "detail": "加班",
    "cardRecords": ["2026-07-15 09:49", "2026-07-15 20:31"],
    "isCompensation": true
  }]
}
```

## Long export reliability

Long loops inside a single `opencli browser eval` may return `This operation was aborted` while still partially advancing. Safer pattern:

1. Store the source list and current index in `localStorage` (`__hermes_ot_list`, `__hermes_ot_index`).
2. Process small batches or launch an in-page async background loop that writes progress after every row to `localStorage`.
3. Poll compact progress only (`done`, `total`, `rows`, `errors`).
4. Store final JSON in `localStorage` (`__hermes_ot_export_all`).
5. Extract large JSON in chunks. Important: `opencli eval` may print raw strings, not JSON-quoted strings, for large string slices. Decode as JSON if possible, otherwise treat stdout as the raw chunk.

Example chunk extraction logic in Python:

```python
def run(js):
    s = subprocess.check_output(['opencli','browser',SESSION,'eval',js], text=True)
    s = s.split('\n\n  Update available:')[0].strip()
    try:
        return json.loads(s)
    except Exception:
        return s
length = int(run("(()=>localStorage.getItem('__hermes_ot_export_all')?.length||0)()"))
text = ''.join(run(f"(()=>localStorage.getItem('__hermes_ot_export_all').slice({i},{i+12000}))()") for i in range(0, length, 12000))
obj = json.loads(text)
```

When generating the final workbook, include at least: `总览`, `加班明细`, `月度汇总`, `类型汇总`, and `错误记录`. Report read failures separately instead of hiding them.
