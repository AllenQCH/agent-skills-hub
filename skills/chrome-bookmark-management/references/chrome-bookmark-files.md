# Chrome bookmark files on macOS

## Common locations

Under:
- `~/Library/Application Support/Google/Chrome/`

Typical per-profile files:
- `Default/Bookmarks`
- `Default/AccountBookmarks`
- `Default/Preferences`
- `Profile 2/Bookmarks` (if present)
- `Profile 2/AccountBookmarks`
- `Profile 2/Preferences`

## Practical distinction

### `Bookmarks`
Local profile bookmark tree.
Some bookmark-reading tools or extensions surface this tree directly.

### `AccountBookmarks`
Account/synced bookmark tree.
A target URL may already exist here even if it does not appear in the local `Bookmarks` file.

## Recommended compatibility pattern

When the user says a bookmark should appear in a plugin/extension but the plugin data source is unclear:

1. Inspect installed extensions first.
2. Search both `Bookmarks` and `AccountBookmarks`.
3. If the URL already exists in `AccountBookmarks` but not in `Bookmarks`, and the plugin likely reads local bookmarks, backfill the same URL into `Bookmarks`.
4. Preserve or reuse an existing folder path if possible.
5. Back up the original `Bookmarks` file before writing.
6. Read back the final tree and tell the user the exact folder path.
7. If Chrome is open, remind the user a restart may be required.

## Example session pattern

A practical case was:
- target links already existed in `Default/AccountBookmarks`
- plugin-specific storage could not be confidently identified
- local `Default/Bookmarks` was nearly empty
- adding the same entries to `Default/Bookmarks` under the intended folder path was the safest compatibility move

This is a good default fallback when the real plugin storage is uncertain but the user’s goal is simply “make it show up in Chrome/plugin bookmarks.”
