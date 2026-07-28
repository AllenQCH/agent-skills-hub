#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
from collections import defaultdict
from pathlib import Path

from hublib import HUB, SKILLS, build_manifest, build_registry, frontmatter, package_hash, write_json


ACTIVE = HUB / "active"
BUILD = HUB / ".v3-build"
ROUTER_TEMPLATE = HUB / "templates" / "skill-router"
MIGRATION_MANIFEST = HUB / "manifests" / "migration-v3.json"
SOURCE_ORDER = {"common": 0, "codex": 1, "claude": 2, "hermes": 3}
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def remove_tree(path: Path) -> None:
    if not path.exists():
        return
    for directory in [path, *path.rglob("*")]:
        if directory.is_dir() and not directory.is_symlink():
            directory.chmod(stat.S_IMODE(directory.stat().st_mode) | stat.S_IWUSR)
    shutil.rmtree(path)


def source_packages() -> list[dict[str, object]]:
    packages: list[dict[str, object]] = []
    for runtime in ("common", "codex", "claude", "hermes"):
        root = ACTIVE / runtime
        if not root.exists():
            continue
        for skill_file in sorted(root.rglob("SKILL.md")):
            if any(part.startswith(".") for part in skill_file.relative_to(root).parts):
                continue
            package = skill_file.parent
            metadata = frontmatter(skill_file)
            name = metadata.get("name") or package.name
            if not NAME_PATTERN.fullmatch(name):
                raise RuntimeError(f"unsupported skill name {name!r}: {skill_file}")
            digest, file_count = package_hash(package)
            packages.append(
                {
                    "name": name,
                    "runtime": runtime,
                    "relative_path": package.relative_to(root).as_posix(),
                    "path": package,
                    "sha256": digest,
                    "file_count": file_count,
                }
            )
    return packages


def adapter_key(item: dict[str, object], used: set[str]) -> str:
    runtime = str(item["runtime"])
    if runtime not in used:
        used.add(runtime)
        return runtime
    suffix = str(item["relative_path"]).replace("/", "-")
    key = f"{runtime}-{suffix}"
    used.add(key)
    return key


def build_tree(packages: list[dict[str, object]]) -> dict[str, object]:
    if BUILD.exists():
        remove_tree(BUILD)
    target_root = BUILD / "skills"
    target_root.mkdir(parents=True)
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in packages:
        groups[str(item["name"])].append(item)

    collisions: list[dict[str, object]] = []
    for name, variants in sorted(groups.items()):
        variants.sort(key=lambda item: (SOURCE_ORDER[str(item["runtime"])], str(item["relative_path"])))
        canonical = variants[0]
        destination = target_root / name
        shutil.copytree(Path(canonical["path"]), destination, symlinks=True, copy_function=shutil.copy2)
        for directory in [destination, *destination.rglob("*")]:
            if directory.is_dir() and not directory.is_symlink():
                directory.chmod(stat.S_IMODE(directory.stat().st_mode) | stat.S_IWUSR)
        adapters: dict[str, str] = {}
        if len(variants) > 1:
            used: set[str] = set()
            for item in variants[1:]:
                key = adapter_key(item, used)
                adapter = destination / "adapters" / key
                shutil.copytree(Path(item["path"]), adapter, symlinks=True, copy_function=shutil.copy2)
                adapters[str(item["runtime"])] = f"adapters/{key}/SKILL.md"
            collisions.append(
                {
                    "name": name,
                    "canonical_runtime": canonical["runtime"],
                    "variant_count": len(variants),
                    "adapters": adapters,
                }
            )
        descriptor = {
            "version": 1,
            "id": name,
            "name": name,
            "source_runtimes": sorted({str(item["runtime"]) for item in variants}),
            "canonical_source": {
                key: canonical[key]
                for key in ("runtime", "relative_path", "sha256", "file_count")
            },
            "source_variants": [
                {key: item[key] for key in ("runtime", "relative_path", "sha256", "file_count")}
                for item in variants
            ],
            "adapters": adapters,
        }
        write_json(destination / "skill.json", descriptor)

    router_target = target_root / "skill-router"
    if router_target.exists():
        raise RuntimeError("source skills already contain reserved name: skill-router")
    shutil.copytree(ROUTER_TEMPLATE, router_target, symlinks=True, copy_function=shutil.copy2)
    write_json(
        router_target / "skill.json",
        {
            "version": 1,
            "id": "skill-router",
            "name": "skill-router",
            "source_runtimes": ["all"],
            "source_variants": [],
            "adapters": {},
            "risk": "readonly",
            "manual_only": False,
            "tags": ["agents", "discovery"],
        },
    )
    return {
        "source_packages": len(packages),
        "unique_source_names": len(groups),
        "canonical_packages": len(groups) + 1,
        "collision_groups": collisions,
    }


def apply_build(summary: dict[str, object]) -> None:
    if SKILLS.exists():
        raise RuntimeError(f"target already exists: {SKILLS}")
    (BUILD / "skills").rename(SKILLS)
    BUILD.rmdir()
    registry = build_registry()
    build_manifest(registry)
    write_json(
        MIGRATION_MANIFEST,
        {
            "version": 3,
            "hub": str(HUB),
            "policy": {
                "archive_existing": False,
                "shorten_descriptions": False,
                "preserve_all_source_variants": True,
                "runtime_neutral_top_level": True,
            },
            **summary,
        },
    )


def finalize(backup: Path, apply: bool) -> int:
    backup_active = backup / "hub" / "active"
    if not backup_active.is_dir():
        raise RuntimeError(f"backup does not contain original active tree: {backup_active}")
    if not SKILLS.is_dir() or not MIGRATION_MANIFEST.is_file():
        raise RuntimeError("V3 canonical tree is not ready")
    action = {"remove": str(ACTIVE), "backup": str(backup_active), "apply": apply}
    if apply:
        remove_tree(ACTIVE)
    print(json.dumps(action, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the runtime-neutral V3 Skill Hub.")
    parser.add_argument("command", choices=("plan", "apply", "finalize"))
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--apply", action="store_true", help="required with finalize")
    args = parser.parse_args()
    if args.command == "finalize":
        if args.backup is None:
            parser.error("finalize requires --backup")
        return finalize(args.backup, args.apply)
    packages = source_packages()
    summary = build_tree(packages)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.command == "apply":
        apply_build(summary)
        print(json.dumps({"status": "applied", "skills": str(SKILLS)}, ensure_ascii=False))
    else:
        remove_tree(BUILD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
