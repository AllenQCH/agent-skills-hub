# Compaction / Handoff Checklist

Use this right before responding in a handed-off or compacted session.

## 30-second check
1. What is the **latest user message** asking for?
2. Does any summary block explicitly say it is **background only**?
3. Am I about to answer a **previous task** instead?
4. If old work exists, is it still relevant to the current ask, or merely historical?
5. Would my first sentence make sense if the user only saw their latest message?

## Failure mode to avoid
- Summary says the active task was A.
- User's newest message asks for B.
- Assistant marks TODOs for A completed and reports A's outcome.
- User's actual request B is ignored.

## Correct behavior
- Use A only as background if it helps with B.
- Otherwise discard A and execute B.

## Quick wording for recovery
- "I answered the stale handoff instead of your latest request. Re-anchoring now."
- Then perform the requested action immediately.
