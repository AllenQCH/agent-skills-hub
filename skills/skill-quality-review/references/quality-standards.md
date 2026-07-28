# Skill Quality Standards

## Contents

- [Instruction surfaces](#instruction-surfaces)
- [Frontmatter](#frontmatter)
- [Progressive disclosure](#progressive-disclosure)
- [UI metadata](#ui-metadata)
- [Links and package files](#links-and-package-files)
- [Scheduled execution](#scheduled-execution)
- [Mutation boundaries](#mutation-boundaries)

## Instruction surfaces

- Treat each package-root `SKILL.md` as the canonical instruction surface.
- Treat `adapters/<runtime>/SKILL.md` as runtime-specific instruction surfaces owned by the same package.
- Audit real Hermes-local packages separately from the Hub and its Router symlink.
- Inventory Codex System and Plugin Skill surfaces without changing them.

## Frontmatter

- Require `name` and `description`.
- Use lowercase hyphen-case names of at most 64 characters.
- Make the description state both the capability and a narrow trigger condition.
- Retain only `name`, `description`, `license`, `allowed-tools`, and `metadata` in frontmatter.
- Preserve unsupported canonical fields in `skill.json.legacy_frontmatter`.
- Preserve unsupported Adapter fields in `skill.json.adapter_metadata[relative_path].legacy_frontmatter`.

## Progressive disclosure

- Keep the package-root `SKILL.md` at or below 500 lines.
- Keep the core workflow and selection guidance in `SKILL.md`.
- Put extended procedures, examples, schemas, and reference material in one-level `references/` files.
- Link every extracted reference directly from `SKILL.md` and explain when to read it.
- Add a contents list to generated reference files over 100 lines.

## UI metadata

- Maintain `agents/openai.yaml` for every canonical package and real Hermes-local package.
- Store UI fields under `interface`.
- Require `display_name`, a 25-64 character `short_description`, and `default_prompt`.
- Make `default_prompt` explicitly mention `$skill-name`.
- Preserve valid `dependencies` and `policy` blocks.

## Links and package files

- Require local Markdown links to resolve from the file that contains them.
- Repair only links whose intended target exists and is uniquely identifiable.
- Do not retain package-root `README.md`, `INSTALLATION_GUIDE.md`, `QUICK_REFERENCE.md`, or `CHANGELOG.md`; move their content to `references/` and link it from `SKILL.md`.
- Keep nested README files when they document a bundled template, test fixture, workflow, or tool.

## Mutation boundaries

- Default to dry-run.
- Do not delete semantic content, rename packages, or broaden triggering descriptions.
- Do not modify System or Plugin Skills.
- Do not commit, push, publish, or invoke external writes.
- Restore the Hub's canonical tree to read-only after successful validation.

## Scheduled execution

- Reuse the existing Agent catalog LaunchAgent and enforce the 72-hour interval inside the review runner.
- Acquire an atomic local lock so interval and WatchPaths triggers cannot overlap.
- Write reports and state outside the Hub to avoid recursive WatchPaths triggers.
- When no fixes are planned, keep the Hub locked and run read-only validation.
- When fixes are planned, validate them in a temporary copy before live apply.
- Before live apply, confirm the managed-input digest still matches the pre-staging digest.
- Back up current Hub and Hermes-local content before live apply; do not automatically delete backups.
- Apply only when `manual_count` is zero. Record ambiguous cases as `pending` without mutation.
- On failure, lock the Hub, retain evidence, and retry after six hours rather than every five minutes.
- An audit-only rehearsal must not update `last_review_at` or `next_review_at`.
