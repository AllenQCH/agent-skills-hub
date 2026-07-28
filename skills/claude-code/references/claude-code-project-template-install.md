# Claude Code project-template install pattern

Use this when a user asks to install a Claude Code workspace/template repo that ships `.claude/commands`, `.claude/skills`, `.agents/skills`, Bun CLIs, and LaTeX/PDF generation.

## Workflow

1. **Clone into a durable personal workspace** rather than `/tmp`.
   ```bash
   TARGET="$HOME/<repo-name>"
   git clone https://github.com/<owner>/<repo>.git "$TARGET"
   cd "$TARGET"
   git log -1 --oneline
   ```
   If `git clone` repeatedly fails due to transient GitHub transport errors, do not give up: query the repo metadata for the default branch, then download the codeload zip for that branch and extract it to the same durable target.
   ```bash
   DEFAULT_BRANCH=$(python3 - <<'PY'
import json, urllib.request
meta=json.load(urllib.request.urlopen('https://api.github.com/repos/<owner>/<repo>', timeout=30))
print(meta['default_branch'])
PY
)
   curl -L "https://codeload.github.com/<owner>/<repo>/zip/refs/heads/$DEFAULT_BRANCH" -o /tmp/<repo>.zip
   python3 - <<'PY'
import zipfile
zipfile.ZipFile('/tmp/<repo>.zip').extractall('/tmp')
PY
   mv "/tmp/<repo>-$DEFAULT_BRANCH" "$TARGET"
   ```

2. **Check prerequisites before installing.**
   ```bash
   for cmd in git gh claude bun python3 npm lualatex xelatex pdftotext brew; do
     command -v "$cmd" >/dev/null && echo "OK $cmd $(command -v "$cmd")" || echo "MISSING $cmd"
   done
   claude --version || true
   claude auth status --text || true
   ```
   If Claude Code is installed but auth is missing, report it as the remaining user action; do not try to handle credentials.

3. **Prefer native Bun on Apple Silicon.**
   On arm64 macOS, verify `file $(command -v bun)`. If the active Bun is x86_64 under `/usr/local/bin`, install native Bun under `~/.bun/bin` and put it first on `PATH` before `bun install`:
   ```bash
   curl -fsSL https://bun.sh/install | bash
   export PATH="$HOME/.bun/bin:$PATH"
   file "$(command -v bun)"
   bun --version
   ```
   This avoids architecture-mismatched optional package resolution and illegal-instruction crashes in Bun-based project CLIs. If you already ran `bun install` with the wrong architecture, remove each affected `node_modules` and lockfile, then reinstall with the native Bun first on `PATH`:
   ```bash
   export PATH="$HOME/.bun/bin:$PATH"
   for tool in .agents/skills/*/cli; do
     [ -f "$tool/package.json" ] || continue
     (cd "$tool" && rm -rf node_modules bun.lock bun.lockb && bun install)
   done
   ```

4. **Install per-skill CLI dependencies from repo root.**
   ```bash
   export PATH="$HOME/.bun/bin:$PATH"
   for tool in .agents/skills/*/cli; do
     [ -f "$tool/package.json" ] || continue
     (cd "$tool" && bun install)
   done
   ```

5. **Install a lightweight LaTeX engine when the template requires PDF output.**
   If `lualatex`/`xelatex` are missing, TinyTeX is usually enough for template smoke tests:
   ```bash
   curl -fsSL https://yihui.org/tinytex/install-bin-unix.sh -o /tmp/tinytex-install-bin-unix.sh
   sh /tmp/tinytex-install-bin-unix.sh /tmp --no-path
   export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
   tlmgr install moderncv fontawesome5 fontawesome6 academicons import luatexbase pgf \
     titlesec textpos xltxtra xunicode cite realscripts needspace
   ```
   Add the TinyTeX bin path to the user's shell rc only after the user has approved persistent shell changes.

6. **Verify with real project checks.**
   Prefer the repo's CI-equivalent commands:
   ```bash
   python3 -m unittest discover -s tests -t . -v
   python3 tools/lint_skills.py
   python3 tools/security_guards.py
   for tool in .agents/skills/*/cli; do
     [ -f "$tool/package.json" ] || continue
     (cd "$tool" && bun run typecheck)
   done
   ```
   If Python tests import local modules under a generic top-level package name like `tools` and fail with `ModuleNotFoundError` because a site-packages `tools` package wins import resolution, make the local package explicit and re-run from the repo root:
   ```bash
   [ -d tools ] && [ ! -f tools/__init__.py ] && printf '"""Local project tools package."""\n' > tools/__init__.py
   python3 -m unittest discover -s tests -t . -v
   ```
   For LaTeX templates, compile the example artifacts and assert output exists:
   ```bash
   (cd cv && lualatex -interaction=nonstopmode -halt-on-error main_example.tex)
   (cd cover_letters && xelatex -interaction=nonstopmode -halt-on-error cover_example.tex)
   ```

7. **Run one low-volume CLI smoke test for each important external source.**
   Capture stdout/stderr to files before summarizing so pipelines do not mask non-empty JSON output.

## Reporting

Report:
- install path;
- exact commit/version;
- dependencies installed;
- checks that passed with counts;
- remaining user action, especially `claude auth login` if not authenticated.

Avoid claiming the workspace is fully ready for `/setup` until `claude auth status` confirms login, but do say the local dependencies and repository checks are ready.