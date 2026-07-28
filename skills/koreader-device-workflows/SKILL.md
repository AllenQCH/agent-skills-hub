---
name: koreader-device-workflows
description: 'Use when managing KOReader on Kindle or other e-readers: installing/verifying plugins, organizing ebook storage, choosing safe transfer methods, or configuring USB, OPDS, Calibre, cloud, and SFTP workflows. Do not use for unrelated productivity apps, general ebook recommendations, or non-KOReader device tasks.'
license: MIT
metadata:
  hermes:
    tags:
    - koreader
    - kindle
    - ebooks
    - plugins
    - opds
    - calibre
    - sftp
---

# KOReader Device Workflows

Use this skill when the user wants to install a KOReader plugin, install or manage StarDict dictionaries, transfer or download ebooks, choose book folders, configure OPDS/Calibre/cloud/SFTP, or troubleshoot why an e-reader only mounts over USB after leaving KOReader.

## Scope

This skill covers the reusable workflow class:

- inspecting and installing third-party `*.koplugin` packages;
- mapping device-internal paths to USB-visible folders;
- separating KOReader program files from personal books;
- transferring books without repeatedly entering native USB mode;
- choosing between OPDS, Calibre wireless, cloud storage, SFTP, and USB;
- verifying plugin and book discovery without destructive resets.

## First principles

1. Determine the device family before giving paths: Kindle, Kobo, PocketBook, Android, or desktop.
2. Prefer the project's **release asset** over GitHub's generated source archive.
3. Inspect the downloaded archive and verify the expected plugin entry file, normally `plugin_name.koplugin/main.lua`.
4. Keep books outside the KOReader application directory.
5. Do not delete KOReader settings, metadata, or the whole `koreader/` directory to fix a loading problem.
6. Treat USB mounting behavior as device-specific. On Kindle, leaving KOReader for native USB mode can be expected; use Wi-Fi workflows when frequent transfer is needed.

## Plugin installation workflow

### SimpleUI case study

For KOReader's SimpleUI, use the upstream repository at `https://github.com/doctorhetfield-cmd/simpleui.koplugin` and prefer its named release asset `simpleui.koplugin.zip` over the generated source archive. The latest observed release was v2.1.0; v1.5.0 may better match older screenshots/videos. On Kindle, install the extracted single `simpleui.koplugin/` directory under `/koreader/plugins/`, then restart KOReader and enable it from `Menu → Tools → SimpleUI`. See `references/simpleui-koreader.md` for release links, version notes, and the wallpaper fork.

### 1. Inspect upstream

Check the repository README, latest release page, release notes, prerequisites, conflicts, and supported device paths. Record version-specific findings in a reference file rather than hard-coding them into the class-level instructions.

### 2. Download and inspect the release artifact

Use the named plugin asset, for example `name.koplugin.zip`, not `Source code (zip)` unless upstream explicitly says otherwise.

Verify:

```text
archive.zip
└── name.koplugin/
    ├── main.lua
    ├── _meta.lua          # common but not universal
    └── ...
```

Reject or correct double nesting:

```text
plugins/name.koplugin/name.koplugin/main.lua
```

The final path should normally be:

```text
plugins/name.koplugin/main.lua
```

### 3. Check conflicts

UI plugins frequently patch the same KOReader modules. Inspect upstream's conflict list. Prefer reversible disablement before deletion:

```text
other_ui.koplugin
→ other_ui.koplugin.disabled
```

Restart KOReader after changing plugin directories.

### 4. Copy to the device-specific plugins directory

Common locations:

| Device | Internal path | USB-visible interpretation |
|---|---|---|
| Kindle | `/mnt/base-us/koreader/plugins/` or equivalent `/mnt/us/koreader/plugins/` view | `<Kindle volume>/koreader/plugins/` |
| Kobo | `/mnt/onboard/.adds/koreader/plugins/` | `<Kobo volume>/.adds/koreader/plugins/` |
| PocketBook | `/mnt/ext1/applications/koreader/plugins/` | device applications tree |
| Android | `/sdcard/koreader/plugins/` | Android shared storage |

Do not assume the macOS volume is always named `Kindle`; discover the mounted volume first.

### 5. Restart and verify

1. Safely eject the device if USB was used.
2. Fully restart KOReader.
3. Confirm the plugin UI appears.
4. If not, check `Tools → More tools → Plugin management`.
5. Verify final path and inspect logs before changing unrelated settings.

## Dictionary installation and lookup

KOReader uses StarDict dictionaries. Prefer the built-in downloader when the device has working Wi-Fi:

```text
Search / magnifying-glass menu
→ Settings
→ Dictionary settings
→ Download dictionaries
```

After download, use `Dictionary settings → Manage dictionaries` to enable and prioritize sources. For English reading, start with `English-English Wiktionary`; optionally add `GNU Collaborative International Dictionary of English` or `English Idioms (eng-eng)`. Be precise about direction: `Chinese-English` means 汉英, not 英汉.

For manual Kindle installation, extract the matching `.ifo`, `.idx`, and `.dict`/`.dict.dz` files into the USB-visible `/koreader/data/dict/` directory, safely eject, and restart KOReader. On older devices, enable one large dictionary first; too many active dictionaries can slow fuzzy lookup.

See `references/dictionaries.md` for current menu paths, recommended English dictionaries, StarDict file requirements, manual paths, and verification.

## Ebook storage conventions

Recommended folder policy:

| Goal | Recommended folder |
|---|---|
| Primarily read with KOReader | `/mnt/us/books/` on Kindle, with category subfolders |
| Share files with Kindle native library when supported | `/mnt/us/documents/Books/` |
| Temporary incoming downloads | `/mnt/us/books/inbox/` |
| Manga/comics | `/mnt/us/books/manga/` |

Keep personal content out of `/mnt/us/koreader/`. That directory is for KOReader code, plugins, settings, patches, and runtime data.

Format caveat: KOReader can open EPUB directly. A side-loaded EPUB placed under `documents` may still be ignored by the native Kindle reader even though KOReader can open it.

## Transfer decision matrix

| Method | Best for | Requires leaving KOReader? | Notes |
|---|---|---:|---|
| OPDS | Discovering and directly downloading books | No | Best first option when the device has Wi-Fi and the user has no local library |
| Calibre wireless | Managed personal library and batch sends | No | Mac/PC and device should be on the same LAN |
| Cloud storage | Existing Dropbox/WebDAV/FTP workflow | No | Set a predictable download directory |
| SSH/SFTP | Direct file transfer and automation | No | Prefer keys; stop the server after use |
| USB | Initial setup, plugin install, large bulk copy | Often yes on Kindle | Safely eject before reopening KOReader |

## OPDS workflow

Typical KOReader route:

```text
File Browser
→ Search / magnifying glass
→ OPDS Catalog
→ Add catalog
```

Set downloads to a stable library folder such as `/mnt/us/books/` or `/mnt/us/books/inbox/`. If content does not appear, refresh the directory or restart KOReader; do not immediately rebuild or erase metadata.

When suggesting public catalogs, distinguish legal public-domain sources from unauthorized download sites.

## Calibre wireless workflow

1. Put Mac/PC and reader on the same trusted Wi-Fi.
2. In Calibre, start the wireless device connection from `Connect/Share`.
3. In KOReader, enable the Calibre plugin and connect as a wireless device.
4. Send selected books from Calibre.
5. Confirm the configured destination/template before a large batch.

A separate Calibre Content Server can also be exposed as an OPDS catalog, commonly using an `/opds` endpoint.

## Cloud storage workflow

KOReader supports suitable Dropbox, FTP, and WebDAV accounts through the File Browser's cloud storage menu. During first setup:

- use a dedicated book directory;
- verify download destination with one small file;
- avoid storing credentials in notes or chat output;
- prefer HTTPS/WebDAV over unencrypted internet-facing FTP.

Do not assume a commercial cloud drive has native KOReader support. Verify the current provider files under `plugins/cloudstorage.koplugin/providers/`; the inspected implementation exposed Dropbox, WebDAV, and FTP only.

### Bridging unsupported cloud drives

For services such as Quark or Baidu Netdisk, use a bridge only when the user wants direct browsing from KOReader:

```text
Cloud drive → OpenList/AList driver → WebDAV → KOReader Cloud storage+
```

Apply these rules:

1. Prefer an OpenList-specific read-only user rather than the cloud-drive account itself.
2. Restrict that user to the book directory and grant only WebDAV read/download permissions unless uploads are required.
3. Keep the bridge on a trusted LAN, NAS, or behind Tailscale/VPN; do not expose an unauthenticated WebDAV endpoint publicly.
4. Treat provider cookies, refresh tokens, and account credentials as secrets.
5. Test directory listing and one small EPUB before bulk use because third-party drivers can break when cloud APIs change.
6. Do not present dynamic Quark/Baidu share pages as a reliable direct-download method; JavaScript, CAPTCHA, temporary URLs, and anti-hotlinking commonly interfere.
7. Offer `cloud client → Mac → Calibre wireless/OPDS` as the lower-complexity fallback.

See `references/cloud-drive-bridge.md` for verified provider support, WebDAV endpoint shape, permissions, and Quark/Baidu topology.

## SSH/SFTP workflow

On supported devices, KOReader can start an SSH server from the network tools menu and display the device IP. On many builds the SFTP port is `2222`, but read the device's displayed information rather than assuming.

Security rules:

- operate only on a trusted LAN;
- prefer public-key authentication;
- do not expose the service to the public internet;
- stop the server after transfer;
- do not recommend permanent default credentials.

Upload books to the content directory, not the KOReader program directory.

## AI reading assistants

When the user asks for an “AI reading assistant,” do not assume there is only one project. Search GitHub with KOReader-specific terms and compare architecture, activity, configuration, and interaction with UI plugins.

Current reusable decision pattern:

- **KOAssistant**: default recommendation for a mature native KOReader AI assistant.
- **AIReadingAssistant**: Chinese-oriented direct plugin with configurable prompts and OpenAI-compatible providers; warn that its menu-cleaner changes the native selection menu.
- **Marginalia**: advanced plugin plus desktop bridge for whole-book indexing, position-bounded RAG, no-spoiler chat, Calibre, and Obsidian.

Install one overlapping AI plugin first, restart, and verify selection/dictionary behavior before combining it with UI modifications. AI plugins do not fix corrupt, DRM-protected, or malformed EPUB files.

See `references/ai-reading-plugins.md` for project links, observed maturity, install paths, and security notes.

## Troubleshooting order

Use this sequence:

1. Confirm device family and KOReader version.
2. Confirm the volume/path actually exists.
3. Verify archive extraction and `main.lua` path.
4. Check conflicting plugins and patches.
5. Restart KOReader and check Plugin management.
6. For missing books, navigate directly to the folder and refresh.
7. Confirm the file format is supported by KOReader.
8. Inspect KOReader logs before resetting state.

### EPUB opens unsuccessfully

KOReader supports normal DRM-free EPUB files, so do not treat “EPUB cannot open” as a folder-placement problem without evidence.

Gather evidence in this order:

1. Ask for the exact symptom: not listed, explicit error, hang/restart, or only one of several books failing.
2. Determine whether every EPUB fails or only a specific file.
3. If the device is mounted, copy the failing file to a safe local inspection directory; do not edit the only copy.
4. Validate that it is a ZIP-based EPUB, not an HTML/login page renamed `.epub`.
5. Test archive integrity and inspect `mimetype`, `META-INF/container.xml`, and the package document.
6. Check for DRM/encryption metadata and compare with a known-good public-domain EPUB.
7. Read KOReader crash/error logs and correlate timestamps before disabling unrelated plugins.
8. Repair or reconvert with Calibre only after identifying malformed packaging; do not claim conversion removes commercial DRM.

Do not suggest installing an AI plugin as a remedy for EPUB parsing failures.

## Pitfalls

### Reversing the replacement direction
When the user says “replace A with B,” restate the direction before giving destructive steps: **disable/remove A, install/enable B**. If wording is ambiguous, use reversible renaming first and keep the old plugin as `*.disabled` until the new one is verified.

### Treating GitHub source ZIP as the install package
Generated source archives may have an extra repository/version directory or omit release packaging. Use the explicit release asset.

### Mixing internal and USB-visible paths
`/mnt/us/...` and `/mnt/base-us/...` are device-side paths; macOS sees a mounted volume. Explain both views.

### Putting books under `koreader/`
This mixes user data with application files and complicates updates and backups. Use a top-level `books/` or `documents/Books/` directory.

### Assuming Kindle can start USB storage from KOReader
KOReader's built-in USB storage action is not uniformly supported on Kindle. Exiting to the native Kindle UI may be normal; recommend wireless transfer for frequent use.

### Recommending insecure SSH defaults
A temporary password on a trusted LAN is not a durable configuration. Prefer key authentication and shut down the service after transfer.

## Verification checklist

- [ ] Correct release asset downloaded
- [ ] Archive contains one top-level `*.koplugin` directory
- [ ] Final path ends in `plugins/<name>.koplugin/main.lua`
- [ ] Conflicting UI patches disabled
- [ ] KOReader restarted
- [ ] Plugin visible or enabled in Plugin management
- [ ] Books stored outside the KOReader program tree
- [ ] One downloaded/transferred book opens successfully
- [ ] Wireless services disabled after use when appropriate

## Support files

- See `references/kindle-zen-ui-and-book-transfer.md` for the Zen UI release inspection, Kindle path mapping, and KOReader transfer notes captured from authoritative sources.
- See `references/simpleui-koreader.md` for SimpleUI release/install details and version-specific notes.
- See `references/cloud-drive-bridge.md` for OpenList/AList WebDAV bridging of unsupported cloud drives such as Quark and Baidu Netdisk.
- See `references/ai-reading-plugins.md` for KOAssistant, AIReadingAssistant, and Marginalia comparisons, install paths, and security caveats.
- See `references/dictionaries.md` for KOReader's built-in dictionary downloader, English dictionary choices, StarDict manual installation, and old-device performance guidance.
