# Codex Windows desktop offline package

## Artifact identity

- Microsoft Store product ID: `9PLM9XGG6VKS`.
- The complete desktop app is a signed package named like `OpenAI.Codex_<version>_x64__<publisher>.msix` (or `arm64`).
- GitHub assets named `codex-*-pc-windows-msvc.*` are Codex CLI/runtime binaries, not the desktop app.
- `ChatGPT Installer.exe` from `get.microsoft.com/installer/download/9PLM9XGG6VKS` is a small online bootstrapper, not the complete offline package.

## Verified resolution workflow

1. Ask/derive architecture; default to x64 for ordinary Intel/AMD Windows systems.
2. Query Microsoft Store metadata for product `9PLM9XGG6VKS`.
3. Resolve Store package rows. A reviewed zero-dependency resolver used successfully is `get_codex_download_link.py` from `daimiaopeng/codex-msix-downloader`; it calls `https://store.rg-adguard.net/api/GetFiles` only to resolve expiring links.
4. Select the newest `OpenAI.Codex_*_<arch>__*.msix` row, excluding `.BlockMap` and the other architecture.
5. Download the payload only if the final host is a Microsoft CDN such as `tlu.dl.delivery.mp.microsoft.com`.
6. Verify the resolver/Store-provided SHA-1 and compute SHA-256 locally. Preserve the exact `.msix` bytes; do not rename a bootstrapper to look like an offline package.
7. Report filename, version, architecture, byte size, source domain, and hashes.

## Delivery semantics

- A `MEDIA:/local/path` line in a Feishu post can remain plain text; it is not proof of upload.
- For Feishu, send with an actual file API/client operation and then read chat history back. Success evidence is a new `msg_type=file` entry with the expected filename and message ID.
- Check channel size limits before downloading. Bot/simple Drive paths can have lower limits than the desktop client.
- If the complete package exceeds available API limits, do not silently send the online installer. Prefer, in order: authenticated large-file Drive upload, user desktop-client upload, or ask the user to choose between a cloud link and explicit byte-split parts.
- Never flood a group with many split parts without explaining the trade-off and obtaining agreement.

## Installation note

On Windows, a valid Store-signed `.msix` can normally be opened with App Installer. If App Installer or required Windows components are absent, diagnose on the target machine rather than replacing the artifact with a CLI build.
