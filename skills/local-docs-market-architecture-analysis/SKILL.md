---
name: local-docs-market-architecture-analysis
description: 'Use when the user needs the local docs market architecture analysis workflow: Read a local project/design directory, extract the existing architecture or agent-splitting logic, compare it against public framework/vendor guidance, and produce a structured recommendation with implementation roadmap. Do not use for tasks outside this software-development workflow or tasks better handled by a narrower debugging, testing, planning, or review skill.'
---

# Local docs + market architecture analysis

Use this when the user asks for a structured analysis that combines:
- local files/directories (design docs, configs, schemas, notes)
- public reference materials (framework docs, engineering articles, pattern writeups)
- an output that explains current design, compares it to market approaches, and recommends a best-practice target architecture

Typical examples:
- analyze agent splitting / multi-agent orchestration design
- compare an internal workflow system to OpenAI/Anthropic/LangGraph/AutoGen patterns
- derive an implementation roadmap from existing local artifacts

## Goals
1. Extract the user's current design from local files first.
2. Identify the actual decomposition logic already present (not just filenames or role names).
3. Compare to 3-5 public sources with concrete pattern language.
4. Recommend a simplified target architecture and phased implementation plan.

## Recommended workflow

### 1) Inspect the local artifacts first
Use `read_file` and `search_files` to locate the highest-signal files:
- architecture/design markdown
- schemas/contracts
- config/registry files
- examples showing canonical input/output

For agent systems specifically, prioritize files like:
- contracts / schema definitions
- stage/gate definitions
- tool/permission matrices
- example payloads

Extract:
- core entities/agents
- decomposition dimension(s): stage, role, tool, risk, artifact, workflow
- input/output contracts
- review/gate/approval mechanisms
- context-boundary rules
- permissions/risk controls

Do **not** start from public articles before understanding the local system.

### 2) Infer the real architecture
Summarize the local design in terms of layers, for example:
- routing / control plane
- stage planners
- execution/operators
- reviewers/gates

Look for the true split logic:
- by lifecycle stage
- by decision authority
- by external system/tool
- by risk boundary
- by output artifact

Call out whether the system is really:
- capability-based
- stage-based
- orchestrator-worker
- handoff-based
- state-machine-driven
- contract-first

### 3) Gather external comparison points
Use browser/web tools to fetch concrete references from major public sources.
For agent architecture comparisons, good anchors are:
- Anthropic: Building Effective Agents
- OpenAI Agents SDK orchestration / handoffs / agents-as-tools
- LangGraph workflows + agents
- AutoGen design patterns (handoffs, reflection, mixture-of-agents)

When reading references, extract the usable claims, not generic summaries:
- when to use workflows vs agents
- manager/tool pattern vs handoff pattern
- orchestrator-worker
- evaluator/reviewer loops
- parallel workers / reflection / debate (and whether they fit)

### 4) Compare current design vs market patterns
Create a mapping table or explicit bullets:
- current local component → closest public pattern
- where the local design is stronger
- where it is overly fragmented
- where naming/layering is unclear
- which public patterns are relevant vs irrelevant for this use case

Important: do not assume the most complex public pattern is best. Prefer the simplest pattern that matches the actual task and risk profile.

### 5) Produce a decision-oriented recommendation
The most useful output format is:
1. **One-line conclusion**
2. **Current local logic** (what the system is really doing)
3. **Strengths**
4. **Problems / overlaps / risks**
5. **Best target split**
6. **Implementation roadmap** (phased)

For architecture recommendations, prefer recommending:
- fewer top-level agent categories
- stronger contracts
- a clearer state machine
- explicit gate/reviewer separation
- thin operators with strict risk controls

### 6) End with actionable next steps
Offer one of these concrete follow-ups:
- generate an architecture diagram / layer table
- write a markdown design doc locally
- convert findings into a state-machine spec / registry YAML
- propose refactors to existing contracts/schemas

## Output template

Use this structure unless the user requests another format:

### 一句话结论
- direct verdict

### 当前拆分逻辑
- what the local system is actually optimized around

### 与市面方案对照
- Anthropic / OpenAI / LangGraph / AutoGen mappings

### 当前优点
- 3-5 bullets

### 当前问题
- overlap, ambiguity, missing state machine, over-fragmentation, etc.

### 最佳拆分逻辑
- target layering and naming

### 后续实现路线
- phase 1 / 2 / 3 / 4

## Pitfalls
- Do not just list filenames; infer the architecture behind them.
- Do not overvalue autonomous multi-agent chat patterns for deterministic engineering workflows.
- Do not recommend more agents unless the added boundary is truly useful.
- Do not skip risk/permission boundaries if local materials already encode them.
- Do not treat public framework docs as prescriptions; use them as comparison points.

## Signals this skill worked
- The analysis explains the *real* decomposition axis of the local system.
- The comparison cites specific public orchestration patterns.
- The recommendation reduces ambiguity, not just adds abstraction.
- The roadmap is implementable and phased, not a vague rewrite plan.
