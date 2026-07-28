---
name: openclaw-to-hermes-migration
description: 'Use when the user needs the openclaw to hermes migration workflow: Migrate OpenClaw historical state into Hermes so Hermes becomes the primary runtime and OpenClaw is retained only as an archive/source, with backup-first safety and verification. Do not use for ordinary direct execution that does not need an autonomous agent, CLI delegate, migration, or Hermes runtime workflow.'
triggers:
- User wants Hermes to stop depending on OpenClaw
- User wants OpenClaw memory, identity, workspace, skills, or sessions migrated into Hermes
- User asks for simplest/cleanest assistant migration between machines
- Need to preserve continuity files while retiring OpenClaw as runtime
---

# OpenClaw → Hermes migration

Use this when the goal is not merely to copy `~/.openclaw`, but to **import its useful contents into Hermes** and make Hermes the primary assistant runtime.

## Principle

- Hermes should become the primary runtime.
- OpenClaw should become a historical source/archive only.
- Do **not** delete or wipe `~/.openclaw` during the first migration pass.
- Always archive first; the user values continuity and does not want persona/memory loss.

## Workflow

### 1) Backup first

Create a rollback archive outside `~/.hermes` to avoid tar adding the archive to itself.

```bash
set -euo pipefail
TS=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$HOME/AssistantMigrationBackups"
mkdir -p "$BACKUP_DIR"
ARCHIVE="$BACKUP_DIR/pre-openclaw-to-hermes-$TS.tar.gz"
tar \
  --exclude='.hermes/audio_cache' \
  --exclude='.hermes/image_cache' \
  --exclude='.hermes/cache' \
  --exclude='.hermes/logs' \
  --exclude='.hermes/backups' \
  -czf "$ARCHIVE" -C "$HOME" .hermes .openclaw
ls -lh "$ARCHIVE"
```

Pitfall learned: creating the archive under `~/.hermes/backups` while archiving `.hermes` can produce `tar: Can't add archive to itself`. Use `~/AssistantMigrationBackups` instead.

### 2) Inspect OpenClaw state

Important paths usually include:

```text
~/.openclaw/memory/main.sqlite
~/.openclaw/workspace/IDENTITY.md
~/.openclaw/workspace/USER.md
~/.openclaw/workspace/MEMORY.md
~/.openclaw/workspace/memory/
~/.openclaw/skills/
~/.openclaw/agents/main/sessions/
~/.openclaw/cron/jobs.json
~/.openclaw/openclaw.direct.json
```

Use Python/sqlite inspection for the memory DB. OpenClaw memory may store chunks in a SQLite table named `chunks` with columns like `path`, `source`, `start_line`, `end_line`, and `text`.

### 3) Import into Hermes archive area

Use this destination structure:

```text
~/.hermes/openclaw-import/
  README.md
  workspace/
  identity/
  raw/
    memory/
    agents-main-sessions/
    cron/
    openclaw.direct.json
  exported-memory/
  reports/
```

Copy data, excluding Git internals from workspace:

```bash
set -euo pipefail
SRC="$HOME/.openclaw"
DST="$HOME/.hermes/openclaw-import"
mkdir -p "$DST/raw" "$DST/exported-memory" "$DST/reports"
rsync -a --delete --exclude='.git' "$SRC/workspace/" "$DST/workspace/"
rsync -a --delete "$SRC/identity/" "$DST/identity/"
rsync -a --delete "$SRC/memory/" "$DST/raw/memory/"
rsync -a --delete "$SRC/agents/main/sessions/" "$DST/raw/agents-main-sessions/"
rsync -a --delete "$SRC/cron/" "$DST/raw/cron/"
cp "$SRC/openclaw.direct.json" "$DST/raw/openclaw.direct.json" 2>/dev/null || true
```

### 4) Sync OpenClaw skills safely

Destination:

```text
~/.hermes/skills/openclaw-imports/
```

If Hermes already has imported skills, do **not** use destructive `rsync --delete` blindly; existing directories may contain additional files and old macOS rsync can fail with `Directory not empty (66)`. Prefer a safe copy that only fills missing files or deliberately compare before replacing.

Safe Python pattern:

```python
import pathlib, shutil
home = pathlib.Path.home()
skills_src = home / ".openclaw" / "skills"
skills_dst = home / ".hermes" / "skills" / "openclaw-imports"
skills_dst.mkdir(parents=True, exist_ok=True)
for file in skills_src.rglob("*"):
    rel = file.relative_to(skills_src)
    target = skills_dst / rel
    if file.is_dir():
        target.mkdir(parents=True, exist_ok=True)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(file, target)
```

### 5) Export OpenClaw memory SQLite to Markdown

Do not assume one row equals one file. `MEMORY.md` may be split across multiple chunks. Group by `path`, order by `start_line`, then concatenate chunks.

```python
import sqlite3, pathlib, collections, json, datetime
home = pathlib.Path.home()
src = home / ".openclaw"
dst = home / ".hermes" / "openclaw-import"
exp = dst / "exported-memory"
exp.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(src / "memory" / "main.sqlite")
cur = con.cursor()
rows = cur.execute(
    "select path,start_line,end_line,text,updated_at from chunks "
    "where source='memory' order by path,start_line"
).fetchall()
con.close()

by = collections.defaultdict(list)
for path, start, end, text, updated in rows:
    by[path].append((start, end, text, updated))

manifest = []
contents = []
for path, chunks in by.items():
    safe = path.replace('/', '__')
    out = exp / safe
    content = chunks[0][2] if len(chunks) == 1 else '\n'.join(c[2].rstrip() for c in chunks) + '\n'
    out.write_text(content, encoding='utf-8')
    contents.append(content)
    manifest.append({"source_path": path, "chunks": len(chunks), "export_path": str(out.relative_to(dst)), "bytes": out.stat().st_size})

(exp / "OPENCLAW_MEMORY_COMBINED.md").write_text('\n\n---\n\n'.join(contents), encoding='utf-8')
(exp / "manifest.json").write_text(json.dumps({"generated": datetime.datetime.now().isoformat(), "files": manifest}, ensure_ascii=False, indent=2), encoding='utf-8')
```

### 6) Write a migration report

Create:

```text
~/.hermes/openclaw-import/reports/MIGRATION_REPORT.md
~/.hermes/openclaw-import/reports/migration-report.json
```

The report should state:

```text
Primary runtime: Hermes
OpenClaw runtime dependency: false
OpenClaw source was not deleted; it is only historical source/backup.
```

Also record counts for workspace, identity, raw memory, sessions, cron, exported memory, and skills.

### 7) Update Hermes memory compactly

Persist the new operating principle, e.g.:

```text
Environment: Hermes is the primary assistant runtime; OpenClaw has been imported into ~/.hermes/openclaw-import as historical archive/source only.
```

If memory is full, replace the older note that says OpenClaw is the local-first assistant runtime.

### 8) Verify before claiming completion

Run fresh verification commands and only then report success.

Example:

```bash
set -euo pipefail
BACKUP=$(ls -t "$HOME"/AssistantMigrationBackups/pre-openclaw-to-hermes-*.tar.gz | head -1)
ls -lh "$BACKUP"
tar -tzf "$BACKUP" '.openclaw/workspace/IDENTITY.md' '.openclaw/workspace/USER.md' '.openclaw/workspace/MEMORY.md' '.hermes/config.yaml'

test -f "$HOME/.hermes/openclaw-import/workspace/IDENTITY.md"
test -f "$HOME/.hermes/openclaw-import/workspace/USER.md"
test -f "$HOME/.hermes/openclaw-import/workspace/MEMORY.md"
test -d "$HOME/.hermes/openclaw-import/workspace/memory"
test -f "$HOME/.hermes/openclaw-import/raw/memory/main.sqlite"
test -f "$HOME/.hermes/openclaw-import/exported-memory/OPENCLAW_MEMORY_COMBINED.md"
test -f "$HOME/.hermes/openclaw-import/reports/MIGRATION_REPORT.md"
test -d "/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/lark-im"
wc -c "$HOME/.hermes/openclaw-import/exported-memory/OPENCLAW_MEMORY_COMBINED.md" "$HOME/.hermes/openclaw-import/reports/MIGRATION_REPORT.md"
```

## What not to do

- Do not immediately delete `~/.openclaw`.
- Do not overwrite existing Hermes skills destructively without comparing.
- Do not keep telling the user to carry OpenClaw forever; the desired outcome is Hermes independence.
- Do not claim migration is complete without verifying backup and imported files.

## Retiring OpenClaw after validation

If the user explicitly asks whether OpenClaw can be deleted after migration, prefer a reversible retirement step first: **rename/archive `~/.openclaw` instead of hard-deleting it**.

Before renaming:

```bash
ps aux | grep -i openclaw | grep -v grep || true
```

Then archive:

```bash
set -euo pipefail
if [ -d "$HOME/.openclaw" ]; then
  ARCH="$HOME/.openclaw.archive-$(date +%Y%m%d-%H%M%S)"
  mv "$HOME/.openclaw" "$ARCH"
  printf 'ARCHIVED_OPENCLAW=%s\n' "$ARCH"
else
  printf 'NO_ACTIVE_OPENCLAW_DIR\n'
fi

test -f "$HOME/.hermes/openclaw-import/workspace/MEMORY.md"
test -f "$HOME/.hermes/openclaw-import/exported-memory/OPENCLAW_MEMORY_COMBINED.md"
test -d "/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/lark-im"
printf 'HERMES_IMPORT_OK\n'
```

This achieves the user's desired independence from OpenClaw while keeping rollback possible. Only consider permanent deletion after the user has used Hermes successfully for a while and still wants cleanup.

## Diagnosing errors after migration

Do not assume post-migration errors are caused by OpenClaw. Check live processes and Hermes logs. In one migration, recurring errors were actually Hermes Feishu/Lark websocket and DNS/network failures, not OpenClaw dependency:

```text
Lark websocket reconnect / no close frame
open.feishu.cn DNS resolution failures
OpenRouter metadata fetch SSL/network errors
openai-codex API call connection errors
```

Useful checks:

```bash
ps aux | egrep 'hermes|openclaw|gateway|node|python' | egrep -v 'egrep'
grep -Rni "error\|exception\|failed\|traceback" "$HOME/.hermes/logs" 2>/dev/null | tail -80 || true
for host in open.feishu.cn openrouter.ai chatgpt.com; do
  dscacheutil -q host -a name "$host" 2>/dev/null | sed -n '1,12p' || true
  python3 - <<PY
import socket
host='$host'
try: print(host, socket.gethostbyname(host))
except Exception as e: print(host, repr(e))
PY
done
hermes gateway status || true
```

If Feishu later reconnects successfully, report it as network/websocket instability rather than a migration failure.

## Related caveat: Hermes image generation is separate from the LLM model

When testing image generation after a model upgrade, do not assume `gpt-5.5` implies working image generation. Hermes's `image_gen` tool may use a separate backend such as FAL/FLUX and can require `FAL_KEY` or a managed gateway. Verify tool implementation and credentials before promising an image was generated.

Quick check:

```bash
hermes tools list | grep -i image
python3 - <<'PY'
import os
for k in ['FAL_KEY','OPENAI_API_KEY','OPENROUTER_API_KEY']:
    print(k, 'set' if os.getenv(k) else 'not_set')
PY
```

If `image_gen` fails with `FAL_KEY environment variable not set`, state that clearly and do not pretend GPT generated an image.

## Recommended final state

```text
Hermes = primary runtime
~/.hermes/openclaw-import = historical archive/source
~/.openclaw = absent or renamed to ~/.openclaw.archive-<timestamp> after explicit user approval/validation
```
