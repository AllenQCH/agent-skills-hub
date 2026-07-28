---
name: obsidian-note-writing
description: Create, normalize, or improve Obsidian notes with consistent YAML properties, folder routing, tags, summaries, sections, source attribution, attachments, and diagram choices. Use when the user asks to put content into Obsidian, write an Obsidian note, organize notes, convert webpages/screenshots/conversations into notes, normalize existing vault notes, create knowledge cards, or decide where a note belongs in an Obsidian vault.
---

# Obsidian Note Writing

## Default Vault

Use `/Users/heytea/Documents/obsidian_note` as the default vault unless the user specifies another vault.

This style applies to every Markdown document in the Obsidian vault, regardless of folder. `Codex工作台/` is only one destination folder, not the scope of the convention.

## Workflow

1. Identify the note source: conversation, URL, screenshot, article, project context, meeting, technical explanation, or diagram.
2. Choose the note type and destination folder using `references/folder-routing.md`.
3. Create or update YAML properties using `references/style-guide.md`.
4. Before writing the body, check whether the topic has a more specific personal style convention that should override the generic note tone. For Python / FastAPI / code-learning notes, read `/Users/heytea/Documents/obsidian_note/Codex工作台/Python学习笔记写作风格规范.md` and follow it for body style.
4. Write the note with summary-first structure. Preserve source attribution and avoid fabricating missing facts.
5. Add stable tags and useful `[[internal links]]` so the Obsidian graph shows real relationships.
6. Use templates from `assets/templates/` when creating new notes.
7. For diagrams, choose Mermaid for maintainable simple flows and Excalidraw for more readable visual explanations.
8. Verify the file exists, frontmatter is valid enough for Obsidian to parse, and new internal links resolve.

## Required Properties

Every normal Markdown note in the vault should include:

```yaml
---
title:
source:
author:
published:
created:
description:
tags:
type:
status:
---
```

Allowed `type` values: `clipping`, `tech-note`, `project-note`, `meeting-note`, `workflow`, `diagram`, `idea`, `note`.

Allowed `status` values: `raw`, `processed`, `evergreen`, `archived`.

## Required Sections

For normal notes, prefer:

```markdown
# Title

## 摘要

## 核心内容

## 可执行动作

## 相关链接
```

Do not force these sections into Excalidraw drawings or files whose plugin format would be damaged. For `.excalidraw.md`, update only safe frontmatter fields unless the user explicitly asks to edit the drawing.

## Writing Rules

- Put the conclusion or summary before detailed content.
- Keep headings shallow: use `##` and `###`, avoid deeper nesting unless necessary.
- Use short paragraphs and bullets.
- If the note is fundamentally a Python / FastAPI / code-learning note, treat `/Users/heytea/Documents/obsidian_note/Codex工作台/Python学习笔记写作风格规范.md` as the body-style authority. In those cases, prefer explanation-first, teaching-style prose over generic knowledge-base structure.
- Preserve original source links in `source` and/or `相关链接`.
- Treat `source` as the origin of the individual note, not the scope of the note-writing convention. For self-authored notes, use the vault-relative file path; for external content, use the original URL, file, meeting, screenshot, or conversation source.
- If information is unavailable, leave the field empty or write `待确认`; do not invent it.
- Prefer English lowercase tags, for example `codex`, `agent`, `workflow`, `tech-note`, `project`, `clipping`.
- Save attachments under `assets/` and reference images as `![[assets/name.png]]`.
- Add 2-5 related `[[internal links]]` under `## 相关链接` when clear relationships exist. Prefer existing note titles over path-like links.
- Do not add speculative links. A sparse accurate graph is better than dense noise.

## Numbered Topic Organization

When organizing or normalizing an Obsidian topic area, prefer numbered filenames and directories so related notes sort together in the file tree.

Default pattern:

```text
NN-Topic/
  NN-00-Topic-索引.md
  NN-01-Topic-总览.md
  NN-02-Topic-子主题.md
  NN-03-Topic-子主题.md
  NN-99-Topic-原始长文归档.md
```

Rules:

- Use two-digit sequence numbers such as `01`, `02`, `03`.
- Put the topic name after the number, for example `02-01-RAG-总览` and `02-02-RAG-架构全景`.
- Use `00` for index pages, `01` for overview pages, and `99` for raw imports or original long-form archives.
- For subtopics under the same topic, keep the same topic prefix: `02-03-RAG-Embedding向量化`, `02-04-RAG-Retrieval召回与混合检索`.
- Prefer renaming internal links to the numbered target names. Add `aliases` for old note names only as compatibility helpers, not as the primary linking style.
- Do not renumber a mature folder casually; preserve stable links unless a user asks for reorganization or the current structure is clearly messy.

## Bulk Normalization

When normalizing an existing vault:

1. Inspect Git status first.
2. Do not overwrite existing frontmatter keys.
3. Add missing required properties.
4. Normalize tags from folder, type, title, and obvious topic keywords.
5. Add conservative internal links between clearly related notes.
6. Add missing standard sections only to normal Markdown notes.
7. Preserve plugin files such as Excalidraw.
8. Report changed file count, internal link count, unresolved link count, and notable risks.

## Resources

- `references/folder-routing.md`: folder selection rules.
- `references/style-guide.md`: property and writing conventions.
- `assets/templates/`: reusable note templates.

## Skill Notes

When creating, updating, merging, archiving, or deleting any Codex skill, update `/Users/heytea/Documents/obsidian_note/Codex工作台/Skill放在哪里以及怎么维护.md` in the same turn. Record the skill name, path, purpose, action taken, and date.
