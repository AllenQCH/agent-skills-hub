# LanguageBreak on Kindle Paperwhite 3 (5.16.2.1.1)

## Device/session facts

- Device shown: Kindle Paperwhite, 7th generation (PW3).
- Firmware shown: `Kindle 5.16.2.1.1`.
- This is the maximum firmware supported by the LanguageBreak method described by the upstream README and BookFere guide; do not update beyond it after jailbreak.
- The user used a Mac and needed an explicit USB/disconnected timeline.

## Source links

- Upstream project: https://github.com/notmarek/LanguageBreak
- Upstream README: https://raw.githubusercontent.com/notmarek/LanguageBreak/master/README.MD
- MobileRead tutorial: https://www.mobileread.com/forums/showthread.php?t=356872
- Chinese guide used for labels and recovery: https://bookfere.com/post/1075.html

## Normal flow distilled

1. Back up `documents/`; remove pending OTA `.bin`/`update.bin.tmp.partial`; remove password; enable Airplane Mode.
2. While disconnected from USB, manually enter ASCII `;enter_demo`, press Enter, then explicitly reboot.
3. Skip Wi-Fi, fill demo registration with arbitrary values, choose `Skip → Standard → Done`.
4. During/after setup, bypass `CONFIGURE DEVICE` or “demonstration device is missing content/network” using the lower-right two-finger/left-swipe gesture.
5. From the library/home screen, manually type ASCII `;demo`; do not select command history.
6. Confirm `Demo Menu` with `Sideload Content` and `Resell Device`.
7. Select `Sideload Content`, connect USB, copy the release's `LanguageBreak` folder contents to the Kindle root, safely eject, and unplug.
8. Return to Demo Menu, select `Resell Device → Resell`; at the “press power button” screen, immediately reconnect USB and copy the same payload again; safely eject, unplug, then press the power button.
9. Select `简体中文` followed by the next/continue button; wait for jailbreak logs.
10. Apply the matching `update_hotfix_languagebreak-<locale>.bin` from the release, then verify normal mode and expected jailbreak files.

## Key state interpretations

- `;enter_demo` normally has no immediate visible result; reboot is required.
- `;demo` is not expected to work until Demo setup is complete.
- Grey Settings/Wi-Fi on a welcome-looking screen indicates Demo/Managed residue, not proof that setup is complete.
- A real full Demo confirmation is a `Demo Menu` containing `Sideload Content` and `Resell Device`.
- `Demo Menu → Exit` closes the menu; it is not necessarily a Demo-mode exit.
- After a successful trigger, log text and hotfix installation are required before claiming jailbreak success.

## Failure reproduced in the session

After `Standard → Done`, the device showed:

- `Application Error — The selected application could not be started. Please try again.`
- then `Collecting Debug Info — Generating Core Dump file for process KPPMainAppV2`.

Treat this as a Demo application crash and failed setup, not as a jailbreak success. Do not click `RAISE A BUG` and do not continue copying the exploit payload from that state.

## Recovery sequence used/recommended

1. Close the dialog; reboot once (long power hold if the UI is unresponsive).
2. If `;demo` opens the full Demo Menu, do not continue the exploit. Choose `Sideload Content` only to enable USB recovery.
3. Connect the Mac and create an empty, extensionless root-level marker named exactly `DO_FACTORY_RESTORE`.
4. Safely eject, unplug, and hold the power button until the Kindle resets.
5. If normal Settings are available instead, use the standard device reset.
6. Reinstall the same official PW3 firmware `5.16.2.1.1` if the guide calls for a clean retry, then restart from the beginning.

Example macOS command after discovering the mounted volume name:

```bash
touch "/Volumes/Kindle/DO_FACTORY_RESTORE"
```

Replace `Kindle` with the actual mounted volume name. Verify that Finder did not append `.txt`; the marker is destructive and erases user data.

## Source-specific caution

The BookFere article's copy list contains a likely typography inconsistency (`document` vs the upstream release's `documents`); follow the actual release archive structure and upstream README, preserving the folder/file names from the downloaded artifact.

## Later KOReader/SimpleUI dependency

SimpleUI is a KOReader plugin, not a native Kindle plugin. Install it only after jailbreak and KOReader are working. Official repository found during the session:

- https://github.com/doctorhetfield-cmd/simpleui.koplugin
- releases: https://github.com/doctorhetfield-cmd/simpleui.koplugin/releases
- latest release observed: `SimpleUI v2.1.0`, asset `simpleui.koplugin.zip`

Kindle KOReader plugin destination:

```text
/koreader/plugins/simpleui.koplugin/
```

The plugin folder must not be double nested. For a video-matching older UI, the upstream `v1.5.0` release may be closer than v2.x; verify compatibility with the installed KOReader build.
