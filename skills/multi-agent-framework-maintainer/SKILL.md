---
name: multi-agent-framework-maintainer
description: Use when the user wants to continue, maintain, refactor, document, or extend the personal multi-agents framework in ~/.codex, especially when they mention multi-agents, four-layer architecture, control/stage/tool/gate, config.toml registration, agent layering, active vs draft state, or resuming the framework in a new session without repeating all context.
---

# Multi-Agent Framework Maintainer

Use this skill as the continuation entry for the user's personal multi-agents framework.

## What this skill is for

Apply this skill when the user says things like:

- continue my multi-agents framework
- maintain the four-layer agent architecture
- keep working on control / stage / tool / gate
- update `~/.codex/config.toml`
- organize agents by layer
- continue from the previous multi-agent discussion in a new session

This skill is not for general software architecture discussion. It is for the user's local Codex multi-agent system and its surrounding docs.

## First-read files

Before proposing changes or editing files, read only the core sources below and treat them as the current truth:

1. `/Users/heytea/Documents/myHeytea/codex-workspace/AGENTS.md`
2. `/Users/heytea/.codex/config.toml`
3. `/Users/heytea/.codex/agents/README.md`
4. `/Users/heytea/.codex/agents/docs/README.md`
5. `/Users/heytea/Documents/obsidian_note/my-multi-agents/00-先看这里/my-multi-agents总览.md`
6. `/Users/heytea/Documents/obsidian_note/my-multi-agents/00-先看这里/当前阶段和下一步.md`

Read more only if the current task needs it.

## Working assumptions

- `~/.codex/config.toml` is the runtime source of truth.
- Only agents registered in `~/.codex/config.toml` count as active.
- Draft files, Obsidian ideas, and template files do not count as active by themselves.
- The framework follows the four-layer model:
  - `control`
  - `stage`
  - `tool`
  - `gate`
- User-facing Chinese scenario names are:
  - `新项目开发` = `new_feature_from_scratch`
  - `迭代开发` = `iterative_feature_development`
  - `迭代再开发` = `existing_feature_continuation`

## Default workflow

1. Reconstruct current state from the first-read files.
2. Identify the user's requested scope:
   - architecture clarification
   - config cleanup
   - agent rename
   - layer split
   - workflow refinement
   - Obsidian sync
3. Keep the task narrow. Do not reopen broad redesign unless the user explicitly asks.
4. Change the smallest set of files that makes the requested update real.
5. If a skill, config, or layer definition changes, sync the matching Obsidian notes.

## Layering rules

- `control`: route and choose workflow; do not perform tool actions.
- `stage`: define phase goal and progression; do not absorb raw tool execution.
- `tool`: perform one small operational capability.
- `gate`: judge `go / warn / block`; do not perform the work being judged.

If an agent mixes two or more of these responsibilities, split it before expanding it.

## Session-resume behavior

When the user opens a new session with only a short instruction, treat it as valid continuation if they mention the multi-agents framework. Rebuild context from the first-read files instead of asking them to restate the whole history.

Recommended interpretation pattern:

- If the user says `继续维护 multi-agents 框架`, first read the core files and then infer the next actionable scope from current state plus the user's newest sentence.
- If the request is still broad, ask only for the single next concrete action, not for the whole historical background.

## Output style for this skill

When replying under this skill:

- explain current framework state briefly
- state what layer or registry surface is being touched
- separate confirmed facts from proposed changes
- prefer concrete file targets over abstract theory

## Avoid

- treating this as a greenfield redesign
- redefining the four-layer model every time
- counting draft artifacts as live runtime state
- changing bottom-layer agent ids unless compatibility has been checked
- expanding into unrelated business-project routing work
