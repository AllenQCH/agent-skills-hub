---
name: skill-quality-review
description: Audit and normalize the shared Agent Skills Hub and Hermes-local Skills against the local Skill standard. Use when reviewing all Skill packages, reducing loaded context through progressive disclosure, repairing metadata or relative links, or preparing a semantics-preserving Skill quality cleanup. Inventory Codex System and Plugin Skills without modifying them.
---

# Skill Quality Review

Audit first, inspect the proposed actions, then apply normalization only after the requested scope is approved.

## Workflow

1. Read [quality standards](references/quality-standards.md).
2. Run the audit and retain both JSON and Markdown evidence:

```bash
python3 scripts/audit_skill_quality.py \
  --json-out reports/skill-quality.json \
  --markdown-out reports/skill-quality.md
```

3. Generate a dry-run normalization plan:

```bash
python3 scripts/normalize_skill_quality.py --include-hermes \
  --json-out reports/skill-normalization-plan.json
```

4. Review unresolved issues and the exact action list. Apply only within an approved scope:

```bash
python3 scripts/normalize_skill_quality.py --include-hermes --apply \
  --json-out reports/skill-normalization-result.json
```

5. Re-run the audit, Hub build, repository tests, runtime doctor checks, and Router golden queries.
6. Restore the canonical `skills/` tree to read-only after validation.

## Scheduled Review

Use the governed scheduler only after explicit approval of its scope:

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/bin/review_skills.py
```

- A dedicated LaunchAgent invokes the runner every Monday and Friday at 10:00 `Asia/Shanghai`.
- Keep Agent Catalog sync independent with `RunAtLoad` and `WatchPaths`; neither job uses interval polling.
- Preserve the Hermes-local promotion queue and require human approval before promoting a local Skill into the Hub.
- Run audit and normalization planning before any mutation.
- Apply only deterministic fixes with zero manual items. Keep ambiguous findings `pending`.
- Validate the same changes in a temporary Hub copy before touching the live Hub.
- Abort if the live Hub or Hermes-local inputs change during staging.
- Back up the live Hub and Hermes-local packages before apply.
- Never commit or push. Always return the Hub to read-only, including after failure.
- On failure, retain evidence and wait for the next Monday/Friday run; do not retry automatically.
- Use `--force --audit-only` for a non-mutating rehearsal; it must not advance the schedule.

## Boundaries

- Preserve valid instructions and package resources.
- Keep `name`, `description`, `license`, `allowed-tools`, and `metadata` in frontmatter.
- Move unsupported frontmatter into `skill.json`; never discard it.
- Split `SKILL.md` files over 500 lines only at a Markdown heading outside code fences.
- Move only package-root auxiliary README files into `references/`; preserve nested template or tool documentation.
- Generate or repair `agents/openai.yaml` while retaining existing `dependencies` and `policy` blocks.
- Repair a relative link only when its intended existing target can be resolved uniquely.
- Treat Codex System and Plugin Skills as inventory-only.
- Do not commit, push, or publish changes. Schedule only through the explicitly approved governed runner above.

## Outputs

The audit JSON is the machine-readable source of truth. The Markdown report is for review. Normalization output records each planned or applied action and any item that requires manual judgment.
