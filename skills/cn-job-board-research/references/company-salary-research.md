# Company Salary Research Checklist

Use this reference when the user asks for a current salary overview of a named company, especially when the role or city is unspecified.

## Evidence ladder

1. Current employer careers page or authenticated company posting
2. Current Liepin/51job company posting
3. Jobui company and role-level salary pages
4. Employee-review platforms as qualitative cross-check only
5. Social posts only as anecdotes, never the main salary source

## Jobui URL pattern

```text
/company/<id>/
/company/<id>/salary/
/company/<id>/jobs/
/company/<id>/salary/j/<role-slug>/
```

Useful browser extraction:

```js
// Discover role salary pages
[...document.querySelectorAll('a')]
  .filter(a => a.href.includes('/salary/j/'))
  .map(a => ({ text: a.innerText.trim(), href: a.href }))

// Pull salary evidence from chart-heavy pages
const lines = document.body.innerText.split('\n').map(x => x.trim()).filter(Boolean)
lines.filter(x => /薪酬区间|取自近一年|截至|按经验统计|按学历统计|招聘地区/.test(x))

// Capture full job cards around matching headings
[...document.querySelectorAll('h3')]
  .filter(h => /目标岗位关键词/.test(h.innerText))
  .map(h => {
    let p = h
    for (let i = 0; i < 4 && p; i++) p = p.parentElement
    return p?.innerText
  })
```

## Minimum output fields

| Field | Requirement |
|---|---|
| Role family | Separate frontline, management, professional, and technical roles |
| Monthly range | Preserve the source unit and do not infer annual package without salary-month data |
| Sample size | Include when the source provides it |
| Evidence date | Include posting date or page statistics date |
| City | Distinguish city-specific examples from nationwide aggregation |
| Employment type | Separate full-time, part-time, daily wage, dispatch, and outsourcing |
| Compensation gaps | Mark bonus, 13薪, stock, overtime, and benefits as unconfirmed unless explicitly sourced |
| Source type | Label official posting vs aggregator vs employee review |

## Interpretation pitfalls

- A company average can be meaningless when frontline workers dominate volume but headquarters roles dominate high salaries.
- Role aliases may overlap: 店长/店经理, 值班主管/值班经理, 工程师/开发工程师.
- A wide range can come from mixed disciplines or seniority rather than a real pay band.
- Location averages can reflect role mix rather than geographic premium.
- Aggregator labels may join legal entities, regional subsidiaries, or unrelated similarly named companies.
- Salary pages can show current summaries alongside older example postings; report both dates clearly.

## Recommended final structure

1. Conclusion: whether compensation is low, market-level, or competitive by role family
2. Role table: range, sample/date, and interpretation
3. Why the overall average is misleading
4. If conversation context indicates a target role, add a focused subsection for it
5. Negotiation checklist: fixed monthly salary, salary months, target bonus, contracting entity, social-insurance base, overtime/shift policy, stock, and outsourcing status
