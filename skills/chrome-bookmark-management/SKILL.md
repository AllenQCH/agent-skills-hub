---
name: chrome-bookmark-management
description: Use when managing Chrome bookmarks or making bookmark-like data visible to bookmark-reading extensions/plugins on macOS. Do not use for tasks outside the named productivity app, document, spreadsheet, meeting, or workflow scope.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
    - chrome
    - bookmarks
    - browser
    - extensions
    - macos
    related_skills:
    - opencli-browser-webapp-exploration
    - obsidian
---

# Chrome Bookmark Management

## Overview

Use this skill when the user wants links added, moved, organized, or made visible inside Chrome bookmarks — especially when a Chrome extension or internal plugin appears to read bookmark data from a specific Chrome profile.

This skill is for **bookmark data management**, not general browser automation.

## When to Use

Use this skill when the user asks for things like:
- “把这个地址加入 Chrome 书签”
- “加到某个书签插件里”
- “整理书签栏 / 文件夹结构”
- “确认某个链接是否已经在书签里”
- “为什么插件里看不到这个书签”

Do not use it for:
- normal page interaction or form filling
- web scraping
- extension UI clicking without any bookmark data need

## Core Idea

Chrome bookmark-related data may live in more than one place:
- local profile bookmarks (for example `Default/Bookmarks`)
- account/synced bookmarks (for example `Default/AccountBookmarks`)
- extension-specific storage, if the extension has its own database

A practical pattern on macOS is:
1. locate the relevant Chrome profile and bookmark files
2. check whether the target URLs already exist in account bookmarks
3. determine whether the extension/plugin likely reads local bookmarks instead of account bookmarks
4. if needed, back up `Bookmarks` and backfill the local bookmark tree so bookmark-reading plugins can see the entries
5. verify the exact folder path and advise a Chrome restart if the browser is already open

## Standard Workflow

1. **Locate the Chrome profile files**
   - inspect profiles such as `Default`, `Profile 1`, `Profile 2`
   - common files: `Bookmarks`, `AccountBookmarks`, `Preferences`

2. **Confirm whether the extension is real and where it lives**
   - inspect installed extension manifests under the profile’s `Extensions/`
   - if the named plugin cannot be confidently mapped to an extension data directory, do not claim you edited plugin-private storage

3. **Search existing bookmark data first**
   - look for the target URLs and likely folder names in both local and account bookmark files
   - prefer updating an existing folder path rather than creating a random new top-level folder

4. **If local backfill is needed, back up first**
   - create a backup of the profile’s `Bookmarks` file before editing
   - preserve folder structure where possible

5. **Write deterministic bookmark entries**
   - add the desired folder path and URLs
   - keep human-readable names
   - avoid duplicate URL spam when the same entry already exists

6. **Verify by reading the resulting bookmark tree**
   - confirm exact folder path and final URLs

7. **If Chrome is open, warn about refresh behavior**
   - some changes may not show up until Chrome restarts or re-syncs

## Common Pitfalls

1. **Assuming the plugin has its own storage without checking**
   - First confirm whether the plugin is actually installed and identifiable from `Extensions/`.
   - If the extension source is available, inspect its JS for `chrome.storage.local`, a storage key (for example `bookmarks:v2`), or `fetch(chrome.runtime.getURL("bookmarks.json"))` before deciding whether Chrome bookmarks matter at all.
   - See `references/extension-private-bookmark-storage.md` for the extension-private bookmark-store pattern and reset workflow.

2. **Editing only synced/account bookmarks**
   - Some bookmark readers/plugins may surface the local `Bookmarks` tree instead. If the entries already exist in `AccountBookmarks` but are not visible where the user expects, backfilling local `Bookmarks` may be the compatibility fix.

3. **Skipping backup**
   - Always back up `Bookmarks` before direct JSON edits.

4. **Claiming success without verifying the written folder path**
   - Read back the final tree and report the exact path, for example `书签栏 / 订货通 / xxl-job`.

5. **Forgetting that Chrome may be open**
   - When Chrome is running, tell the user a restart may be needed before the UI or plugin refreshes.

## Support Files

- `references/chrome-bookmark-files.md` — common Chrome bookmark file locations and the account-vs-local backfill pattern.
- `references/unpacked-extension-source-loss.md` — how to diagnose/recover locally loaded unpacked extensions whose source directory was deleted or moved, while preserving extension-private data.

## Verification Checklist

- [ ] Correct Chrome profile identified
- [ ] Existing bookmark/account bookmark data checked first
- [ ] `Bookmarks` backup created before editing
- [ ] Desired folder path and URLs written or confirmed present
- [ ] Final bookmark tree read back and reported
- [ ] User warned if Chrome is currently open and may need restart
