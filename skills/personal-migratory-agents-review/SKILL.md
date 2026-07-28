---
name: personal-migratory-agents-review
description: 'Use when the user needs the personal migratory agents review workflow: Review Allen''s personal_migratory_agents export for safe private GitHub migration: ensure no company assets, no credentials or permission assets, and only personal Agent capability assets remain. Use when Allen asks to review /Users/[user]/Documents/personal_migratory_agents or mentions personal_migratory_agents migration/review. Do not use for tasks outside this software-development workflow or tasks better handled by a narrower debugging, testing, planning, or review skill.'
---

# Personal Migratory Agents Review Workflow

## Trigger
Use this skill when Allen asks to review `/Users/<user>/Documents/personal_migratory_agents` or the `personal_migratory_agents` migration/export before GitHub/private repo setup.

## Core goals
Confirm three things:
1. No company assets.
2. No keys, tokens, permissions, sessions, or credential assets.
3. Remaining content is genuinely Allen's personal Agent capability asset.

Do **not** begin with a full directory scan. Follow the ordered review below.

## Review order

### 1. Read boundary docs first
Open/read:
- `/Users/<user>/Documents/personal_migratory_agents/README.md`
- `/Users/<user>/Documents/personal_migratory_agents/docs/asset-boundary.md`

Verify:
- It stores capabilities, not permissions.
- Obsidian is explicitly excluded.
- Company code/docs/credentials are explicitly excluded.
- Future machine migration uses re-authorization, not migrating old tokens.

If boundary language feels uncomfortable, too specific, or company-revealing: edit/delete/generalize it.

### 2. Check sync manifest
Open/read:
- `/Users/<user>/Documents/personal_migratory_agents/SYNC_MANIFEST.md`

Expected includes: Hermes skills, Hermes memories, Hermes scripts, Codex skills, Codex rules, Codex commands, Codex agents, Claude skills, dotfiles, config templates, re-auth checklist.

Expected excludes: `.env`, API keys, tokens, OAuth cache, SSH private keys, raw sessions, logs/caches/runtime DB, Obsidian, company repos, company docs, company credentials, Codex sessions.

If a migrated category should not be migrated, add it to exclude rules.

### 3. Prioritize risk findings
Open/read:
- `/Users/<user>/Documents/personal_migratory_agents/REVIEW_FINDINGS.txt`

Triage rules:
- API key / token / secret / password: must delete.
- Company project name / internal system name / internal domain: delete or generalize.
- Personal methodology that occasionally mentions company name: preferably generalize.
- Placeholders such as `YOUR_API_KEY`: can keep.
- Skill names with obvious internal systems: judge if they are generalized personal capabilities; otherwise delete/generalize.

Decision test:
- Would Allen feel uncomfortable if this file existed in a future private GitHub repo?
- Would the content still be needed after changing jobs?
- Could someone infer company internal systems/process/data from it?

If any answer is yes, delete or generalize.

### 4. Review Hermes memories line by line
Open/read:
- `/Users/<user>/Documents/personal_migratory_agents/hermes/memories/MEMORY.md`
- `/Users/<user>/Documents/personal_migratory_agents/hermes/memories/USER.md`

`USER.md` can usually keep long-term preferences such as Allen's name, Chinese-first communication, direct/practical style, Mac + iPhone, Obsidian habits, stock-analysis preferences, and Agent workflow preferences.

Delete or generalize: phone numbers, company identity, internal orgs, coworker names, specific group names, company systems, internal paths, token/auth state.

`MEMORY.md` can keep Hermes as primary assistant runtime, OpenClaw as historical archive, Obsidian vault path if personal, minimal-permission migration preference, and Feishu/Lark/Yahoo Finance MCP generic usage experience if personal and generalized.

Delete or generalize: company services/projects/APIs, company group or robot IDs, personal/company access tokens, concrete `chat_id`, `open_id`, OAuth/session state.

Judgment: keep only if it helps reproduce personal capability; remove if it is only current-company permissions/context.

### 5. Review dotfiles
Open/read:
- `/Users/<user>/Documents/personal_migratory_agents/dotfiles/zshrc`
- `/Users/<user>/Documents/personal_migratory_agents/dotfiles/zprofile`
- `/Users/<user>/Documents/personal_migratory_agents/dotfiles/gitconfig`

Search for: `token`, `secret`, `password`, `key`, `bearer`, `auth`, `cookie`, `heytea`, `gitlab`, `kube`, `prod`, `staging`, `mysql`, `redis`.

Verify no exported API keys, company registry/GitLab addresses, kube contexts, internal DB addresses, or private/company paths.

Can keep generic aliases, PATH config, shell habits, Git config, and tool initialization.

### 6. Skim skills/agents by directory name, then inspect suspicious ones
Open/list:
- `/Users/<user>/Documents/personal_migratory_agents/hermes/skills`
- `/Users/<user>/Documents/personal_migratory_agents/codex/skills`
- `/Users/<user>/Documents/personal_migratory_agents/codex/agents`
- `/Users/<user>/Documents/personal_migratory_agents/claude/skills`

Usually keep generic capability categories: `api-design`, `backend-patterns`, `bug-killer`, `coding-standards`, `database-migrations`, `deployment-patterns`, `github`, `mcp`, `obsidian-note-writing`, `python-testing`, `security-review`, `release-workflow`, `multi-agent-framework`.

Pay special attention to names like: `internal-*`, `company-*`, `heytea-*`, `gitlab-*`, `sso-*`, `dbauto-*`, `trace-log-*`, `alidocs-*`, `dws-*`.

Judge whether each is personal generalized capability, whether it contains internal addresses/process/data, whether it has value after leaving the environment, and whether it can be generalized into enterprise-system operation guidance. Delete if company-specific.

### 7. Check forbidden dirs/files
These should not exist in the final repo:
- `obsidian/`
- `sessions/`, `session/`
- `logs/` (local review logs may exist but should not be committed)
- `cache/`, `tmp/`, `raw/`, `backup/`, `archives/`
- `.env`, `.env.*`
- `*.sqlite`, `*.db`
- `*.pem`, `*.key`
- `id_rsa`, `id_ed25519`

Known note: `obsidian/` was previously confirmed absent. `logs/` may exist during local review but should be deleted before push or added to `.gitignore`.

### 8. GitHub private repo preflight
Confirm before initializing/pushing:
- `REVIEW_FINDINGS.txt` handled or confirmed false positive.
- `MEMORY.md` / `USER.md` contain no sensitive content.
- dotfiles contain no tokens/internal addresses/company paths.
- Codex sessions excluded.
- Obsidian excluded.
- logs not committed.
- `.gitignore` is strict enough.
- repo will be private.
- old permissions/tokens are not migrated; new machine will re-authorize.

## Output style
Produce a practical human-confirmation list. If requested, make a `待人工确认清单` grouped by high / medium / low risk, with each item ready for Allen to answer: 保留 / 删除 / 泛化.
