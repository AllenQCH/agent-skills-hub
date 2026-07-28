# 钉钉聊天记录定时同步到本地文件

适用场景：用户要求把某个钉钉群中某位成员的发言，按固定时间同步到本机 Downloads 或其他目录。

## 推荐形态

优先使用 Hermes cron 的 `no_agent=true` + 本地脚本，而不是每天让 LLM agent 解释执行。理由：
- 行为稳定、成本低；
- 文件写入和去重逻辑可验证；
- cron stdout 可作为本地运行结果，失败时 stderr 明确暴露。

## 建议流程

1. 先定位目标人：`dws contact user search --keyword <姓名> --format json`，记录 `userId`、`openDingTalkId`、`nick`。
2. 先定位目标群：`dws chat search --query <群名> --format json`，记录 `openConversationId`。
3. 先做一次小样本验证：
   `dws chat message list-by-sender --sender-user-id <userId> --limit 5 --format json`
   并确认返回消息中存在目标群的 `openConversationId`。
4. 编写本地同步脚本，脚本中固定目标人和目标群 ID：
   - 用 `dws chat message list-by-sender --sender-user-id ... --start ... --end ... --limit 100 --format json` 拉取；
   - 按 `openConversationId` 过滤目标群；
   - 再用 `senderOpenDingTalkId` 或 sender nick 做显式 guard；
   - 以 `openMessageId` 去重；
   - 写入日 Markdown 和累计 JSONL；
   - 写完后验证文件存在且非空。
5. 先手动运行脚本验证，再创建/更新 cron：
   - `script`: 脚本名，放在 `~/.hermes/scripts/` 下；
   - `no_agent=true`；
   - `deliver=local`，除非用户明确要求发送回聊天；
   - `schedule='0 19 * * *'` 这类明确 cron 表达式。

## 输出文件建议

目录形态：
`~/Downloads/dingtalk-chat-history/<群名>-<姓名>/`

文件：
- `YYYY-MM-DD.md`：当天 Markdown，可重生成，按 `createTime` 升序；
- `messages.jsonl`：累计原始结构化记录，按 `openMessageId` 去重追加；
- `last_sync.json`：最后一次同步状态，包括同步时间、抓取条数、新增条数、文件路径。

Markdown 每条消息建议包含：
- 时间；
- `openMessageId`；
- 正文；
- 如有 `quotedMessage`，作为“引用上下文”保存发送人、时间、内容。

## Pitfalls

- 不要把“别人 @ 某人 / 回复某人”的消息当作目标人发言。`quotedMessage` 只能作为上下文。
- `list-by-sender` 可能返回多个会话；必须用目标群 `openConversationId` 再过滤。
- 不要只创建 cron 就结束；必须先手动跑一次脚本并验证 Downloads 中文件真实存在。
- 需要长期稳定的同步任务时，不要用 LLM prompt 每天临场写文件；应将确定性逻辑固化为脚本并设为 `no_agent`。
