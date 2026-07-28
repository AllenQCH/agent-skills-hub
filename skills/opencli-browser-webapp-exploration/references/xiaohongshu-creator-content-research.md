# Xiaohongshu / Rednote creator content research with opencli

Use this when the user wants a creator's posts organized into themes, especially when the home feed is noisy or not chronological.

## What worked

### 1) Prefer the Xiaohongshu adapter over raw browser clicking
For creator-content research, the dedicated adapter is much more reliable than trying to navigate the web UI manually.

Useful commands:
- `opencli xiaohongshu search '<query>' --limit 20 -f json --site-session persistent`
- `opencli xiaohongshu user '<profile-url-or-user-id>' --limit 30 -f json --site-session persistent`
- `opencli xiaohongshu note '<full-signed-note-url>' -f json --site-session persistent`
- `opencli xiaohongshu feed --limit 20 -f json --site-session persistent`

### 2) Finding a creator from a nickname query
Searching a nickname may return note hits first rather than the creator directly. In the results, inspect:
- `author`
- `author_url`

If the target creator appears as an author on one of the hits, use that `author_url` as the canonical profile URL, then call `opencli xiaohongshu user` on it.

Example pattern:
1. Search creator nickname.
2. Find the row where `author` matches the target creator.
3. Copy `author_url` from that row.
4. Call `opencli xiaohongshu user '<author_url>' --limit 30 -f json`.

### 3) Important pitfall: `note` requires a full signed URL
`opencli xiaohongshu note` does **not** accept a bare note ID. It needs the full Xiaohongshu note URL including `xsec_token`.

Reliable source of signed URLs:
- `opencli xiaohongshu user ... -f json`
- `opencli xiaohongshu search ... -f json`

Each note entry returned by those commands includes a usable signed `url`.

### 4) Good workflow for content organization
For a creator study task:
1. Use `search` to locate the creator if you only have the display name.
2. Use `user` to fetch the recent note list.
3. Group titles into buckets before reading every post:
   - 学习路线 / 方法论
   - 工程实战 / 项目设计
   - 面试 / 简历 / 求职
   - 职业转型 / 决策
4. Then read only the high-value notes in each bucket with `note`.
5. Produce two outputs:
   - a categorized inventory
   - a short “rapid learning” reading order

This avoids wasting time on every post and keeps the final writeup structured.

## What did NOT work well

### Raw browser exploration for following feed / creator detail
Using generic browser-state exploration on Xiaohongshu web UI was much noisier than the adapter path:
- the visible homepage is recommendation-heavy
- following/follows lists are not trivially exposed as clickable state
- direct fetches to some internal endpoints may fail even when logged in

For content research, start with the adapter first; drop to browser inspection only if the adapter lacks a needed surface.

## Output pattern that worked well

For the final deliverable, produce:
1. one-paragraph conclusion about what the creator is actually valuable for
2. 3-5 major topic buckets
3. 6-10 recommended priority posts
4. a rapid learning path (what to read first / second / third)
5. optional local markdown artifact path if you wrote a study note
