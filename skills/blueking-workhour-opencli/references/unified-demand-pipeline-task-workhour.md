# 蓝鲸需求—流水线—任务—工时统一编排

## 适用目标

当用户希望把蓝鲸需求、需求/服务流水线、关联任务、每日工时和周期工时汇总串成统一工作流时，使用本参考。

## 推荐架构

采用一个统一 CLI/Skill 入口，底层按领域拆分适配器：

```text
Hermes / Feishu
  -> blueking operations skill
  -> unified CLI
     -> DemandAdapter (VTeam API)
     -> TaskAdapter (VTeam API)
     -> WorklogAdapter (man-hour plugin API)
     -> PipelineAdapter (BK-CI OpenAPI or MCP)
     -> BrowserFallback (OpenCLI authenticated page)
     -> ServiceRegistry (service-to-pipeline mapping)
     -> AuditStore (dry-run, idempotency, read-back)
```

### 实现优先级

1. API/OpenAPI 优先：稳定、参数化、容易回读验证。
2. OpenCLI 作为认证态或尚未封装接口的兜底，不把 DOM 点击作为长期主路径。
3. 流水线可复用腾讯蓝鲸 `managing-devops-pipeline` 的安全语义：先取启动参数，展示完整参数，确认后启动，再按 `buildId` 查询状态。
4. 不把“操作现有流水线”误判为“创建或修改流水线定义”。新建流水线定义应单独立项。

## 五类业务动作

| 动作 | 推荐主路径 | 验证方式 |
|---|---|---|
| 创建需求并匹配服务 | VTeam API + ServiceRegistry | 回读需求详情和编号 |
| 打开需求/流水线 | URL 生成 + 系统浏览器/OpenCLI | 校验 URL 与项目/流水线 ID |
| 从需求创建任务 | VTeam API | 回读任务及需求关联 |
| 填写每日工时 | Man-hour plugin API | 回读记录、累计和剩余工时 |
| 查询时间范围工时 | 枚举相关任务并并发读取工时记录，按 `jobDate` 过滤聚合 | 与页面抽样对账 |
| 查询/启动流水线 | BK-CI OpenAPI/MCP | 回读 `buildId`、终态和 Stage 状态 |

## 服务流水线映射

不要靠名称模糊搜索作为唯一依据。维护非敏感注册表：

```yaml
projects:
  agile_project: <vteam-project-id>
  pipeline_project: <bk-ci-project-id>
services:
  invoice:
    aliases: [发票, 发票助手]
    demand_pipeline:
      project_id: <project-id>
      pipeline_id: p-xxxx
    service_pipelines:
      - name: invoice-service
        project_id: <project-id>
        pipeline_id: p-yyyy
        defaults:
          branch: master
          env: test
```

只保存业务映射和非敏感 ID；Token、Cookie、Authorization Header 不进入 Skill、配置、Git 或审计日志。

## 写操作统一规则

| 操作 | 默认 | 实际执行 | 回读验证 |
|---|---|---|---|
| 查询、打开页面 | 直接执行 | 无需确认 | 检查返回状态/URL |
| 创建需求/任务 | dry-run | `--yes` | 回读对象及关联关系 |
| 填写工时/状态流转 | dry-run | `--yes` | 回读记录、累计工时和最终状态 |
| 启动流水线 | dry-run | 完整参数预览后 `--yes` | 查询构建终态和失败 Stage |
| 删除工时 | 默认禁止 | 精确 recordId + 明确确认 | 回读确认记录消失 |

## 幂等键建议

- 需求：`project + normalized_title`
- 任务：`project + demandId + operator + taskType + startDate + titleSuffix`
- 工时：`project + taskId + jobDate + normalized_content + hours`
- 流水线启动：默认不自动去重；在预览中展示最近同参数构建，避免误触发。

## 周期工时汇总算法

1. 拉取本人创建、负责或参与的任务集合。
2. 并发读取每个任务的工时记录。
3. 以 `jobDate` 过滤起止日期，不要只按任务创建时间或计划时间过滤。
4. 按记录 ID 去重。
5. 按日期、任务、需求和服务聚合。
6. 输出每日总工时、周期总工时、未满/超过 8 小时的工作日及任务链接。

## 分阶段交付

1. 只读发现：识别真实 `projectId`、`pipelineId`、服务映射和 OpenAPI。
2. 统一查询：需求、任务、工时范围报告、流水线历史。
3. 任务/工时写入：dry-run、幂等、回读。
4. 流水线启动：启动参数、确认、状态轮询。
5. 一键编排：创建需求、匹配流水线、创建任务并输出入口；默认不要随创建需求自动启动构建。

## 已落地的关联任务 OpenCLI

本机统一 CLI 已支持：

```bash
cd '/Users/heytea/Documents/new_tools/auto蓝鲸工时'
node blueking-opencli-workhour.mjs create-related-task \
  --demand p35_15439 \
  --title '任务标题' \
  --type code \
  --operator H003919 \
  --start 2026-07-16 \
  --end 2026-07-18 \
  --hours 8
```

- 默认是 dry-run：真实查询需求、解析经办人、检查关联任务、展示请求，但不写入。
- 确认后加 `--yes` 执行。
- 幂等身份使用 `需求 + 标题 + 经办人 + 起止日期`；预估工时等字段变化应作为 conflict 返回，不能因为字段漂移再创建一个同名任务。
- `--yes` 也必须先通过相同的防重检查；命中已有任务时返回 `skipped: true`，不能 POST。
- 新建成功后必须回读任务详情及需求关联；任一回读失败都不能报告成功。

## 常见陷阱

- 不要继续堆叠多套入口各自维护认证、项目 ID、输出格式和幂等逻辑。
- 不要把浏览器扩展或 DOM 选择器作为长期唯一实现。
- 不要在创建需求后自动启动所有服务流水线；创建与构建应分开确认。
- 不要仅查询单个任务的工时来回答时间范围汇总；必须跨任务聚合。
- 不要把个人令牌写进示例或日志；优先使用系统密钥存储并申请最小权限。
