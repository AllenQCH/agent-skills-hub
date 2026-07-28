#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from hublib import (
    HUB,
    PROFILES,
    REGISTRY_FILE,
    RUNTIME_ROOTS,
    SKILLS,
    build_manifest,
    build_registry,
    frontmatter,
    instruction_for,
    read_json,
    registry_by_name,
    verify_manifest,
    verify_registry,
)


ROUTER = SKILLS / "skill-router"
DEPLOY_TARGETS = {
    "codex": Path("/Users/heytea/.agents/skills/skill-router"),
    "claude": Path("/Users/heytea/.claude/skills/skill-router"),
    "hermes": Path("/Users/heytea/.hermes/skills/skill-router"),
}
MANAGED_ROOTS = [
    Path("/Users/heytea/.codex/skills"),
    Path("/Users/heytea/.agents/skills"),
    Path("/Users/heytea/.claude/skills"),
    Path("/Users/heytea/.hermes/skills"),
]
PROFILE_SIGNALS = {
    "backend": ("backend", "java", "spring", "django", "api", "service", "后端"),
    "heytea-operations": ("heytea", "invoice", "bfc", "dinghuotong", "蓝鲸", "数据库", "日志", "流水线"),
    "collaboration": ("lark", "feishu", "dingtalk", "alidocs", "github", "obsidian", "飞书", "钉钉", "文档"),
    "agents": ("agent", "skill", "mcp", "openspec", "multi-agent"),
}
QUERY_SYNONYMS = {
    "数据库": ("database", "sql", "dbauto"),
    "日志": ("log", "trace"),
    "流水线": ("pipeline", "release", "deploy"),
    "测试": ("test", "tdd", "verification", "regression"),
    "文档": ("document", "docs", "alidocs", "lark-doc"),
    "飞书": ("lark", "feishu"),
    "钉钉": ("dingtalk", "dws", "alidocs"),
    "技能": ("skill", "router"),
    "智能体": ("agent", "multi-agent"),
}


def emit(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def expanded_query(query: str) -> str:
    values = [query.lower()]
    for marker, synonyms in QUERY_SYNONYMS.items():
        if marker in query:
            values.extend(synonyms)
    return " ".join(values)


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]{2,}", text.lower()))


def profile_members() -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for path in sorted(PROFILES.glob("*.json")):
        payload = read_json(path, {}) or {}
        result[str(payload.get("name", path.stem))] = set(payload.get("skills", []))
    return result


def active_profiles(query: str, cwd: str) -> set[str]:
    text = f"{query} {cwd}".lower()
    return {
        profile
        for profile, signals in PROFILE_SIGNALS.items()
        if any(signal in text for signal in signals)
    }


def score_skill(skill: dict[str, Any], query: str, cwd: str, profiles: dict[str, set[str]]) -> tuple[int, list[str]]:
    expanded = expanded_query(query)
    query_tokens = tokens(expanded)
    name = skill["name"].lower()
    description = skill.get("description", "").lower()
    tags = set(skill.get("tags", []))
    score = 0
    reasons: list[str] = []
    if name == query.strip().lower() or name in query.lower():
        score += 120
        reasons.append("exact-name")
    name_tokens = tokens(name.replace("-", " "))
    name_overlap = query_tokens & name_tokens
    if name_overlap:
        score += 24 * len(name_overlap)
        reasons.append("name-token")
    description_overlap = query_tokens & tokens(description)
    if description_overlap:
        score += 5 * len(description_overlap)
        reasons.append("description")
    tag_overlap = query_tokens & tags
    if tag_overlap:
        score += 10 * len(tag_overlap)
        reasons.append("tag")
    for profile in active_profiles(query, cwd):
        if name in profiles.get(profile, set()):
            score += 18
            reasons.append(f"profile:{profile}")
    if skill.get("manual_only") and "manual" not in query.lower() and name not in query.lower():
        score -= 3
    return score, reasons


def command_search(args: argparse.Namespace) -> int:
    registry = read_json(REGISTRY_FILE)
    if not registry:
        registry = build_registry()
    profiles = profile_members()
    ranked: list[tuple[int, str, dict[str, Any], list[str]]] = []
    for skill in registry.get("skills", []):
        score, reasons = score_skill(skill, args.query, args.cwd, profiles)
        if score > 0:
            ranked.append((score, skill["name"], skill, reasons))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    candidates = []
    for score, _, skill, reasons in ranked[: args.limit]:
        candidates.append(
            {
                "name": skill["name"],
                "description": skill.get("description", "")[:180],
                "score": score,
                "match_reasons": reasons,
                "risk": skill.get("risk"),
                "manual_only": skill.get("manual_only"),
                "instruction_path": str(instruction_for(skill, args.runtime)),
                "source_runtimes": skill.get("source_runtimes", []),
            }
        )
    emit(
        {
            "query": args.query,
            "cwd": args.cwd,
            "runtime": args.runtime,
            "registry_size": len(registry.get("skills", [])),
            "candidates": candidates,
        }
    )
    return 0


def command_get(args: argparse.Namespace) -> int:
    skill = registry_by_name().get(args.name)
    if not skill:
        emit({"ok": False, "error": "skill-not-found", "name": args.name})
        return 1
    emit(
        {
            "ok": True,
            "name": skill["name"],
            "description": skill.get("description", ""),
            "risk": skill.get("risk"),
            "manual_only": skill.get("manual_only"),
            "instruction_path": str(instruction_for(skill, args.runtime)),
            "canonical_path": skill["path"],
            "source_runtimes": skill.get("source_runtimes", []),
        }
    )
    return 0


def hub_symlinks() -> list[Path]:
    links: list[Path] = []
    hub_prefix = str(HUB.resolve()) + os.sep
    for root in MANAGED_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_symlink():
                continue
            try:
                target = str(path.resolve(strict=False))
            except OSError:
                target = ""
            if target.startswith(hub_prefix):
                links.append(path)
    return sorted(set(links))


def prune_empty(root: Path) -> None:
    directories = sorted((path for path in root.rglob("*") if path.is_dir() and not path.is_symlink()), key=lambda path: len(path.parts), reverse=True)
    for directory in directories:
        if directory.name == ".system" or any(part.startswith(".") for part in directory.relative_to(root).parts):
            continue
        try:
            directory.rmdir()
        except OSError:
            pass


def command_deploy(args: argparse.Namespace) -> int:
    if not ROUTER.is_dir():
        emit({"ok": False, "error": "router-missing", "path": str(ROUTER)})
        return 1
    removals = [path for path in hub_symlinks() if path not in DEPLOY_TARGETS.values() or path.resolve(strict=False) != ROUTER]
    additions = [path for path in DEPLOY_TARGETS.values() if not path.is_symlink() or path.resolve(strict=False) != ROUTER]
    plan = {
        "apply": args.apply,
        "remove_links": [str(path) for path in removals],
        "add_router_links": [str(path) for path in additions],
        "preserve_real_directories": True,
    }
    if not args.apply:
        emit(plan)
        return 0
    staged: list[tuple[Path, Path]] = []
    for target in additions:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".next")
        if temporary.exists() or temporary.is_symlink():
            temporary.unlink()
        temporary.symlink_to(ROUTER, target_is_directory=True)
        staged.append((temporary, target))
    for path in removals:
        path.unlink()
    for root in MANAGED_ROOTS:
        if root.exists():
            prune_empty(root)
    for temporary, target in staged:
        if target.exists() or target.is_symlink():
            if target.is_symlink():
                target.unlink()
            else:
                raise RuntimeError(f"router target occupied by real path: {target}")
        temporary.rename(target)
    emit({**plan, "ok": True})
    return 0


def visible_skill_files(runtime: str) -> list[Path]:
    roots = list(RUNTIME_ROOTS.get(runtime, []))
    if runtime == "codex":
        roots.append(Path("/Users/heytea/.codex/plugins/cache"))
    files: set[Path] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("SKILL.md"):
            if path.is_file():
                files.add(path.resolve())
        for link in root.rglob("*"):
            if link.is_symlink():
                candidate = link.resolve(strict=False) / "SKILL.md"
                if candidate.is_file():
                    files.add(candidate.resolve())
    return sorted(files)


def command_doctor(args: argparse.Namespace) -> int:
    files = visible_skill_files(args.runtime)
    rows = []
    for path in files:
        metadata = frontmatter(path)
        if not metadata.get("name"):
            continue
        rows.append((metadata["name"], metadata.get("description", ""), path))
    name_desc_chars = sum(len(name) + len(description) for name, description, _ in rows)
    with_path_chars = sum(len(name) + len(description) + len(str(path)) for name, description, path in rows)
    payload = {
        "runtime": args.runtime,
        "visible_skills": len(rows),
        "name_description_chars": name_desc_chars,
        "with_path_chars": with_path_chars,
        "budget_chars": args.budget,
        "within_budget": with_path_chars <= args.budget,
        "descriptions_over_120": sum(1 for _, description, _ in rows if len(description) > 120),
        "largest_descriptions": [
            {"name": name, "chars": len(description)}
            for name, description, _ in sorted(rows, key=lambda row: len(row[1]), reverse=True)[:10]
        ],
    }
    emit(payload)
    return 0 if payload["within_budget"] else 1


def verify_deployment() -> list[str]:
    errors: list[str] = []
    for runtime, target in DEPLOY_TARGETS.items():
        if not target.is_symlink():
            errors.append(f"router link missing for {runtime}: {target}")
        elif target.resolve(strict=False) != ROUTER:
            errors.append(f"router target mismatch for {runtime}: {target}")
    for link in hub_symlinks():
        if link not in DEPLOY_TARGETS.values():
            errors.append(f"unexpected Hub runtime link: {link}")
    if not Path("/Users/heytea/.codex/skills/.system").is_dir():
        errors.append("Codex system skills directory was not preserved")
    return errors


def command_verify(_: argparse.Namespace) -> int:
    errors = [*verify_registry(), *verify_manifest(), *verify_deployment()]
    if errors:
        emit({"ok": False, "errors": errors})
        return 1
    emit({"ok": True, "registry": str(REGISTRY_FILE), "router": str(ROUTER)})
    return 0


def command_build(_: argparse.Namespace) -> int:
    registry = build_registry()
    manifest = build_manifest(registry)
    emit({"ok": True, "registry_skills": len(registry["skills"]), "manifest_resources": len(manifest["resources"])})
    return 0


def command_scan(_: argparse.Namespace) -> int:
    patterns = {
        "private-key": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
        "github-token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
        "openai-key": re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{30,}"),
        "aws-key": re.compile(r"AKIA[0-9A-Z]{16}"),
    }
    findings = []
    for path in sorted(HUB.rglob("*")):
        if ".git" in path.parts:
            continue
        if not path.is_file() or path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".pyc"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(lines, 1):
            for category, pattern in patterns.items():
                match = pattern.search(line)
                if match and len(set(match.group(0))) > 6:
                    findings.append({"category": category, "path": str(path), "line": number})
    emit({"ok": not findings, "high_confidence_findings": findings})
    return 0 if not findings else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search and manage the shared local Skill Hub.")
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search")
    search.add_argument("--query", required=True)
    search.add_argument("--cwd", default=os.getcwd())
    search.add_argument("--runtime", choices=("codex", "claude", "hermes"), default="codex")
    search.add_argument("--limit", type=int, default=5)

    get = sub.add_parser("get")
    get.add_argument("name")
    get.add_argument("--runtime", choices=("codex", "claude", "hermes"), default="codex")

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--runtime", choices=("codex", "claude", "hermes"), default="codex")
    doctor.add_argument("--budget", type=int, default=8000)

    deploy = sub.add_parser("deploy")
    deploy.add_argument("--apply", action="store_true")

    sub.add_parser("build")
    sub.add_parser("verify")
    sub.add_parser("scan")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    commands = {
        "search": command_search,
        "get": command_get,
        "doctor": command_doctor,
        "deploy": command_deploy,
        "build": command_build,
        "verify": command_verify,
        "scan": command_scan,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
