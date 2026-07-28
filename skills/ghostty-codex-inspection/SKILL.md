---
name: ghostty-codex-inspection
description: 'Use when the user needs the ghostty codex inspection workflow: On macOS, inspect what Ghostty is doing — especially Codex CLI sessions — by combining process/TTY discovery, AppleScript window enumeration, per-display screenshots, and fallback cwd inference when direct text capture is unavailable. Do not use for ordinary direct execution that does not need an autonomous agent, CLI delegate, migration, or Hermes runtime workflow.'
license: MIT
metadata:
  hermes:
    tags:
    - macOS
    - Ghostty
    - Codex
    - AppleScript
    - screencapture
    - terminal-inspection
    related_skills:
    - codex
    - findmy
---

# Ghostty + Codex inspection on macOS

Use this when the user wants you to understand what Ghostty is currently doing, especially when Codex CLI sessions are running inside Ghostty.

This is a **read-first** workflow. Do **not** inject input into existing TTYs or control Ghostty interactively unless the user explicitly asks, because that has real side effects.

## What worked in practice

A reliable inspection stack on macOS was:

1. Confirm Ghostty / Codex processes exist
2. Map Codex processes to TTYs and cwd
3. Check whether Accessibility is enabled for AppleScript / System Events
4. Enumerate Ghostty windows and their coordinates
5. Capture the **correct display** or window region
6. Use vision/OCR to read the visible terminal text
7. If text capture still fails, fall back to cwd + process metadata to summarize what Ghostty is doing

## Key findings / pitfalls

### 1) Accessibility is required for window inspection
Without Accessibility permission, AppleScript calls like these fail with:
- `osascript 不允许辅助访问`
- `System Events ... (-1719)`

Detection command:

```bash
osascript <<'APPLESCRIPT'
tell application "System Events"
  tell process "ghostty"
    return name of every window
  end tell
end tell
APPLESCRIPT
```

If it fails, send the user to:

```bash
open 'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
```

Ask them to enable the relevant executor chain (commonly Terminal / osascript / Python depending on how Hermes is running).

### 2) Whole-screen screenshots can mislead you
A fullscreen screenshot may show:
- a black image
- only the desktop
- Ghostty as the active app in the menu bar, but **no visible Ghostty window**

That does **not** mean Ghostty is absent. It may be:
- on a secondary display
- in another space
- positioned off the main display

### 3) Ghostty may live on a secondary display with negative coordinates
This was the key experiential finding.

Window enumeration returned values like:
- window name: `codex-workspace`
- position: `0, -1440`
- size: `2560, 1440`

Negative Y means the window is on a display arranged **above** the main screen in macOS display coordinates.

Do not assume display 1 or the main screen contains Ghostty.

### 4) Per-display capture is often better than region capture first
If window coordinates suggest a secondary display, capture each display and inspect the likely one:

```bash
/usr/sbin/screencapture -D 1 -x /tmp/display-1.png
/usr/sbin/screencapture -D 2 -x /tmp/display-2.png
```

Then run vision/OCR on the per-display screenshots.

This worked better than relying on a single fullscreen image.

### 5) When text capture fails, cwd inference still gives high-value visibility
Even without readable screen text, you can still infer useful state by mapping Codex PIDs to cwd:

```bash
ps -o pid,ppid,tty,etime,command -p <pid1>,<pid2>,...

lsof -a -p <codex_pid> -d cwd -Fn 2>/dev/null | sed 's/^n//'
```

This lets you report:
- how many Codex sessions are active
- which TTY each session uses
- how long each has been running
- which project directory each session is working in

That is often enough to answer “Ghostty 在干嘛” at a practical level.

## Step-by-step workflow

### Step 1: Discover Ghostty and Codex processes

```bash
ps aux | grep -i '[G]hostty'
ps aux | grep -i '[c]odex'
```

Useful details to extract:
- Ghostty app path
- Codex node launcher path
- Codex native binary path
- TTYs (`s000`, `s004`, etc.)
- elapsed time
- `-C <workspace>` or `resume` flags

### Step 2: Map TTYs and cwd

For known PIDs:

```bash
ps -o pid,ppid,tty,etime,command -p 51461,51462,18325,18326

lsof -a -p 51462,18326 -d cwd -Fn 2>/dev/null | sed 's/^n//'
```

Interpretation:
- one Codex session may be attached to `ttys000`
- another resumed session may be attached to `ttys004`
- cwd tells you which repo each session is focused on

### Step 3: Test Accessibility / window enumeration

```bash
osascript <<'APPLESCRIPT'
tell application "System Events"
  tell process "ghostty"
    set frontmost to true
    delay 0.5
    return name of every window
  end tell
end tell
APPLESCRIPT
```

If this works, continue.
If not, open Accessibility settings and stop there until the user enables it.

### Step 4: Read window coordinates and size

```bash
osascript <<'APPLESCRIPT'
tell application "System Events"
  tell process "ghostty"
    repeat with w in windows
      try
        set _name to name of w
        set _pos to position of w
        set _size to size of w
        set _min to value of attribute "AXMinimized" of w
        return {_name, _pos, _size, _min}
      end try
    end repeat
  end tell
end tell
APPLESCRIPT
```

Look for:
- window title like `codex-workspace`
- coordinates such as `0, -1440`
- minimized state

### Step 5: Capture displays

First capture the main screen and likely secondary displays:

```bash
/usr/sbin/screencapture -D 1 -x /tmp/display-1.png
/usr/sbin/screencapture -D 2 -x /tmp/display-2.png
```

If needed, also inspect display topology:

```bash
system_profiler SPDisplaysDataType | sed -n '1,220p'
```

This confirms how many displays are online and helps explain negative coordinates.

### Step 6: Vision/OCR the correct display

Use the vision tool on the display image that actually contains the Ghostty window.

Ask specifically:
- whether Ghostty / Codex is visible
- what text is readable
- what task Codex appears to be performing

### Step 7: Summarize at the right confidence level

Separate:
- **hard facts**: process exists, TTY, cwd, visible window title, readable text
- **interpretation**: “looks like it is editing AGENTS.md rules” or “designing a Chrome extension SSO flow”

If only cwd is known, say so explicitly:
- “I can tell Codex is active in repo X and Y, but I still can’t read the visible terminal text.”

## Common interpretation patterns

### If you can read visible Codex text
Report:
- current repo/project
- what file or subsystem it is touching
- whether it is exploring, editing, summarizing, or waiting
- whether the visible output suggests completion or active work

### If you only have process + cwd
Report:
- number of active Codex sessions
- project directories
- elapsed runtimes
- whether sessions are `resume` vs fresh

This still answers the user’s practical question better than saying “I can’t see anything.”

## Safety boundary

Do not do these unless explicitly asked:
- write to `/dev/ttys*`
- inject keystrokes
- click inside Ghostty
- submit commands to Codex
- change focus/workspaces persistently

Inspection is fine; control requires explicit user intent.

## Good fallback plan if the user wants durable visibility

If the user wants you to know what Ghostty is doing **continuously**, recommend one of:

1. **log Codex output to a file**
   ```bash
   codex ... | tee ~/codex.log
   ```
2. **have Hermes launch/manage the task** so output is available via process tools
3. **periodic screenshot inspection** only if the user is comfortable with screen-level monitoring

Logging is usually the most reliable and least fragile method.

## Verification checklist

Before concluding:
1. Did you confirm Ghostty/Codex processes exist?
2. Did you extract TTY + cwd?
3. Did you test Accessibility rather than assuming it?
4. If fullscreen capture failed, did you try per-display capture?
5. Did you consider negative coordinates / secondary displays?
6. Did you clearly separate confirmed facts from inferred activity?
