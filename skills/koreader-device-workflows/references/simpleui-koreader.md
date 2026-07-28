# SimpleUI for KOReader

## Identified upstream

- Main repository: https://github.com/doctorhetfield-cmd/simpleui.koplugin
- Releases: https://github.com/doctorhetfield-cmd/simpleui.koplugin/releases
- Latest release observed during research: `SimpleUI v2.1.0`
- Named release asset: `simpleui.koplugin.zip`
- Older release: `SimpleUI v1.5.0` (use when matching an older video/screenshot or when a legacy KOReader build is incompatible with v2.x)

## What it provides

A customizable KOReader home screen, bottom navigation, quick actions, reading statistics, bookmarks, collections, library access, power controls, and optional modules/widgets. The exact screen varies by version and configuration.

## Kindle install

After KOReader itself is installed and working on a jailbroken Kindle:

1. Download `simpleui.koplugin.zip` from the release page.
2. Extract it and verify there is exactly one top-level folder named `simpleui.koplugin`.
3. Copy that folder to:

```text
/koreader/plugins/
```

4. Verify the final path resembles:

```text
/koreader/plugins/simpleui.koplugin/main.lua
```

5. Safely eject the Kindle and restart KOReader.
6. Enable/configure through:

```text
Menu → Tools → SimpleUI
```

Do not create:

```text
/koreader/plugins/simpleui.koplugin/simpleui.koplugin/
```

## Wallpaper fork

A personal fork with home-screen wallpaper support was found at:

https://github.com/kalinatringas/Simple-UI-original-home-wallpaper

Its README describes `homescreen_bg.png` for normal mode and `homescreen_bg_night.png` for night mode under the plugin's `icons/` directory. Treat it as a community modification rather than the primary release; install the upstream plugin first and use the fork only if the wallpaper feature is wanted.

## Compatibility caution

SimpleUI is a KOReader plugin, not a native Kindle plugin. Finish and verify the Kindle jailbreak and KOReader installation first. For an older PW3/legacy KOReader build, test v1.5.0 before assuming the current v2.1.0 build is compatible. Prefer reversible plugin disablement over deleting KOReader state when troubleshooting.
