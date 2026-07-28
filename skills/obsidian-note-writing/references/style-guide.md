# Obsidian Style Guide

This guide applies to all Markdown documents in the target Obsidian vault, regardless of folder.

## Topic-Specific Style Override

Generic structure rules apply to all notes, but some topic areas have a stronger personal writing style and should override the default body tone.

For Python / FastAPI / code-learning notes, read and follow:

- `/Users/heytea/Documents/obsidian_note/Codex工作台/Python学习笔记写作风格规范.md`

Use that note as the authority for:

- how to open the explanation
- how much to emphasize "本质"
- whether to explain from code upward
- whether to add overall execution flow
- the preferred teaching-style, explanation-first tone

Do not default those notes to official-doc tone, encyclopedia tone, or generic knowledge-card tone.

## Frontmatter

Use YAML properties:

```yaml
---
title: "Readable title"
source: "URL or relative source"
author: "author or source owner"
published:
created: YYYY-MM-DD
description: "One-sentence summary"
tags: ["tag-one", "tag-two"]
type: "tech-note"
status: "processed"
---
```

`source` is the origin of the individual note. It is not the scope of this convention.

- For self-authored notes: use the vault-relative file path.
- For webpages or clippings: use the original URL.
- For screenshots/files: use the file name or source path.
- For meetings/conversations: use the meeting title, date, or conversation source.

## Body Structure

Default body:

```markdown
# Title

## 摘要

## 核心内容

## 可执行动作

## 相关链接
```

## Note Type Hints

- `clipping`: include source, author, published date, and extracted key points.
- `tech-note`: include concept, workflow, caveats, and examples.
- `project-note`: include background, decision, risks, and next steps.
- `meeting-note`: include conclusion, decisions, action items, and blockers.
- `workflow`: include trigger, inputs, steps, outputs, and verification.
- `diagram`: keep frontmatter, do not force prose sections into drawing files.

## Tags

Use lowercase English tags. Keep them few and stable.

Recommended tags: `codex`, `agent`, `workflow`, `tech-note`, `project`, `meeting`, `clipping`, `diagram`, `todo`, `evergreen`.

## Internal Links

Use `[[internal links]]` to build the graph. Tags help filtering, but links create the strongest note-to-note relationships.

Rules:

- Add links under `## 相关链接`.
- Prefer note titles, for example `[[Codex 启动加载顺序]]`, not fragile relative paths.
- Add 2-5 links only when the relationship is obvious.
- Do not create links to non-existent notes unless the user wants placeholders.
- For attachments, use Obsidian embeds such as `![[assets/image.png]]`.
