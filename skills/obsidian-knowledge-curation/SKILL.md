---
name: obsidian-knowledge-curation
description: 'Use when the user needs the obsidian knowledge curation workflow: Persist researched topics, article timelines, and tool/site capability summaries into an existing Obsidian vault with the user''s local note style, links, and follow-up structure. Do not use for tasks that do not read, write, migrate, or curate durable notes.'
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - obsidian
    - knowledge-base
    - notes
    - research
    - articles
    - curation
    category: note-taking
    related_skills:
    - obsidian
    - llm-wiki
---

# Obsidian Knowledge Curation

Use this when the user wants research results, article lists, timelines, tool capability summaries, or workflow notes **persisted into their existing Obsidian vault** rather than returned only in chat.

This skill is especially useful when:
- The user says "整理一下放到我的 Obsidian"
- You have researched several articles/tools/sites and should turn them into reusable notes
- The user values continuity and wants future efficiency from saved notes
- You need to integrate with an already-structured vault instead of inventing a fresh format

## Core Principle

Do **not** dump raw results into a random markdown file. First orient to the vault's structure and writing style, then write notes that fit the existing system:
- correct folder
- matching frontmatter
- meaningful wikilinks
- concise summary + structure
- useful next-step scaffolding

## Workflow

### 1. Locate the vault

First resolve the Obsidian vault path.

Priority order:
1. `OBSIDIAN_VAULT_PATH` environment variable
2. Known project/user memory about the vault path
3. Search for directories containing `.obsidian`

Example discovery approach:
- inspect environment
- search for `.obsidian` directories under the user's home/documents
- confirm the actual vault root before writing

### 2. Inspect existing note conventions

Before creating any note, inspect nearby notes in the likely destination area.

Check for:
- frontmatter keys (`title`, `source`, `author`, `published`, `created`, `description`, `tags`, `type`, `status`)
- naming conventions (number prefixes, Chinese vs English titles, topic folder layout)
- section structure (摘要 / 核心内容 / 可执行动作 / 相关链接)
- wikilink habits

Never assume a new note format if the vault already has one.

### 3. Choose the right destination folder

Pick a destination that matches the content domain.

Examples:
- tool/site capability notes → tool/skill/automation folders
- article timelines → engineering/research folders
- article-by-article notes → same topic folder as the timeline/index note

When a topic already exists, prefer **connecting** to the existing note tree over creating a disconnected folder.

### 4. Research and verify before writing

For each external topic/site/tool:
- verify the official site or repo
- distinguish official product/specification from adjacent or easily-confused tools
- extract concrete capabilities, not vague claims
- capture the few facts that will matter later

Important lesson learned:
- A familiar name may be overloaded. Example pattern: a user note may describe a tool as a browser automation route, while the official site turns out to describe a specification/standard instead. Verify before persisting.

### 5. Write the note in the vault's style

Use the existing frontmatter and section structure.

A good note usually contains:
- what it is
- why it matters
- concrete capabilities / classification
- where it fits in the user's workflow
- what it is **not**
- related links to existing notes
- optional next actions / TODOs

For article collections, prefer:
- a timeline/index note
- one-line summaries per article
- layered interpretation (why it matters, how to read it, common themes)

For tool/site notes, prefer:
- official links
- exact capability list
- ideal use cases
- non-goals / common confusions
- workflow relevance

### 6. Patch nearby notes if they contain incorrect framing

If the vault already has a note that partially covers the topic but with misleading framing, patch it immediately.

Typical pattern:
- create a dedicated note for the corrected topic
- patch the older note with a short correction and link to the dedicated note

This keeps the vault internally consistent.

### 6.5. When writing into a numbered topic series, maintain the local topology

If the destination folder is a numbered concept series (for example `01-...`, `02-...`, `03-...` in one topic area), do not treat the new note as isolated.

Do this explicitly:
- inspect adjacent notes before writing so you understand the local concept ladder
- choose the next consistent filename/number instead of inventing an unrelated name
- add reciprocal wikilinks between the new note and its immediate neighbors when conceptually related
- if the new topic is literature-heavy, prefer creating **two notes**:
  1. a main concept note
  2. a timeline / reading-list companion note
- patch the nearest existing hub note so the new note is discoverable from the older concept chain

This is especially important for research topics that extend an existing sequence like prompt → context → harness → loop. The value is not just the new note itself, but preserving the navigable progression.

### 6.6. For emerging topics, separate concept synthesis from source chronology

When a topic is new, fast-moving, or buzzword-heavy, do not mix everything into one note.

Preferred structure:
- **main concept note**: definition, first-principles framing, distinctions, practical use
- **timeline note**: sources, dates, one-line takeaway per article, points of disagreement

This separation keeps the concept note readable while preserving provenance and later update paths.

### 7. Scheduled source monitoring into Obsidian

When the user asks to "定期整理" a source site into an Obsidian topic folder, turn the one-off curation workflow into a repeatable monitored pipeline instead of only writing today's notes.

Recommended pattern:
1. Inspect the existing destination folder, index note, and nearby note style before creating the schedule.
2. Build a small deterministic scan script under `~/.hermes/scripts/` that fetches the official source, extracts canonical article URLs, and compares them with URLs already present in the destination notes.
3. Have the script output compact JSON: source URL, vault path, destination dir, total articles, covered count, missing/backlog list, and errors if fetch fails.
4. Create a Hermes cron job with that script as pre-context; the agent prompt should process missing/new articles, write notes in the existing local style, update `_index.md`, and maintain a lightweight watch/backlog note in the destination folder.
5. For a large backlog, instruct the cron job to process a bounded batch per run (for example at least 4 items), so it converges without producing one huge brittle run.
6. The watch note should record the cron job ID, script path, schedule, current coverage, backlog, and sorting/curation rules so future sessions can audit or adjust the job.
7. When the user later changes the schedule or delivery policy, update all three places in lockstep: the Hermes cron schedule, the cron prompt's human-readable timing text, and the Obsidian watch/backlog note. Then verify with `cronjob list` before reporting success.

Session reference: `references/anthropic-engineering-watch.md` captures the Anthropic Engineering implementation pattern.

### 8. Open the note for the user

On macOS, after writing the note, open it in Obsidian (or via the vault path) so the user can immediately inspect it.

Example pattern:
- `open -a Obsidian '/absolute/path/to/note.md'`

Verify success via exit code.

### 8. Save only compact, durable memory

If the task reveals a durable environment fact, save it to memory.

Good example:
- Obsidian vault path on this machine

Do **not** try to save long lists of sites/articles/tools into Hermes memory if memory is tight. Persist those in Obsidian instead and keep memory compact.

## Output expectations

When reporting back to the user, include:
- exact file path written
- whether any existing note was updated
- what was researched/verified
- whether the note was opened
- suggested next note(s) to create

## Pitfalls

- Don’t write into Obsidian before locating the real vault root.
- Don’t invent a new markdown style when the vault already has one.
- Don’t trust prior assumptions about a tool/site category without checking official sources.
- Don’t save bulky site lists into Hermes memory; store them in Obsidian instead.
- Don’t leave a new note isolated — add wikilinks to nearby concepts.

## Reusable patterns

### A. Article timeline note
Use for 3+ related articles:
- sort by publish date
- one-line takeaway per article
- common themes
- recommended reading order
- related concept links

### B. Tool capability note
Use for a tool/spec/site:
- official site/repo
- what it is
- concrete capability list
- best-fit scenarios
- non-goals / common confusion
- relationship to current workflow

### C. Topic hub upgrade
If a weak placeholder note exists:
- upgrade it from `raw` to `processed`
- add summary + scope + linked index note
- leave TODOs for deeper expansion
