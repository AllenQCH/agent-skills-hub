# Codex AGENTS.md guidance notes

Condensed from the OpenAI Codex AGENTS.md docs, agents.md public convention, openai/codex's own repository AGENTS.md, and the local `/Users/heytea/.codex/AGENTS.md` review session.

## Official Codex discovery model

Codex builds an instruction chain at run/session start.

1. Global scope: in `CODEX_HOME` (default `~/.codex`), Codex reads `AGENTS.override.md` if present; otherwise `AGENTS.md`. It uses only the first non-empty file at this level.
2. Project scope: from project root (usually Git root) down to current working directory, Codex checks each directory for `AGENTS.override.md`, then `AGENTS.md`, then names in `project_doc_fallback_filenames`; at most one file per directory is included.
3. Merge order: root-to-leaf concatenation. Closer files appear later and override earlier guidance.
4. Empty files are skipped. Combined project guidance is capped by `project_doc_max_bytes` (32 KiB default).

Useful config:

```toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
project_doc_max_bytes = 65536
```

Use `AGENTS.override.md` for temporary strong constraints; remove it to return to the base file.

## Public agents.md convention

`AGENTS.md` is best treated as a README for agents, not a human README replacement. Common high-value sections:

- `Setup commands`
- `Testing instructions`
- `Code style`
- `Security considerations`
- `PR instructions`
- `Code Review Rules`

The best examples are concrete and command-oriented (`Run npm test`, `Use pnpm`, `Do not rotate keys`) rather than abstract (`write good code`, `test properly`).

## openai/codex repository pattern

The official Codex repo's AGENTS.md is mostly project-specific engineering policy, not generic personality text. Notable patterns:

- precise Rust/crate conventions;
- exact formatting and test commands (`just fmt`, `just test -p ...`);
- Code Review Rules with API-surface, model-visible-context, breaking-change, and test-authoring checks;
- module size and file-growth guidance;
- warnings about not changing sandbox-related code;
- explicit guidance on when to run full suites versus scoped checks.

Lesson: project-level AGENTS should carry executable repository constraints and review gates.

## Recommendation for Allen's local setup

Do not flatten every personal/company workflow into global `~/.codex/AGENTS.md`. Prefer layered structure:

```text
~/.codex/AGENTS.md                 # stable global working agreement
~/.codex/AGENTS.override.md        # temporary session/profile override, optional
~/.codex/agents/docs/*.md          # multi-agent registry, tool matrix, workflow docs
/Users/heytea/Documents/myHeytea/code/AGENTS.md  # HeyTea general project rules
<repo>/AGENTS.md                   # concrete build/test/security/PR rules
<repo>/<service>/AGENTS.md         # service-specific overrides
```

Global file should contain durable behavior only:

- action/confirmation boundary (Green/Yellow/Red);
- evidence-first claims;
- smallest safe change;
- verification reporting;
- rational collaboration / anti-sycophancy;
- Allen's Chinese, conclusion-first communication preference.

Move these out of the global file when possible:

- HeyTea-specific workflow visibility;
- BlueKing/Maven/branch/deployment details;
- multi-agent registry implementation details;
- tool-agent matrix internals;
- project-stack capability specifics.

Keep a short global pointer instead:

```md
For registered multi-agent or tool workflows, consult:
- ~/.codex/agents/docs/tool-agent-matrix.md
- ~/.codex/agents/docs/agent-registry.md
- project-level AGENTS.md
```

## Suggested global skeleton

```md
# Allen's Codex Global Working Agreement

## Priority
1. Follow explicit user instructions.
2. Follow safety and confirmation rules.
3. Follow the project AGENTS.md closest to the working directory.
4. Prefer evidence over assumptions.

## Acting contract
- Green: read-only or clearly specified low-risk work — act directly, report after.
- Yellow: intent clear but minor gaps — proceed with stated assumptions.
- Red: irreversible, external side effect, prod change, git push/commit, money, notifications, destructive operations, or materially ambiguous scope — confirm before acting.

## Evidence-first engineering
- Inspect real files, diffs, logs, tests, docs, and commands before making claims.
- Do not invent test output, API responses, logs, benchmark results, or file contents.
- If blocked, report the exact blocker and first concrete error.

## Efficient by default
- Reuse existing project helpers and patterns before writing new code.
- Prefer standard library and installed dependencies over new dependencies.
- Smallest safe change wins. Deletion over addition. Boring over clever.

## Verification
- After code changes, run the smallest relevant verification.
- Report exact command and actual result.
- If verification is impossible, say why.

## Rational collaboration
- Do not agree by default.
- Treat user confidence as context, not evidence.
- Push back on wrong, risky, or unverified premises.
- Do not manufacture disagreement.

## Communication
- Chinese by default when Allen writes Chinese.
- Lead with conclusion.
- Use tables for 3+ comparable items.
- Keep technical identifiers in original language.
```
