---
name: language-learning-group-cron
description: 'Use when the user needs the language learning group cron workflow: Set up a recurring group-based language learning workflow with daily reading content, evening vocab submission reminders, and next-day spaced-review plans via cron jobs. Do not use for tasks outside the named productivity app, document, spreadsheet, meeting, or workflow scope.'
---

# Language Learning Group Cron Workflow

Use this when a user wants a long-running study routine in a chat/group, especially for English learning with daily articles and follow-up review.

## Goal

Create a closed-loop schedule:
1. Daily new article/content
2. Same-day reminder to submit difficult words / unknown vocabulary
3. Next-day spaced-repetition review plan
4. Future articles that gradually recycle recent vocabulary

## Recommended default schedule

For Asia/Shanghai unless user says otherwise:
- **08:30** daily article
- **18:50** reminder to submit today's new words before 19:00
- **10:00 next day** spaced-review plan

## Implementation pattern

### 1) Inspect existing cron jobs first
Always run `cronjob(action='list')` before creating or changing jobs.
Reason: avoid duplicates, confirm delivery target, and discover whether a partial workflow already exists.

### 2) Use three separate jobs
Keep the workflow modular so each part can be tuned independently:
- `...daily...` for the article
- `...vocab-submit-reminder...` for evening reminder
- `...spaced-review-plan...` for next-day review

This makes later prompt edits safer and avoids rebuilding the entire system for one content change.

### 3) Article job prompt design
Customize the article job to the user's actual reading goal instead of assuming exercises are welcome.

Common dimensions to constrain:
- theme domain: AI / programming / product / tooling / tech workflow
- audience level: beginner-intermediate or intermediate-advanced Chinese learners
- target length: e.g. **580–630** or **600–900 English words**
- paragraph count: **5–8 paragraphs**
- style: like a real newsletter/blog post, not textbook/exam prose
- output sections: explicitly list which sections are allowed, and where the article must end

Important format lesson from Allen's group:
- If the user says they mainly want to **read the article**, do **not** append reading-comprehension tails by default.
- For Allen's current preference, keep `## Vocabulary` but end the article **immediately after the vocabulary table**.
- Explicitly forbid extra sections such as `## Check Yourself`, `Output Task`, `Today Before 19:00`, homework prompts, or generic study reminders unless the user asks for them.
- When tightening format, say both what to include **and** what must not appear; negative constraints materially reduce drift.

Useful reusable output format for Allen's current preference:

```text
# AI English Daily | [Topic]

## Type
[Article / Interview Dialogue / Term Explanation / Famous Person Story]

## English Content
[580-630 words]

## Vocabulary
| Word / Phrase | IPA | 中文 | Simple Explanation |
|---|---|---|---|
| ... | /.../ | ... | ... |
```

### 4) Reminder job prompt design
Keep it short and action-oriented.
The reminder should:
- mention the article already posted today
- ask learners to submit new words before 19:00
- suggest one simple submission format, e.g. `word - your guessed meaning / sentence`
- avoid long explanation

### 5) Review-plan job prompt design
For Allen's English group, the review task must be strict about vocabulary source and forgetting-curve scheduling.

The review task should explicitly say:
- use **Obsidian vocabulary library as the single source of truth**: `/Users/heytea/Documents/obsidian_note/02 Areas/英语学习/AI英语学习群-生词库.md`
- do **not** automatically extract review words from the daily article, ordinary group messages, or surrounding context
- accepted vocabulary sources are only:
  - words Allen/learners actively submit by @-mentioning the assistant in the group
  - words Allen manually adds to Obsidian
  - words Allen explicitly tells the assistant
- the cron job should only generate a review plan; it must not add/delete/rewrite the vocabulary library unless separately asked
- follow an Ebbinghaus-style schedule, preferably: D1, D2, D4, D7, D15, D30
- choose words by recorded date and review window; if no exact window match exists, use the nearest eligible words from the library
- if the library has too few eligible words, say so and produce a minimal plan; never pad with article words
- include short active-recall prompts, not just definitions
- encourage reuse in fresh example sentences or mini writing prompts

Recommended output sections:
```text
# 生词复习计划 | Ebbinghaus Review

## 今日复习重点
## 今日词表
阶段｜生词｜中文意思｜来源日期｜今日任务
## 分阶段复习
D1 / D2 / D4 / D7 / D15 / D30
## 5-Minute Drill
## Tonight
```

### 6) Immediate activation pattern
After creating or significantly changing the article job, only run it immediately when the user explicitly wants an immediate send or is willing to accept an out-of-band extra post.

For Allen's English group, prefer this resend rule:
- target outcome is **one article per day**
- if the scheduled article failed and the user asks to "resend" or "补发", treat that as a **replacement for the missed daily article**, not an extra bonus article
- do **not** both trigger the cron and also manually draft/send another article unless the user explicitly asks for two separate versions
- before any resend, inspect the latest article-job output file; if it already contains a usable article body, resend that exact body rather than generating a second different article
- if the latest output contains only an error (for example connection/provider failure), generate **one** replacement article and stop there

## Update pattern

If the user says the article is too short / too easy / too hard:
- use `cronjob(action='update', job_id=...)`
- preserve the schedule and delivery target
- only strengthen the prompt constraints

Typical upgrades:
- **Too short** → specify explicit word count and paragraph count
- **Too easy** → say "intermediate-advanced" and allow more abstract expression
- **Too textbook-like** → require newsletter/blog tone
- **Needs vocab reinforcement** → add a fixed recent-vocabulary reuse section

## Pitfalls

- Do **not** replace the whole workflow with a single cron unless the user asks; modular jobs are easier to maintain.
- Do **not** forget to check existing jobs first, or you'll often create duplicates.
- `deliver='origin'` is only safe when the cron was created from, and should continue delivering to, the same current chat. If the user says content “should go to the English group” or another named group, explicitly resolve the group chat ID first (e.g. search Feishu/Lark chats by group name) and update all related jobs to `deliver='feishu:<chat_id>'` rather than relying on `origin`.
- When retargeting an existing workflow, update all modular jobs together (daily article, reminder, spaced-review) so follow-ups do not remain in the old destination.
- Before retargeting or resending, verify the existing cron jobs' `deliver` fields and inspect the target group's recent messages. If the article job already delivers to the requested English group and today's article is present there, do **not** resend; simply confirm the plan is already correct.
- Allen's current Feishu English-learning target group is `AI 英语学习群｜Easy Daily` with chat ID `oc_9e1a15d3af402182ed3d60f5636c409f`; the modular jobs should deliver to `feishu:oc_9e1a15d3af402182ed3d60f5636c409f` unless Allen explicitly changes the group.
- If today’s article was already generated in the wrong place, first try to read the latest cron output file and resend that exact content to the correct group via the chat messaging tool/CLI with an idempotency key; do not regenerate a different article unless the user asks.
- If the user says they did not receive today’s article, inspect the relevant article job output under `~/.hermes/cron/output/<job_id>/...` before answering. If the output contains only a provider/API failure such as `API call failed after 3 retries` and no usable article body, say the automated generation failed and immediately produce a replacement article in the current chat (or send it to the target group if requested). Do not pretend the cron produced content.
- If cron output files are missing or hard to locate, use the chat message history (`lark-cli im +chat-messages-list --chat-id <oc_...>`) to verify whether the expected `Cronjob Response: <job-name>` message already landed in the group.
- `cronjob(action='run')` may schedule or trigger a run, but for urgent correction verify delivery. If immediate group delivery is required and cron delivery is uncertain, send the saved output directly with the messaging tool.
- When the user customizes article format (for example: keep `## Vocabulary` but remove all exercise/review sections after it), update the article cron prompt to encode that exact stop condition. Do not assume study questions are always helpful.
- If the user asks for a resend after a failed morning article, the safe default is **exactly one replacement article total**. Avoid the failure mode of `cronjob(action='run')` plus a separate manual send, which creates duplicate same-day articles.
- If a related review-plan job still uses `deliver='origin'` while the article workflow is meant for a fixed Feishu group, retarget the review job to the same explicit `feishu:<chat_id>` destination so article/review outputs stay aligned.

## Verification checklist

Before finishing:
- Confirm the three jobs exist or were updated
- Confirm schedule times
- Confirm article prompt includes length/difficulty/style constraints
- If appropriate, run the article job once to seed the loop immediately
- Summarize the final routine for the user in plain Chinese
