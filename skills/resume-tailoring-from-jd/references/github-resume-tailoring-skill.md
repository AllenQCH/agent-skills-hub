# GitHub Resume Tailoring Skill Notes

Session source: user asked whether GitHub has a skill/solution that automatically writes/tailors resumes from a JD, then chose to try `amanattar/resume-tailoring-skill` with a Chinese Java JD screenshot and a DOCX resume.

## Useful Repositories Found

| Repo | Shape | Notes |
|---|---|---|
| `amanattar/resume-tailoring-skill` | Claude Skill / workflow spec | Best match for “skill”; assumes Markdown resume library; workflow covers JD analysis, research, content matching, truthful resume generation. |
| `waygeance/AutoATS` | Next.js + Ollama + LaTeX local app | Privacy-first local ATS resume builder; needs Node/Ollama/pdflatex. |
| `JaimeYeung/Resume-Tailor-AI` | Web app with Fact Bank | Good fact-bank model for long-term resume source-of-truth. |
| `thechandanbhagat/cv-forge` | MCP server | Good fit for agent ecosystems; generates CV, cover letter, email template. |
| `farmerTheodor/Resume-Tailor` | CLI/LaTeX | Experience bank + template + JD → generated resume. |

## `amanattar/resume-tailoring-skill` Caveat

The repo is useful but not a complete runnable toolchain. Its README says it is a minimal standalone repo for Claude skill installation. `SKILL.md` references support files such as:

- `research-prompts.md`
- `matching-strategies.md`
- `branching-questions.md`
- `multi-job-workflow.md`

During inspection, the repo root only contained:

```text
LICENSE
README.md
SKILL.md
```

So adapt it as a process/workflow rather than expecting an executable app. For Hermes/local usage, create the missing artifacts yourself as output files or add them as support files in this skill.

## Minimal Hermes Adaptation

Given:

- JD from screenshot/text/URL
- Existing resume DOCX/PDF/Markdown

Do:

1. Extract/normalize the resume into `resumes/master-resume.md`.
2. Normalize the JD into `jobs/target-jd.md`.
3. Create `output/phase0-library-summary.md` with role/project/skill/risk extraction.
4. Create `output/phase1-jd-analysis.md` with JD success profile and matching table.
5. If key requirements are unsupported, generate a conservative draft and ask targeted follow-ups for a stronger version.

Example workspace:

```text
/Users/heytea/Documents/other/resume-tailoring-java/
  README.md
  resumes/master-resume.md
  jobs/target-jd.md
  output/phase0-library-summary.md
  output/phase1-jd-analysis.md
  output/next-step-prompt.md
```

## Risk Pattern Learned

For JD-driven resume tailoring, hard requirements are often where over-claiming happens. Explicitly detect and label them:

- Experience years mismatch.
- Degree/major mismatch.
- Team management headcount mismatch.
- Public-safety of metrics/system names.
- Ambiguous metrics like “production 0 bug” that need precise wording.

The correct behavior is not to hide the mismatch, but to propose a truthful positioning alternative and list what evidence would be needed to strengthen the draft.
