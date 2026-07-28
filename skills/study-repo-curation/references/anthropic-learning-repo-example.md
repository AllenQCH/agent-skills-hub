# Anthropic learning repo example

This reference captures one concrete, reusable instance of the study-repo-curation pattern.

## Goal

Create a topic folder named `anthropic学习` with class-level module folders based on Anthropic's public site structure, then seed each module with numbered article-note files.

## Module structure used

1. `01-Engineering`
2. `02-Research`
3. `03-Blog-News`
4. `04-Learn-Tutorials`
5. `05-Policy-Commitments`

## File scaffolding pattern

Each article file used this structure:

```md
# <Article title>

- 原文链接：<url>
- 推荐理由：<why this is worth reading>

## 阅读关注点
- <focus 1>
- <focus 2>
- <focus 3>

## 我的笔记
- 阅读日期：
- 一句话总结：
- 最重要的 3 个观点：
  1.
  2.
  3.
- 可以迁移到我自己工作流/产品里的点：
- 仍然没想明白的问题：
- 想继续延伸阅读的关键词：
```

## Representative article choices

### Engineering
- Building effective agents
- Effective context engineering for AI agents
- The think tool
- How we built our multi-agent research system
- How we contain Claude across products

### Research
- Natural Language Autoencoders
- Teaching Claude why
- Project Deal
- Anthropic Economic Index report: Cadences
- What 81,000 people want from AI

### Blog / News
- Harnessing Claude’s intelligence
- Claude Managed Agents: get to production 10x faster
- Built-in memory for Claude Managed Agents
- Redesigning Claude Code on desktop for parallel agents
- Claude Code now supports artifacts

### Learn / Tutorials
- Anthropic Academy: Build and Learn with Claude
- Tutorials
- Developer docs

### Policy / Commitments
- Core views on AI safety
- Claude’s Constitution
- Responsible Scaling Policy

## Practical lesson

When the user wants both local structure and GitHub publishing, finish the local repo first, verify sample files, then treat remote publish as a separate step with its own confirmation/auth handling.