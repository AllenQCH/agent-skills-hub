---
name: stock-momentum-fallback
description: 'Use when the user needs the stock momentum fallback workflow: Fallback workflow for checking U.S. stock momentum and catalysts when common finance sites/APIs are blocked; prioritize CNBC quote, market movers, and related articles. Do not use for execution-only tasks that do not require research, monitoring, market data, or literature discovery.'
---

# When to use

Use this when the user asks things like:
- 哪些美股/股票比较有冲劲
- why is <ticker> up/down today
- 给我看今天最强的股票/板块

Especially use it when common sources such as Google Finance search results, Yahoo Finance, MarketWatch, Finviz, Barchart, Reuters pages, or unauthenticated quote APIs are blocked, geo-restricted, rate-limited, or return bot-detection pages.

# Core idea

Do **not** get stuck retrying blocked sources endlessly. Quickly pivot to **CNBC**, which often exposes enough structured quote data, market movers lists, and catalyst articles through browser tools even when other finance sites fail.

# Workflow

1. **Try direct accessible quote/news pages first**
   - `browser_navigate("https://www.cnbc.com/quotes/TICKER")`
   - Read the quote snapshot for:
     - current/last price
     - daily % move
     - volume
     - 52-week range
     - returns (5 day / 1 month / YTD)
     - latest article links

2. **Check market movers on CNBC**
   - `browser_navigate("https://www.cnbc.com/markets/us-market-movers/")`
   - The text snapshot may omit tables. If so, use `browser_console()` and inspect DOM tables.
   - Useful expression:
     ```js
     Array.from(document.querySelectorAll('table')).map((t,i)=>({
       i,
       text:t.innerText.slice(0,1000)
     }))
     ```
   - To identify which table is gainers/losers, inspect parent text:
     ```js
     Array.from(document.querySelectorAll('table')).map((t,i)=>{
       let p=t.parentElement; let texts=[];
       for(let k=0;k<4 && p;k++,p=p.parentElement){
         texts.push((p.innerText||'').slice(0,200));
       }
       return {i,texts};
     })
     ```
   - This often reveals top gainers even if the browser snapshot hides them.

3. **Open catalyst articles from the quote page**
   - From the ticker quote page, look for:
     - earnings article
n     - “biggest movers” article
     - options/flow article
   - Open those pages directly with `browser_navigate()`.
   - Extract the catalyst stack:
     - earnings beat/miss
     - guidance beat/cut
     - management explanation for revenue timing
     - legal/regulatory overhang easing or worsening
     - customer demand commentary
     - analyst target changes
     - options/call-put skew / squeeze behavior

4. **Cross-check company IR when possible**
   - Try investor relations news page for official press release titles/dates.
   - Be aware: the IR landing/news index may load, but article pages or stock-detail pages may trigger Cloudflare verification.
   - If article body is blocked, still use accessible news headlines and CNBC’s direct summary.

5. **Summarize in trader language**
   - Separate:
     - **what moved** (price, momentum rank)
     - **why it moved** (earnings/guidance/news)
     - **what kind of move it is** (short-covering, sentiment repair, AI infra sympathy, options squeeze, etc.)
     - **risk** (high beta, headline risk, volatility)
   - If the user asked for “有冲劲”, group nearby names in the same theme (e.g. AI servers, chips, networking).

# Known blocked/weak sources from this session

These may fail due to geography, bot detection, auth requirements, or local process pressure:
- Browser tools themselves may fail to spawn with `EAGAIN` / `[Errno 35] Resource temporarily unavailable`
- Google search via browser → often lands on `/sorry/` bot page
- Yahoo Finance quote/chart endpoints may return a Yahoo error page / sad-panda page
- MarketWatch → empty page
- Finviz / Nasdaq / Zacks / Barchart / Reuters / StockTitan → connection reset or 403
- Public finance APIs with `demo` keys (FMP, Polygon, TwelveData) → unusable without real API keys
- Stooq CSV historical endpoint (`/q/d/l/`) → requires captcha-derived API key

# Ultra-light fallback when browser/process spawning is impaired

If browser tools fail with `EAGAIN` or shell commands intermittently hit `fork: Resource temporarily unavailable`, switch to the lightest possible stack:

1. **Prefer `terminal` + `curl` over browser automation**
   - Use short, single-purpose calls.
   - Avoid large parallel batches when the machine is already process-constrained.
   - Prefer one ticker per command if shell instability is visible.

2. **Use Python stdlib, not `requests`**
   - `requests` may not be installed.
   - For HTML fetches and lightweight parsing, use `urllib.request` and regex / simple string extraction.
   - Useful for DuckDuckGo HTML results pages when you just need article titles/links.

3. **Use Stooq single-quote endpoint for spot OHLC when broader quote APIs are blocked**
   - Example:
     - `https://stooq.com/q/l/?s=smci.us`
   - This can return a compact row like:
     - `SMCI.US,YYYYMMDD,HHMMSS,open,high,low,close,volume,...`
   - Good for confirming the latest trading date and spot OHLC.
   - Important: the historical CSV endpoint (`/q/d/l/`) often asks for an API key/captcha, so do not depend on it.

4. **CNBC quote pages are the most reliable fallback for last close + daily % move**
   - In degraded conditions, prefer:
     - `https://www.cnbc.com/quotes/TICKER`
   - Fetch with `terminal` + Python `requests` + `bs4` instead of browser automation when you need many tickers.
   - Practical extraction pattern from page text:
     - normalize with `text=' '.join(BeautifulSoup(html, 'html.parser').get_text(' ', strip=True).split())`
     - regex for close block:
       - `After Hours:.*?Close\s+PRICE\s+CHANGE\s*\(\s*PCT\s*\)`
     - regex for support fields:
       - `Prev Close\s+...`
       - `52 Week High\s+...`
       - `Earnings Date\s+...`
   - This worked well for multi-ticker daily scans when Yahoo MCP was rate-limited and browser pages were blocked/geo-restricted.

5. **Compute percent change explicitly with a tool when needed**
   - Do not estimate mentally.
   - If CNBC exposes `Prev Close` and `Close`, you can verify `% change = (close-prev_close)/prev_close` with Python.
   - If CNBC already shows daily % move, you may report it directly, but still prefer tool-based verification when there is any ambiguity.

6. **Be careful with CNBC quote-page headlines**
   - The "Latest On" / article list on a quote page is useful for theme context, but not every headline is a company-specific catalyst.
   - For single-stock catalyst analysis:
     - prioritize headlines explicitly naming the ticker/company
     - use broad AI/market headlines only as secondary context
   - If headlines are generic or cross-company, say the catalyst read is thematic rather than company-specific.

7. **Treat search-result snippets as catalyst triangulation, not ground truth**
   - DuckDuckGo HTML result titles can quickly reveal the market narrative:
     - earnings beat
     - guidance beat
     - margin expansion
     - revenue miss but stock up
   - Then validate with at least one accessible article or company/IR-related source if possible.

8. **Keep output honest about coverage**
   - If the environment is degraded, frame conclusions as:
     - “based on accessible public pages I could still reach”
     - not “full market scan”

# Practical heuristics

- A stock “起飞” after earnings is often **guidance-driven**, not quarter-driven. Call this out explicitly.
- If revenue misses but stock rallies, look for:
  - future-quarter guide above consensus
  - deferred revenue recognition / deployment timing issues
  - supply constraints expected to ease
  - narrative repair after prior scandal/selloff
- If momentum is extreme, mention:
  - 5-day return
  - 1-month return
  - volume vs average volume
  - whether options flow is heavily call-skewed

# Pitfalls

- Do not pretend you have full market-wide coverage if only one accessible movers page is available.
- Do not state exact “today’s strongest stocks” across the whole market unless the source clearly covers the relevant universe (e.g. S&P / Nasdaq / Dow tab on CNBC).
- Distinguish **after-hours**, **intraday**, and **last close** timestamps from the page.
- Mention source limitations if other finance sites were blocked.

# Output template

Use a structure like:

1. **最有冲劲的票**
   - TICKER: +X%
   - peers/themes

2. **为什么 TICKER 起飞**
   - catalyst 1
   - catalyst 2
   - catalyst 3

3. **这波本质是什么**
   - guidance beat / sentiment repair / AI infra sympathy / squeeze

4. **风险点**
   - volatility
   - legal/regulatory
   - execution / deployment timing

5. **可对比的同链条股票**
   - adjacent names by theme
