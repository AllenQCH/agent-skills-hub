---
name: internal-gitlab-downloader
description: Use when a user needs to discover, clone, mirror, or organize many private internal GitLab repositories by group, subgroup, business module, or company-specific repository catalog.
---

# Internal GitLab Downloader

## Overview

Use this skill to turn a private GitLab group or internal repository catalog into a local, grouped checkout tree. The core rule is: discover repos from the most authoritative catalog available, then clone by SSH while preserving GitLab namespace paths.

## Required Access

- Network access to GitLab and any internal repository catalog.
- GitLab SSH login works: `ssh -T git@<host>`.
- The account has project-level access for every repo to clone.
- Optional GitLab API token when using native GitLab group discovery.
- Local write permission to the destination directory.

## Workflow

1. Confirm the destination root. Prefer a dedicated folder such as `~/code/codex-downloads`.
2. Discover repos using the strongest available source:
   - GitLab API group listing with `--gitlab-url`, `--group`, and token env.
   - Company catalog adapter, if one exists.
   - Existing local remotes with `--scan-remotes`.
   - Explicit URL list with `--repo-file`.
3. Filter by namespace prefixes, not only keywords, when possible.
4. Run with `--dry-run` first for new companies or unfamiliar groups.
5. Clone with SSH and preserve paths under the destination root.
6. Verify repo count, remotes, and failures before claiming completion.

## Downloader Script

Use the bundled script:

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/internal-gitlab-downloader/scripts/internal_gitlab_download.py --help
```

Common patterns:

```bash
# GitLab API discovery
GITLAB_TOKEN=... python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/internal-gitlab-downloader/scripts/internal_gitlab_download.py \
  --gitlab-url https://git.example.com \
  --group service/scm \
  --include-prefix service/scm/ims \
  --dest ~/code/codex-downloads \
  --dry-run

# Explicit URL list
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/internal-gitlab-downloader/scripts/internal_gitlab_download.py \
  --repo-file repos.txt \
  --dest ~/code/codex-downloads

# HeyTea BlueKing DevOps catalog, when the local bug-killer package exists
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/internal-gitlab-downloader/scripts/internal_gitlab_download.py \
  --heytea-bk-project-code yc9e25 \
  --include-prefix service/scm/dinghuotong \
  --dest /Users/heytea/Documents/myHeytea/code/codex-downloads
```

## Quick Reference

| Need | Option |
|---|---|
| Preserve GitLab folder structure | default behavior |
| Avoid downloading before review | `--dry-run` |
| Download selected business modules | repeat `--include-prefix` |
| Use full history | `--depth 0` |
| Reuse local known repos | `--scan-remotes <path>` |
| Use private GitLab API | `--gitlab-url`, `--group`, `--token-env` |

## Common Mistakes

- Treating a group URL as a repo URL. `service/scm` is a group; clone URLs usually include a project below it.
- Searching only by keyword and missing shared/domain packages. Prefer prefix filtering from a full catalog.
- Assuming catalog visibility equals Git clone permission. Always verify SSH clone results.
- Mixing downloaded repos into an existing project tree. Use a dedicated downloads root.
