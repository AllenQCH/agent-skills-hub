# KOReader AI reading plugins — observed options

Use this reference when a user asks for AI translation, contextual explanation, book chat, RAG, or Obsidian integration inside KOReader. Re-check release pages before installation because these projects move quickly.

## Comparison

| Project | Architecture | Best fit | Observed maturity | Important caveats |
|---|---|---|---|---|
| [`zeeyado/koassistant.koplugin`](https://github.com/zeeyado/koassistant.koplugin) | Native KOReader Lua plugin calling AI services | General-purpose, actively maintained AI assistant | Observed: ~152 stars, 47 tags, ~1,370 commits, active updates | Requires API configuration; inspect supported providers and release asset before install |
| [`chunbo129/AIReadingAssistant`](https://github.com/chunbo129/AIReadingAssistant) | Native KOReader plugin; OpenAI-compatible providers | Chinese-oriented prompts, translation, grammar, AI dictionary | Observed: ~15 stars, 1 tag, ~20 commits | Renames `configuration.lua.sample` to `configuration.lua`; menu-cleaner modifies the native selection menu and may interact with UI plugins |
| [`samfoy/marginalia`](https://github.com/samfoy/marginalia) | KOReader plugin + Python bridge on Mac/Linux/Windows | Book Index/X-Ray, position-bounded RAG, spoiler-safe chat, Obsidian notes | Observed latest release v0.9.0, small user base | Requires Python 3.11+, bridge on port 7731, API credentials, optional Calibre/Obsidian; more experimental and operationally complex |

## Recommendation heuristic

1. Prefer **KOAssistant** when the user wants a mature, direct-on-device AI assistant.
2. Prefer **AIReadingAssistant** when Chinese prompts and a simple OpenAI-compatible configuration are the priority, after warning about menu cleanup.
3. Prefer **Marginalia** only when the user explicitly wants whole-book RAG, no-spoiler context, series intelligence, or Obsidian capture and accepts running a companion service.
4. Install only one overlapping AI reading plugin initially. Verify normal selection, dictionary, and book-opening behavior before adding another.

## AIReadingAssistant installation notes

Expected final path:

```text
<device>/koreader/plugins/aireadingassistant.koplugin/main.lua
```

Configuration workflow:

```text
configuration.lua.sample → configuration.lua
```

Configure provider, API endpoint/model, and secret locally. Never paste or preserve API keys in reports or chat transcripts. The plugin advertises OpenAI-compatible services including OpenAI, Claude-compatible gateways, Gemini, DeepSeek, Volcengine/Doubao, DashScope/Qwen, GLM, and custom endpoints; verify current README and code before promising compatibility.

## Marginalia topology

```text
KOReader marginalia.koplugin
  → LAN or Tailscale
  → bridge host:7731
  → configured LLM + optional Calibre + optional Obsidian vault
```

Set a shared token when the service is reachable beyond a private trusted LAN. Do not expose port 7731 unauthenticated to the public internet.

## EPUB caveat

AI assistant plugins do **not** repair an EPUB that KOReader cannot open. Treat EPUB opening as a separate diagnostic flow: capture the exact error, compare both books, inspect archive integrity/mimetype/DRM, and read KOReader logs before changing plugins or settings.
