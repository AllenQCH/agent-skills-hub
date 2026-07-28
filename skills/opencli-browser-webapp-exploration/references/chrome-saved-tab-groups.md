# Chrome: `OpenCLI Browser` items on the bookmarks bar may be Saved Tab Groups, not bookmarks

## When to suspect this
- The user sees multiple repeated `OpenCLI Browser` items on the bookmarks bar.
- Chrome bookmark data (`Bookmarks`, `AccountBookmarks`) does not contain matching bookmark entries.
- The visual UI looks like rounded tab-group pills/buttons rather than normal bookmark labels.

## Fast verification workflow
1. Check Chrome bookmark data first:
   - `~/Library/Application Support/Google/Chrome/Default/Bookmarks`
   - `~/Library/Application Support/Google/Chrome/Default/AccountBookmarks`
2. If `OpenCLI Browser` is not present there, inspect the OpenCLI extension bundle under Chrome profile `Extensions/`.
3. Search the extension code for tab-group related terms such as:
   - `CONTAINER_TAB_GROUP_TITLE`
   - `chrome.tabGroups`
   - `tabGroups.update`
   - `groupId`
4. If the extension uses a constant/title like `OpenCLI Browser` while creating or updating tab groups, treat the visible items as Saved Tab Groups shown in the bookmarks bar area, not ordinary bookmarks.

## Session-specific evidence that proved the pattern
- `Bookmarks` bookmark-bar children were empty.
- `AccountBookmarks` contained normal bookmarks/folders like `ChatGPT`, `我的`, `工作`, but not `OpenCLI Browser`.
- OpenCLI Chrome extension background script contained tab-group logic and `OpenCLI Browser` title usage.

## User-facing explanation
Explain that these entries are most likely Chrome Saved Tab Groups created or reused by the OpenCLI browser workflow. They can appear in the bookmarks-bar region, so users often mistake them for duplicated bookmarks.

## Cleanup guidance
- Right-click each `OpenCLI Browser` pill/item and remove it if it is a saved tab group.
- Or open Chrome tab groups / bookmarks-bar saved groups UI and delete stale saved groups.
- If OpenCLI keeps recreating them, inspect the extension behavior before deleting repeatedly.
