---
name: openai-codex-release-monitoring
description: 'Use when the user needs the openai codex release monitoring workflow: Monitor Codex CLI releases and OpenAI model/news updates using npm, GitHub Releases, and OpenAI RSS when normal docs pages are blocked by Cloudflare. Do not use for ordinary direct execution that does not need an autonomous agent, CLI delegate, migration, or Hermes runtime workflow.'
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - OpenAI
    - Codex
    - Releases
    - Monitoring
    - RSS
    - GitHub
    - npm
    related_skills:
    - codex
    - blogwatcher
---

# OpenAI Codex Release Monitoring

Use this skill when the user wants to know:
- whether Codex has a new version
- what changed in recent Codex releases
- whether OpenAI shipped new GPT/o-series models
- how to automate reminders or auto-updates for Codex

## Why this skill exists

OpenAI docs/help pages are often protected by Cloudflare and may return `403` or browser challenges to CLI/browser automation. In practice, these sources worked reliably:
- npm registry for published `@openai/codex` versions
- GitHub Releases API for Codex changelogs
- OpenAI News RSS for model and product announcements

## Reliable sources

### 1) Installed Codex version
If `codex --version` is broken, inspect the package directly:

```bash
command -v codex
node -p "require('/path/to/node_modules/@openai/codex/package.json').version"
```

If the global path is unknown, first locate the binary and derive the package path.

### 2) Latest Codex version from npm

```bash
npm view @openai/codex version time --json
```

This gives the current published version plus a release timestamp map.

### 3) Codex changelog from GitHub Releases
Prefer the GitHub API over scraping pages:

```bash
curl -L -H 'Accept: application/vnd.github+json' -H 'User-Agent: Hermes' \
  'https://api.github.com/repos/openai/codex/releases?per_page=10'
```

For a specific release body:

```bash
curl -L -H 'Accept: application/vnd.github+json' -H 'User-Agent: Hermes' \
  'https://api.github.com/repos/openai/codex/releases/tags/rust-v0.124.0'
```

Useful fields:
- `name`
- `tag_name`
- `published_at`
- `prerelease`
- `body`

## OpenAI model/news monitoring

### Preferred source: OpenAI News RSS

```bash
curl -L 'https://openai.com/news/rss.xml'
```

Filter items mentioning terms like:
- `GPT`
- `Codex`
- `o3`
- `o4-mini`
- `GPT-4.1`
- `GPT-5`

This is much more reliable than trying to scrape:
- `platform.openai.com/docs/changelog`
- `help.openai.com` release notes pages
- `openai.com/index/...` article pages directly

## Known pitfalls

### Cloudflare blocks many OpenAI pages
These may fail with `403` or browser challenges:
- `help.openai.com/en/articles/...`
- `openai.com/index/...`
- `platform.openai.com/docs/changelog`

If that happens, do **not** keep retrying the same scraping path. Switch to:
- OpenAI RSS
- GitHub API
- npm registry

### Broken local Codex install
A local install may have the correct npm version but still fail to run, e.g. missing optional platform package such as:
- `@openai/codex-darwin-x64`

In that case report both facts separately:
- installed package version
- runtime health status

Example repair:

```bash
npm install -g @openai/codex@latest
```

Then verify again with `codex --version`.

## Suggested reporting format

When summarizing for the user, separate into:
1. **Local installed version**
2. **Latest upstream Codex version**
3. **Recent Codex changes**
4. **Recent GPT/model updates**
5. **Recommended action** (do nothing / notify only / upgrade now)

## Automation ideas

### Notify-only cron
Create a cron job that periodically:
- checks `npm view @openai/codex version time --json`
- checks GitHub Releases API
- checks `https://openai.com/news/rss.xml`
- sends a concise summary to the user

### Auto-upgrade Codex
Only do this with explicit user approval. Safe pattern:
1. detect new version
2. run `npm install -g @openai/codex@latest`
3. verify `codex --version`
4. report success/failure and any dependency errors

## Verification checklist
- confirm local version from package metadata if CLI is broken
- confirm upstream latest version from npm
- confirm changelog from GitHub API
- confirm model/news updates from OpenAI RSS
- explicitly mention if direct OpenAI docs pages were inaccessible due to Cloudflare
