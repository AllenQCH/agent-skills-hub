# 飞书需求控制面 × 本地 Codex Multi-Agent 执行面

## 适用场景

Allen 提供一个需求链接，希望建立专属沟通群，并让需求真正进入本地 Multi-Agent 开发流水线，而不是只得到一份理论流程或提示词。

## 稳定架构

```text
Requirement URL
-> Hermes 读取与提炼需求
-> 飞书需求群（沟通、澄清、人工确认控制面）
-> URL/chat/route binding
-> 本地 Codex control -> stage -> tool -> gate（执行面）
-> OpenSpec / repo / tests / pipeline evidence（事实源）
-> 状态与证据回刷飞书群
```

## 落地判定

以下内容全部成立，才算“功能已实现”：

1. 本地 Multi-Agent 运行时源被实际检查，而不是按印象设计。
2. 新能力有正式 Agent 定义，例如 `~/.codex/agents/<layer>/<agent>.toml`。
3. Agent 已注册进运行时真源 `~/.codex/config.toml`。
4. 有可重复执行的确定性脚本或稳定底层 Skill/CLI。
5. 路由器、编排器、tool matrix、registry、workflow、contract 同步更新。
6. 有最小可运行测试和 dry-run；运行时配置通过 doctor/parse 验证。
7. 同一规范化需求只创建/复用一个群，并持久化 `chat_id -> role/workspace/prompt` 绑定。
8. 建群不会自动修改代码、建分支、提交、推送或触发流水线。

只有 Skill/Markdown/流程图，没有注册 Agent 和执行入口，不算实现。

## 典型绑定字段

```json
{
  "demand_key": "stable key",
  "demand_id": "p35_xxxxx",
  "demand_url": "https://...",
  "chat_id": "oc_xxx",
  "region": "cn|intl",
  "module": "module",
  "role": "iterative_feature_development",
  "primary_workspace": "/absolute/path",
  "prompt_file": "/absolute/path/to/prompt"
}
```

## 关键边界

- 飞书群是控制面，不是代码状态真源。
- 本地 Multi-Agent 是执行面，不替代人工确认。
- OpenSpec、代码 diff、测试证据和流水线结果是长期事实源。
- `gate_design_confirmed` 前不改代码。
- `gate_test_passed` 前不 commit/push/pipeline。
- 建群是外部写动作：默认 dry-run；在用户明确要求建立需求群时执行。
- 群内默认通过 `@笨笨` 触发 Hermes，除非当前 Feishu gateway 配置明确允许免 @。

## 验证清单

- [ ] Agent TOML 可解析
- [ ] `config.toml` 中存在注册项
- [ ] Codex runtime 加载无 Agent 定义告警
- [ ] 确定性脚本单元测试通过
- [ ] 飞书建群命令 dry-run 通过
- [ ] dry-run 不创建状态文件或外部资源
- [ ] 路由可解析 `region/module/role/workspace/prompt`
- [ ] 同 URL 可复用已有绑定
- [ ] launcher 使用当前可用 Codex runtime，而非硬编码陈旧安装路径
- [ ] 首个真实需求执行后回读群信息和首条上下文消息

## 常见误区

1. **只更新 Hermes Skill**：这只是编排知识，不代表本地 Codex Agent 已注册。
2. **把飞书群当执行器**：群只承载沟通和确认，代码工作仍由本地执行面完成。
3. **建群时顺便启动开发**：会绕过路由和设计门禁，应拆成两个阶段。
4. **每次收到链接都新建群**：必须先查持久化绑定，避免重复协作空间。
5. **硬编码某个 Codex 安装路径**：launcher 应优先使用当前验证可执行的 runtime，并保留可配置覆盖。