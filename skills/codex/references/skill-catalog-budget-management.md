# Skill catalog and context-budget management

Use this when a user has many installed company/project skills and complains that even the initial `name + description` listing is bloating context or causing relevant skills to be missed.

## Verified external patterns

### OpenAI Codex skills

Codex uses progressive disclosure for skills:

- initial context gets skill `name`, `description`, and path;
- full `SKILL.md` loads only after Codex decides to use the skill;
- the initial skill list is capped at about 2% of the model context window, or about 8,000 characters when the context window is unknown;
- if many skills are installed, Codex shortens descriptions first and may omit some skills from the initial list.

Implication: do not rely on “only name+desc” being free. The skill catalog itself needs budget governance.

### Claude Code skills

Claude Code has a similar skill-listing pressure point:

- the listing always contains every skill name;
- descriptions are fit into a budget;
- least-used skills lose descriptions first;
- `/doctor` estimates listing context cost and biggest contributors;
- `skillListingBudgetFraction` can raise the budget;
- `skillListingMaxDescChars` caps per-skill description length;
- `skillOverrides` can mark low-priority skills as `name-only`.

Implication: usage frequency, manual-only flags, and description truncation are durable management primitives.

### Large skill libraries on GitHub

Observed patterns worth copying:

- `tw93/Waza`: small high-signal set of eight broad engineering skills; avoids heavy “everything installed” designs.
- `pvliesdonk/agents.md`: global rules provide routing and a delegation table; on-demand skills are loaded by role/task.
- `trailofbits/skills`: large security capability set split into domain plugins/marketplace entries rather than one global skill pile.
- `jmagly/aiwg`: workspace-aware deployment, profiles, `doctor` budget checks, and a persisted workspace skill plan for auditability.

## Recommended design for company skill libraries

Avoid putting every company skill into the always-visible startup catalog. Prefer:

```text
Always loaded:
  - compact skill-router / capability-index skill
  - safety and confirmation rules
  - active profile summary

Not always loaded:
  - all company skill names/descriptions
  - long descriptions
  - project-specific procedures
  - rare or high-risk workflows

Runtime:
  1. classify task
  2. detect workspace/profile
  3. retrieve top-k skills from registry
  4. inject only top-k name + short description
  5. load full SKILL.md only after match
  6. record usage and outcome
```

## Budget rules of thumb

| Item | Suggested budget |
|---|---:|
| Global skill router | <= 800 chars |
| Active profile summary | <= 1,000 chars |
| Top-K candidate skill list | <= 2,000 chars |
| Individual listing description | <= 80 Chinese chars or <= 120 English chars |
| Global always-on skills | <= 20 |
| Active profile skills | usually 20-50 |

## Skill metadata to maintain outside the prompt

A full registry can live outside model context as JSON/YAML or a searchable DB:

```yaml
name: blueking-workhour
description: 填写/查询蓝鲸工时；提交前确认任务、日期、小时、内容。
tags: [blueking, workhour, heytea]
scope: company
risk: external-side-effect
manual_only: false
profiles: [personal-ops, heytea-backend]
owner: platform-productivity
last_used: 2026-07-24
use_count_30d: 12
```

Keep long `when_to_use`, examples, gotchas, and scripts in the full skill directory, not in the startup listing.

## Recommended doctor check

Implement a `skills doctor`-style command that reports:

- number of active skills;
- total `name + description` characters;
- estimated token cost using ~4 chars/token;
- top contributors by description length;
- descriptions over the threshold;
- unused/rare skills;
- high-risk skills that are still auto-invocable;
- suggested profile/bundle moves.

Example output shape:

```text
Skill listing budget:
- active skills: 42
- name+desc chars: 4,180
- estimated tokens: ~1,045
- top contributors:
  1. lark-mail 362 chars
  2. blueking-workhour 288 chars
- warning: 8 descriptions exceed 160 chars
- suggestion: move 23 rare skills to backend.yaml or manual-only
```

## Pitfalls

- Do not solve skill bloat by simply raising the context window; retrieval noise and startup cost still grow.
- Do not make high-risk skills auto-trigger by default. Writes, notifications, production changes, deletes, publishing, and external submissions should be manual-only or require explicit confirmation.
- Do not put project-specific business procedures in global skill descriptions. Use project-level skills, bundles, or profiles.
- Do not let installed equals active. Large libraries should support profiles, bundles, disabled/archive directories, and workspace-aware deployment.
