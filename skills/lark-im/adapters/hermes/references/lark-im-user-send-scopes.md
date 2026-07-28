# 用户身份直发消息（raw API）scope 备忘

适用场景：
- 需要以 `--as user` 直接给单聊/群聊发文本消息
- `lark-cli im +messages-send` 不适用，因为该 shortcut 是 bot-only
- 需要改用 raw API：`lark-cli api POST /open-apis/im/v1/messages ... --as user`

## 官方要求（本次会话已核对官方文档）

飞书“发送消息”接口支持 `tenant_access_token` 或 `user_access_token`。

但当使用 **用户身份** 发消息时，需要同时具备两个 scope：
- `im:message`
- `im:message.send_as_user`

仅有其中一个都不够。

## 先检查再发送

先做 scope 检查：

```bash
lark-cli auth check --scope "im:message"
lark-cli auth check --scope "im:message.send_as_user"
```

如果任一缺失，不要继续排查命令格式、chat_id、content JSON；先补授权。

## 补授权

分别单独授权更稳妥：

```bash
lark-cli auth login --scope "im:message"
lark-cli auth login --scope "im:message.send_as_user"
```

说明：
- 分别单独发起授权，便于确认是哪一个缺失
- 若同时传多个 scope 失败，退回逐个授权
- 授权完成后重新运行 `auth check`

## raw API 发送示意

```bash
lark-cli api POST /open-apis/im/v1/messages \
  --as user \
  --params '{"receive_id_type":"chat_id"}' \
  --data '{
    "receive_id":"oc_xxx",
    "msg_type":"text",
    "content":"{\"text\":\"你好\"}"
  }'
```

## 排查顺序

1. 先确认目标 chat_id 正确
2. 再确认 `im:message` 已授权
3. 再确认 `im:message.send_as_user` 已授权
4. 再尝试 raw API 发送
5. 发送后必须回查消息历史确认是否真的发出

## 常见误区

- 误以为 user token 有效就一定能 user-send：不对，发消息还取决于额外 scope
- 误把 bot-only shortcut 当成 user-send 方案：不对，`+messages-send` 主要是 bot 路径
- 未做 `auth check` 就先怀疑 content JSON / receive_id：排查顺序反了
