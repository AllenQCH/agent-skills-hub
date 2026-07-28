---
name: gitdiagram-style-diagrams
description: Use when the user wants repo-centric technical diagrams in a GitDiagram-like style for AI coding, codebase understanding, or architecture overviews. Do not use for tasks outside this software-development workflow or tasks better handled by a narrower debugging, testing, planning, or review skill.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - diagram
    - gitdiagram
    - repo-map
    - architecture
    - ai-coding
    - visualization
    related_skills:
    - architecture-diagram
    - obsidian
    - hermes-agent
---

# GitDiagram-Style Diagrams

## Overview

Use this skill when Allen wants diagrams that feel closer to **GitDiagram / repository maps** than to a classic Mermaid flowchart or a whiteboard canvas.

This style is best for:
- repo/module structure overviews
- entry points and dependency hotspots
- AI coding prep, where the agent first builds a global map of the codebase
- architecture notes that should look like a technical system map, not a business flowchart

The goal is not maximum prettiness. The goal is a diagram that answers:
- what are the major folders/modules/services?
- how do they connect?
- where are the entry points / hot paths / blast radius?
- what should the agent understand before editing code?

## When to Use

Use this skill when the user asks for any of the following:
- “给我画 repo 图 / 仓库结构图 / 模块图”
- “先把代码库结构摊开给我看”
- “想要像 GitDiagram 那种风格”
- “AI coding 过程中先理解全局，再开工”
- “把系统拆成 repo map / module graph / AI understanding output”

Prefer other styles when:
- the user wants strict text-first maintainability inside markdown → prefer Mermaid
- the user wants presentation/whiteboard/AI canvas style → prefer Eraser-like style
- the user wants fine-grained function call graphs only → pair with code2flow output

## Style Contract

A GitDiagram-style deliverable should usually include these visual blocks:

1. **Repository / folders / packages**
   - left-side or top-level structure panel
   - examples: `apps/web`, `apps/api`, `packages/core`, `scripts/`

2. **Module Graph**
   - central simplified architecture graph
   - examples: Web UI → API → DB, workflow engine, shared core logic

3. **AI Understanding Output**
   - right-side analysis cards such as:
     - Entry Points
     - Hot Paths
     - Dependencies
     - Change Risk / Blast Radius

4. **Then AI Turns It Into Action**
   - optional lower section showing the workflow:
     - understand repo
     - generate flow/diagram
     - write code + verify

## Deliverable Format

Default output should be:
- one standalone `.html` diagram file
- one `.png` preview rendered from the HTML

Recommended save locations:
- ad hoc work: current working directory or user-specified directory
- durable note assets: nearby an Obsidian note or inside a project docs folder

## Local Assets Installed By This Skill

This skill ships with:
- `templates/gitdiagram-style-repo-map.html` — base template example
- `scripts/render_html_to_png.py` — render a local HTML file to PNG using Playwright

## Workflow

1. Gather structure first
   - repo folders / services / major modules
   - key entry points / APIs / jobs / workflows
   - any known hotspots or risk areas

2. Decide scope
   - repo map only
   - repo map + module graph
   - repo map + module graph + AI action lane

3. Generate or edit the HTML
   - start from `templates/gitdiagram-style-repo-map.html`
   - replace labels, panels, and arrows to fit the actual system

4. Render PNG preview
   - use `scripts/render_html_to_png.py`

5. If the user works in Obsidian
   - add/update a note explaining the diagram
   - link the HTML/PNG assets and explain what each panel means

## Command Pattern

Example render command:

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/gitdiagram-style-diagrams/scripts/render_html_to_png.py \
  /path/to/diagram.html \
  /path/to/diagram.png
```

## Common Pitfalls

1. **Making it too much like Mermaid**
   - This style should feel repo-centric and panel-based, not a single flat flowchart.

2. **Trying to show every file**
   - Keep to modules, entry points, dependencies, and risk areas.

3. **No AI interpretation layer**
   - The right-side analysis boxes are important. They show why the map matters to an AI coding workflow.

4. **No rendered preview**
   - Do not stop at the HTML source. Render a PNG so the user can compare styles quickly.

## Verification Checklist

- [ ] HTML file created
- [ ] PNG preview rendered successfully
- [ ] Diagram includes repo/module understanding, not only business flow
- [ ] Labels are adapted to the actual project or use case
- [ ] If requested, an Obsidian note was updated with usage instructions
