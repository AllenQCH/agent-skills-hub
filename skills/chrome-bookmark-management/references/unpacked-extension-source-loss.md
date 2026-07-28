# Unpacked Chrome Extension Source Path Loss

Use this reference when a locally loaded Chrome extension appears to be “missing” after earlier working.

## Pattern

Chrome extensions loaded through **Load unpacked** are not copied into Chrome’s normal `Extensions/<id>/<version>/` tree. Chrome keeps a reference to the original source folder in the profile’s `Secure Preferences` under `extensions.settings.<extensionId>.path`.

If that folder is later deleted, moved, or lived under a temporary location such as `~/Downloads`, Chrome may still remember the extension ID/settings but cannot load the extension UI.

## Diagnosis

1. Inspect Chrome profiles:
   - `~/Library/Application Support/Google/Chrome/Default/Secure Preferences`
   - other profiles such as `Profile 2` when the visible browser profile differs.
2. Look for the extension ID or expected name/path under `extensions.settings`.
3. Check whether the recorded `path` still exists and contains `manifest.json`.
4. Check extension-private storage before declaring data lost:
   - `Local Extension Settings/<extensionId>/`
   - `Local Storage/leveldb`
   - extension-specific keys such as `bookmarks:v2`.

## Recovery

- Prefer restoring/recreating the source folder in a stable location, for example under `~/Applications/<extension-name>/`, not `~/Downloads`.
- Reload the extension from `chrome://extensions` using **Load unpacked**.
- If the extension ID changes, migrate extension-private storage only after verifying the data format and backing up the profile files.
- When the extension stores its own bookmark data (for example a bundled `bookmarks.json` or `chrome.storage.local` key), do not treat Chrome’s `Bookmarks` file as the source of truth.

## Reporting to Allen

State the distinction clearly:

```text
Chrome still remembers the extension, but the unpacked source directory it points to no longer exists. The plugin was not overwritten by another extension; it cannot load because its local folder is gone. Its private data may still be recoverable from extension storage.
```
