---
name: x-content-cron
description: 'Use when the user needs the x content cron workflow: Set up recurring cron jobs that generate ready-to-post X/Twitter content drafts with a fixed daily cadence, bilingual output, and per-slot content themes. Do not use for non-social-media tasks or platforms outside the named social workflow.'
triggers:
- User wants daily or recurring X/Twitter post ideas delivered automatically
- User has a personal-brand posting cadence (morning/noon/afternoon/evening)
- User wants drafts sent back into the current chat on a schedule
- User wants bilingual CN-first + EN output instead of English-only
---

# X content cron setup

Use this when a user wants recurring X/Twitter drafts delivered automatically via Hermes cron jobs.

## What worked well

For a creator-style X workflow, a single daily bundle is often less useful than separate time-based jobs. A better structure is:

1. Morning AI brief
2. Noon lunch-photo + anti-hustle post
3. Afternoon AI usage/workflow post
4. Evening cat/lifestyle/light post

This matches how users actually post during the day and lets each prompt stay focused.

## Recommended approach

### 1) Capture posting structure first
Extract or confirm:
- posting times
- number of posts per slot
- language style
- fixed themes by slot
- delivery target

Example slot structure:
- 09:00 morning AI brief
- 11:30 lunch-photo anti-hustle post
- 16:00 AI usage / workflow post
- 20:30 cat / evening-life post

### 2) Prefer multiple cron jobs over one large daily batch
Create one cron per posting slot instead of a single daily bundle when:
- each time slot has a different content goal
- the user wants to post throughout the day
- prompts need different tone / output extras

Use `cronjob(action='update')` if converting an existing daily bundle into a structured cadence.

### 3) Write slot-specific prompts
Each cron prompt should be self-contained because cron runs do not have current-chat context.

Include:
- the user's positioning
- the slot theme
- output language rules
- tone constraints
- formatting requirements
- one useful extra note per slot

### 4) Use bilingual output carefully
If the user dislikes English-only drafts because they feel too "pretentious", use:
- Chinese first
- natural English underneath
- explicit instruction that Chinese should feel native and conversational
- explicit instruction that English should be simple and natural, not over-polished

### 5) Add slot-specific helper metadata
This increases usefulness without much token cost:
- Morning: `适合什么时候发`
- Noon: `配图建议`
- Afternoon: `使用场景`
- Evening: `配图建议`

## Prompt templates

### Morning AI brief
Generate 1 ready-to-post bilingual (Chinese-first, then natural English) X/Twitter draft for the morning. Focus on AI brief / AI observation / AI industry or tool insight. Tone: calm, smart, authentic, not preachy, not too polished, not salesy. Keep it concise and natural for X. Avoid hashtags unless truly necessary. Add a short Chinese note called `适合什么时候发` with a recommended posting time in the morning and one-sentence reason.

### Noon lunch anti-hustle post
Generate 1 ready-to-post bilingual (Chinese-first, then natural English) X/Twitter draft for noon. It should pair with a lunch photo and carry a light anti-hustle / sustainable work / breathing-space angle. It should feel personal, grounded, and unpretentious. Add a short Chinese note called `配图建议` describing how to pair it with the lunch photo.

### Afternoon AI usage post
Generate 1 ready-to-post bilingual (Chinese-first, then natural English) X/Twitter draft for the afternoon. Focus on a practical AI use case, workflow, experiment, or tool observation from the perspective of a programmer. Useful but not a tutorial thread. Add a short Chinese note called `使用场景` explaining the implied real usage context.

### Evening cat post
Generate 1 ready-to-post bilingual (Chinese-first, then natural English) X/Twitter draft for the evening. Involve the cat, daily life, humor, or a soft reflection. Warm, lightly witty, authentic, not cheesy. Add a short Chinese note called `配图建议` describing the best cat or evening-life photo to pair with it.

## Example cron commands

### Update existing morning job
```json
{
  "action": "update",
  "job_id": "<existing_job_id>",
  "name": "morning-ai-brief",
  "schedule": "0 9 * * *",
  "deliver": "origin",
  "prompt": "<self-contained morning prompt>"
}
```

### Create noon job
```json
{
  "action": "create",
  "name": "noon-lunch-anti-hustle-post",
  "schedule": "30 11 * * *",
  "deliver": "origin",
  "prompt": "<self-contained noon prompt>"
}
```

### Create afternoon job
```json
{
  "action": "create",
  "name": "afternoon-ai-usage-post",
  "schedule": "0 16 * * *",
  "deliver": "origin",
  "prompt": "<self-contained afternoon prompt>"
}
```

### Create evening job
```json
{
  "action": "create",
  "name": "evening-cat-post",
  "schedule": "30 20 * * *",
  "deliver": "origin",
  "prompt": "<self-contained evening prompt>"
}
```

## Pitfalls

- Do not leave prompts dependent on current conversation context; cron runs are stateless.
- English-only output may be rejected by Chinese-first users as too performative.
- A single bundle of 5+ posts can be less useful than dayparted drafts.
- If the user wants a very specific posting rhythm, store exact times and update schedules explicitly.
- Keep tone constraints explicit: not salesy, not preachy, not over-branded, not content-factory style.

## Good defaults

- Delivery target: `origin`
- Style: bilingual, Chinese first
- Structure: one post per slot
- Hashtags: avoid by default
- Voice: calm, smart, lightly witty, authentic

## Nice follow-up upgrades

After the core cron setup works, offer:
- reply/comment templates for interacting under other people's posts
- per-post image guidance
- best post order for the day
- more than one candidate per slot if the user posts frequently
- attach 2-3 same-day reply ideas to each slot if the user wants growth through interaction, not just posting

### Optional: include reply templates in the cron output
If the user wants help engaging under other people's posts, extend each cron prompt with a small second section such as:
- `今日可回复` or `今天可互动`
- 2-3 short replies
- replies should match the user's language preference and the slot theme
- replies should feel conversational, not like networking spam

This works especially well for AI / programmer / anti-hustle accounts where replies can reinforce positioning without needing a full new post.

## Verification checklist

Before finishing:
1. Confirm the final cron schedules match the user's requested times.
2. Confirm all jobs deliver to the intended target.
3. Confirm prompts are self-contained and include the personal-brand positioning.
4. Confirm output language and tone match the user's preference.
5. If any cron job shows `last_status=error`, first simplify the prompt into a shorter fully self-contained version, then `cronjob(action='run')` it once to verify recovery before declaring success.
6. For reliability-first users, prefer pausing obviously misconfigured jobs over leaving them scheduled to fail repeatedly.
