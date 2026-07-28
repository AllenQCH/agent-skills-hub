---
name: study-repo-curation
description: 'Use when the user needs the study repo curation workflow: Build a structured local study repository for a topic from curated web resources, with numbered module folders, article note files, and optional GitHub publishing. Do not use for tasks that do not read, write, migrate, or curate durable notes.'
---

# Study Repo Curation

Use this when the user wants a topic turned into a local learning repository they can study over time — especially when they ask for folders by module/category, numbered reading files, note templates, and optional GitHub sync.

## What this skill produces

A durable, human-browsable study repo with:
- one top-level topic folder
- module folders named with numeric prefixes (for reading order)
- article files named with numeric prefixes inside each module
- one `_index.md` per module
- one root `README.md` with suggested learning order
- each article file prefilled with link, why-it-matters, reading focus, and note placeholders

## Workflow

1. **Identify learning modules from the source domain**
   - Use the site's information architecture first (top nav, hub pages, sections, categories).
   - Prefer 4–7 class-level modules rather than many tiny folders.
   - If the site already separates Engineering / Research / Tutorials / Policy-style areas, mirror that structure.

2. **Curate representative articles per module**
   - Pick the classic / foundational / high-signal entries, not every recent post.
   - Prefer 3–5 items per module for a first-pass repo unless the user asked for exhaustive coverage.
   - Use numbered filenames like `01-...`, `02-...` to encode learning order.

3. **Write article note files as study stubs, not copied articles**
   Each file should include:
   - title
   - original link
   - why it is worth reading
   - 3–5 reading focus bullets
   - a note area for the user's own summary/questions/transferable ideas

4. **Create navigation scaffolding**
   - Root `README.md`: what the repo is, module list, suggested study order.
   - Module `_index.md`: links to the numbered files in that folder.

5. **Keep names stable and readable**
   - Folder names: `01-Engineering`, `02-Research` style.
   - File names: concise English slug plus numbering.
   - Repo root can use the user’s preferred language or topic wording.

6. **Treat GitHub publish as a separate side-effecting phase**
   - Build and verify the local repo first.
   - Then create/init/push the Git repo only after explicit confirmation or when clearly requested.
   - If auth/approval blocks the push, report local completion first and ask for the go-ahead to continue publishing.

## Output pattern

When reporting back, separate:
- **local structure created**
- **sample files verified**
- **GitHub publish status** (done / waiting for approval / blocked by auth)

Do not imply the GitHub upload is complete just because the local files exist.

## Pitfalls

- Do not dump raw article text into the repo unless the user explicitly asked for archives or summaries.
- Do not make one folder per article; keep modules class-level.
- Do not skip `_index.md` and `README.md`; the study repo should be navigable without opening every file.
- Do not silently publish to GitHub while still uncertain about repo visibility; default to safer handling and state whether the next step is local-only or remote.

## Support files

- `references/anthropic-learning-repo-example.md` — concrete example of a study repo structure distilled from an Anthropic-learning session.
