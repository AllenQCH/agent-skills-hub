# 指定发送者聊天记录定时同步到本地文件

适用场景：Allen 要把某个钉钉群里某个同事本人发出的消息，每天定时同步到本机 Downloads / Obsidian / 其他本地目录。

## 推荐口径

- 先 `contact user search` 定位目标人的 `userId` / `openDingTalkId`。
- 先 `chat search` exact 搜群名，拿到 `openConversationId`。
- 用 `chat message list-by-sender --sender-user-id <userId>` 抓发送者消息，再按 `openConversationId` 过滤目标群。
- 严格只保留目标人本人发出的消息；`quotedMessage` 只能作为上下文保存，不能算作目标人观点。
- 本地输出建议同时保留：
  - 当日 Markdown：方便阅读；
  - 累计 JSONL：方便去重和后续再加工。

## 稳定实现方式

如果是每天自动同步，优先做成 Hermes `cronjob` 的 `no_agent=true` 脚本型任务，而不是每天让 LLM 重走抓取和写文件逻辑。

脚本要做：
1. 计算当天时间窗口：`YYYY-MM-DD 00:00:00` 到当前执行时间。
2. 调用：
   ```bash
   dws chat message list-by-sender \
     --sender-user-id <userId> \
     --start '<YYYY-MM-DD 00:00:00>' \
     --end '<YYYY-MM-DD HH:mm:ss>' \
     --limit 100 \
     --format json
   ```
3. 如返回 `hasMore=true`，继续带 `--cursor <nextCursor>` 分页。
4. 过滤 `openConversationId == <targetGroup>`。
5. 用 `openMessageId` 对 JSONL 去重。
6. 当日 Markdown 可重生成，按 `createTime` 升序展示。
7. 写完后验证文件存在且非空。

## Markdown 建议字段

- 日期、群名、目标人、同步时间；
- 每条消息：`createTime`、`openMessageId`、正文；
- 如果有引用消息：引用发送人、引用时间、引用内容。

## Pitfalls

- 不要用 `chat message list-direct`，那只适合单聊；指定群里某人的发言应使用 `list-by-sender` 后过滤群 ID。
- 不要把别人 @ 目标人、回复目标人的消息当成目标人发言。
- 如果只是本地归档，不要把 cron 结果投递到群里；`deliver=local` 即可。
- 脚本型任务比 LLM 型任务更稳定、更省 token，也更适合固定同步。