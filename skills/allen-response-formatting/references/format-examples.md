# Allen Response Formatting — Examples

## 1. Short factual answer

```text
## 结论
可以，而且现在就能做。

## 关键依据
- 我已经核实当前配置生效。
- 当前只有 default profile 在运行。
- 这条规则已写入 profile 级行为约束。

## 下一步
你现在直接在群里 @我测一条就行。
```

## 2. Research / exploration answer

```text
## 结论
这个仓库值得参考，但更重要的是它背后的“收束式信息组织”方法。

## 关键依据
- README 强调把 thinking、tool、final answer 收束到同一张卡片。
- event protocol 只有少数明确状态：思考中 / 等待选择 / 已完成。
- render 层把工具过程压缩成摘要，而不是刷屏日志。

## 对你的意义
这正好对应你现在最不满意的问题：回答太散、太乱、太像过程倾倒。

## 下一步
我建议以后默认按 v2 格式回答；如果你愿意，再细分一个群聊短版模板。
```

## 3. Debug / troubleshooting answer

```text
## 当前判断
问题大概率在网关运行态配置没有重新加载，不在静态配置文件本身。

## 已确认事实
- config.yaml 已启用 feishu。
- .env 中存在必需 FEISHU_* 变量。
- gateway 进程正在运行。

## 根因
运行中的 gateway 可能没有吃到最新环境变量。

## 处理建议
- 先重启 gateway
- 再看日志是否还有 Unauthorized user
- 然后发一条新消息复测
```

## 4. Group chat / Feishu answer

```text
## 结论
可以，已经同步到当前 agent 默认行为里了。

## 关键依据
- 当前只跑着一个 default profile。
- Feishu gateway 已启用。
- 规则已写入 profile 级技能/约束。

## 下一步
你现在在群里 @我测一条就行。
```

## 5. Anti-patterns to avoid

Do not do this:
- long background before the answer
- dump tool exploration in chronological order
- finish without a recommendation
- mix conclusion, evidence, and caveats in one dense paragraph
