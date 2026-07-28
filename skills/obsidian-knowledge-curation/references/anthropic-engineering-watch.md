# Anthropic Engineering Watch Pattern

Session-derived pattern for turning an official article index into an Obsidian learning backlog + Hermes cron job.

## Trigger

Use this when the user asks to periodically monitor an official source and organize new/old articles into an existing Obsidian learning folder.

Example source/destination from the session:
- Source: `https://www.anthropic.com/engineering`
- Vault: `/Users/heytea/Documents/obsidian_note`
- Destination: `anthropic 学习/01-Engineering`

## Steps

1. Inspect the destination folder before scheduling:
   - list existing notes
   - read `_index.md`
   - read 1-2 representative notes to match format
   - extract original source URLs already present in notes

2. Build a deterministic scan script in `~/.hermes/scripts/`:
   - fetch the source index page
   - extract canonical article URLs
   - normalize trailing slashes and query strings
   - compare against URLs found in existing notes
   - output compact JSON with `article_count`, `covered_count`, `missing_count`, `articles`, and `missing`

3. Create a Hermes cron job:
   - attach relevant Obsidian skills
   - enable only needed toolsets such as `terminal` and `file`
   - use the scan script as `script`
   - instruct the cron prompt to process missing/new articles, not merely report them
   - use a bounded batch size for large backlogs

4. Write a watch/backlog note in the destination folder:
   - source URL
   - cron job ID/name
   - scan script path
   - schedule
   - current coverage counts
   - backlog checklist
   - curation rules

5. Update `_index.md` so the watch note is discoverable.

6. If the user changes timing later, update schedule metadata consistently:
   - `cronjob update` schedule expression
   - cron prompt wording (for example `每天北京时间 19:00`)
   - the Obsidian watch note's schedule line
   - verify the next run with `cronjob list` before saying it is done.

## Note format for article curation

Match the local folder style. For Anthropic learning notes, this structure worked well:

```md
# <Article Title>

- 原文链接：<url>
- 推荐理由：<why Allen should read it>
- 阅读日期：YYYY-MM-DD

## 阅读关注点
- ...

## 一句话总结
...

## 中英对照笔记
### 1. <core point>
**English**
<key terms / short faithful restatement>

**中文**
<faithful Chinese explanation>

**我的理解**
- <connection to Hermes / Codex / multi-agent / QA / workflow>

## 最重要的 3 个观点
1. ...

## 可以迁移到我自己工作流/产品里的点
- ...

## 仍然没想明白的问题
- ...

## 想继续延伸阅读的关键词
- ...

## 相关链接
- [[Anthropic 学习总览]]
- [[01-Engineering/_index|01-Engineering]]
```

## Pitfalls

- Do not create the cron before inspecting the existing Obsidian note style.
- Do not use a pure notification/watchdog job if the user asked to整理旧文章; the job must actually write/update notes.
- Do not overfit to RSS availability. If the official page has stable article links, a small HTML link extractor is often enough.
- Do not mark missing articles as covered unless an existing note contains the exact canonical original URL.
- Do not mirror full article text into Obsidian; write high-signal learning notes with provenance.
