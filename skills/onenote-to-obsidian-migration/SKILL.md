---
name: onenote-to-obsidian-migration
description: 'Use when the user needs the onenote to obsidian migration workflow: Migrate OneNote content into Obsidian on macOS with a practical decision tree: prefer Obsidian Importer via Microsoft sign-in, fall back to Windows exporter for high-fidelity bulk migration, and treat local .one backup conversion as experimental. Do not use for tasks that do not read, write, migrate, or curate durable notes.'
version: 1.0.0
author: Hermes Agent
license: MIT
---

# OneNote → Obsidian Migration

Use when the user wants to move OneNote notes into Obsidian, especially on macOS.

## What we learned

There are **three different routes**, and they are not interchangeable:

1. **Obsidian official Importer plugin**
   - This is the best first choice.
   - It imports OneNote via **Microsoft account sign-in / Graph API**.
   - It is **not** a direct local `.one` file importer.
   - It only supports notebooks owned by the user's personal account.

2. **Windows `onenote-md-exporter` route**
   - Best for high-fidelity, bulk migration.
   - Preserves hierarchy and more structure.
   - Requires Windows + supported OneNote/Word setup.

3. **Local `.one` conversion route**
   - Tools like `one2html` + `onenote-to-obsidian` may work on some files.
   - On macOS OneNote backup files, this can fail with malformed FSSHTTPB / parser errors.
   - Fallback `strings` extraction can produce huge garbage markdown and is not acceptable as a real migration result.
   - Treat this path as experimental / sample-only unless verified on the user’s files.

## macOS-specific findings

On macOS, local OneNote backups may exist under:

```text
~/Library/Containers/com.microsoft.onenote.mac/Data/Library/Application Support/Microsoft User Data/OneNote/15.0/备份/
```

In one real machine, this path contained notebook-like backup folders such as:
- `呈辉 的笔记本`
- `喜茶`
- `samsung`
- `神马`

You can search for `.one` files there, but **do not assume** official Obsidian Importer can use those paths directly.

### Important real-world finding about macOS backups

A large section backup such as `AI_related.one (于 2026-4-19).one` can fail both ways:

1. `one2html` may fail with malformed FSSHTTPB / object header parsing errors.
2. `onenote-to-obsidian` may fall back to `strings` extraction and generate a giant unreadable markdown file.

Treat any successful file discovery in the backup folder as **source availability only**, not proof that local conversion is viable.

## Recommended workflow

### Path A — Preferred: Official Obsidian Importer

1. Confirm Obsidian and OneNote are installed.
2. Check whether the vault is actually opening normally before doing any plugin work.
3. Install/enable the **community plugin** `obsidian-importer`.
   - Important: OneNote import uses the **community plugin**, not just the core `markdown-importer` toggle.
4. Open Importer.
5. Choose **Microsoft OneNote** as file format.
6. Sign in with Microsoft account.
7. Select notebook/sections.
8. Import into a test folder first.
9. Verify hierarchy, images, attachments, links, dates, and checkboxes.

### Path B — If official importer quality is poor or needs bulk/high fidelity

Use `alxnbl/onenote-md-exporter` on Windows.

Use this when:
- The user has many notebooks.
- Attachments / structure fidelity matters.
- Official importer is incomplete.

### Path C — Local `.one` conversion sample only

Only use when:
- The user explicitly wants to test local `.one` backups.
- Official importer is unavailable.
- A sample conversion is acceptable.

Steps:
1. Install Rust/Cargo if needed.
2. Install `one2html`.
   - If stable Rust fails on feature gating, try:
     ```bash
     RUSTC_BOOTSTRAP=1 cargo install one2html
     ```
3. Clone/install the `onenote-to-obsidian` converter.
4. Run against a **small sample `.one` file first**, not a giant notebook section.
5. Inspect output carefully.
6. If output is mostly binary noise / garbage, abort this route.

## Concrete failure pattern to recognize

If `one2html` reports errors like malformed FSSHTTPB/object header problems, or conversion falls back to `strings` extraction and produces:
- giant markdown files,
- thousands of lines of garbage,
- mostly unreadable binary-like text,

then **do not continue bulk migration with that route**.

## Obsidian plugin notes

### Important distinction
- `markdown-importer` in `.obsidian/core-plugins.json` is **not sufficient** for OneNote import.
- Official OneNote import requires community plugin:
  - `obsidian-importer`

### Manual plugin install fallback

If GUI/plugin browser is unstable, you can manually install the plugin into the vault.

For example, the plugin assets can be fetched from the GitHub release page for `obsidianmd/obsidian-importer` and placed into:

```text
<VAULT>/.obsidian/plugins/obsidian-importer/
  manifest.json
  main.js
  styles.css
```

Then create/update:

```json
// <VAULT>/.obsidian/community-plugins.json
[
  "obsidian-importer"
]
```

Real finding: after manual install, `workspace.json` may show the ribbon command key:

```text
obsidian-importer:Open Importer
```

and the plugin command found in `main.js` is:

```text
id: open-modal
name: Open importer
```

So if the GUI is healthy, the importer can be opened either from the ribbon icon or by searching command palette for **Open importer**.

But if Obsidian is white-screening or failing to render, prefer asking the user to manually stabilize/open the app before continuing GUI automation.

## Verification checklist

Always verify on a sample import:
- notebook / section hierarchy
- page titles
- created / updated timestamps
- images
- attachments
- internal links
- checkboxes / tasks
- tables / rich text degradation

## Practical advice

- Start with a **small notebook or section**, not the largest AI notebook.
- Prefer official importer first.
- Use Windows exporter for serious production migration.
- Treat local `.one` parsing on macOS as best-effort only.
- If GUI automation gets stuck on trust dialogs, welcome screens, or white screens, pause and ask the user to perform the minimal interactive step (open vault, sign in), then resume.

### Device-code fallback for Microsoft sign-in

If the official importer GUI is installed but Obsidian is unstable/white-screening, there is a reusable backup tactic:

1. Use a public Microsoft client that supports device code flow (for example the Azure CLI public client) to request Graph scopes.
2. Open `https://login.microsoft.com/device` for the user.
3. Ask the user to enter the generated code and sign in.
4. Poll the token endpoint in the background until authorization completes.
5. Once a Graph token is available, continue by listing notebooks/sections via Microsoft Graph.

Important lesson: the client ID embedded in the Importer plugin may not support device-code flow directly, so use a known public client for this fallback rather than assuming the plugin's own client ID will work.

## When to stop

Stop and report clearly if:
- the importer requires Microsoft sign-in and the session cannot complete OAuth without user interaction,
- Obsidian GUI is unstable/white-screening,
- local `.one` conversion outputs garbage.

At that point, recommend the next best route rather than continuing to brute-force.