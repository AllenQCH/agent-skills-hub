# Private company stock-analysis fallback

Use this note when the user asks for `股价分析 / 走势 / 值不值得买` on a company that may not be listed.

## Decision order
1. Resolve listed status first.
2. If private/unlisted, say so in the first line.
3. Do not pretend a public stock chart exists.
4. Reframe into:
   - company quality / stage
   - whether ordinary investors can buy it now
   - public proxy names / beneficiaries

## Fast evidence stack
- Finance search tool: is there a public ticker?
- HTML search result: official site + recent reporting
- Official site: product stage, team size, customer claims, funding claims
- Reputable news: valuation, funding round size, demand/contracts, named investors
- Public comps: use priced equities only after the private/public status is settled

## Response skeleton
- 结论：未上市/无ticker/无公开股价
- 公司怎么样：技术路线、商业进度、融资/客户验证
- 为什么值得/不值得关注：核心多空点
- 想参与怎么办：给 public proxies / beneficiaries

## Example: Etched pattern
- Official site can establish product stage and company claims
- Recent news can establish valuation/funding/customer-contract headlines
- Then pivot to AI inference/public comps such as NVDA / AMD / AVGO / SMCI instead of forcing fake Etched stock analysis
