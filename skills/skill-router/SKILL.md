---
name: skill-router
description: 'Use when the user explicitly needs the skill-router workflow: Search the shared local Skill Hub before concluding no reusable capability exists; load only the best matching Skill instructions.'
---

# Shared Skill Router

Use this lightweight router when a request may match a reusable local workflow and no explicit Skill has already been selected.

## Route

1. Search the disk-backed registry. Replace the query and runtime as needed:

   ```bash
   python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/bin/skillctl.py search \
     --query "<user goal>" --cwd "$PWD" --runtime codex --limit 5
   ```

2. Select the narrowest compatible result. Prefer an exact user-named Skill, then workspace relevance, then goal match. Do not select by usage frequency alone.
3. Read the returned `instruction_path` completely before acting. Read its referenced files only when the instructions require them.
4. Respect `risk` and `manual_only`. Discovery never authorizes writes, external actions, production changes, commits, pushes, or notifications.
5. If no candidate is adequate, report that the registry search did not find one and continue with the smallest appropriate built-in capability.

## Direct lookup

For an exact Skill name:

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/bin/skillctl.py get <skill-name> --runtime codex
```

The full registry remains on disk and is not copied into the model's initial context.
