---
name: resume-tailoring-from-jd
description: Use when the user wants to tailor an existing resume to a specific job description/JD, especially by using an agent/skill-style workflow. Trigger on requests like “根据 JD 改简历”, “岗位匹配简历”, “自动写简历”, or “试用 GitHub resume-tailoring skill”. Output a truth-preserving tailored resume plus JD analysis, change report, and risk check. Exclude generic resume writing from scratch, cover-letter-only work, and LinkedIn profile optimization.
---

# Resume Tailoring from JD

## Purpose

Turn a target job description plus the user's existing resume material into a targeted, truthful application resume. Optimize positioning, wording, keyword coverage, and structure while preserving factual integrity.

Core rule: **do not invent experience, years, management scope, metrics, degrees, systems, or responsibilities.** Reframe and emphasize only facts that are present in the source material or explicitly confirmed by the user.

## When to Use

Use this skill when:

- The user provides a JD screenshot, JD text, or JD URL and an existing resume file.
- The user asks whether GitHub/Claude/Hermes has a skill or workflow to tailor resumes from JDs.
- The user wants to try or adapt `amanattar/resume-tailoring-skill` or a similar resume-tailoring repo.
- The task requires converting DOCX/PDF/text resumes into a Markdown resume library before tailoring.

Do not use this for:

- Writing a resume from nothing with no source facts.
- Pure cover letters or outreach emails unless explicitly requested as an add-on.
- Fabricating experience to pass hard JD requirements.

## Preferred Output Shape for Allen

Default to Chinese unless the user asks for English/bilingual. Use a concise conclusion-first structure and tables for 3+ comparable items.

For a complete run, produce these artifacts:

| Artifact | Purpose |
|---|---|
| `resumes/master-resume.md` | Markdown version of the original resume/source facts |
| `jobs/target-jd.md` | Cleaned JD text from screenshot/text/URL |
| `output/phase0-library-summary.md` | Resume-library initialization summary |
| `output/phase1-jd-analysis.md` | JD analysis, matching table, positioning, risks |
| `output/tailored-resume.md` | Tailored resume draft |
| `output/change-report.md` | What changed and why |
| `output/risk-check.md` | Over-claiming/hard-requirement/sensitive-info risk review |
| `output/next-step-prompt.md` | Prompt for continuing the workflow in another agent/session |

## Workflow

### 1. Intake

Collect or extract:

1. Target JD: screenshot, text, URL, or document.
2. Existing resume: Markdown preferred; DOCX/PDF/text acceptable.
3. Target language: Chinese, English, or bilingual.
4. Target positioning: e.g. senior Java backend, tech lead, QA agent PM, engineering productivity.
5. Constraints: sensitive company/system names, metrics that cannot be public, facts not to mention.

If the user provides a screenshot, use OCR/vision content as the initial JD text and normalize it into Markdown.

### 2. Build a Minimal Workspace

Create a local working directory near the source resume unless the user specifies otherwise:

```text
resume-tailoring-<role>/
  README.md
  resumes/
    master-resume.md
  jobs/
    target-jd.md
  output/
    .gitkeep
```

For DOCX/PDF resumes, extract text first, then normalize into Markdown sections:

```markdown
# Name

## Basic Information
## Education
## Skills
## Core Strengths
## Work Experience
## Project Experience
```

Keep the original source path traceable in `README.md`.

### 3. Phase 0 — Resume Library Initialization

Scan `resumes/*.md` and summarize:

- Roles: company, dates, title, possible positioning.
- Projects: role, business domain, technical highlights, metrics.
- Skills: languages, frameworks, middleware, architecture, domain expertise.
- Evidence quality: which claims are explicit vs. need confirmation.
- Risk points: hard JD requirements not supported by source facts.

Write `output/phase0-library-summary.md`.

### 4. Phase 1 — JD Analysis / Success Profile

Parse the JD into:

- Role essence: what the job actually wants.
- Must-have requirements.
- Nice-to-have requirements.
- Keywords/ATS terms.
- Responsibilities mapped to resume evidence.
- Gaps and hard risks.
- Recommended positioning.

Use a table like:

| JD requirement | Importance | Matching resume evidence | Current judgment |
|---|---:|---|---|

Write `output/phase1-jd-analysis.md`.

### 5. Hard-Requirement Risk Handling

Never smooth over unsupported hard requirements. Call them out clearly.

Examples:

- JD says “8+ years Java”, resume shows ~5 years: do **not** write 8 years. Recommend emphasizing complex-system ownership instead.
- JD says “managed 5+ people”, resume only says “system owner/version manager”: do **not** write team management unless the user confirms people count and responsibility.
- JD says “computer-related major”, resume shows another major: do **not** modify the degree. Compensate with system delivery evidence.

### 6. Phase 2.5 — Ask Focused Follow-up Questions

Before generating an aggressive tailored resume, ask for missing evidence that materially improves fit:

- Actual team size coordinated/managed.
- Whether the candidate did technical reviews, code reviews, task decomposition, delivery planning.
- Business scale: stores, orders, QPS, data volume, service count, interface count.
- Performance/stability metrics: RT reduction, query latency, success rate, incident recovery time.
- Production incident examples.
- Whether specific metrics/system names are public-safe.

If the user wants immediate output, generate a conservative truthful version and list questions for a stronger second pass.

### 7. Generate the Tailored Resume

Prefer a role-aligned but truthful headline, e.g.:

- “高级 Java 后端工程师 / 复杂业务系统负责人”
- “Java 后端工程师 / 供应链履约系统核心开发”
- “Java 技术负责人” only if leadership evidence is confirmed.

Rewrite bullets to emphasize:

- System design and architecture decisions.
- Core feature implementation.
- High availability and stability.
- Performance optimization.
- Production troubleshooting.
- Cross-team business communication and global impact.

Demote unrelated but useful AI/Agent content unless the target role asks for it; frame it as engineering efficiency or troubleshooting support.

### 8. Change Report and Risk Check

Always include:

- What was strengthened.
- What was removed/demoted.
- Which claims need user confirmation.
- Which JD requirements remain weak.
- Interview defense notes for risky claims.

## GitHub Reference

See `references/github-resume-tailoring-skill.md` for notes from evaluating `amanattar/resume-tailoring-skill` and how to adapt its Claude-style process into a Hermes/local Markdown workflow.

## Pitfalls

- Do not assume a GitHub “skill” is directly runnable; many are workflow specs rather than apps.
- Do not stop at recommending a repo when the user says “try it”; create the workspace, convert inputs, and run at least the analysis phases.
- Do not over-index on ATS keywords at the cost of truthfulness.
- Do not bury hard mismatches; they are important application risks.
- Do not output only the final resume; include a change report and risk check so the user can safely review.
