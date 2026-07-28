# DingTalk / AliDocs online-doc export via opencli

Session-derived pattern for Allen-style tasks where the user wants: “if the online doc can be downloaded as Word, do it; if not, skip it.”

## Goal
Use `opencli` to explore a logged-in DingTalk/AliDocs online document and determine whether a **real** Word export (`.docx`) can be verified.

## Minimal workflow

1. Open the target doc in a named session:
   ```bash
   opencli browser dingdoc-inner open '<alidocs-url>'
   ```

2. Expand the top-right “更多操作” menu, then enumerate menu rows compactly:
   ```bash
   opencli browser dingdoc-inner eval "(() => [...document.querySelectorAll('.wd3-listitem')].map(el=>({text:(el.innerText||'').trim(), key:(()=>{const k=Object.keys(el).find(x=>x.startsWith('__reactProps$')); return k?el[k]['data-item-key']:null})()})).filter(x=>x.text).slice(0,50))()"
   ```

3. Expected useful menu keys observed in DingTalk online docs:
   - `export` → `下载到本地`
   - `exportCloud` → `导出到钉盘或知识库`
   - `print` → `打印`

4. If you need to trigger a React-rendered row more deterministically, inspect `__reactProps$*` and call its handlers rather than guessing CSS selectors.

5. **Verification requirement**: after any attempted export flow, check the filesystem for a real newly written `.docx`:
   ```bash
   python - <<'PY'
   from pathlib import Path
   import time
   p=Path('/Users/heytea/Downloads')
   files=sorted(p.glob('*.docx'), key=lambda x:x.stat().st_mtime, reverse=True)
   for f in files[:10]:
       print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(f.stat().st_mtime)), f.name)
   PY
   ```

## Decision rule

If the user’s rule is “能下载为 Word 就下载，下载不了就跳过”, then use this strict classification:

- **Success**: a new `.docx` file exists and is attributable to the attempted export.
- **Skip**: the menu shows export entries but no real `.docx` artifact can be verified.

Do **not** claim success merely because the UI contains `下载到本地`.

## Pitfalls

- The first-level menu is often discoverable, but the second-level format picker (Word/PDF/etc.) may not surface cleanly to opencli automation.
- Large `document.body.innerText` dumps are too noisy for repeated diagnosis; once the menu opens, prefer the compact `.wd3-listitem + __reactProps$* + data-item-key` pattern.
- Existing old `.docx` files in `~/Downloads` are common; always compare modification times before telling the user a download happened.

## What to report to the user

Recommended wording when export is inconclusive:
- “我已经用 opencli 确认到 `下载到本地` 入口，但没有验证到新的 `.docx` 文件落盘；按你要求，这类在线文档本次跳过。”

This preserves the distinction between:
- explored UI path
- verified download artifact
- user-directed skip behavior
