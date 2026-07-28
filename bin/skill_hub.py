#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import stat
from pathlib import Path

from hublib import SKILLS, build_manifest, build_registry, verify_manifest, verify_read_only, verify_registry


def command_manifest(_: argparse.Namespace) -> int:
    registry = build_registry()
    manifest = build_manifest(registry)
    print(json.dumps({"registry_skills": len(registry["skills"]), "manifest_resources": len(manifest["resources"])}))
    return 0


def command_verify(_: argparse.Namespace) -> int:
    errors = [*verify_registry(), *verify_manifest(), *verify_read_only()]
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"OK: {SKILLS}")
    return 0


def set_writable(path: Path, writable: bool) -> int:
    changed = 0
    paths = [path, *path.rglob("*")]
    for item in sorted(paths, key=lambda candidate: len(candidate.parts), reverse=not writable):
        if item.is_symlink():
            continue
        mode = stat.S_IMODE(item.stat().st_mode)
        target_mode = mode | stat.S_IWUSR if writable else mode & ~0o222
        if target_mode != mode:
            item.chmod(target_mode)
            changed += 1
    return changed


def command_lock(_: argparse.Namespace) -> int:
    print(json.dumps({"skills": str(SKILLS), "locked_entries": set_writable(SKILLS, False)}))
    return 0


def command_unlock(args: argparse.Namespace) -> int:
    target = SKILLS / args.skill
    if not (target / "SKILL.md").is_file():
        print(f"unknown skill: {args.skill}")
        return 1
    print(json.dumps({"skill": args.skill, "unlocked_entries": set_writable(target, True)}))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage the runtime-neutral Agent Skills Hub.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("manifest")
    sub.add_parser("verify")
    sub.add_parser("lock")
    unlock = sub.add_parser("unlock")
    unlock.add_argument("skill")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    commands = {
        "manifest": command_manifest,
        "verify": command_verify,
        "lock": command_lock,
        "unlock": command_unlock,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
