# 钉钉会议室可用性扫描经验

## 场景
用户要查某一天某几个会议室（例如深圳前海新总部 29F「绿妍 / 29F」「椰椰 / 29F」）的空闲时间，而不是只查某一个固定半小时/一小时。

## 推荐做法
1. 先用 `dws calendar room list-groups --format json` 定位城市/办公区分组，例如深圳前海新总部为 `groupId=95`（以实时返回为准，不要硬编码）。
2. 不要直接用一个很长时间窗（如 `09:00-20:00`）判断全天空闲；长窗口可能只返回 `labels: null` 等不可用结构，无法判断具体会议室。
3. 以 30 分钟为粒度循环查询：
   ```bash
   dws calendar room search \
     --start "2026-07-24T09:00:00+08:00" \
     --end "2026-07-24T09:30:00+08:00" \
     --group-id 95 \
     --available true \
     --format json
   ```
4. 每个 slot 的返回里按 `roomName` 过滤目标会议室；目标会议室出现在 `--available true` 结果中即该 slot 可用。
5. 将连续可用的 30 分钟 slot 合并成更易读时间段，例如 `09:00-10:30`。

## 注意
- `--available` 在 dws 中按布尔参数传值更稳妥：`--available true`，不要写成裸 flag。
- 时间必须用 ISO-8601，并带时区：`YYYY-MM-DDTHH:MM:SS+08:00`。
- 如果查询会议室列表超过 100 条，先 `room list-groups`，再按 `--group-id` 查。
- 查询完成后报告：查询日期、时间范围、分组、目标会议室、可用时间段、是否有错误。