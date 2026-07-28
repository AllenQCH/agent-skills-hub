# Extensions that do NOT read Chrome Bookmarks

Use this note when the user says a link was added to Chrome bookmarks but a bookmark-like extension/plugin still does not show it.

## Core lesson

Some Chrome extensions do **not** read the profile `Bookmarks` / `AccountBookmarks` trees at all. They may instead:
- seed defaults from a bundled file like `bookmarks.json`
- copy those defaults into `chrome.storage.local`
- keep showing the extension-local dataset even after Chrome bookmarks change

## Practical detection pattern

1. Confirm the extension is real from `chrome://extensions/` or the profile’s extension dirs.
2. Inspect the extension source if available (common on macOS for unpacked/internal extensions kept under Downloads or a work folder).
3. Search the extension JS for:
   - `chrome.storage.local`
   - a storage key like `bookmarks:v2`
   - `fetch(chrome.runtime.getURL("bookmarks.json"))`
4. If found, treat the extension as a **private bookmark store**, not a Chrome-bookmark consumer.

## Useful local paths on macOS

- Chrome local bookmarks: `~/Library/Application Support/Google/Chrome/<Profile>/Bookmarks`
- Chrome synced/account bookmarks: `~/Library/Application Support/Google/Chrome/<Profile>/AccountBookmarks`
- Extension local storage (LevelDB):
  `~/Library/Application Support/Google/Chrome/<Profile>/Local Extension Settings/<extension_id>/`

## Repair pattern

When the extension seeds from bundled JSON into local storage:

1. Back up both:
   - the extension source `bookmarks.json`
   - the extension’s `Local Extension Settings/<extension_id>/`
2. Update the bundled `bookmarks.json` with the desired URLs/names.
3. Clear the extension’s old local storage directory so the extension rehydrates from the updated defaults on next load.
4. Reload the extension from `chrome://extensions/` or restart Chrome.

## Example class of fix

A side-panel bookmark extension may show “no tasks found” even though Chrome bookmarks were updated, because:
- the extension data comes from its own `bookmarks.json`
- the old `chrome.storage.local` cache still points at stale root URLs
- the fix is to update the extension dataset itself and clear the cached LevelDB

## Warning

Do not claim you changed plugin-private data unless you verified the extension’s actual storage path or source behavior.
