---
name: heytea-project-stack
description: Classify repositories in registered HeyTea project groups, distinguish Maven dependency artifact install/publish from deployable service startup/deployment, validate and sync project manifests, and delegate local stack startup. Use for multi-repository development, dependency-first builds, local integration environments, Docker/service startup, deploy planning, or when a project gains a new repository.
---

# HeyTea Project Stack

Use the project manifest as the deterministic source for repository type and action order. Do not infer deploy behavior from repository names after the project has an explicit manifest.

## Commands

```bash
STACK="/Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/heytea-project-stack/scripts/project_stack.py"

python3 "$STACK" inventory invoice
python3 "$STACK" validate invoice
python3 "$STACK" sync invoice
python3 "$STACK" plan invoice --mode local hsp-invoice center-hsp-invoice
python3 "$STACK" plan invoice --mode remote hsp-invoice center-hsp-invoice
python3 "$STACK" status invoice
python3 "$STACK" start invoice center
```

Run `sync <project>` as a dry run when direct child repositories change. Use `sync <project> --apply` only when the project `AGENTS.md` already defines the default classification or the user has confirmed the new repository type.

## Action Meanings

- `artifact_install`: install a changed dependency package into the local Maven repository for local downstream builds.
- `artifact_publish`: publish a changed dependency package with Maven deploy/publish so remote CI or pipelines can consume it.
- `local_start`: start a concrete service for local integration verification.
- `service_deploy`: deploy a concrete service through its service pipeline.

For local-only verification, use `artifact_install`; do not publish an artifact. For remote CI or delivery, publish changed dependency artifacts before building or deploying affected consumer services.

## Maven Dependency Branches

- Never create or use a BlueKing demand branch such as `feature/<蓝鲸需求号>-<蓝鲸需求中文标题>` in a Maven dependency repository.
- Before selecting the dependency branch, inspect the affected downstream services' `pom.xml` files or effective POMs and record the dependency versions they actually consume.
- When all affected consumers use the same version, develop on that version's existing maintenance branch. When they use different versions, use the version consumed by the majority of the affected consumers.
- Reuse the dependency repository's existing version-branch convention, such as `feature/1.0.1`; do not invent a new prefix or version branch.
- If the versions are tied, cannot be resolved from the consumers, or the corresponding version branch does not exist, stop and ask the human to choose. Do not fall back to a BlueKing demand branch.

## Workflow

1. Resolve the current project manifest from `~/.codex/state/heytea-project-stack/<project>.json`.
2. Run `validate` and stop on missing repositories, stale entries, secrets, or invalid types.
3. For every changed Maven dependency repository, resolve and report its target version branch from the affected consumers before creating or switching branches.
4. Run `plan` with the actual changed repositories and `local` or `remote` mode.
5. Execute only the actions authorized by the user and current development workflow.
6. Use the manifest's local launcher for `status` and `start`.
7. When a service has `localRuntime=discovery_required`, inspect its project-local profile, ports, dependencies, and health endpoint before registering a runnable target. Do not guess them.

## Boundaries

- Never execute `artifact_publish` or `service_deploy` merely because `plan` displays them.
- Never store passwords, tokens, credentials, or secret values in a project manifest.
- Treat project `AGENTS.md` as the stable classification source and the state manifest as the machine-local execution source.
- Keep project-specific launch commands in a local adapter; keep classification and dependency ordering in the common manifest.
