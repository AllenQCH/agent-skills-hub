# 钉钉消息雷达（私聊 + @我）

适用场景：用户说“钉钉消息太多，看不过来”，希望定时整理真正需要他处理的消息，而不是查看全部未读。

## 目标范围
只抓两类：
1. 私聊我的消息
2. 群里 @ 我的消息

不要默认扩展到“所有未读群消息”。如果用户只关心这两类，就保持最小可用范围。

## 推荐命令组合
- `dws chat message list-mentions --limit 20 --format json`
- `dws chat message list-unread-conversations --count 50 --format json`
- `dws chat message list-direct --user <userId> --time <start> --limit 100 --forward true --format json`
- `dws contact user search --keyword <姓名> --format json`
- `dws chat search --query <群名> --format json`（当需要把结果投递到工作群）
- `dws chat bot search --format json`（当需要找可发群消息的机器人）

## 输出格式
优先输出正文/摘要，不要只给条数：

- 私聊：`姓名 + 内容`
- 群聊 @ 我：`群名 + 发消息的人 + 内容`
- 内容很长时：先给摘要，再保留关键原文片段

如果消息是提醒/告警/工时类内容，要提炼“与用户直接相关的事项”。

## 自动化工作流（Hermes cron + 本地脚本）
1. 先确认 `dws auth status --format json` 已登录
2. 本地脚本轮询 mentions + unread conversations
3. 对未读私聊，继续拉 `list-direct` 拿正文
4. 维护一个本地状态文件，记录已处理的 mention ID / 私聊时间戳，避免重复推送
5. 脚本在“没有新消息”时保持静默
6. 用 Hermes cron 定时运行；若脚本放在 `~/.hermes/scripts/`，cron 配置里必须使用**相对文件名**，不要写绝对路径

### 已验证的 cron 坑位
- `script` 字段必须写成例如 `dingtalk_message_radar.py`
- 不能写 `/Users/.../.hermes/scripts/dingtalk_message_radar.py`
- 首次联调可先 `deliver=origin` 验证链路，再改投递目标

## 推荐频率
如果用户没有强实时诉求，默认建议 `every 30m`，比 5 分钟更低打扰。

## 投递到工作群时的思路
1. 先从用户拿到准确群名（截图指认不等于已经识别成功）
2. 用 `dws chat search --query <群名>` 定位群
3. 确认可用的发送方式：
   - 机器人：`dws chat bot search` + `dws chat message send-by-bot`
   - 已有 webhook：`dws chat message send-by-webhook`
4. 再把自动摘要输出改为发进目标群

## 常见误区
- 只返回“有几条未读/几条@我”——对用户价值很低
- 把所有未读群会话都塞进摘要——噪音太大
- 没做去重，导致每次 cron 都重复发同一批消息
- 还没拿到群名或群 ID 就假设能直接发到“这个群里”
