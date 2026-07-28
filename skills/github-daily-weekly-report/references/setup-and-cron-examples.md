# Setup and cron examples

## One-shot daily report

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
python3 "$HERMES_HOME/skills/github/github-daily-weekly-report/scripts/github_report.py" \
  --mode daily \
  --repos owner/repo1 owner/repo2
```

## One-shot weekly report

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
python3 "$HERMES_HOME/skills/github/github-daily-weekly-report/scripts/github_report.py" \
  --mode weekly \
  --repos owner/repo1 owner/repo2
```

## Hermes cron: daily

```json
{
  "action": "create",
  "name": "github-daily-report",
  "schedule": "0 10 * * *",
  "deliver": "origin",
  "prompt": "为以下 GitHub 仓库生成中文日报：owner/repo1, owner/repo2。统计窗口为过去 24 小时。必须包含：新增 PR、合并 PR、新增 issue、关闭 issue、失败 CI、风险摘要。若无数据，明确写无。输出为简洁 Markdown。"
}
```

## Hermes cron: weekly

```json
{
  "action": "create",
  "name": "github-weekly-report",
  "schedule": "0 10 * * 1",
  "deliver": "origin",
  "prompt": "为以下 GitHub 仓库生成中文周报：owner/repo1, owner/repo2。统计窗口为过去 7 天。必须包含：PR/issue 汇总、活跃作者、失败 workflow、release、风险与下周关注项。输出为简洁 Markdown。"
}
```
