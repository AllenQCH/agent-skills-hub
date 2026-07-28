---
name: dingtalk-webhook-send
description: Use when 使用钉钉自定义群机器人 webhook + 加签发送群消息。适用于 CLI 个人数据权限不可用时，快速向钉钉群发送测试或通知消息. Do not use for non-Lark/Feishu/DingTalk/OpenClaw-import workflows or tasks covered by a narrower platform skill.
---

# 钉钉群机器人 Webhook 发送

当用户提供钉钉自定义机器人 webhook 和可选的加签 secret，需要向钉钉群发送文本/Markdown 消息时使用。

## 适用场景
- 组织未开启 CLI 数据访问权限，无法走 dws / 个人身份链路
- 用户只需要向钉钉群发消息
- 群里可能只有用户自己一个人，用于自测
- 当前用户环境已实际验证：CLI 路线会被组织权限页拦截，Webhook 机器人路线可用

## 不要做的事
- 不要把 webhook token 或 secret 写进长期记忆
- 不要把 secret 回显给用户，除非用户刚刚主动提供并要求核对
- 不要假设未开启加签；先实际发送或确认安全设置

## 推荐做法
1. 优先用用户提供的 webhook URL 直接尝试发送一次
2. 如果返回 `errcode=310000` 或提示签名不匹配，再向用户索要 `SEC...` secret
3. 用 `timestamp + "\n" + secret` 计算 HMAC-SHA256，再做 base64 和 URL 编码
4. 拼接 `timestamp` 和 `sign` 到 webhook URL 后发送 JSON
5. 以钉钉返回的 `errcode:0` 作为成功标准

## 文本消息 payload
```json
{"msgtype":"text","text":{"content":"我是笨笨"}}
```

## Python 发送模板
见 `scripts/send_dingtalk_webhook.py`。

## Ctool 代码 CR 机器人配置

当用户要把 Ctool Chrome 扩展的“代码CR钉钉机器人”配置到群里时，参考 `references/ctool-cr-robot-config.md`：Ctool 需要填写 webhook URL 中的 `access_token` 值和 `SEC...` 加签密钥，而不是完整 webhook URL。优先走 Ctool 设置 UI；不要把 token/secret 写入长期记忆或在回复中回显。

## 验证
成功时返回：
```json
{"errcode":0,"errmsg":"ok"}
```

## 常见错误
- `310000`：签名不匹配，通常是缺少 secret、时间戳/签名错误、URL 未带 `timestamp`/`sign`
- 安全策略拒绝：检查关键词、IP 白名单、加签设置
- webhook 失效：让用户重新生成机器人 webhook
