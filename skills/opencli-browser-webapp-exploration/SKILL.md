---
name: opencli-browser-webapp-exploration
description: 'Use when the user needs the opencli browser webapp exploration workflow: Explore authenticated web apps using opencli browser sessions; before ad-hoc handling of an unfamiliar reusable or open-source-derived internal workflow, run bounded local and find-skills capability discovery, then inspect UI state, frontend bundles, APIs, and safe update calls without leaking secrets or making unauthorized changes. Do not use for tasks outside this software-development workflow or tasks better handled by a narrower debugging, testing, planning, or review skill.'
---

# opencli Browser Webapp Exploration

References:
- `references/chrome-saved-tab-groups.md` covers a recurrent Chrome/UI confusion where repeated `OpenCLI Browser` items shown in the bookmarks-bar area are actually Saved Tab Groups created or reused by the OpenCLI browser workflow, not ordinary bookmarks.
- `references/github-personal-repo-deletion.md` captures the bind-first, minimal-friction workflow and disposable experiment for deleting Allen's personal GitHub repositories with OpenCLI.

Use this when the user asks to explore a web page/app with `opencli`/`ooencli`, especially authenticated dashboards where the normal browser tool may not share the logged-in Chrome session.

## Bounded capability-discovery preflight

Before building a new browser flow, check whether an existing Skill already covers the underlying product or workflow.

Run this preflight only when all are true:

- no named or clearly matching local Skill already covers the task;
- the workflow is repeated, multi-step, or expensive to rediscover;
- the page appears to be an internal adaptation of a reusable open-source product or common web application category.

Skip discovery and continue directly to browser exploration when any are true:

- the task is a one-off read or simple click likely to finish within two minutes;
- the task is urgent incident handling;
- an installed local Skill already covers it;
- the user explicitly asks to proceed directly.

Use this fixed budget:

1. **Local discovery: at most 15 seconds.** Use Hermes `skills_list` / `skill_view` and, when useful, the local catalog at `~/.codex/agent-catalog-runtime/agent_catalog.json`.
2. **External discovery: at most 2 queries and 90 seconds total.** Load the existing `find-skills` Skill, use specific generic product/function keywords, set each terminal/search timeout to the remaining budget, and inspect at most 3 candidates.
3. **Stop early.** Use the first credible installed match whose trigger and workflow fit the task.
4. **Do not auto-install.** A matching but uninstalled third-party Skill is only a candidate; ask before `npx skills add` or any equivalent installation.
5. **Fall back promptly.** If the budget expires or results are weak, continue with the opencli workflow below and record `fallback_reason=no_local_or_bounded_external_skill_match`.

External search terms must be generic. Never include internal URLs, company or tenant names, IDs, screenshots, schemas, cookies, tokens, request payloads, or business data. A safe query describes the upstream category and action, for example `admin dashboard bulk edit playwright`, not the internal system name or page URL.

## Tool selection: OpenCLI vs AutoCLI

Do not conflate `opencli` and `autocli` just because both can turn websites into CLIs.

- Prefer **`opencli`** when the job is *logged-in browser execution*: open a page in the user's existing Chrome context, inspect DOM/state, click/fill, run page-context JS, or safely call authenticated APIs through the browser session.
- Treat **`autocli`** as more *discovery/generation oriented*: explore a site's API surface, probe auth style, search for an existing adapter, or generate a new adapter with AI assistance.
- For Allen's environment specifically, `opencli` is the established browser bridge and existing internal tooling may already depend on it. If the task is "operate the site I already use" rather than "discover how a new site works", start with `opencli`.
- If asked to compare the two, verify live state instead of assuming: check binary type/version, `--help`, and doctor/extension connectivity. A common finding is that both CLIs are installed but the Chrome extension is not currently connected; that is a setup/status fact, not a reason to avoid the tool class.

## Workflow

1. **Confirm opencli is available and Browser Bridge can start**
   ```bash
   command -v opencli && opencli --help | head -40
   opencli doctor -v
   ```

   If `opencli doctor` or `opencli browser <session> state/open` says `Failed to start opencli daemon`, run the daemon entry printed in the hint to get the real first error, for example:
   ```bash
   node /Users/heytea/.hermes/node/lib/node_modules/@jackwener/opencli/dist/src/daemon.js
   ```
   Then act on the concrete result:
   - `listen EPERM ... 127.0.0.1:19825` usually means the current execution sandbox is not allowed to bind the local daemon port; ask/run with local unsandboxed approval or have Allen run `opencli daemon restart && opencli doctor -v` in his terminal.
   - `EADDRINUSE ... 19825` means another daemon/process owns the port; use `opencli daemon stop` / restart or inspect the local process before retrying.
   - Do not describe the target website as broken until the daemon and extension status have been verified.

2. **Bind-first: reuse the user's already-open tab before opening anything new**
   ```bash
   # If the target page is already open, select that real Chrome tab, then:
   opencli browser <session> bind
   opencli browser <session> state

   # Only when no suitable existing tab exists:
   opencli browser <session> open <url>
   opencli browser <session> state
   ```
   Rules:
   - `bind` attaches the named OpenCLI session to the current real Chrome tab/window; this is the preferred path for authenticated pages and preserves the user's visible context.
   - A session name only identifies an OpenCLI lease. Reusing the same name does **not** prove that the desired user tab was selected.
   - `open` may create/lease another tab or window. Do not call it first when Allen says the page is already open.
   - On macOS, when multiple Chrome windows exist, enumerate tabs and select the exact URL before `bind`; otherwise OpenCLI may bind whichever Chrome window is frontmost.
   - Multiple Chrome windows can still share one browser process/profile and cookies. Verify process/profile and actual page login state rather than assuming a new window means a separate authentication context.
   - `opencli browser <session> open` may not support command-local `--window`; check `--help` instead of assuming options.
   - Raw-IP URLs may trigger command approval; proceed only within user-provided scope.

3. **Interact using refs or semantic selectors**
   ```bash
   opencli browser <session> click <ref>
   opencli browser <session> click --text '选择分组'
   opencli browser <session> click --role button --name '刷新'
   opencli browser <session> hover --text '选择分组'
   opencli browser <session> state
   ```
   Pitfall: DOM indices returned by custom `eval` are not opencli clickable refs. Use refs from `state`/`find`, or selectors/text/role.

4. **If dropdown/popover contents do not appear in `state`, inspect DOM text and elements**
   ```bash
   opencli browser <session> eval "(() => document.body.innerText)()"
   opencli browser <session> eval "(() => JSON.stringify([...document.querySelectorAll('body *')].map((el,i)=>({i,tag:el.tagName,txt:(el.innerText||el.textContent||'').trim(),cls:el.className,role:el.getAttribute('role'),aria:el.getAttribute('aria-label')})).filter(x=>x.txt && /分组|选择|group/i.test(x.txt)).slice(0,80), null, 2))()"
   ```

5. **Inspect frontend bundles for API endpoints when UI state is insufficient**
   ```bash
   opencli browser <session> eval "(() => Array.from(document.scripts).map(s=>s.src).filter(Boolean).join('\\n'))()"
   python3 - <<'PY'
   import urllib.request, re
   url = '<asset-js-url>'
   js = urllib.request.urlopen(url, timeout=20).read().decode('utf-8','ignore')
   for pat in ['groups','keys','group_id','/api/v1']:
       print('\nPAT', pat)
       for m in re.finditer(pat, js, re.I):
           print(js[max(0,m.start()-220):m.end()+350].replace('\n',' ')[:900])
           break
   PY
   ```
   For code-split apps, download referenced chunks such as `keys-*.js`, `groups-*.js`, or view bundles to discover methods like:
   - list: `GET /api/v1/keys`
   - groups: `GET /api/v1/groups/available`
   - update: `PUT /api/v1/keys/{id}` with `{"group_id": ...}`

6. **Use browser-internal fetch for authenticated reads, but do not reveal tokens**
   If the app uses bearer token in localStorage, keep token usage inside the page context and only output sanitized data:
   ```bash
   opencli browser <session> eval "(async () => { const token=localStorage.getItem('auth_token'); const headers={'Content-Type':'application/json','Authorization':'Bearer '+token}; const [keys, groups] = await Promise.all([fetch('/api/v1/keys?page=1&page_size=50',{headers}).then(r=>r.json()), fetch('/api/v1/groups/available',{headers}).then(r=>r.json())]); const safeKeys=(keys.items||keys.data?.items||[]).map(k=>({id:k.id,name:k.name,key_mask:(k.key||k.api_key||'').replace(/^(.{6}).*(.{4})$/,'$1...$2'),group_id:k.group_id,group_name:k.group_name||k.group?.name,status:k.status,last_used_at:k.last_used_at,created_at:k.created_at})); return JSON.stringify({keys:safeKeys, groups}, null, 2); })()"
   ```

7. **Do not perform side-effecting changes unless explicitly instructed**
   For update endpoints, report the exact safe action plan and IDs first. Example:
   ```json
   PUT /api/v1/keys/45
   {"group_id": 14}
   ```
   Only execute after the user asks to switch/update.

## Gaia Portal / Workforce iframe workflow notes

Reference: `references/gaia-attendance-overtime-export.md` captures the verified Gaia WFM patterns for broad attendance-calendar exports, self-application/overtime list exports, signed workflow-detail requests, long-running export progress via `localStorage`, and large JSON chunk extraction.

For Gaia Portal pages like `portal-hw.gaiaworkforce.com/#/module-attendance-management/app-workflow-apply-self`, the useful app is often inside cross-origin iframes. Use:ong-running export progress via `localStorage`, and large JSON chunk extraction.

For Gaia Portal pages like `portal-hw.gaiaworkforce.com/#/module-attendance-management/app-workflow-apply-self`, the useful app is often inside cross-origin iframes. Use:
```bash
opencli browser <session> frames
opencli browser <session> eval --frame <index> "(() => ({url:location.href,text:document.body.innerText.slice(0,4000), inputs:[...document.querySelectorAll('input,textarea,button')].map((e,i)=>({i,tag:e.tagName,type:e.type,value:e.value,placeholder:e.placeholder,txt:e.innerText,disabled:e.disabled})).slice(0,100)}))()"
```

Specific findings from Gaia WFM:
- Reference: `references/gaia-attendance-overtime-export.md` captures a verified Gaia attendance-calendar and overtime-export workflow: cross-origin iframe access, Pandora ajax API use, Gaia signed-header generation via `ajax.clone().processParamsAfter()`, localStorage checkpointing for long overtime detail exports, and recommended Excel sheets/metrics.
- The leave application form may be in frame `module-wfm-app-workflow-leave-apply` at `#/workflow/sign-histroy?formType=leave&path=module-wfm/app-workflow-leave-apply`; default leave type can be `调休假`.
- The self-apply/history list may be in frame `module-attendance-management-app-workflow-apply-self` at `#/workflow/my-apply-form`.
- History rows can be extracted by DOM text from `.table-row`, e.g. matching `OT-...` and `LEAVE-...`; this is useful to avoid duplicate submissions by verifying existing completed overtime/leave forms first.
- Gaia API calls such as `/api/wfm4api-heytea/workflow/form/apply/histroy/tableData/data` may reject direct browser `fetch` with `签名失败` / missing nonce-time signature. Prefer UI interaction or inspect/reuse the frontend signing mechanism instead of assuming plain authenticated POST will work.
- Verified signing reuse pattern: in the Gaia WFM app page, initialize webpack require if needed, then use Pandora ajax clone/signing rather than `ajax.loadable` for bulk scripts:
  ```js
  try { window.webpackChunkwfm4_integration.push([[Math.random()],{},req=>{window.__wfm_req=req;}]); } catch(e) {}
  const ajax = window.__wfm_req('ZffG').ajax.clone();
  async function sign(method, params) {
    const n = { params: params || null, paramsInOptions: null, method, options: {}, processData: true };
    await ajax.processParamsAfter(n);
    return n.options.headers || {}; // includes app-nonce, timestamp, sign
  }
  async function signedJson(url, method, body) {
    const headers = await sign(method.toLowerCase(), body);
    if (method !== 'GET') headers['Content-Type'] = 'application/json';
    const r = await fetch(url, { method, credentials: 'include', headers, body: method === 'GET' ? undefined : JSON.stringify(body) });
    const j = await r.json();
    if (!r.ok || j.result === false) throw new Error(j.message || j.errorMsg || j.reason || `HTTP ${r.status}`);
    return j.data;
  }
  ```
- Gaia “我的申请表单” overtime export path verified for Allen: open `https://gateway-hw.gaiaworkforce.com/wfm4integration-wfm4api/app.html#/workflow/my-apply-form`, then query `/wfm4api-heytea/workflow/form/apply/histroy/tableData/data` with `pageSize:1000` and a date range such as `2020-01-01` to `2026-12-31`; filter rows where `formType === 'OT'`, `type === 'PROCESSOVERTIMEFORM'`, or `number` starts with `OT-`. Each OT list row only has summary fields; detail fields require `GET /wfm4integration-wfm4api/api/common/workflow/detail/{processInstanceId}` with signed headers. Detail response `data.form[]` contains `scheduleDate`, `startDate`, `endDate`, `startTime`, `endTime`, `typeLabel`, `hours`, `mealHours`, `monthOverTimeHours`, `detail`, `cardRecords`, and `isCompensation`.
- Gaia overtime detail export pitfall: long `opencli browser eval` calls can print `✖ This operation was aborted` even after partial progress, and large localStorage extraction may be raw strings rather than JSON-quoted output. For long exports, persist `__hermes_ot_list`, `__hermes_ot_rows`, `__hermes_ot_errors`, `__hermes_ot_index`, and `__hermes_ot_export_all` in page `localStorage`; poll progress in small calls; extract large strings in chunks and, if `json.loads` fails on a chunk, treat the eval output as the raw string after stripping the OpenCLI update notice.
- When a task is “execute yesterday’s overtime compensatory leave,” first check the history list for paired records submitted around the same time: `加班申请单-*` (`OT-*`) and `调休假请假申请单-*` (`LEAVE-*`) with status `完成`. If both exist, report completion and do not submit a duplicate.

## Gmail web UI classification notes

Use these when Allen asks to organize Gmail through the logged-in browser rather than Gmail API access. Safety rule: **do not delete** unless explicitly asked; prefer label + archive/remove from Inbox.

Recommended classification system:
- `01_重要_需处理`
- `02_AI与开发`
- `03_工作机会`
- `04_金融账单`
- `05_安全账号`
- `06_社交社区`
- `07_工具产品通知`
- `08_学习资讯`
- `09_购物旅行`
- `99_低优先归档`

Workflow:
1. Search by source/topic, e.g. `in:inbox from:redditmail.com`, `in:inbox (subject:(security OR verification) OR from:accounts.google.com)`, then operate only on search results.
2. Select visible results with the toolbar checkbox. In Gmail, custom DOM `eval` indices are not opencli refs; use CSS/semantic selectors or page-context JS. The selector `[aria-label="Select"]` may be ambiguous; try `opencli browser <session> find --css '[aria-label="Select"]'` or click with `--nth`, then verify visible checkboxes via JS.
3. After selecting messages, inspect toolbar buttons. Gmail exposes safe buttons like `Archive`, `Mark as read`, and dangerous `Delete`. Avoid `Delete` and `Report spam` unless explicitly requested.
4. For labels, Gmail’s menu/popovers sometimes do not show in `state`; inspect with DOM text/elements after opening the label/more menu. If UI automation is flaky, stop after explaining the filter scheme rather than risking a wrong click.
5. Verification: confirm labels appear in the left sidebar with counts and/or re-run representative searches such as `label:02_AI与开发` and `in:inbox from:<source>` to ensure items were labeled/removed from Inbox. Explicitly state no delete action was performed.

Long-term recommendation: create Gmail Filters with actions `Apply label` and, for low-priority categories, `Skip Inbox`; never include `Delete it` by default. Keep security/finance/job-opportunity categories visible or in Inbox until the user decides otherwise.

## Zhihu org post monitoring / update alerts

When monitoring Zhihu org/user post pages where direct HTTP requests hit anti-bot/403, use the browser-session pattern in `references/zhihu-org-post-monitoring.md`: open the page with `opencli browser`, extract the `page` id, run page-context `fetch()` with `credentials:'include'`, store seen IDs under `~/.hermes/state/`, initialize a no-spam baseline on first run, and schedule Hermes cron with a script path relative to `~/.hermes/scripts/`.

## DingTalk / AliDocs online-doc export notes

Reference: `references/dingtalk-alidocs-export.md` captures the concrete opencli pattern for DingTalk online docs.

When exploring a DingTalk/AliDocs online document for local export:

1. Open the document in a named opencli browser session.
2. If the visible state is insufficient, inspect the “更多操作” menu through page-context JS rather than relying only on plain `state` output.
3. For menu items rendered by React, inspect `__reactProps$*` on `.wd3-listitem` nodes to recover stable `data-item-key` values. Useful observed keys include:
   - `export` → `下载到本地`
   - `exportCloud` → `导出到钉盘或知识库`
4. After triggering a candidate export path, verify success on disk instead of assuming the click worked. Check `~/Downloads` (or the expected directory) for newly modified `.docx` files and compare mtimes.
5. If the user explicitly said “能下载为 Word 就下载，下载不了就跳过”, then a visible export entry is **not** enough to claim success. Without a real new `.docx` artifact, report that the export path was explored but not verified, and skip that document.

Pitfalls:
- AliDocs export options may exist in the menu but not expose a stable secondary format picker to opencli automation.
- Repeated large `document.body.innerText` dumps are noisy; once the menu keys are identified, prefer the compact `data-item-key` extraction pattern.
- Do not tell the user “downloaded” based only on seeing `下载到本地`; require a real filesystem artifact.

## X / Twitter account analysis via opencli

When a user asks to analyze a specific X account through opencli, prefer the dedicated `opencli twitter` adapter over raw browser clicks.

Recommended read path:
1. Profile metadata:
   ```bash
   opencli twitter profile <handle> -f json --window background --site-session persistent
   ```
2. Recent tweets (preferred):
   ```bash
   opencli twitter tweets <handle> --limit 40 -f json --window background --site-session persistent
   ```
3. If `tweets` fails with adapter/query expiry or transient fetch issues (for example `HTTP 429: UserTweets fetch failed — queryId may have expired`), retry with search fallback instead of stopping:
   ```bash
   opencli twitter search "from:<handle>" --product live --limit 50 -f json --window background --site-session persistent
   ```
   Useful variants:
   - today's posts: `from:<handle> since:YYYY-MM-DD`
   - broader backfill: `from:<handle> since:YYYY-MM-DD` with a larger `--limit`
   - `--product top` can help recover high-engagement posts when `live` is too reply-heavy.

Operational notes:
- The `tweets` command tends to return cleaner chronological profile posts, but `search --product live` may include replies and lightweight interactions; say that explicitly in the report.
- `search` results may use `https://x.com/i/status/...` links. Keep them as real clickable source links unless you have a verified canonical status URL.
- For daily monitoring/cron, write prompts so the agent first tries `tweets`, then falls back to `search live`, and reports the fallback if used.
- When summarizing “today’s posts”, separate:
  - original thesis/analysis tweets
  - short replies / community interaction
  This matters because some days the account shifts from research output into audience-management behavior.

## Xiaohongshu / Rednote creator-content research

Reference: `references/xiaohongshu-creator-content-research.md` captures the concrete opencli workflow for researching a Xiaohongshu creator's posts and organizing them into a study note.

Key takeaways:
- Prefer the dedicated `opencli xiaohongshu` adapter (`search`, `user`, `note`, `feed`) over raw browser clicking for creator-content research.
- To locate a creator from a nickname query, inspect `author` + `author_url` from `search` results, then call `user` on that profile URL.
- Important pitfall: `opencli xiaohongshu note` requires a **full signed note URL** (including `xsec_token`), not a bare note ID. Reuse the `url` field returned by `search` or `user`.
- Efficient workflow: search creator → fetch recent note list → bucket titles by theme → read only representative/high-value posts with `note` → produce a categorized inventory plus a rapid-learning reading order.

## Chrome extension / `chrome://` page operation notes

When the task is to configure a local Chrome extension or a `chrome://extensions` page:

- Prefer the user's existing installed/unpacked extension directory when they say it already exists; do not re-download unless the local copy is missing or stale.
- OpenCLI may not bind or evaluate reliably on `chrome://` pages or `chrome-extension://` pages. If that happens, switch promptly to the macOS UI fallback: AppleScript to list/select Chrome windows/tabs, window screenshots, vision inspection, and direct clicks/typing via `cliclick` or the computer-use tool.
- For Chrome extension settings, direct UI is the default path. Inspect source only to identify labels/field names or verify what a setting means; do not jump to editing Chrome LevelDB/localStorage unless UI is impossible and the user accepts that risk.
- If a blocker lasts more than a few minutes, tell Allen exactly what step is blocked and what help/action is needed. Do not silently keep trying unrelated low-level workarounds.
- After filling secrets in UI, verify by state rather than disclosure: visually confirm fields are non-empty, run an allowed test action if available, and report only masked/structural facts.

## Safety and reporting

- Never print full API keys, bearer tokens, refresh tokens, cookies, localStorage secrets, webhook tokens, or signed webhook URLs.
- Mask keys and summarize IDs/names/status/rates.
- Separate “exploration completed” from “change performed”; be explicit if no change was made.
- If an existing completed workflow is found, explicitly state that no new submission was made to avoid duplicates.
- If the user corrects the intended task, acknowledge and immediately resume the requested opencli exploration rather than continuing unrelated prior plans.
