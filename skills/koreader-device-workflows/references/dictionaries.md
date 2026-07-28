# KOReader dictionary workflow

## Authoritative findings

KOReader uses StarDict dictionaries. A valid dictionary normally contains matching basename files such as:

```text
name.ifo
name.idx
name.dict or name.dict.dz
```

Official references:

- KOReader dictionary support: https://github.com/koreader/koreader/wiki/Dictionary-support
- Current menu implementation: `frontend/apps/reader/modules/readerdictionary.lua`
- Current built-in download catalog: `frontend/ui/data/dictionaries.lua`

## In-app download

On current KOReader builds, open the search/magnifying-glass menu and navigate:

```text
Settings
→ Dictionary settings
→ Download dictionaries
```

The downloader groups available dictionaries by language and asks for confirmation after checking archive size. After download, use `Dictionary settings → Manage dictionaries` to enable, disable, and prioritize dictionaries.

For English reading, useful built-in choices include:

| Dictionary | Direction | Notes |
|---|---|---|
| English-English Wiktionary | English → English | Broad, modern vocabulary; good default |
| GNU Collaborative International Dictionary of English | English → English | Useful secondary dictionary; older source |
| English explanatory dictionary (main) | English → English | Optional alternative |
| English Idioms (eng-eng) | English → English idioms | Useful for novels and idiomatic phrases |
| Chinese-English dictionary | Chinese → English | This is 汉英, not 英汉 |

Do not describe `Chinese-English` as an English-to-Chinese dictionary. The built-in catalog may not provide a high-quality free English-Chinese dictionary; that usually requires a separately sourced, legally distributable StarDict package.

## Manual installation

For Kindle's USB-visible storage, place extracted dictionaries under:

```text
/koreader/data/dict/
```

The equivalent device-side path is commonly:

```text
/mnt/us/koreader/data/dict/
```

Keep each dictionary's `.ifo`, `.idx`, and `.dict`/`.dict.dz` files together. Safely eject, restart KOReader, then verify it under `Dictionary settings → Manage dictionaries`.

## Performance guidance

Older devices such as Kindle Paperwhite 3 can become slow when many large dictionaries are enabled with fuzzy search. Start with one primary English-English dictionary, verify long-press lookup, then add a secondary dictionary. If lookup becomes slow, disable unused dictionaries before disabling fuzzy search.

## Verification

1. Open a DRM-free EPUB or text-capable PDF.
2. Long-press an English word.
3. Confirm a definition appears.
4. Swipe between results if multiple dictionaries are active.
5. Check dictionary order in `Manage dictionaries` if the wrong source appears first.
