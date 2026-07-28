# Kindle + Zen UI + KOReader transfer reference

Captured from the 2026-07-15 investigation. Treat release numbers and UI labels as version-specific; re-check upstream before future installation.

## Zen UI upstream

Repository: `https://github.com/AnthonyGress/zen_ui.koplugin`

At inspection time:

- latest release: `v2.4.4`;
- install asset: `zen_ui.koplugin.zip`;
- direct asset URL: `https://github.com/AnthonyGress/zen_ui.koplugin/releases/download/v2.4.4/zen_ui.koplugin.zip`;
- inspected archive size: about 914 KiB;
- inspected SHA-256: `bdf0ebd7f8c40bc521fb8782d1d4bc044eec334cffca32a68870043bcc98bb23`;
- archive had one top-level `zen_ui.koplugin` folder;
- both `zen_ui.koplugin/main.lua` and `_meta.lua` were present.

Upstream installation summary:

1. KOReader must already be installed.
2. Download the named release asset, not the GitHub source archive.
3. Extract it.
4. Copy `zen_ui.koplugin` to the device plugin directory.
5. On Kindle the upstream path is `/mnt/base-us/koreader/plugins/`; from a USB-mounted Mac volume this is the root-level `koreader/plugins/` folder.
6. Final path must be `.../plugins/zen_ui.koplugin/main.lua`.
7. Restart KOReader; if necessary enable Zen UI from `Tools → More tools → Plugin management → Zen UI`.

Known UI conflicts named upstream:

- Simple UI;
- Project: Title / `projecttitle.koplugin`;
- VOS;
- other patches that replace Cover Browser, navigation, menus, or status bars.

Prefer reversible disablement, for example:

```text
projecttitle.koplugin
→ projecttitle.koplugin.disabled
```

## Zen UI download-folder behavior

Inspection of the release showed its OPDS patch resolves the download folder in this order:

```text
sync_dir when synchronizing
→ KOReader download_dir
→ KOReader lastdir
→ Device.home_dir
→ /
```

Set `download_dir` explicitly if predictable storage matters.

## Official KOReader transfer findings

Official user guide: `https://koreader.rocks/user_guide/`

The guide lists these transfer options:

- USB mass storage;
- cloud storage using Dropbox/FTP/WebDAV;
- KOReader acting as an SSH/SFTP server;
- Calibre wireless transfer;
- News downloader;
- Wallabag retrieval.

Important Kindle distinction: the user guide describes KOReader's own USB mass-storage action as available for Kobo and some Cervantes devices, while SSH/SFTP is available on Kindle. Therefore needing to leave KOReader for Kindle's native USB mode is expected on many Kindle setups, not necessarily a malfunction.

The guide also notes that transferred documents may require a KOReader restart or directory refresh to be indexed/displayed.

## OPDS

Official wiki: `https://github.com/koreader/koreader/wiki/OPDS-support`

OPDS lets the File Manager browse public or custom catalogs and download ebooks. Typical route:

```text
Search / magnifying glass
→ OPDS Catalog
→ top-left add button
```

For a local Calibre Content Server, the wiki example uses an endpoint like:

```text
http://<mac-or-pc-lan-ip>:8080/opds
```

Verify the live address and port shown by Calibre rather than assuming `8080`.

## Calibre wireless

Official wiki: `https://github.com/koreader/koreader/wiki/calibre`

- Mac/PC and KOReader device must normally share the same LAN.
- Start Calibre's wireless device connection under `Connect/Share`.
- Connect KOReader through the Calibre plugin.
- Calibre should recognize KOReader as a wireless device and can send selected books.

## SSH/SFTP

Official wiki: `https://github.com/koreader/koreader/wiki/SSH`

- Supported on Kindle, Kobo, Cervantes, and PocketBook.
- KOReader menu location is under the Tools/cog network menu.
- Starting the server displays connection information including the device IP.
- The documented SFTP port is commonly `2222`.
- The wiki shows a simple `root` login workflow, but also explicitly warns against leaving the Kindle SSH server unsecured.

For durable use, configure public-key authentication, restrict use to a trusted LAN, and stop the server after transfer.

## Folder recommendation for Kindle

Use one of these conventions:

```text
/mnt/us/books/                # KOReader-first, clean separation
/mnt/us/books/inbox/          # incoming wireless downloads
/mnt/us/books/manga/          # comics/manga
/mnt/us/documents/Books/      # when native Kindle visibility is also desired
```

Do not place personal books under `/mnt/us/koreader/`. That tree is application code and configuration.

A side-loaded EPUB can be opened by KOReader but may not appear in the native Kindle library merely because it was copied under `documents`.
