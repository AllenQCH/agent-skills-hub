---
name: alidocs-test-delivery-doc
description: Use when Codex needs to create a DingTalk AliDocs online spreadsheet test-delivery document from development evidence, BK demand pipeline results, service branches, commits, verification output, risks, rollback notes, or release handoff data.
---

# AliDocs Test Delivery Doc

## Overview

Create a DingTalk online spreadsheet as the test-delivery handoff after development and BK demand pipeline creation. Follow the legacy AliDocs test-delivery template structure; use deterministic evidence first and leave missing source data blank instead of inventing facts.

## Required Inputs

- Target location:
  - Domestic demands (`region=cn`) must be created in `国内迭代`; the script defaults to `workspaceId=26116527504` and `folderId=P7QG4Yx2Jp7N1PAgi41lknj2V9dEq3XD` when no explicit target is provided.
  - Overseas demands (`region=intl`) must be created in `海外迭代`; if the local default mapping is not configured, pass `--workspace-id` and `--folder-id` explicitly instead of creating in a generic workspace.
  - Explicit `--workspace-id` / `--folder-id` always overrides region defaults.
- Development evidence: BK requirement number/Chinese title/url, role, region, module, services, branches, commits, change summary, verification, risks, rollback. The requirement number and Chinese title are mandatory because the document name must match the BK demand. Mark Maven dependency repositories with `repository_type=maven_dependency` or `remote_action=artifact_publish` when no BK config is available.
- BK pipeline result: prefer `docs/bk/{需求编号}.json` after `bk-pipeline-create step2`, because it contains `pipelineId`, `buildId`, `taskId`, project, services, branches, and demand metadata.
- Template reference: legacy AliDocs template `https://alidocs.dingtalk.com/i/nodes/93NwLYZXWygl1LqZCZzbGwavJkyEqBQm` has 6 sheets in the required order.

## Workflow

1. Verify `dws auth status --format json`; if unauthenticated, use `dws-auth-helper`.
2. Gather evidence from deterministic sources: BK config JSON, `git status`, branch, commit log, diff stat, OpenSpec, test/build output, and user notes.
   The `服务清单` represents deployable services in the demand pipeline, not every changed repository. When BK config is present, its bound services are authoritative; Maven dependency artifacts used only for `install/deploy` must not appear as service rows.
3. Build an evidence JSON. Leave unknown owners, environments, verification, DB scripts, config changes, rollback, and other missing source data empty or omit those fields.
   If the evidence omits负责人 and `developer.name/id`, the script will fall back to the matching service repo's `git config user.name` under the current working directory, preferring repo-local config when present.
4. Preview with the OpenCLI entry in dry-run mode. For normal domestic delivery, rely on `region=cn` in the evidence JSON and do not pass a generic workspace target:

```bash
opencli heytea-alidocs create-test-delivery \
  --evidence /path/to/evidence.json \
  --bk-config /path/to/docs/bk/p35_12345.json \
  --dry-run
```

5. Before writing online, check the dry-run `targetSource`, `targetFolderName`, `workspaceId`, and `folderId`. If `region=cn`, it must show `targetFolderName=国内迭代`. If `region=intl`, it must show `海外迭代` or require explicit target parameters. Set the document name to `<蓝鲸需求号>-<蓝鲸需求中文标题>`, exactly matching the BK demand and the deployable-service branch name after removing `feature/`. Do not add a date, shorten the title, or create when either field is missing. If `--name` is supplied, it must equal this generated name.
6. Create the spreadsheet and write sheets. The default `batch` strategy bootstraps the six tabs in one `table_put` call, then writes all values and header styles in one atomic `batch_update` call:

```bash
opencli heytea-alidocs create-test-delivery \
  --evidence /path/to/evidence.json \
  --bk-config /path/to/docs/bk/p35_12345.json
```

Use `--write-strategy legacy` only as a compatibility fallback when the current DingTalk batch tools are unavailable. A dry-run reports the estimated remote calls for both strategies; the current six-sheet workbook is approximately 6 calls with `batch` versus 22 with `legacy`.

7. Read back the created sheet list with `dws sheet list --node <nodeId> --format json` and report the online link.

## Evidence JSON

Use this shape; extra keys are ignored unless the script supports them:

```json
{
  "role": "iterative_feature_development",
  "region": "intl",
  "module": "pof",
  "requirement": {
    "number": "p45_1234",
    "title": "需求标题",
    "url": "https://..."
  },
  "services": [
    {
      "name": "service-name",
      "repository_type": "deployable_service",
      "remote_action": "service_deploy",
      "branch": "feature/p45_1234-中文描述",
      "commits": ["abc1234 summary"],
      "changes": ["新增字段透传", "补充 mapper"],
      "verification": ["mvn test passed"],
      "risks": [],
      "rollback": ""
    }
  ],
  "test_focus": ["接口回归", "字段落库"],
  "open_questions": []
}
```

## Output Sheets

The spreadsheet uses the legacy 6-sheet template in this exact order:

- `服务清单`: `流水线名称 / 服务AppID / 服务名 / 名称 / 负责人 / 分支 / 服务等级 / 是否新服务 / 服务规格 / 首次部署流水线 / 需求流水线`
- `提测配置清单-TEST`: `服务 / 配置 / 负责人 / 备注`
- `提测配置清单-PROD`: `服务 / 配置 / 负责人 / 备注`
- `数据库脚本`: `数据库类型 / 数据库名称 / DDL语句 / 负责人 / 涉及服务名称 / 状态`
- `定时任务 XXL-JOB`: top section `AppName / 名称 / 注册方式`, plus job section `执行器 / 任务描述 / 负责人 / 报警邮件 / 调度类型 / Cron / 运行模式 / JobHandler / 任务参数 / 路由策略 / 子任务id / 调度过期策略 / 阻塞处理策略 / 任务超时时间 / 失败重试次数 / 状态`
- `发布流程`: `步骤 / 动作 / 完成情况 / 预计时间 / 备注`

DingTalk creates one default blank sheet when a new spreadsheet is created. The script reuses that first sheet for `服务清单`, then calls hidden canonical MCP tool `dws mcp sheet update_sheet` to rename it and pin it at index `0`. In the default batch strategy, `table_put` receives empty data and only bootstraps missing tabs in reverse order; this avoids the `dws v1.0.10` schema mismatch that rejects primitive `table_put.data` cells. One `batch_update` then writes all six value matrices with their header styles. Every first-row header is bold, and `定时任务 XXL-JOB` also bolds its second header row at `A11:P11`. Always read back with `dws sheet list --node <nodeId> --format json`; do not claim success until the returned tab order matches the expected 6-sheet template.

## Guardrails

- Do not use `dws doc` as a dependency for v1. In current HeyTea DingTalk setup, doc MCP may be disabled by the enterprise admin.
- Do not assume the parent folder from an AliDocs URL. Use `workspaceId` root unless a real `folderId` is available.
- Do not trigger, stop, retry, or create BK pipelines here. This skill only consumes pipeline results.
- Do not claim the document was created until `dws` returns success and `sheet list` can read it back.
- Treat online document creation as an external write. Confirm parameters with the user unless the active project workflow already explicitly authorized this delivery step.
- Do not create delivery docs in a generic workspace root for demand handoff. Resolve the region folder first: `国内迭代` for `cn`, `海外迭代` for `intl`.
- Do not create a delivery document when its name differs from `<蓝鲸需求号>-<蓝鲸需求中文标题>`.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Using browser-visible AliDocs state as write proof | Use `dws sheet` write/readback results. |
| Trying `dws doc info/list/copy` first | Use `sheet create` for v1; doc MCP can be disabled. |
| Inventing verification or rollback | Leave cells blank and list the evidence gap in the final response. |
| Returning only a pipeline URL | Put the demand pipeline detail URL into `服务清单.需求流水线`, then return the AliDocs link. |
| Listing Maven dependency repositories as services | Keep them in build/dependency evidence, but omit them from `服务清单`; only demand-pipeline deployable services belong there. |
| Creating a custom 5-sheet document | Use the legacy 6-sheet template names and headers exactly. |
| Assuming create success means tab order is correct | Read back `dws sheet list`; confirm the first tab is `服务清单` and the 6 tabs are in template order. |
| Forgetting sheet header emphasis | After writing values, apply bold to template header rows so generated docs are visually distinguishable from raw sheets. |
| Adding a date or shortening the BK title in the document name | Use the exact `<蓝鲸需求号>-<蓝鲸需求中文标题>` value and block creation when either source field is missing. |
