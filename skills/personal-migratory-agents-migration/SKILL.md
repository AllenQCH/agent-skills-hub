---
name: personal-migratory-agents-migration
description: 'Use when the user needs the personal migratory agents migration workflow: Plan and execute a clean migration of personal AI agent capabilities across machines or employment transitions. Use when Allen asks how to back up, migrate, or preserve Hermes/Codex/Claude/skills/dotfiles/Obsidian agent workflows while excluding company assets and credentials. Do not use for ordinary direct execution that does not need an autonomous agent, CLI delegate, migration, or Hermes runtime workflow.'
---

# Personal Migratory Agents Migration

## Trigger
Use this when the user wants to migrate or back up their personal AI agent capabilities, especially Hermes/Codex/Claude skills, prompts, workflows, dotfiles, and Obsidian methods, across machines or before leaving a work environment.

## Core principle
Migrate **capability**, not **authority**:

- Capability assets: skills, prompts, workflows, templates, dotfiles, install/restore scripts, clean configuration examples, personal methodology notes.
- Authority/credentials: API keys, tokens, SSH private keys, OAuth refresh tokens, cookies, login state. Treat these as re-generable and do **not** migrate them by default.
- Company assets: source code, business docs, internal APIs, chats, tickets, data, credentials, kubeconfigs, private registry tokens. Do **not** migrate.

Use this framing in replies:

> Repo stores how to rebuild the capability, not the permissions already granted.

## Recommended architecture

1. **GitHub private repo** such as `personal_migratory_agents`
   - Store only clean, versionable capability assets.
   - Good for: `~/.hermes/skills`, clean Hermes config templates, Codex/Claude rules, dotfiles, Brewfile, restore scripts, health checks. Include sanitized Obsidian agent notes only if Allen has not already delegated Obsidian to a separate sync pipeline.
   - Bad for: `.env`, private keys, OAuth tokens, raw session DBs, logs, company context.

2. **Re-auth checklist instead of credential migration**
   - New machine regenerates/re-authorizes all credentials.
   - SSH keys should usually be newly generated.
   - OAuth should be re-login/re-authorize.
   - Old tokens/keys should be revoked after migration.

3. **Optional encrypted raw cold backup**
   - Purpose: recover missed personal methodology, not restore old permissions.
   - Encrypt locally with age/GPG before storage.
   - Store on iCloud Drive or external disk.
   - Do not commit raw backups to Git.
   - Do not directly restore raw `.hermes`, `.codex`, `.claude` into a new environment.

## Suggested clean repo layout

```text
personal_migratory_agents/
├── README.md
├── Brewfile
├── install.sh
├── restore.sh
├── healthcheck.sh
├── .gitignore
├── hermes/
│   ├── skills/
│   ├── config.example.yaml
│   └── cron/
├── codex/
│   ├── AGENTS.md
│   └── prompts/
├── claude/
│   └── CLAUDE.md
├── dotfiles/
│   ├── zshrc
│   ├── zprofile
│   └── gitconfig
├── scripts/
│   ├── backup-clean.sh
│   ├── redact-scan.sh
│   └── restore-hermes.sh
├── templates/
│   ├── env.template
│   ├── hermes-config.template.yaml
│   └── mcp-config.template.yaml
└── docs/
    ├── asset-boundary.md
    ├── redaction-policy.md
    ├── re-auth-checklist.md
    └── recovery-runbook.md
```

## GitHub private repo allowlist

Commit:

- Hermes skills and reusable agent workflows.
- Config examples/templates, not real configs with tokens.
- Brewfile and install scripts.
- Dotfiles after scanning for tokens and company paths.
- Codex/Claude generic rules, prompts, skills, and agent definitions.
- Exclude Codex runtime/session artifacts, including `~/.codex/sessions/` and session index helpers such as `~/.codex/commands/sessionids.md`.
- Sanitized Obsidian notes about AI agents/methodology.
- Redaction policy and recovery runbook.

Do not commit:

- `.env`, `.env.*`, `auth.json`, OAuth caches.
- SSH private keys: `id_rsa`, `id_ed25519`, `*.pem`, `*.key`.
- API keys/tokens/secrets.
- `~/.kube/config`, company Docker/npm registry auth.
- Raw Hermes/Codex/Claude sessions, logs, caches, SQLite DBs.
- Company repos, PRDs, handoff docs, chats, tickets, internal service names/data.

## Minimum `.gitignore`

```gitignore
# Secrets
.env
.env.*
*.key
*.pem
*.p12
*.pfx
id_rsa
id_ed25519
*.token
*.secret
auth.json
secrets/
credentials/

# Agent runtime state
sessions/
logs/
cache/
tmp/
*.sqlite
*.db
*.db-wal
*.db-shm
trajectory/
trajectories/

# Raw backups
*.tar
*.tar.gz
*.zip
*.age
raw/
backup/
archives/

# Company/work
HeyTea/
company/
work/
projects/
repos/

# macOS
.DS_Store
```

## Re-auth checklist template

Create `docs/re-auth-checklist.md`:

```markdown
# Re-auth Checklist

## AI Providers
- [ ] OpenRouter: create new API key
- [ ] Anthropic: create new API key
- [ ] OpenAI: create new API key

## GitHub / Git
- [ ] Generate new SSH key: `ssh-keygen -t ed25519 -C "personal-email@example.com"`
- [ ] Add public key to GitHub
- [ ] Test: `ssh -T git@github.com`
- [ ] Remove old keys from GitHub after migration

## Hermes
- [ ] Create `.env` from `templates/env.template`
- [ ] Fill provider keys generated on new machine
- [ ] Restore clean skills
- [ ] Run healthcheck

## MCP / Messaging
- [ ] Re-login or re-authorize each personal integration
- [ ] Re-create bot/webhook only if personal and still needed
- [ ] Do not restore company tokens or OAuth state
```

## Redaction scanning
Before committing or packaging, scan clean assets for:

```text
token secret password BEGIN PRIVATE KEY AKIA
heytea 喜茶 gitlab kube prod staging mysql redis
feishu lark dingtalk webhook oauth bearer
```

If a match appears, classify it:

- Company code/data/credentials: remove, do not migrate.
- Personal credential: omit and regenerate on the new machine.
- Company name/path in methodology: sanitize into a generic example.
- False positive in a template: keep only if clearly placeholder text.

## Reusable safe-sync implementation pattern

When Allen asks to operationalize the backup, prefer a conservative **staging repo + sync script + cron** pattern rather than copying live agent directories wholesale.

1. Create/maintain a local staging folder such as `/Users/<user>/Documents/personal_migratory_agents` with:
   - `README.md` documenting capability-vs-authority boundaries.
   - `.gitignore` blocking secrets, runtime DBs, logs, raw backups, company/work paths.
   - `docs/asset-boundary.md` and `docs/re-auth-checklist.md`.
   - `scripts/sync_personal_migratory_agents.sh` as the single controlled sync entrypoint.
2. The sync script should:
   - Use explicit allowlists for personal capability assets.
   - Copy Hermes skills and generalized memory/config **templates**, not `.env`, OAuth caches, tokens, runtime DBs, raw sessions, logs, or company repos.
   - Include selected Obsidian methodology/AI-agent notes only when they are personal/generalized and there is no separate Obsidian sync job. If Allen says Obsidian already has its own scheduled sync, explicitly exclude Obsidian here to avoid duplicate/competing sync pipelines.
   - Emit a manifest/report of copied files and skipped categories.
   - Run a redaction scan before declaring success.
3. Verify after first run:
   - Inspect `README.md`, `.gitignore`, `docs/`, and sync manifest.
   - Confirm no git repo is initialized/pushed until Allen reviews the staged files.
   - If `git status` says “not a git repository,” that is acceptable before the private GitHub repo is intentionally initialized.
4. For automation:
   - Create a daily cronjob that runs the sync script and reports the result.
   - The cron prompt must be self-contained and must not recursively schedule more cron jobs.
   - Keep delivery to `origin` unless Allen explicitly asks to post sync reports elsewhere.
5. Next step after local validation:
   - Initialize a **private** GitHub repo only after review.
   - Push the staging folder as the clean source of truth.
   - Re-authenticate integrations on new machines; never restore old credentials as a shortcut.

## Answer structure for exploration requests
For Allen, use first-principles plus Qian Xuesen-style systems framing:

1. Goal
2. Boundary
3. Elements
4. Structure
5. Mechanism
6. Constraints
7. Plan
8. Verification
9. Iteration

Keep the recommendation direct and practical.
