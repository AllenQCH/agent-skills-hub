# Zhihu org post monitoring with opencli browser

Use this when monitoring a Zhihu organization/user posts page such as `https://www.zhihu.com/org/<token>/posts` and direct HTTP requests hit Zhihu anti-bot/403.

## Proven pattern

1. Open the target page in a named opencli browser session:
   ```bash
   opencli browser qwen-zhihu open 'https://www.zhihu.com/org/a-li-ji-zhu/posts'
   sleep 5
   opencli browser qwen-zhihu tab list
   ```

2. Use the returned `page` id explicitly with `--tab`. Without `--tab`, later `eval` calls may run on `about:blank` if the active tab changed.

3. Fetch the Zhihu API from inside the browser context so cookies/login state and JS anti-bot handling are available:
   ```bash
   opencli browser qwen-zhihu eval --tab <PAGE_ID> "(async()=>{const url='https://www.zhihu.com/api/v4/members/a-li-ji-zhu/articles?sort_by=created&include=data%5B*%5D.comment_count%2Csuggest_edit%2Cis_normal%2Cthumbnail_extra_info%2Cthumbnail%2Ccan_comment%2Ccomment_permission%2Cadmin_closed_comment%2Ccontent%2Cvoteup_count%2Ccreated%2Cupdated%3Bdata%5B*%5D.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3B&limit=10&offset=0'; const r=await fetch(url,{credentials:'include'}); const t=await r.text(); return JSON.stringify({status:r.status,text:t.slice(0,3000)});})()"
   ```

4. For Hermes cron notifications, write a script under `~/.hermes/scripts/` that:
   - opens the page with opencli browser;
   - extracts the tab/page id;
   - does browser-context `fetch()` against `/api/v4/members/<token>/articles`;
   - stores seen article IDs under `~/.hermes/state/`;
   - initializes a baseline on the first successful run and prints nothing;
   - prints a Markdown notification only for newly seen IDs;
   - exits non-zero on real failures so cron alerts instead of failing silently.

5. Create the cron as script-only/no-agent. The `script` argument must be relative to `~/.hermes/scripts/`, not absolute:
   ```python
   cronjob(action='create', name='千问云知乎文章更新监控', schedule='every 30m', script='zhihu_qwen_cloud_watch.py', no_agent=True, deliver='origin', prompt='...')
   ```

## Pitfalls

- `requests.get('https://www.zhihu.com/org/.../posts')` may return 403/anti-bot HTML. Do not conclude monitoring is impossible; use opencli browser session + page-context fetch.
- `opencli browser <session> open ... --window background` is invalid for the browser subcommand in current opencli; inspect `opencli browser open --help` and use `opencli browser <session> open <url>`.
- `location.origin` may be `null` if `eval` runs on `about:blank`; always pass `--tab <page-id>` from `open` or `tab list`.
- First run should establish a baseline to avoid flooding the chat with historical posts.
- In Hermes cron, absolute script paths are rejected; put the script in `~/.hermes/scripts/` and pass only the filename.
