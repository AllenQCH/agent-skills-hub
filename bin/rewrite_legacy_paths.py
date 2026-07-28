#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from hublib import REGISTRY_FILE, SKILLS, read_json


TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".txt"}


def replacements() -> dict[str, str]:
    registry = read_json(REGISTRY_FILE, {}) or {}
    result: dict[str, str] = {}
    for skill in registry.get("skills", []):
        name = skill["name"]
        canonical = str(SKILLS / name)
        for prefix in ("/Users/heytea/.codex/skills", "~/.codex/skills", "$HOME/.codex/skills"):
            result[f"{prefix}/{name}"] = canonical
        for variant in skill.get("source_variants", []):
            if variant.get("runtime") != "hermes":
                continue
            relative = variant.get("relative_path", "")
            for prefix in ("/Users/heytea/.hermes/skills", "~/.hermes/skills", "$HOME/.hermes/skills"):
                result[f"{prefix}/{relative}"] = canonical
        for prefix in ("/Users/heytea/.hermes/skills", "~/.hermes/skills", "$HOME/.hermes/skills"):
            result[f"{prefix}/{name}"] = canonical
    return dict(sorted(result.items(), key=lambda item: len(item[0]), reverse=True))


def candidate_files() -> list[Path]:
    return sorted(
        path
        for path in SKILLS.rglob("*")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and path.name != "skill.json"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Rewrite exact legacy Skill package paths to the shared Hub.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    mapping = replacements()
    changes = []
    for path in candidate_files():
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = original
        matched = []
        for old, new in mapping.items():
            if old in updated:
                updated = updated.replace(old, new)
                matched.append(old)
        if updated == original:
            continue
        changes.append({"path": str(path), "replacements": len(matched)})
        if args.apply:
            path.chmod(path.stat().st_mode | 0o200)
            path.write_text(updated, encoding="utf-8")
    print(json.dumps({"apply": args.apply, "changed_files": len(changes), "changes": changes}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
