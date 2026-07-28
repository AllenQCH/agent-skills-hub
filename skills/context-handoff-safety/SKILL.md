---
name: context-handoff-safety
description: 'Use when the user needs the context handoff safety workflow: Prevent stale-summary mistakes when a conversation contains compaction, handoff, or partial-session context. Use whenever the prompt includes a context summary, handoff note, or any explicit instruction that the latest user message may override earlier work. Do not use for tasks outside this software-development workflow or tasks better handled by a narrower debugging, testing, planning, or review skill.'
---

# Context Handoff Safety

## When to use
Load this skill when:
- The conversation includes a compaction/handoff block, recap, or "reference only" summary.
- A previous task is still described in context, but the user's newest message may have changed topic.
- You inherit a session where the assistant might otherwise continue stale work.

## Core rule
**The latest user message is the source of truth.**
A handoff summary is background context only. If the newest user message changes topic, narrows scope, says "stop", "undo", "never mind", or asks for something else, abandon the stale task immediately.

## Procedure
1. **Read the newest user message first.** Classify the current ask before touching any recap.
2. **Treat handoff summaries as non-binding background.** Use them only if they are consistent with the current ask.
3. **For ambiguous continuation prompts, re-anchor explicitly.** If the user only says “继续 / continue”, recover the likely prior task, but before doing substantial work say the one-line target you are continuing (e.g. “我继续上次的 X：先做 Y”). If multiple recent tasks are plausible, ask a short clarification instead of silently picking one.
4. **Check for topic drift.** Ask: "Is the assistant about to answer a previous task instead of the user's current request?"
5. **If the topic changed, drop the old task completely.** Do not "wrap up" old work unless the user explicitly asked for it.
6. **Only use old state that still matters.** Files already modified, installs already done, or prior discoveries may still be relevant, but they do not define the current goal.
7. **Before finalizing, run a mismatch check:**
   - Does my reply answer the latest user message directly?
   - Am I mentioning stale work the user did not ask about?
   - Did I accidentally continue an earlier plan because it was more detailed than the new ask?
   - If the user said only “continue”, did I make the resumed target visible early enough that they can stop me before wasted work?

## Scheduled context-governance / session recap jobs
When running a cron whose job is to inspect recent sessions and produce a handoff/governance report:
1. Browse recent sessions, then read only the likely long/unfinished ones; do not dump whole transcripts into the report.
2. Identify themes that are recoverable: unresolved blockers, partially completed research/Obsidian curation, repeated workflow friction, or user-corrected preferences.
3. For each theme, output a compact recoverable summary: **goal, current state, key facts, next step, suggested sink** (`memory`, `skill`, `Obsidian`, follow-up cron/task, or none).
4. Avoid secrets, credentials, private raw chat logs, and long quoted artifacts. Prefer stable facts and paths only when they are needed to resume.
5. Do not modify user files from a governance job unless the cron explicitly asks for write actions; reporting recommendations is usually enough.
6. If nothing material is found, say so and include one context-control tip rather than inventing work.

## Pitfalls
- Letting a detailed handoff summary overpower a short new user request.
- Silently continuing a recovered prior task after an ambiguous “继续”, causing the user to ask “你在干什么？” because the resumed target was not made visible.
- Reporting completion of an earlier task instead of acting on the current one.
- Carrying forward stale TODO state after the user changed direction.
- Treating previous "active task" sections as instructions rather than historical notes.
- In context-governance reports, over-exposing raw transcript details instead of producing resumable summaries.

## Recovery pattern
If you realize a handoff mismatch happened:
1. Stop continuing the stale thread.
2. Acknowledge the mismatch briefly.
3. Re-anchor on the user's latest ask.
4. Execute the correct task immediately.

## Notes
- This skill governs **conversation control flow**, not domain content.
- Pair it with the domain skill for the actual task after re-anchoring.
- See `references/compaction-handoff-checklist.md` for a compact pre-response checklist and example failure mode.