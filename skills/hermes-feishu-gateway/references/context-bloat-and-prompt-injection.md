# Hermes context bloat and prompt-injection troubleshooting

Use when Allen reports that Hermes/Feishu replies look polluted by hidden context, repeated instructions, memory blocks, or unexpectedly large context usage.

## GitHub issue signals found

- NousResearch/hermes-agent#44397: IM gateways (WeChat/Feishu-family reports) can echo internal `<memory-context>` system-note blocks into user-visible bubbles, polluting conversation rendering. Related PR: #44646 filters internal memory-context blocks from final Feishu/WeCom/Weixin replies.
- #17251: context compaction can demote `MEMORY.md` / `USER.md` to "background reference" framing, causing memory to be loaded but not treated as active instructions after compaction/restart. Related regression-test PR: #43778.
- #7192 / #64342: `MemoryProvider.on_pre_compress()` return text can be dropped before compression, so provider insights are not preserved in summaries.
- #65905: provider context-window values can be cached indefinitely in `context_length_cache.yaml`; stale cached windows may make Hermes overestimate available context.
- #67530: copying long personality/system prompts into per-channel overrides creates prompt duplication/drift; compose or centralize behavior instead.

## Local diagnostic pattern

1. Check for duplicate instruction paths before blaming model behavior:
   - `agent.system_prompt`
   - enabled plugins with `pre_llm_call` hooks
   - channel/topic overrides
   - skill/user memory injected into the system prompt
2. Verify local behavior from config and source before treating GitHub issue numbers as proof. Public GitHub API/`gh` calls can rate-limit or require auth; when that happens, mark specific issue details as unverified instead of overstating them.
3. In current Hermes code, `pre_llm_call` plugin results with `{"context": ...}` are appended to the current user message for that API call, not stored in the system prompt. This is useful for ephemeral context but can look like user-message pollution and wastes tokens if it duplicates `agent.system_prompt`.
4. If the same formatting/personality rules exist in both `agent.system_prompt` and a `pre_llm_call` plugin, prefer one canonical location. For Allen's default response formatting, keep `agent.system_prompt` and disable the duplicate plugin.
5. If visible replies contain literal `<memory-context>...</memory-context>`, treat it as an internal-context leak and check whether the installed Hermes version contains the #44646-style final-response filtering.
6. If provider context-limit errors appear, inspect `~/.hermes/context_length_cache.yaml` and compare with the live provider's documented/authenticated limit before changing compression behavior.

## Recommended mitigation order

- First: remove duplicate prompt injection. Keep stable global behavior in `agent.system_prompt`; avoid also injecting the same block through `pre_llm_call` every turn.
- Second: keep Feishu display quiet: no streaming, no tool previews, no interim assistant messages unless debugging.
- Third: if memory blocks leak visibly, update Hermes or apply a targeted scrubber/final-response filter rather than disabling memory entirely.
- Fourth: only reduce `model.context_length` after seeing actual context-limit/provider errors or stale cache evidence.

## Commands commonly used

```bash
hermes config set plugins.enabled '[]'
hermes config set model.context_length 272000   # only if provider limit evidence supports it
hermes gateway restart
```

Prefer `hermes config set` over direct writes to `~/.hermes/config.yaml` when modifying security-sensitive config.
