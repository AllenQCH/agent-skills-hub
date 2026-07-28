---
name: kindle-jailbreak-recovery
description: 'Use when the user needs the kindle jailbreak recovery workflow: Safely identify Kindle firmware/device state, run software-jailbreak workflows, recover from Demo/Managed mode failures, apply persistence hotfixes, and verify readiness for KUAL/KOReader. Do not use for tasks outside the named productivity app, document, spreadsheet, meeting, or workflow scope.'
license: MIT
metadata:
  hermes:
    tags:
    - kindle
    - jailbreak
    - languagebreak
    - demo-mode
    - recovery
    - hotfix
    - koreader
---

# Kindle Jailbreak and Recovery

Use this skill when a user wants to jailbreak a Kindle, is stuck in Demo/Managed mode, sees disabled settings, encounters a blank screen or debug/core-dump dialog, needs to recover safely, or wants to prepare the device for KUAL/KOReader.

## Safety boundary

Treat the Kindle as user-owned hardware. Prefer reversible diagnosis before factory reset. Clearly warn when a step deletes books, annotations, registration state, or user files.

Never infer success from one visual symptom. Distinguish:

- exploit eligibility;
- Demo-mode entry;
- exploit execution;
- hotfix persistence;
- normal-mode restoration;
- KUAL/KOReader readiness.

## Authoritative-source order

1. Current jailbreak project's README and release assets.
2. MobileRead's maintained tutorial/thread and device-specific reports.
3. Reputable localized guides such as BookFere for Chinese UI labels.
4. Videos only as visual supplements.

Re-check upstream before prescribing commands because supported firmware ceilings and recovery steps change.

## Preflight

Before changing modes:

1. Identify exact Kindle model/generation and firmware.
2. Confirm the jailbreak explicitly supports that exact firmware.
3. Enable Airplane Mode and prevent automatic updates.
4. Remove the lock-screen password.
5. Back up the USB-visible user storage, especially `documents/`.
6. Remove pending OTA files such as unknown update `.bin` files and `update.bin.tmp.partial` when the jailbreak documentation requires it.
7. Download the named release artifact, not an arbitrary mirror or GitHub generated source archive.
8. Explain which steps require USB and which require the Kindle UI.

Do not expose serial numbers or MAC addresses in shared screenshots; advise redaction.

## State model

| State | Strong indicators | Meaning |
|---|---|---|
| Normal/unregistered | Welcome page; Settings usable | Consumer mode, possibly factory-reset |
| Demo entry pending | `;enter_demo` accepted, then reboot required | No immediate UI response is expected |
| Demo setup | Registration demo form; `Standard`; content setup | Demo transition in progress |
| Full Demo mode | `;demo` opens `Demo Menu` with `Sideload Content` and `Resell Device` | Demo services are active |
| Managed residue | Normal-looking welcome/library UI but Settings/Wi-Fi are greyed | Demo/management flags remain |
| Exploit executed | Language selection trigger followed by jailbreak log output | Payload ran, persistence not yet proven |
| Persistent jailbreak | Hotfix installs; `mkk` exists; jailbreak verification command works | Ready for KUAL/KOReader setup |

Use the strongest available indicator. Grey Settings alone suggests Managed/Demo residue but does not prove a complete Demo setup.

## Search-command rules

Kindle diagnostic commands typically produce no ordinary search result. Make these input checks explicit:

- use the English half-width semicolon `;`, not Chinese `；`;
- do not type a backslash before `_`;
- manually retype the command using the Kindle virtual keyboard instead of selecting search history;
- press the keyboard's Enter/Search key;
- do not expect `;enter_demo` to open a page immediately—reboot is the activation step;
- `;demo` is meaningful only after Demo services are active.

Common commands must be sourced from the active jailbreak documentation. For LanguageBreak-era workflows these include `;enter_demo`, `;demo`, `;uzb`, and `;dsts`.

## USB choreography

State explicitly whether USB should be connected:

- Kindle UI commands and Demo menu actions: disconnected.
- File copy or recovery-marker creation: connected only after USB/Sideload mode is enabled.
- Always safely eject before returning to Kindle UI actions.
- During time-sensitive `Resell Device` flows, copy the payload only at the documented screen/window, then eject before pressing power.

Avoid vague advice like “connect it during the process”; provide a numbered connection timeline.

## Demo-mode troubleshooting

### Secret gesture

After Demo setup, a screen may say `CONFIGURE DEVICE` or that the demonstration device has no content/network. The gesture is intended to bypass that screen into the library/home UI, where `;demo` can open the Demo menu.

Common gesture variants:

1. two-finger tap at the lower-right, immediately followed by a right-to-left swipe;
2. hold two fingers at the lower-right, lift the right finger, slide the left finger left;
3. hold two fingers and slide both left.

The expected destination is the library/home screen with the global search bar—not the language chooser, Wi-Fi wizard, or registration form.

### Blank screen

A short blank e-ink interval can be normal during setup or reboot. Diagnose by stage before forcing a restart:

- during initial Demo configuration: wait several minutes, try wake and the secret gesture;
- during exploit/log execution or firmware/hotfix update: wait longer and avoid interruption;
- if still unresponsive, check power LED and USB enumeration before a hard restart;
- do not repeatedly reboot during a documented time-sensitive payload-copy window.

### Application Error / Collecting Debug Info

An `Application Error` for `KPPMainAppV2` followed by `Collecting Debug Info` indicates the Demo application crashed; it is not a successful jailbreak signal.

1. Do not choose `Raise a Bug` or continue copying the exploit payload.
2. Allow dump collection to finish, close the dialog, and reboot once.
3. If `;demo` opens the Demo menu, use recovery mode rather than continuing the exploit.
4. Factory-reset and reinstall the same supported firmware before retrying when the maintained guide requires a clean state.

## Exiting or recovering Demo/Managed mode

The `Exit` button in `Demo Menu` generally exits the menu, not Demo mode.

Preferred recovery order:

1. Reboot once and manually retry `;demo`.
2. If a documented two-button restoration prompt appears, follow the current guide's exact button semantics.
3. If the full Demo menu appears, use `Sideload Content` to enable USB, then create the documented factory-reset marker.
4. Safely eject and perform the documented power-button restart.
5. If normal Settings are available, use the standard factory reset instead.

For Kindle factory recovery, a commonly documented marker is an empty root-level file named exactly:

```text
DO_FACTORY_RESTORE
```

It must not be a folder and must not acquire a `.txt` extension. Treat this as destructive: it erases user data.

On macOS, do not assume the volume is named `Kindle`; discover the mounted volume. An example only:

```bash
touch "/Volumes/Kindle/DO_FACTORY_RESTORE"
```

If a password screen blocks recovery, use a vendor-documented reset code only in that password field and warn that it wipes the device.

## Clean retry

After a failed attempt:

1. Restore normal mode/factory-reset state.
2. Reinstall the exact same supported official firmware if the maintained guide recommends it.
3. Verify firmware did not update beyond the exploit ceiling.
4. Re-enable Airplane Mode and remove passwords.
5. Re-download/verify the jailbreak release artifact.
6. Start from the first step rather than resuming midway.

Never recommend installing a newer firmware merely to recover if it would close the jailbreak path.

## Persistence and completion

Do not declare success immediately after log text appears. Complete the project-specific persistence/hotfix step, exit Demo/Managed mode, then verify:

- normal Settings and radios work;
- expected jailbreak directories such as `mkk` exist when applicable;
- project verification commands behave as documented;
- hotfix may need a second installation on some device generations if persistence directories are absent;
- only then proceed with MRPI, KUAL, or KOReader.

## Response format for live troubleshooting

Use Allen's troubleshooting structure:

1. `## 当前判断`
2. `## 已确认事实`
3. `## 根因/可能原因`
4. `## 下一步`

Give one immediate action sequence, then conditional branches. Avoid repeatedly restating the full jailbreak tutorial when the user is asking about one current screen.

## Pitfalls

- Treating “no response” after `;enter_demo` as failure instead of rebooting.
- Testing `;demo` before Demo setup is complete.
- Confusing Chinese `；` with ASCII `;`.
- Treating grey Settings as proof of a fully initialized Demo mode.
- Treating `Demo Menu → Exit` as a Demo-mode exit.
- Continuing after a core-dump/debug dialog.
- Factory-resetting before backing up user content.
- Copying release folders with an extra nesting level.
- Skipping the persistence hotfix and later losing jailbreak state.
- Suggesting KOReader plugins before the jailbreak and KOReader prerequisites are complete.

## Verification checklist

- [ ] Exact model and firmware confirmed
- [ ] Firmware is within the current exploit's supported range
- [ ] User data backed up
- [ ] Password removed and Airplane Mode enabled
- [ ] Demo state confirmed with strong indicators
- [ ] Error/debug dialogs handled as failure states, not success
- [ ] Recovery actions clearly marked destructive or non-destructive
- [ ] Hotfix/persistence completed
- [ ] Normal device functions restored
- [ ] Jailbreak verified before KUAL/KOReader installation

## Support files

- See `references/languagebreak-pw3-5.16.2.1.1.md` for the PW3/LanguageBreak state transitions, known failure screen, recovery sequence, and source links captured during a real troubleshooting session.
