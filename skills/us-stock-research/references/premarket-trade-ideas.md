# 美股盘前交易想法工作流

用于北京时间晚间、美股开盘前生成以“标的 / 逻辑 / 风险 / 关注价位”为核心的战术报告。

## 1. 时间与数据口径

- 先确认北京时间与美国东部时间，明确当前处于盘前还是常规交易时段。
- Nasdaq `quote/<TICKER>/info` 的 `primaryData` 可提供：
  - `lastSalePrice`
  - `netChange`
  - `percentageChange`
  - `lastTradeTimestamp`
  - `marketStatus`
- ETF 使用 `assetclass=etf`；股票使用 `assetclass=stocks`。
- 报告中标明行情时间，并说明盘前价格可能在开盘后快速变化。

## 2. Nasdaq 历史行情日期格式

历史接口示例：

```text
https://api.nasdaq.com/api/quote/NVDA/historical?assetclass=stocks&fromdate=2026-06-15&todate=2026-07-14&limit=30
```

实测应优先使用 ISO 日期 `YYYY-MM-DD`。`MM/DD/YYYY`、URL 编码斜杠或 `MM-DD-YYYY` 可能返回 `rCode: 400` / `Bad or No parameter fromdate`。

从 `data.tradesTable.rows` 提取 `date / close / high / low / volume`，用最近约20个交易日确定：

- 近期密集成交区与反复测试区；
- 最近摆动高点/低点；
- 整数关口；
- 盘前跳空后最近可参考的支撑和阻力。

不要把机械计算出的单点写成精确预测，优先给区间。

## 3. 新闻与宏观交叉验证

当 Yahoo 新闻稀疏或限流时，可用 Google News RSS 快速发现候选催化：

```text
https://news.google.com/rss/search?q=<URL_ENCODED_QUERY>&hl=en-US&gl=US&ceid=US:en
```

推荐并行查询：

- `US stock market premarket <date>`
- `US CPI <date>` / `Treasury yields <date>` / `oil prices <date>`
- `<TICKER> <date>`
- `<company> earnings / guidance / product / regulation <date>`

RSS 标题只用于发现线索。优先采用 Reuters、AP、CNBC、公司 IR、监管机构等来源；低质量转载或预测文只可作为待验证线索，不能作为核心逻辑。

## 4. 候选筛选

优先选择 3–5 个想法，并允许使用不同方向：

- `看多`：宏观、主题、价格结构三者至少两项同向；
- `观察`：逻辑成立，但价格尚未确认或盘前缺口过大；
- `谨慎`：催化存在，但阻力、估值、拥挤度或事件风险突出；
- `回避`：相对弱势且缺少可验证催化。

不要为了凑数量硬推个股。若盘前缺乏可靠催化，明确写“今晚以观察为主”。

## 5. 盘前跳空处理

- 指数上涨不等于个股普涨，要比较 SPY、QQQ、SOXX 与候选个股的相对强弱。
- 盘前涨幅明显高于板块时，避免直接给“追涨”建议；改写为突破确认或回踩承接条件。
- 对跳空标的至少给两套触发条件之一：
  1. 开盘后守住盘前关键区间；
  2. 放量突破最近摆动高点并完成回踩。
- 如果公司新闻无法确认，直说“未见单一确认催化”，不要用普通行业叙事硬解释当日涨跌。

## 6. 推荐字段

每个标的保持固定字段：

- 标的（代码）
- 方向
- 核心逻辑（1–3条）
- 触发因素
- 风险点（1–2条）
- 关注价位（支撑、阻力、确认条件）

结尾必须注明：信息仅供参考，不构成投资建议或收益保证。