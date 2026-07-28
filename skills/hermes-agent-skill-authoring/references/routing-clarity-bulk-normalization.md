# Routing Clarity Bulk Normalization

Use this reference when Allen asks to audit or normalize an existing Hermes skill library for ambiguous names/descriptions.

## Durable workflow

1. Back up the whole skills tree before editing:
   ```bash
   cd ~/.hermes
   mkdir -p backups
   tar -czf "backups/skills-before-routing-clarity-$(date +%Y%m%d-%H%M%S).tar.gz" skills
   ```
2. Parse every `SKILL.md` frontmatter and audit:
   - duplicate `name`
   - invalid `name` syntax: not lowercase hyphenated or >64 chars
   - `description` not starting with `Use when`
   - `description` >1024 chars
   - missing exclusion boundary such as `Do not use for ...`
3. Preserve valid stable names. Do not rename skills just because wording can be improved; name changes can break cron jobs, related skill references, and user muscle memory.
4. Normalize descriptions mechanically only for safe frontmatter cases:
   - Prefix with `Use when ...`.
   - Preserve the original description content as the behavior/output clause.
   - Add a scoped `Do not use for ...` exclusion boundary based on category/platform.
5. Run a second-pass audit for mechanical artifacts such as `workflow workflow`, generic exclusions, duplicate descriptions, and suspicious generic names.
6. Manually patch any suspicious descriptions found in the second pass.
7. Write an audit report under `~/.hermes/skill-audits/` with total skills, category counts, validation errors, and a table of final descriptions.
8. Persist the rule in the governing skill-authoring skill and, if appropriate, in compact memory as Allen's durable preference.

## Validation checks

A final pass should show:

- zero duplicate names
- zero invalid names
- zero descriptions missing `Use when`
- zero descriptions over 1024 chars
- zero descriptions missing an exclusion boundary

## Pitfalls

- Do not create one new skill per bad description. This is a library hygiene task and belongs under the class-level skill-authoring umbrella.
- Do not rewrite every `name` in a bulk pass unless names are invalid or duplicate. Renames are higher risk than description fixes.
- Do not trust the first mechanical normalization pass as final. Always search for artifacts and patch them manually.
- Do not overwrite user-local skills without a timestamped archive first.
