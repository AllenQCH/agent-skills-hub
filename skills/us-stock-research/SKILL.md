---
name: us-stock-research
description: 'Use when the user needs the us stock research workflow: Use Yahoo Finance MCP tools in Hermes to research US stocks, ETFs, earnings, options, news, and recent price action with a practical analyst workflow. Do not use for execution-only tasks that do not require research, monitoring, market data, or literature discovery.'
license: MIT
---

# US stock research via Yahoo Finance MCP

Use this skill when the user wants practical research on US equities and ETFs inside Hermes.

## Prerequisites

This skill assumes Hermes has the Yahoo Finance MCP server configured and loaded on startup.

Expected tool names after restart:
- `mcp_yahoo_finance_search`
- `mcp_yahoo_finance_get_ticker_info`
- `mcp_yahoo_finance_get_ticker_news`
- `mcp_yahoo_finance_get_price_history`
- `mcp_yahoo_finance_ticker_option_chain`
- `mcp_yahoo_finance_ticker_earning`
- `mcp_yahoo_finance_get_top_entities`

If the tools are missing, first verify:
1. `mcp` is installed in Hermes's Python environment
2. `~/.hermes/config.yaml` has a `yahoo_finance` entry under `mcp_servers`
3. Hermes was restarted after the config change

## Best-use patterns

### 1) Single-stock move explanation
When the user asks why a ticker moved:
1. Pull ticker basics with `get_ticker_info`
2. Pull recent news with `get_ticker_news`
3. Pull recent price history with `get_price_history`
4. Pull earnings timing with `ticker_earning` if relevant
5. Summarize the move as:
   - direct catalyst
   - supporting narrative
   - market structure / sentiment angle
   - key risk to the move

Good framing:
- `what happened`
- `why the market liked/disliked it`
- `whether this looks like one-day noise or narrative continuation`

### 2) Quick stock snapshot
For a fast read on one ticker, return:
- company / theme
- latest price context
- recent trend
- latest news drivers
- next earnings if available
- one-line risk/reward summary

### 3) AI / sector basket scan
When the user asks for names with momentum or a theme basket:
1. Use `get_top_entities` if the request is broad enough
2. Use `search` to resolve theme-related names or ETFs
3. Compare 3-8 names max to avoid noisy output
4. Prefer practical buckets:
   - chips
   - servers / infrastructure
   - networking
   - software / applications
   - ETFs

### 4) Earnings / options context
If the user wants a more tactical view:
- use `ticker_earning` for schedule / earnings context
- use `ticker_option_chain` for strikes / expiries and general positioning clues
- do not overclaim options flow if the raw tool output is thin

## Private-company / pre-IPO proxy workflow

When the user asks about a private company (for example SpaceX, OpenAI, Stripe, Etched) that has no public ticker:
1. Resolve listed status first.
   - If Yahoo Finance search returns no direct result, verify with the company website and recent reporting before assuming it is public.
   - In the first line of the answer, say explicitly: `未上市 / 无公开 ticker / 没有可做常规技术分析的公开股价`.
2. Reframe the request instead of forcing fake stock analysis.
   - If the user asked `股价分析/走势/值不值得买`, answer in this order:
     - whether it is listed
     - whether ordinary investors can buy it now
     - how the company itself looks operationally
     - which public proxy stocks or beneficiaries map to the theme
3. Split the answer into three buckets:
   - direct private-company access is unavailable to ordinary public-market investors
   - listed proxy vehicles that explicitly hold or package private-company exposure
   - publicly traded sector beneficiaries / competitors that may move on the same theme
4. For listed proxy vehicles, verify exposure from the issuer/fund website rather than relying only on third-party summaries.
   - Example pattern: fetch the issuer holdings/portfolio page and search the raw HTML/text for the private company name.
   - This is especially useful for products like private-company baskets, crossover ETFs, or mutual funds with disclosed top holdings.
5. Be explicit about the difference between:
   - actual disclosed portfolio exposure
   - theme correlation only
   - speculative “concept stock” association
6. For proxy lists, prefer a compact table with columns like:
   - ticker
   - vehicle type
   - relationship to the private company
   - latest price snapshot
   - recent return / momentum
   - main risk
7. Warn clearly that proxy vehicles can trade at sentiment-driven premiums/discounts versus underlying NAV or private marks.
8. If the core data source is rate-limited or sparse, fall back fast:
   - use an HTML search endpoint to establish listed vs private status and find the official site
   - use the official site for current company claims (team size, funding, product stage)
   - use recent reputable news to cross-check valuation/funding/order claims
   - only then pivot to public comps or beneficiaries for market-priced analysis

## Company-customer / supply-chain workflow

Use this when the user asks questions like:
- `台积电给哪些公司做服务？`
- `某家公司主要客户是谁？`
- `这家公司受益于哪些下游厂商？`

Recommended workflow:
1. If the company is public, still pull market data first (`get_ticker_info`, price history, earnings/news if available) so the answer includes both business relationships and stock trend.
2. If Yahoo Finance MCP is sparse or rate-limited, switch to fallback sources immediately:
   - Nasdaq quote/info, chart, historical, analyst ratings, earnings-surprise for ticker trend and fundamentals
   - Google News RSS for recent catalysts
3. For customer mapping, use public descriptive sources that often summarize major customers more directly than finance APIs:
   - company Wikipedia page or equivalent neutral overview page
   - company annual report / investor relations if easy to retrieve
4. Distinguish clearly between:
   - officially disclosed major customers
   - widely reported / market-consensus customers
   - ecosystem partners that are not necessarily direct revenue customers
5. For foundries / manufacturers like TSMC, explain the service by customer bucket, not just a flat list:
   - smartphone / consumer electronics
   - AI / data center
   - networking / communications
   - CPU / GPU / HPC
6. If exact customer revenue mix is not publicly disclosed, say so explicitly and avoid fake precision.
7. Good default output:
   - `主要服务对象`
   - `客户结构变化`
   - `业务趋势`
   - `股价/市场趋势`
   - `风险点`

## Premarket tactical recommendation workflow

When the task is a U.S. premarket evening recommendation rather than a general market brief:
1. Confirm the live Beijing and U.S. Eastern times and label all extended-hours prices with their timestamp.
2. Compare `SPY / QQQ / SOXX` first to identify broad-market versus technology versus semiconductor relative strength.
3. Select only 3–5 trade ideas. It is valid to mix `看多 / 观察 / 谨慎 / 回避`, or state `今晚以观察为主` when catalysts are weak.
4. For each idea, separate:
   - durable thesis
   - tonight's verified trigger
   - invalidation risks
   - support/resistance range and confirmation condition
5. Treat large premarket gaps as a reason to require pullback or breakout confirmation, not as an automatic buy signal.
6. If no single company catalyst can be verified, say so explicitly rather than forcing a narrative from generic sector news.

See `references/premarket-trade-ideas.md` for Nasdaq quote/history endpoints, ISO date handling, RSS fallback queries, candidate scoring, and a compact report checklist.

## Reference notes
- `references/private-company-stock-analysis.md` — compact decision tree and response skeleton for users who ask for stock analysis on unlisted/private companies.
- `references/premarket-trade-ideas.md` — repeatable workflow for Chinese premarket trade-idea reports with catalysts, risks, and price levels.

## Response style

The user prefers direct, practical, result-oriented help in Chinese.

Default output format:
1. `先说结论`
2. `核心驱动`
3. `数据/新闻支持`
4. `接下来怎么看`
5. `风险点`

Keep it concise unless the user asks for a deeper breakdown.

## Good defaults

### For “为什么涨/跌了”
Use a 3-part diagnosis:
- company-specific catalyst
- sector / macro tailwind or headwind
- trading / positioning effect

### For “哪些股票有冲劲”
Give:
- 3 to 6 names max
- one-line reason each
- separate `最猛` from `更稳`

### For “值不值得追”
Avoid pretending certainty. Use:
- short-term momentum view
- medium-term narrative view
- what would invalidate the thesis

## Pitfalls

- Yahoo-derived data can be incomplete or rate-limited; if one tool is sparse, cross-check with another Yahoo Finance MCP tool instead of overconfidently guessing.
- In practice, Yahoo MCP may hard-fail with `Too Many Requests` across both price history and earnings endpoints. When that happens, switch immediately to a fallback workflow instead of retry-looping:
  1. Use Nasdaq quote endpoints for last close / daily change / volume:
     - `https://api.nasdaq.com/api/quote/<TICKER>/info?assetclass=stocks`
     - `https://api.nasdaq.com/api/quote/<TICKER>/chart?assetclass=stocks`
  2. Use Nasdaq analyst ratings when available:
     - `https://api.nasdaq.com/api/analyst/<TICKER>/ratings`
  3. Use Nasdaq earnings-surprise endpoint as a substitute for recent earnings quality:
     - `https://api.nasdaq.com/api/company/<ticker-lower>/earnings-surprise`
  4. Use Google News RSS for recent headlines/catalysts:
     - `https://news.google.com/rss/search?q=<query>&hl=en-US&gl=US&ceid=US:en`
- Nasdaq endpoints usually require a browser-like `User-Agent` plus `Accept: application/json, text/plain, */*`, and often work better with `Origin: https://www.nasdaq.com` and `Referer: https://www.nasdaq.com/` headers.
- For ETFs on Nasdaq quote endpoints, use `assetclass=etf` (for example `QQQ`, `SOXX`, `SPY`). Using `assetclass=stocks` can falsely return `Symbol not exists`.
- Nasdaq `historical` requires explicit `fromdate` and `todate` query params; omitting them returns a 400 even when the symbol is valid. Prefer ISO dates (`YYYY-MM-DD`) for both parameters. In observed responses, `MM/DD/YYYY`, URL-encoded slashes, and mixed date formats returned `Bad or No parameter fromdate/todate`.
- Distinguish `info.primaryData.lastSalePrice` from the latest row in `historical`: `lastSalePrice` may reflect a newer reference/extended-hours value, while `historical` gives the latest regular-session close. In market notes, label them accordingly instead of mixing the two.
- Some Nasdaq historical/news endpoints may return empty arrays or 404s even when quote/info works; do not assume the whole source is broken.
- Google News RSS for ETF queries can be noisy or low-signal; use it mainly for broad theme context, and prefer company-specific queries for single-name catalysts.
- Do not treat raw news headlines as sufficient; tie them back to earnings, guidance, valuation, or theme rotation.
- Do not present this as financial advice.
- For broad market momentum lists, avoid dumping too many tickers.

## Fallback workflow for next-day review

When the user asks for a review split into `近期节奏 / 昨天涨跌原因 / 预计涨跌分析`, use this structure:
1. Pull yesterday close, net change, percentage change, and previous close from Nasdaq `quote/<TICKER>/chart` or `info`.
2. Pull analyst stance from Nasdaq ratings (`Buy/Hold/etc.`).
3. Pull latest earnings-surprise row from Nasdaq earnings-surprise to anchor the fundamental backdrop.
4. Pull 3-5 recent Google News RSS headlines for catalyst context.
5. Write the output in three blocks:
   - `近期节奏`: trend/state of the name
   - `昨天的涨跌原因`: likely direct catalyst vs. profit-taking vs. sector move
   - `预计的涨跌分析`: short-term view, medium-term view, and key risk
6. If you cannot verify a specific catalyst, say it looks more like `高位回吐 / 技术性回撤 / 资金降温` rather than inventing news.

## Example analyst prompts this skill should support well
- `看看 SMCI 为什么起飞了`
- `给我 5 个最近最有冲劲的美股 AI 标的`
- `比较一下 SMCI / AMD / DELL / ANET 哪个更适合追`
- `查一下 NVDA 下次 earnings 和最近新闻`
- `看下 TSLA 这周走势和催化`

## Verification checklist

Before answering:
1. Did you actually call Yahoo Finance MCP tools instead of guessing?
2. Did you separate facts from interpretation?
3. Did you explain both catalyst and risk?
4. Is the answer in concise Chinese by default?
