---
name: bk-pipeline
description: Use when creating, triggering, retrying, stopping, or inspecting a HeyTea BlueKing (蓝盾/devops-bk) pipeline or service sub-pipeline through a fast deterministic opencli command instead of the slower LLM operator. Reuses the logged-in `bk-console` browser session and calls BK process REST APIs directly.
---

# BK Pipeline (opencli 指令)

用一条确定性脚本替代 `tool_bk_pipeline_operator` 的逐步 UI 导航：复用浏览器里已登录的
`bk-console` session，在页面上下文里跑同源鉴权 fetch 直接调 BK process REST API。
快、无需重复登录、可被任何 agent 直接调用。

## 前置
- Chrome + opencli Browser Bridge 已连通（`opencli doctor -v`）。
- 已在 Chrome 手动登录 `https://devops-bk.heyteago.com`（脚本不代登录，未登录会报 `LOGIN_REQUIRED`）。

## 命令
脚本：`scripts/bk_pipeline.py`

创建需求流水线时复用现有创建器的 OpenCLI 传输层。`create-only` 默认 dry-run，且永远不触发构建：

```bash
python3 /Users/heytea/Documents/skills/shop-ofc-skill/bk-pipeline/2.0.3/skills/bk-pipeline-create/scripts/run_pipeline.py \
  create-only \
  --config /absolute/workspace/docs/bk/<需求编号>.json \
  --workspace /absolute/workspace \
  --transport opencli \
  --name-suffix OpenCLI测试-YYYYMMDD-HHMMSS

# 人工核对计划后加 --confirm 才真正创建；创建后必须回读详情和构建历史 count=0。
```

父需求流水线完成登记后，可批量触发配置中的服务流水线；默认 dry-run：

```bash
python3 /Users/heytea/Documents/skills/shop-ofc-skill/bk-pipeline/2.0.3/skills/bk-pipeline-create/scripts/run_pipeline.py \
  trigger-services \
  --config /absolute/workspace/docs/bk/<需求编号>.json \
  --main-pipeline-id <父流水线ID> \
  --main-build-id <父构建ID> \
  --date-branch YYYYMMDD \
  --developer <工号>

# 校验全部服务启动字段、分支和运行状态后，加 --confirm 批量触发。
```

只读（随时可跑）：

```bash
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bk-pipeline/scripts/bk_pipeline.py inspect --project <projectCode> --pipeline <pipelineId> [--build <buildId>]
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bk-pipeline/scripts/bk_pipeline.py status --project <projectCode> --pipeline <pipelineId> --build <buildId>
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bk-pipeline/scripts/bk_pipeline.py startup-info --project <projectCode> --pipeline <pipelineId>
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bk-pipeline/scripts/bk_pipeline.py params --project <projectCode> --pipeline <pipelineId> --build <buildId>
```

写操作（默认 dry-run，只打印将发送的 payload；加 `--confirm` 才真正 POST）：

```bash
# 触发：参数是顶层字符串键值，例如 {"BK_CI_BUILD_MSG":"手动触发"}
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bk-pipeline/scripts/bk_pipeline.py trigger --project <p> --pipeline <id> --values-file payload.json
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bk-pipeline/scripts/bk_pipeline.py trigger --project <p> --pipeline <id> --values-file payload.json --confirm

python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bk-pipeline/scripts/bk_pipeline.py retry --project <p> --pipeline <id> --build <b> [--task <taskId>] --confirm
python3 /Users/heytea/Documents/myHeytea/code/agent-skills-hub/skills/bk-pipeline/scripts/bk_pipeline.py stop  --project <p> --pipeline <id> --build <b> --confirm
```

## 安全约束（沿用 operator 规则）
- 只读优先；`trigger/retry/stop` 需显式 `--confirm`。
- 绝不批量触发全部 service；必须指定明确的 pipeline/build。
- trigger payload **首次必须**先用 `params`/`startup-info` 或一次成功构建的真实 body 核验，再 `--confirm`。
- `params` 输出必须脱敏；禁止输出 PAT、token、password、cookie、credential 等变量值。
- 服务批量触发前，父需求构建必须已完成需求登记且不能处于失败/取消/终止状态。
- 不打印 cookie / CSRF / session。

## 获取入参
- projectCode / pipelineId / buildId 从流水线 URL 解析：
  `.../console/pipeline/<projectCode>/<pipelineId>/detail/<buildId>`
- demand↔service 关系与常用参数（DEMEND_ID、DEMEND_BUILD_ID、FEATURE_BRANCH 等）见
  `~/.codex/agents/operator/tool_bk_pipeline_operator.toml`。

## 与 operator 分工
- 新建需求流水线：使用上面的 `create-only`；需要完整初始化时才使用创建器原有 `step2`。
- 日常触发/重试/查状态：直接用本脚本（快）。
- 信息不全（不知道 pipelineId、需要在多个 service 里定位、需要复杂判断）：仍走
  `tool_bk_pipeline_operator` 让 LLM 兜底找 ID，拿到 ID 后回到脚本执行。

## BK process REST API（脚本内已封装）
- 流水线信息：`GET /ms/process/api/user/pipelineInfos/<p>/<id>/detail`
- 构建详情：`GET /ms/process/api/user/builds/<p>/<id>/<b>/detail`
- 启动字段：`GET /ms/process/api/user/builds/<p>/<id>/manualStartupInfo`
- 构建参数：`GET /ms/process/api/user/builds/<p>/<id>/<b>/parameters`
- executeCount：`GET /ms/process/api/user/pipelines/cw/pipeline/<id>/build/<b>/executeCount`
- 触发：`POST /ms/process/api/user/builds/<p>/<id>`  body `{"values":[...]}`
- 重试：`POST /ms/process/api/user/builds/<p>/<id>/<b>/retry`
- 停止：`POST /ms/process/api/user/builds/<p>/<id>/<b>/stop`
