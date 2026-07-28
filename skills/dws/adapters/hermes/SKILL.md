---
name: dws
description: Use when 用户请求匹配此工作流：管理钉钉产品能力(AI表格/日历/通讯录/群聊与机器人/待办/审批/考勤/日志/DING消息/工作台/开放平台文档等)。当用户需要操作表格数据、管理日程会议、查询通讯录、管理群聊、机器人发消息、创建待办、提交审批、查看考勤、提交日报周报（钉钉日志模版）时使用. Do not use for non-Lark/Feishu/DingTalk/OpenClaw-import workflows or tasks covered by a narrower platform skill.
---

# 钉钉全产品 Skill

通过 `dws` 命令管理钉钉产品能力。

## 严格禁止 (NEVER DO)
- 不要使用 dws 命令以外的方式操作（禁止 curl、HTTP API、浏览器）
- 不要编造 UUID、ID 等标识符，必须从命令返回中提取
- 不要猜测字段名/参数值，操作前必须先查询确认

## 严格要求 (MUST DO)
- 所有命令必须加 `--format json` 以获取可解析输出
- 危险操作必须先向用户确认，用户同意后才加 `--yes` 执行
- 单次批量操作不超过 30 条记录
- 所有命令必须**严格遵循**对应产品参考文档里面规定的参数格式（如：如果有参数值，则参数和参数值之间至少用一个空格隔开）


## 产品总览

| 产品                | 用途                                                   | 参考文件                                                           |
|-------------------|------------------------------------------------------|----------------------------------------------------------------|
| `aitable`         | AI表格：表格/数据表/字段/记录增删改查/模板搜索                           | [aitable.md](./references/products/aitable.md)                 |
| `approval`        | 审批：审批表单/发起实例/审批/撤销                                   | [simple.md](./references/products/simple.md)                   |
| `attendance`      | 考勤：打卡记录/排班查询                                         | [attendance.md](./references/products/attendance.md)           |
| `calendar`        | 日历：日程/参与者/会议室/闲忙查询                                   | [calendar.md](./references/products/calendar.md)               |
| `chat`            | 群聊与机器人：搜索群/建群/群成员管理/改群名/机器人群发/单聊/撤回/Webhook/机器人搜索     | [chat.md](./references/products/chat.md)                       |
| `contact`         | 通讯录：用户查询(当前用户/搜索/详情)/部门查询(搜索/子部门/成员列表)               | [contact.md](./references/products/contact.md)                 |
| `devdoc`          | 开放平台文档：搜索开发文档                                        | [simple.md](./references/products/simple.md)                   |
| `ding`            | DING消息：发送/撤回（应用内/短信/电话）                              | [ding.md](./references/products/ding.md)                       |
| `report`          | 日志：按模版创建/收件箱/已发送/模版查看/详情/已读统计                         | [report.md](./references/products/report.md)                   |
| `todo`            | 待办：创建(含优先级/截止时间)/查询/修改/标记完成/删除                       | [todo.md](./references/products/todo.md)                       |
| `workbench`       | 工作台：应用管理                                             | [workbench.md](./references/products/workbench.md)             |

## 意图判断决策树

用户提到"表格/多维表/AI表格/记录/数据" → `aitable`
用户提到"审批/请假/报销/出差/加班" → `oa`
用户提到"考勤/打卡/排班" → `attendance`
用户提到"日程/日历/会议室/约会" → `calendar`
用户提到"群聊/建群/群成员/群管理/机器人发消息/Webhook/机器人群发/机器人单聊/通知" → `chat`
用户提到"通讯录/同事/部门/组织架构" → `contact`
用户提到"开发/API/调用错误 文档" → `devdoc`
用户提到"DING/紧急消息/电话提醒" → `ding`
用户提到"日志/日报/周报/日志统计/写日报/提交周报/发日志/填日志" → `report`

周报链路补充：如果 Allen 明确说“用 dws 填周报”，且要求先从群里拿陆建波发的最新周报链接，再从蓝鲸取本周/下周内容：
1. **先找链接，不要先查 report template**：用 `dws chat` / Hermes DingTalk MCP 消息工具在钉钉群消息中定位陆建波最新的周报链接，不要猜链接或群；
2. 如果 Allen 已贴出近期 `dws auth status --format json` 为有效，但本会话 shell 报 `not_authenticated`，先按“执行上下文不一致”处理：确认正在调用同一个 dws/同一 HOME，并优先尝试 Hermes 当前暴露的 DingTalk MCP 工具读取消息；不要直接让用户重新登录或把任务判死；
3. 再切到 BlueKing/OpenCLI 技能收集本周/下周工作内容；
4. 回到 `dws report`、`dws sheet` 或对应文档写入路径填写并验证。若陆建波发的是 `alidocs.dingtalk.com/spreadsheetv2/...` 表格链接，优先使用 `dws sheet`：用完整 URL `sheet list` 获取 sheetId，`sheet find --match-entire-cell true` 定位戚呈辉行，再 `range update` 写入本周/下周/待开发列并回读验证。不要把短 `dentryKey` 当 nodeId 传给 sheet API。DWS sheet 的布尔参数必须显式传 `true`/`false`，不要写成裸 flag（例如不要用 `--match-entire-cell --format json`）。详见 `blueking-workhour-opencli` 的 `references/weekly-report-dws-blueking.md` 与 `references/allen-weekly-report-cli.md`。
用户提到"待办/TODO/任务提醒" → `todo`
用户提到"工作台/应用管理" → `workbench`

关键区分: aitable(数据表格) vs todo(待办任务)
关键区分: report(钉钉日志/日报周报) vs todo(待办任务)
关键区分: chat send-by-bot(机器人身份发消息) vs send-by-webhook(自定义机器人Webhook告警)

## Chat 消息查询输出规范（重要）

当用户查询“谁给我发消息 / 谁 @ 我 / 未读消息 / 最近消息 / 聊天记录总结”时，不要只返回会话条数、未读数或会话名。必须优先给出**消息内容本身**，并按场景整理：

## Chat 群定位与成员排查工作流（重要）

当用户要找“某个群的成员 / 某个会议群是不是这个 / 先把群找出来再分析”时，优先按下面顺序执行：

1. 先用 `chat search` 搜 **exact 群名**。
2. 如果 exact 未命中，不要停在“没搜到”；立即把群名拆成 2~4 个更短关键词继续搜（例如：业务词、平台词、会议词、评审词分开搜）。
3. 如果仍未命中，要把 **最接近候选群** 列出来，并保留至少这些字段：`title`、`openConversationId`、`memberCount`、`gmtCreateAt`。
4. 若用户当前目标是“先找成员”，不要先陷入消息导出；应直接对 1~3 个最接近候选群并行执行 `chat group members list`，把成员名单先拉出来给用户确认。
5. 输出时明确区分：
   - exact 命中的目标群
   - 语义接近但不是同名的候选群
   - 会议群 vs 业务群/联调群
6. 若 exact 群名不存在，但存在高度相似候选（如“会议群”和“业务群”各一个），必须把两边成员都列出，再让用户指定后续分析对象。

### 这一类任务的默认输出骨架
- `搜索结论`：exact 是否命中
- `候选群`：按相似度列 1~3 个，附 `openConversationId` / 成员数 / 创建时间
- `成员列表`：每个候选群单独成节，先群主，再普通成员
- `下一步`：请用户确认要继续分析哪个群

### Pitfall
- 不要把“没搜到 exact 群”直接当作任务失败；很多真实群名会存在“虚拟平台 / 虚拟商品平台 / 联调 / 会议群 / 测试方案评审”这类命名偏差。
- 当用户眼下目标是“先找群成员”时，优先级应是 `search -> candidate groups -> members list`，而不是先做聊天记录导出。

- 私聊：`姓名 + 消息内容`
- 群里 @ 我：`群名 + 发消息的人 + 消息内容`
- 如果内容很长：先给 1~3 句摘要，再保留关键原文片段
- 如果同时有私聊和 @ 我：分成两个小节分别列出

### 最低可用标准
- 不能只说“有 1 条未读私聊 / 有 3 条 @ 你”
- 至少要包含：谁发的、什么群（如适用）、说了什么
- 如果消息本质是机器人/系统提醒，要提炼出**与用户直接相关**的事项，而不是整段原样堆砌

### 推荐工作流
1. 先查未读会话 / @我 列表，定位目标会话
2. 对私聊会话继续拉取最近消息正文
3. 对 @我 的群消息提取最新命中消息正文
4. 最终按“私聊我的 / 群里 @ 我的”输出

### 指定群 + 指定人的聊天整理 / 文件更新工作流
当用户要求“把某群里某人的聊天内容整理出来 / 更新到刚才文档 / 别人发他的不用整理”时：

> 定时同步某个群里某个发送者的消息到本地文件时，优先参考 [references/chat-sender-scheduled-sync.md](./references/chat-sender-scheduled-sync.md)：用 `list-by-sender` 抓目标发送者，再按 `openConversationId` 过滤目标群，并做 Markdown + JSONL 双输出去重。
1. 先 `contact user search` 定位姓名对应的 userId/openDingTalkId，再 `chat search` exact 搜群名，拿到 openConversationId；不要猜人或群。
2. 优先用 `chat message list-by-sender --sender-user-id <userId>` 拉该发送者消息，再按 openConversationId 过滤目标群；必要时再用 `chat message list --group <group>` 校验最新消息和 quotedMessage 上下文。
3. 严格区分两类内容：
   - “某人本人发出的内容”：sender 必须是该 userId/openDingTalkId；可保留必要的 quotedMessage 作为上下文，但不要把别人发给他的消息当作他的观点。
   - “别人 @ 某人 / 回复某人”：只有用户明确要求才单独整理；如果用户说“不用整理别人发他的”，必须移除这类章节。
4. 用户要求“把他的话放进文档”时，新增或更新一个“原话汇总（按时间倒序）”章节：按时间列出该人原话代码块，再保留一个摘要表和提炼重点。
5. 写入 Downloads 等本地文件后必须回读验证：确认文件存在、行数/大小、关键新原话和整理口径都在文件中。

### 指定群 + 指定人的聊天记录定时同步到本地
当用户要求“每天/定时把某群某人的聊天历史同步到 Downloads/本地文件”时，不要只创建一个 LLM prompt 型 cron 就结束。推荐流程：
1. 先按上面的流程定位并验证目标人 `userId/openDingTalkId/nick`、目标群 `openConversationId`，并用 `chat message list-by-sender` 小样本确认有消息。
2. 将确定性同步逻辑写成 `~/.hermes/scripts/` 下的脚本：按时间窗口拉取 sender 消息、按目标群过滤、以 `openMessageId` 去重、写入日 Markdown + 累计 JSONL + `last_sync.json`。
3. 先手动运行脚本并验证文件真实存在、行数/大小合理，再用 Hermes cron 创建或更新为 `no_agent=true` + `script=<脚本名>` + `deliver=local`。
4. 口径必须写清：只同步目标人本人发言；`quotedMessage` 只保存为引用上下文。
5. 详细模板和坑点见 `references/dingtalk-chat-history-sync.md`。

### 长消息压缩规则
- 工时/告警/报表类群消息：提炼成“提醒类型 + 日期/环境 + 与用户相关的任务/错误”
- 多条连续追问：合并总结成“对方在催什么、需要你给什么信息”
- 若消息已经很短，直接给原文，不要过度总结

> 更多易混淆场景见 [intent-guide.md](./references/intent-guide.md)

## 危险操作确认

以下操作为不可逆或高影响操作，执行前**必须先向用户展示操作摘要并获得明确同意**，同意后才加 `--yes` 执行。

| 产品 | 命令 | 说明 |
|------|------|------|
| `aitable` | `base delete` | 删除整个 AI 表格，含全部数据表和记录 |
| `aitable` | `record delete` | 删除记录（支持批量） |
| `calendar` | `event delete` | 删除日程，所有参与者同步取消 |
| `calendar` | `participant delete` | 移除日程参与者 |
| `calendar` | `room delete` | 取消会议室预定 |
| `chat` | `group members remove` | 移除群成员 |
| `todo` | `task delete` | 删除待办 |

### 确认流程
```
Step 1 → 展示操作摘要（操作类型 + 目标对象 + 影响范围）
Step 2 → 用户明确回复确认（如 "确认" / "好的"）
Step 3 → 加 --yes 执行命令
```

## 核心流程
作为一个智能助手，你的首要任务是**理解用户的真实、完整的意图**，而不是简单地执行命令。在选择 `dws` 的产品命令前，必须严格遵循以下四步流程：

1. 意图分类：首先，判断用户指令的核心 动词/动作 属于哪一类。这比关注名词更重要。
2. 歧义处理与信息追问：如果用户指令模糊或包含多个产品的关键字，严禁猜测。必须主动向用户追问以澄清意图。这是你作为智能助手而非命令执行器的核心价值。
3. 精准产品映射：在完成前两步，意图已经清晰后，参考产品总览和意图判断决策树 来选择产品。
4. 充分阅读产品参考文件，通过编写代码或直接调用指令实现用户意图。

## 错误处理
1. 遇到错误，加 `--verbose` 重试一次
2. 若 stderr 出现 `RECOVERY_EVENT_ID=<event_id>`，优先按 [recovery-guide.md](./references/recovery-guide.md) 执行 recovery 闭环
3. 仍然失败，报告完整错误信息给用户，禁止自行尝试替代方案
4. 认证失败时，参考 [global-reference.md](./references/global-reference.md) 中的认证章节处理
5. 各产品高频错误及排查流程见 [error-codes.md](./references/error-codes.md)


## 详细参考 (按需读取)

- [references/products/](./references/products/) — 各产品命令详细参考
- [references/calendar-room-availability.md](./references/calendar-room-availability.md) — 按 30 分钟粒度扫描并合并会议室全天空闲时间段的实践
- [references/intent-guide.md](./references/intent-guide.md) — 意图路由指南（易混淆场景对照）
- [references/global-reference.md](./references/global-reference.md) — 全局标志、认证、输出格式
- [references/field-rules.md](./references/field-rules.md) — AI表格字段类型规则
- [references/error-codes.md](./references/error-codes.md) — 错误码 + 调试流程
- [references/recovery-guide.md](./references/recovery-guide.md) — recovery 闭环、`RECOVERY_EVENT_ID`、`execute/finalize` 规范
- [references/chat-message-radar.md](./references/chat-message-radar.md) — 私聊 + @我 的消息雷达、cron 自动整理、群投递思路
- [scripts/](./scripts/) — 各产品批量操作脚本（AI表格/日历/机器人消息/通讯录/考勤/日志/待办等）
