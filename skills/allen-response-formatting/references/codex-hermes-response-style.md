# Codex 与 Hermes Agent 返回格式研究（GitHub main）

## 结论

两者没有共同的强制 Markdown 模板，但存在稳定共识：结果优先、按复杂度组织、保持简洁、报告真实验证、显式格式要求优先。

- **Codex** 有明确的 final-answer house style，适合作为版式和篇幅底座。
- **Hermes Agent** 更重视执行闭环、验证、平台适配和用户级覆盖，适合作为行为底座。
- Allen 的默认格式应是偏好而非死协议：复杂回答采用“结论 → 关键依据 → 建议”，简单回答直接给结果。

## Codex 可复用规则

来源：
- `openai/codex/codex-rs/core/gpt_5_2_prompt.md` 的 “Presenting your work” 与 “Final answer structure and style guidelines”。
- `openai/codex/codex-rs/models-manager/prompt.md` 的同类 final-message 规范。
- `openai/codex/sdk/typescript/README.md` 的 Structured output 章节。

核心规则：

1. 最终回答像简洁队友的工作交接，协作、自然、事实导向。
2. 简单确认或单一步骤不使用重格式；复杂结果才分段。
3. 默认尽量短，必要时为理解完整性放宽。
4. 标题只在提升扫描效率时使用；标题短、描述性强。
5. Bullet 合并相关信息，按重要性排列，避免每个细节单独成条。
6. 命令、路径、环境变量、代码标识使用反引号。
7. 文件引用尽量带起始行号，避免粘贴用户本地已有的大段文件内容。
8. Structured output 是独立模式：用户或调用方给 JSON Schema 时，严格返回机器可解析 JSON，不叠加普通 Markdown 模板。

### 建议的复杂度分级

| 复杂度 | 推荐呈现 |
|---|---|
| 极小/简单 | 2–5 句或不超过 3 个 bullet；不加标题 |
| 中等 | 1–3 个短章节；不超过约 6 个核心 bullet |
| 大型/多项 | 按工作流、模块或文件分组；每组 1–2 个重点；不粘贴大段代码 |

## Hermes Agent 可复用规则

来源：
- `NousResearch/hermes-agent/agent/prompt_builder.py`：默认身份、任务完成、工具执行、平台提示。
- `NousResearch/hermes-agent/agent/system_prompt.py`：SOUL、USER profile、Skills、项目上下文和平台提示的组装机制。
- `NousResearch/hermes-agent/agent/turn_finalizer.py`：`final_response`、异常结束解释、文件修改失败 footer、输出转换 hook。

核心规则：

1. 默认 direct、clear、targeted、efficient，不为展示过程而啰嗦。
2. 构建、执行、验证任务必须交付真实产物和真实工具结果；不能以计划、stub 或模拟输出代替完成。
3. 失败时明确 blocker，并先尝试合理替代路径。
4. 格式服从平台能力：CLI/SMS 偏纯文本，Feishu/Desktop 可使用 Markdown，窄屏消息平台谨慎使用宽表格。
5. 用户级规则通过 USER profile、SOUL、Skills 和项目上下文覆盖通用默认。
6. Runtime 的 `final_response` 和内部结果字典属于传输/状态协议，不等于面向用户的固定版式。

## Allen 推荐混合规范

```text
默认：先给结论，再给关键依据；存在真实后续动作时再给建议。

简单问题：直接回答，不强制标题。
复杂回答：结论 → 关键依据 → 建议/下一步。
排查回答：当前判断 → 已确认事实 → 根因/可能原因 → 下一步。
执行回答：结果 → 实际验证 → 剩余 blocker/下一步。
三项以上同构信息：优先表格，但移动端或单元格文本较长时改用 bullet。
用户指定 JSON、代码、SQL、curl、日志或其他 schema：完全服从指定格式。
没有实质下一步：不强行生成“建议”章节。
```
