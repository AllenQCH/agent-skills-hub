---
name: cn-job-board-research
description: 'Use when the user needs the cn job board research workflow: Research current Chinese hiring, company salary, role requirements, and job-market trends using Liepin, 51job, Jobui, and resilient browser extraction when search engines or dynamic DOMs are flaky. Do not use for execution-only tasks that do not require research, monitoring, market data, or literature discovery.'
---

# Chinese Job Board Research (Liepin + 51job)

Use this when a user asks for current hiring requirements, role trends, or a transition plan based on **real Chinese recruitment listings**.

## Why this skill exists

In browser automation, generic search engines often block bots or show CAPTCHA, and some Chinese job boards expose only partial structured DOM content. A reliable workflow is to:
1. skip search engines quickly if challenged,
2. go directly to the job board search pages,
3. open representative postings,
4. extract requirement text from the JD page or from page `innerText` when DOM anchors are unreliable,
5. synthesize recurring requirements into actionable advice.

## Reliable workflow

### 1) Avoid wasting time on search engines
- If Bing/DuckDuckGo shows a challenge/CAPTCHA, stop using it.
- Navigate directly to the target sites instead:
  - Liepin search: `https://www.liepin.com/zhaopin/?key=<URL-encoded-keyword>`
  - 51job search: `https://we.51job.com/pc/search?keyword=<URL-encoded-keyword>`

Typical keywords:
- `AI工程师`
- `AI应用开发`
- `Agent工程师`
- `大模型工程师`
- `算法工程师`

### 2) On Liepin, use full snapshots and open representative JDs
Liepin often exposes enough structured content in the accessibility snapshot.

Recommended sequence:
1. `browser_navigate()` to search page.
2. `browser_snapshot(full=true)` to reveal more listing content.
3. Open 3-5 representative jobs spanning different subtypes, e.g.:
   - AI应用开发工程师
   - Python AI Engineer / LLM Engineer
   - AI Agent平台研发工程师
   - AI算法工程师
4. Read the JD text from the detail page snapshot; it usually includes a long `职位介绍` block with requirements.

### 3) On 51job, use search results + page text extraction
51job search results often show useful skill tags in rendered text, but link extraction can be weak in the accessibility snapshot.

Reliable method:
1. Navigate to `https://we.51job.com/pc/search?keyword=...`
2. Type keyword if needed and press Enter.
3. If structured link extraction is weak, use:
   - `browser_console({ expression: 'document.body.innerText.slice(0,4000)' })`
4. Extract repeated skills/keywords from the visible text blocks in search results.

This is especially useful for quick market-scan evidence like:
- Python / Java / Flask
- Docker / Git / GCP
- Transformer / Chatbot / 多轮对话
- SQL / Hadoop / Hive / Spark
- 图像识别 / 目标检测 / 图像分割
- Agent / 智能问答 / 工作流优化 / AI平台

### 4) Research company-wide and role-level salary data on Jobui
When the user asks “某家公司薪资如何” without naming a single role, Jobui can provide a useful company→role drill-down even when search engines, BOSS, Indeed, or Glassdoor are blocked.

Reliable sequence:
1. Open `https://www.jobui.com/` and switch to **按公司关键词**.
2. Search the legal/company name and open the best-matching entity; distinguish headquarters, regional operating companies, and similarly named companies.
3. On the company page, identify the numeric company ID from URLs such as `/company/<id>/`.
4. Open these directly:
   - `/company/<id>/salary/` — aggregate salary distribution and sample count
   - `/company/<id>/jobs/` — current job titles, cities, dates, and disclosed ranges
   - `/company/<id>/salary/j/<role-slug>/` — role-level range, sample count, experience, education, and city distribution
5. If snapshots truncate chart text or job cards, use `browser_console` on `document.body.innerText` and search for durable phrases such as `薪酬区间`, `取自近一年`, `截至`, `按经验统计`, and the target role name.
6. Extract role detail links programmatically when necessary:
   ```js
   [...document.querySelectorAll('a')]
     .filter(a => a.href.includes('/salary/j/'))
     .map(a => ({text: a.innerText.trim(), href: a.href}))
   ```
7. Cross-check current corporate openings on Liepin or the employer’s official careers page. Many headquarters jobs show `薪资面议`; report that honestly instead of inventing a range.

Interpretation rules:
- Treat Jobui as **aggregated recruiting-post data**, not internal payroll or employee-reported take-home pay.
- Always report sample count/date when visible; small role samples can be distorted by one posting.
- Do not use the company-wide average when frontline and headquarters roles are mixed. Break out major role families.
- Separate full-time, part-time, daily wage, and monthly salary samples.
- Duplicate titles such as 店长/店经理 or 值班主管/值班经理 may represent regional naming differences rather than separate levels.
- City averages can be misleading when each city contains different role mixes.
- If annual bonus, 13薪, stock, or benefits are not explicitly shown in a current posting, label them “待向招聘方确认”.

See `references/company-salary-research.md` for a compact evidence and reporting checklist.

### 5) Choose representative jobs, not random noise
Some postings on 51job/Liepin use “AI工程师” loosely for automation, operations, or industry-specific roles. Do not overgeneralize from one noisy posting.

Prefer roles that clearly mention:
- LLM / 大模型
- Agent / Workflow
- RAG / 检索 / embedding / 向量库
- Dify / LangGraph / Coze / n8n
- Prompt engineering / context engineering
- API integration / platform development

Use at least one contrasting role like `AI算法工程师` to show the difference between:
- **应用型 AI 岗** (AI application / LLM / Agent / platform)
- **算法型 AI 岗** (training, optimization, ML frameworks, stronger math/research requirements)

### 6) Handle BOSS直聘 mobile links as a protected source
BOSS直聘 mobile “微JD” links often render as blank/`about:blank` in browser automation or show only “打开APP”. Direct terminal/API fetches may return anti-bot responses such as:
- `{"code":37,"message":"您的环境存在异常."}` on `.../wapi/zpgeek/job/detail.json`

Practical rule:
- Treat BOSS mobile links as **best-effort only** in automated sessions.
- Try once in the browser and once via terminal if useful, but do not burn many turns fighting anti-bot.
- If the JD body is blocked, immediately switch to one of these fallbacks:
  1. ask the user for screenshots containing 职责/要求,
  2. ask the user to paste the JD text,
  3. ask for 公司名 + 岗位名 and continue with public-source research,
  4. if the user only wants general preparation, synthesize common requirements from Liepin/51job instead.

This saves time and avoids overpromising extraction from a protected page.

## Synthesis pattern for the final answer

### A. Start with the market conclusion
Example structure:
- The most realistic transition path from Java is **AI应用开发 / Agent开发 / AI平台研发**.
- The least realistic first target is **pure algorithm / training-heavy roles**.

### B. Summarize repeated requirements into buckets
Use concise categories such as:
- Python
- LLM application development
- Agent / workflow frameworks
- RAG
- Backend/API integration
- Docker/deployment
- Logging / tracing / evaluation
- SQL / data processing
- Frontend basics
- PyTorch / model training (only high priority for algorithm roles)

### C. Separate “common demand” from “role-specific demand”
This improves accuracy:
- Common demand across AI application roles: Python, LLM APIs, RAG, Agent frameworks, delivery ability
- Algorithm-role-specific demand: PyTorch/TensorFlow/Jax, training experience, stronger math/research background

### D. Convert research into an actionable transition plan
For career-switch advice, recommend:
1. pick one realistic role target,
2. learn Python + FastAPI,
3. build RAG project,
4. build Agent/workflow project,
5. build one vertical domain demo,
6. then start applying.

## Pitfalls
- Do **not** rely on search engines if they challenge the browser session.
- Do **not** generalize from “AI” jobs that are actually automation/operations-heavy unless the user specifically wants those roles.
- Do **not** recommend pure algorithm roles first to a backend engineer unless they explicitly want a long research-oriented transition.
- On 51job, if clickable detail links are hard to isolate, treat the search-results text as supporting evidence rather than forcing brittle clicks.

## Verification checklist
Before answering, make sure you have:
- At least 3 representative JD samples from a real Chinese job board, OR 2 JD samples + a broad search-results keyword scan.
- Clear distinction between application AI roles and algorithm AI roles.
- A transition recommendation that matches the user’s background and job-market reality.
- No claims about “current market demand” that aren’t grounded in the retrieved listings.
