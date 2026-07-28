---
name: github-daily-weekly-report
description: Use when 用户请求匹配此工作流：基于 GitHub API 生成仓库日报/周报，汇总 PR、Issue、CI、Release、活跃成员与风险项；支持 Hermes cron 定时投递. Do not use for non-GitHub tasks, generic git-only work, or adjacent GitHub workflows covered by a narrower github-* skill.
license: MIT
metadata:
  hermes:
    tags:
    - GitHub
    - Daily-Report
    - Weekly-Report
    - Automation
    - Cron
    - Metrics
    related_skills:
    - github-auth
    - github-pr-workflow
    - github-issues
    - github-repo-management
---

# GitHub 日报 / 周报

为一个或多个 GitHub 仓库生成结构化的日报、周报，适合团队同步、个人跟进、外部汇报。

## 适用场景

- "帮我做 GitHub 日报"
- "按几个 repo 输出周报"
- "每天汇总 PR / issue / CI 状态"
- "每周看哪些项目最活跃、哪些地方卡住了"
- "把 GitHub 动态发回 Hermes / Feishu / 邮件"

## 核心能力

可汇总以下维度：

1. **PR**
   - 新开 PR
   - 已合并 PR
   - 仍然打开的重点 PR
   - 按作者统计

2. **Issue**
   - 新建 issue
   - 已关闭 issue
   - 仍然未关闭的高风险 issue
   - 按标签 / assignee 统计

3. **CI / Workflow**
   - 最近失败的 workflow runs
   - 重复失败的 workflow
   - 最近一次成功/失败时间

4. **Release / Deployment**
   - 新 release
   - 新 tag
   - 可选：部署工作流摘要

5. **活跃度与风险**
   - 最活跃 repo
   - 最活跃作者
   - 风险摘要
   - 建议关注项

## 前置条件

开始前先检查 GitHub 鉴权。必须先阅读并遵循：
- `github-auth`

推荐检测命令：

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH=gh"
else
  HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
  if [ -z "$GITHUB_TOKEN" ] && [ -f "$HERMES_HOME/.env" ]; then
    export GITHUB_TOKEN=$(grep '^GITHUB_TOKEN=' "$HERMES_HOME/.env" | head -1 | cut -d= -f2- | tr -d '\r')
  fi
  if [ -n "$GITHUB_TOKEN" ]; then
    echo "AUTH=curl"
  else
    echo "AUTH=none"
  fi
fi
```

本机如果没有 `gh` 也没关系，**优先走 GitHub REST API + token fallback**。

> 补充：如果目标仓库是 **公开仓库**，临时日报/周报可直接走 **未鉴权的 GitHub 公开 REST API**（带 `User-Agent` 头），即使没有 `GITHUB_TOKEN` 也能先产出一版；只有遇到私有仓库、较高频率调用或更高配额需求时，才必须配置 token。

## 输入约定

执行这个 skill 前，先明确以下输入：

- **repo 列表**：例如 `owner1/repo-a owner2/repo-b`
- **周期**：`daily` 或 `weekly`
- **时间窗口**：
  - 日报：最近 24 小时
  - 周报：最近 7 天
- **输出渠道**：origin / Feishu / 钉钉 / 邮件 / 本地文件
- **是否包含：**
  - CI 失败
  - release
  - 活跃作者排行
  - 风险总结

## 推荐工作流

```text
repo 列表
   │
   ├─► PR 数据（opened / merged / open backlog）
   ├─► Issue 数据（opened / closed / open backlog）
   ├─► Workflow runs（failed / success / repeated failures）
   ├─► Releases（optional）
   └─► 作者 / 仓库聚合
              │
              ▼
         AI 总结 + 风险判断
              │
              ▼
        输出日报 / 周报 Markdown
```

## 推荐实现方式

### 方式 A：轻量直接跑
用 skill 附带的 `scripts/github_report.py`。注意要优先走 `HERMES_HOME`，不要硬编码 `~/.hermes`：

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
python3 "$HERMES_HOME/skills/github/github-daily-weekly-report/scripts/github_report.py" \
  --mode daily \
  --repos owner/repo1 owner/repo2
```

周报：

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
python3 "$HERMES_HOME/skills/github/github-daily-weekly-report/scripts/github_report.py" \
  --mode weekly \
  --repos owner/repo1 owner/repo2
```

### 方式 B：Hermes cron 定时投递
适合自动日报 / 周报。

日报 cron 示例：

```json
{
  "action": "create",
  "name": "github-daily-report",
  "schedule": "0 10 * * *",
  "deliver": "origin",
  "prompt": "为以下 GitHub 仓库生成中文日报：owner/repo1, owner/repo2。统计窗口为过去 24 小时。必须包含：新增 PR、合并 PR、新增 issue、关闭 issue、失败 CI、风险摘要。若无数据，明确写无。输出为简洁 Markdown。"
}
```

周报 cron 示例：

```json
{
  "action": "create",
  "name": "github-weekly-report",
  "schedule": "0 10 * * 1",
  "deliver": "origin",
  "prompt": "为以下 GitHub 仓库生成中文周报：owner/repo1, owner/repo2。统计窗口为过去 7 天。必须包含：PR/issue 汇总、活跃作者、失败 workflow、release、风险与下周关注项。输出为简洁 Markdown。"
}
```

> 注意：cron 是无上下文执行，prompt 必须写全 repo 列表和输出要求。

## 指标抓取建议

### PR

REST API：

```bash
GET /repos/{owner}/{repo}/pulls?state=all&sort=updated&direction=desc&per_page=100
```

建议统计：
- `created_at` 落入窗口 → 新开 PR
- `merged_at` 落入窗口 → 已合并 PR
- `state=open` 且 `updated_at` 最近 → 重点 open PR

### Issue

REST API：

```bash
GET /repos/{owner}/{repo}/issues?state=all&since=<ISO8601>&per_page=100
```

注意：`/issues` 会混入 PR，需要过滤掉含 `pull_request` 字段的项。

建议统计：
- `created_at` 落入窗口 → 新增 issue
- `closed_at` 落入窗口 → 已关闭 issue
- open 且高优标签 → 风险项

### Workflow runs

REST API：

```bash
GET /repos/{owner}/{repo}/actions/runs?per_page=50
```

建议统计：
- `conclusion=failure` 且 `updated_at` 落入窗口 → 失败 CI
- 同一个 workflow 多次 failure → 重复问题

### Releases

REST API：

```bash
GET /repos/{owner}/{repo}/releases?per_page=20
```

建议统计：
- `published_at` 落入窗口 → 新 release

## 推荐输出格式

### 日报

```markdown
# GitHub 日报
> 时间窗口：{start} ~ {end}
> 仓库：{repo_list}

## 总览
- 新开 PR：X
- 合并 PR：Y
- 新增 Issue：A
- 关闭 Issue：B
- 失败 CI：C
- 新 Release：D

## 各仓库摘要
### owner/repo1
- PR：...
- Issue：...
- CI：...
- 风险：...

### owner/repo2
- PR：...
- Issue：...
- CI：...
- 风险：...

## 活跃作者
1. user-a：...
2. user-b：...

## 今日风险
- ...

## 建议关注
- ...
```

### 周报

```markdown
# GitHub 周报
> 时间窗口：{start} ~ {end}
> 仓库：{repo_list}

## 本周总览
- 新开 PR：X
- 合并 PR：Y
- 新增 Issue：A
- 关闭 Issue：B
- 失败 CI：C
- 新 Release：D

## 仓库维度
### owner/repo1
- 本周进展：...
- 关键 PR：...
- 关键 Issue：...
- CI 情况：...
- 风险：...

## 活跃作者排行
1. user-a：开 PR 2 / 合并 3 / issue 1
2. user-b：...

## 本周风险
- ...

## 下周建议关注
- ...
```

## 风险判断规则

生成总结时优先关注：

1. **CI 连续失败**
2. **高优 issue 未关闭且持续更新**
3. **open PR 积压明显**
4. **只有 issue 增长、没有 PR/merge 对应推进**
5. **单个 repo 活跃度异常下降**

## 适合的默认判断

### 日报更适合看：
- 今天发生了什么
- 有什么阻塞
- 哪个仓库需要盯

### 周报更适合看：
- 哪个项目真的推进了
- 谁在持续产出
- 风险有没有累计
- 下周应把注意力放哪

## 常见坑

- GitHub `/issues` 接口包含 PR，必须过滤。
- merged PR 不能只看 `state=closed`，必须检查 `merged_at`。
- workflow runs 只看最新一次会漏掉重复失败，要按 workflow name 聚合。
- 周报不要只堆数字，必须给出**风险和关注项**。
- cron prompt 必须自包含，不能依赖当前聊天上下文。
- 如果 repo 仍是 `owner/repo1` 这类占位符，或 `GITHUB_TOKEN` 实际未配置，任务大概率只会反复报错；这种情况下**先 pause 任务**，等真实 repo 和 token 配好后再 resume，比让错误任务长期运行更稳。
- 本机曾出现 `HERMES_HOME/.env` 里只有 `# GITHUB_TOKEN` 注释、没有真实值的情况；创建任务前应先确认 token 真存在，而不是只看见相关注释就误判为已配置。
- 如果用户目标只是“定时任务能成功”，优先修复已有失败任务，并暂停那些因外部前置条件缺失而必然失败的任务。
- 如果用户要的不是 repo 运营日报，而是**类似截图那种 AI 开源/AI 编码资讯简报**，不要继续沿用 PR/Issue/CI 模板；应改用**固定栏目 prompt**直接驱动 cron 输出：`Cronjob Response` + 日期标题 + `GitHub Trending 日榜/周榜` + `GitHub 近期热门补充` + `中文资讯` + `Hacker News 热门讨论` + `开发者社区讨论`。
- `https://github.com/trending?since=daily|weekly` 在这个环境里可能频繁超时；实现这类简报时要准备 fallback：优先用 GitHub Search API / 公开 GitHub API 补“近期热门项目”，而不是因为 Trending 页面超时就整份任务失败。
- Reddit 在这个环境里经常 reset / timeout；若 Reddit 不可访问，可自然替换为 Lobsters、HN 相关 Show HN、Product Hunt 或其他公开开发者社区内容，但不要把“系统报错”写进最终简报。
- 对这类“按截图效果输出”的任务，优先直接匹配用户给定格式，不要反复讨论模板优劣或改写成分析型报告。

## 验证清单

输出前检查：
1. repo 列表是否完整
2. 时间窗口是否正确
3. issues 里是否已过滤 PR
4. merged PR 是否按 `merged_at` 统计
5. 是否输出了风险摘要，而不只是流水账
6. 若要自动发送，cron deliver 目标是否正确
