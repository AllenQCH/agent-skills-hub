# Agent Skills Hub

This repository is the canonical source for user-maintained skills shared by
local agent runtimes. Runtime directories remain compatibility entry points;
they do not own the canonical files stored here.

## Layout

- `skills/<name>`: one runtime-neutral canonical package per unique Skill.
- `skills/<name>/adapters`: preserved runtime-specific variants for collisions.
- `registry/skills.json`: searchable disk registry; it is not preloaded into prompts.
- `profiles`: small ranking hints for common work contexts.
- `templates/skill-router`: lightweight bootstrap Skill deployed to runtimes.
- `manifests`: generated inventory and migration evidence.
- `bin`: search, deployment, review, locking, and verification helpers.

## Ownership

Runtimes discover canonical packages through `skill-router`; they do not scan the
full Hub during initial prompt construction. Hermes may continue creating mutable
skills under `~/.hermes/skills`; the review queue identifies real local packages
for later human-approved promotion.

The `skills` tree is filesystem read-only. For an approved change, temporarily
add owner write permission only to the target package, make and verify the
change, rebuild the manifest, then run `python3 bin/skill_hub.py lock`. The
`verify` command fails if any Hub package remains writable.

The first migration preserves every existing skill and keeps same-name runtime
variants separate. It does not archive, merge, or shorten descriptions.

## Current Inventory

- Original packages preserved: 238.
- Unique original names: 217.
- Canonical packages: 219, including `skill-router` and `skill-quality-review`.
- Collision groups: 20, containing 21 runtime adapter copies.

Codex uses `~/.agents/skills/skill-router`; Claude and Hermes use the matching
`~/.claude/skills` and `~/.hermes/skills` Router links. Codex system and plugin
skills remain runtime-managed. Real Hermes-local skills remain mutable and are
excluded from the Hub until a human approves promotion.

## Review And Catalog

- Hermes may continue generating mutable local skills under
  `~/.hermes/skills`.
- `bin/review_skills.py` runs every Monday and Friday at 10:00
  `Asia/Shanghai` through a dedicated LaunchAgent.
- The review may apply deterministic local quality fixes, but promotion from
  Hermes-local storage into the Hub always requires human approval.
- Review failures are retained as evidence and wait for the next scheduled run;
  there is no polling or automatic retry.

On macOS, the Catalog LaunchAgent remains independent and uses only `RunAtLoad`
plus `WatchPaths`; it has no interval polling. The review LaunchAgent template is
`templates/com.heytea.skill-quality-review.plist`. It has two calendar triggers,
does not run when installed, and never commits or pushes scheduled changes.

## Commands

```bash
python3 bin/skillctl.py search --query "<goal>" --runtime codex --limit 5
python3 bin/skillctl.py get <skill-name> --runtime codex
python3 bin/skillctl.py build
python3 bin/skillctl.py deploy
python3 bin/skillctl.py deploy --apply
python3 bin/skillctl.py doctor --runtime codex
python3 bin/skillctl.py scan
python3 bin/skillctl.py verify
python3 bin/skill_hub.py manifest
python3 bin/skill_hub.py lock
python3 bin/skill_hub.py verify
python3 bin/review_skills.py
python3 bin/review_skills.py --force
```
