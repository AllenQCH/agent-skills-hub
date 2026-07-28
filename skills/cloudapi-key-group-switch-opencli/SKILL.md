---
name: cloudapi-key-group-switch-opencli
description: Use when 使用 opencli browser 在已登录 CloudAPI 管理页面里切换 Allen 的 API Key 分组，并在切换后查询验证。适用于用户说“切 codex-pro / 切日抛分组 / 切图片生成 / 切换 CloudAPI key 分组”. Do not use for tasks outside the named productivity app, document, spreadsheet, meeting, or workflow scope.
---

# CloudAPI Key 分组切换（opencli）

## 触发场景

当用户要求切换 CloudAPI / API Key / 中转站 / Codex 应用的分组，例如：

- “切 codex-pro”
- “切日抛分组”
- “切图片生成”
- “帮我把 allen 这个 key 切到 codex-pro”
- “帮我切换 CloudAPI 的 key 分组”

使用本 skill。

## 已知固定信息

管理页面：

```text
http://139.224.107.55:9077/keys
```

目标 Key：

| 字段 | 值 |
|---|---|
| Key 名称 | `allen` |
| Key ID | `45` |

分组映射：

| 用户说法 | group_id | 标准分组名 |
|---|---:|---|
| `codex-pro` / `codex pro` / `pro` | `2` | `codex-pro` |
| `日抛` / `日抛分组` | `14` | `日抛分组` |
| `图片` / `图片生成` / `image` | `16` | `图片生成` |

## 前提

- 本机已安装 `opencli`。
- opencli browser 里已有名为 `cloudapi` 的浏览器会话，且已经登录 CloudAPI 页面。
- 认证 token 存在浏览器页面的 `localStorage.auth_token`。

如果没有登录态，先导航登录：

```bash
opencli browser cloudapi goto 'http://139.224.107.55:9077/keys'
```

然后让用户在浏览器里完成登录，再重试。

## 查询当前分组

先查询当前 key 状态，确认 opencli 会话和登录态可用：

```bash
opencli browser cloudapi eval "
(async () => {
  const token = localStorage.getItem('auth_token');
  if (!token) return JSON.stringify({ error: 'missing auth_token; please login first' }, null, 2);

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  };

  const keys = await fetch('/api/v1/keys?page=1&page_size=50', { headers }).then(r => r.json());
  const item = (keys.items || keys.data?.items || []).find(k => k.id === 45);

  return JSON.stringify({
    key: {
      id: item?.id,
      name: item?.name,
      group_id: item?.group_id,
      group_name: item?.group_name || item?.group?.name,
      status: item?.status,
      last_used_at: item?.last_used_at,
      updated_at: item?.updated_at
    }
  }, null, 2);
})()
"
```

## 切换分组

把下面命令里的 `TARGET_GROUP_ID` 替换成目标分组 ID。

```bash
opencli browser cloudapi eval "
(async () => {
  const targetGroupId = TARGET_GROUP_ID;

  const token = localStorage.getItem('auth_token');
  if (!token) return JSON.stringify({ error: 'missing auth_token; please login first' }, null, 2);

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  };

  const res = await fetch('/api/v1/keys/45', {
    method: 'PUT',
    headers,
    body: JSON.stringify({ group_id: targetGroupId })
  });

  const text = await res.text();
  let update;
  try { update = JSON.parse(text); } catch { update = text; }

  const keys = await fetch('/api/v1/keys?page=1&page_size=50', { headers }).then(r => r.json());
  const item = (keys.items || keys.data?.items || []).find(k => k.id === 45);

  return JSON.stringify({
    update_status: res.status,
    update_message: update?.message ?? update,
    key: {
      id: item?.id,
      name: item?.name,
      group_id: item?.group_id,
      group_name: item?.group_name || item?.group?.name,
      status: item?.status,
      last_used_at: item?.last_used_at,
      updated_at: item?.updated_at
    }
  }, null, 2);
})()
"
```

常用替换：

```text
TARGET_GROUP_ID=2   # codex-pro
TARGET_GROUP_ID=14  # 日抛分组
TARGET_GROUP_ID=16  # 图片生成
```

## 一行命令模板

### 切到 codex-pro

```bash
opencli browser cloudapi eval "(async () => { const token=localStorage.getItem('auth_token'); if(!token) return JSON.stringify({error:'missing auth_token; please login first'},null,2); const headers={'Content-Type':'application/json','Authorization':'Bearer '+token}; const res=await fetch('/api/v1/keys/45',{method:'PUT',headers,body:JSON.stringify({group_id:2})}); const text=await res.text(); let update; try{update=JSON.parse(text)}catch{update=text}; const keys=await fetch('/api/v1/keys?page=1&page_size=50',{headers}).then(r=>r.json()); const item=(keys.items||keys.data?.items||[]).find(k=>k.id===45); return JSON.stringify({update_status:res.status, update_message:update?.message ?? update, key:{id:item?.id,name:item?.name,group_id:item?.group_id,group_name:item?.group_name||item?.group?.name,status:item?.status,last_used_at:item?.last_used_at,updated_at:item?.updated_at}}, null, 2); })()"
```

### 切到日抛分组

```bash
opencli browser cloudapi eval "(async () => { const token=localStorage.getItem('auth_token'); if(!token) return JSON.stringify({error:'missing auth_token; please login first'},null,2); const headers={'Content-Type':'application/json','Authorization':'Bearer '+token}; const res=await fetch('/api/v1/keys/45',{method:'PUT',headers,body:JSON.stringify({group_id:14})}); const text=await res.text(); let update; try{update=JSON.parse(text)}catch{update=text}; const keys=await fetch('/api/v1/keys?page=1&page_size=50',{headers}).then(r=>r.json()); const item=(keys.items||keys.data?.items||[]).find(k=>k.id===45); return JSON.stringify({update_status:res.status, update_message:update?.message ?? update, key:{id:item?.id,name:item?.name,group_id:item?.group_id,group_name:item?.group_name||item?.group?.name,status:item?.status,last_used_at:item?.last_used_at,updated_at:item?.updated_at}}, null, 2); })()"
```

### 切到图片生成

```bash
opencli browser cloudapi eval "(async () => { const token=localStorage.getItem('auth_token'); if(!token) return JSON.stringify({error:'missing auth_token; please login first'},null,2); const headers={'Content-Type':'application/json','Authorization':'Bearer '+token}; const res=await fetch('/api/v1/keys/45',{method:'PUT',headers,body:JSON.stringify({group_id:16})}); const text=await res.text(); let update; try{update=JSON.parse(text)}catch{update=text}; const keys=await fetch('/api/v1/keys?page=1&page_size=50',{headers}).then(r=>r.json()); const item=(keys.items||keys.data?.items||[]).find(k=>k.id===45); return JSON.stringify({update_status:res.status, update_message:update?.message ?? update, key:{id:item?.id,name:item?.name,group_id:item?.group_id,group_name:item?.group?.name||item?.group_name,status:item?.status,last_used_at:item?.last_used_at,updated_at:item?.updated_at}}, null, 2); })()"
```

## 验证标准

切换完成后，必须以后续 `GET /api/v1/keys?page=1&page_size=50` 的结果为准，找到 `id=45` 的 key，确认：

- `group_id` 等于目标分组 ID
- `group_name` 等于目标分组名
- `status` 是 `active`

## 注意事项

1. 不要把 token 输出给用户。只在浏览器页面上下文里读取并用于请求头。
2. `PUT /api/v1/keys/45` 返回里的 `data.group` 可能是旧对象，不可靠；必须以后续 GET 列表查询结果为准。
3. 如果命令返回 `missing auth_token`，说明 opencli browser 会话未登录或 localStorage 没有 token，先打开页面让用户登录。
4. 如果用户只说“切日抛”，默认目标是 `group_id=14`。
5. 如果用户只说“切 pro”，默认目标是 `group_id=2`。
