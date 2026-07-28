#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import re
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HUB = Path(__file__).resolve().parents[1]
SKILLS = HUB / "skills"
REGISTRY_DIR = HUB / "registry"
REGISTRY_FILE = REGISTRY_DIR / "skills.json"
MANIFEST = HUB / "manifests" / "resources.json"
PROFILES = HUB / "profiles"
IGNORED_NAMES = {".DS_Store", "__pycache__"}
RUNTIME_ROOTS = {
    "codex": [Path("/Users/heytea/.agents/skills"), Path("/Users/heytea/.codex/skills")],
    "claude": [Path("/Users/heytea/.claude/skills")],
    "hermes": [Path("/Users/heytea/.hermes/skills")],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _yaml_scalar(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if value[0:1] in {"'", '"'}:
        try:
            parsed = ast.literal_eval(value)
            return str(parsed)
        except (SyntaxError, ValueError):
            return value.strip("'\"")
    return value


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        return {}
    result: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, raw = match.groups()
        if raw in {"|", ">", "|-", ">-"}:
            block: list[str] = []
            index += 1
            while index < end and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                block.append(lines[index].strip())
                index += 1
            result[key] = ("\n" if raw.startswith("|") else " ").join(block).strip()
            continue
        result[key] = _yaml_scalar(raw)
        index += 1
    return result


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_hash(package: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    count = 0
    for path in sorted(package.rglob("*")):
        if not path.is_file() or path.name in IGNORED_NAMES or path.suffix == ".pyc":
            continue
        relative = path.relative_to(package).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hash_file(path).encode("ascii"))
        digest.update(b"\0")
        count += 1
    return digest.hexdigest(), count


def canonical_packages(root: Path = SKILLS) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())


def infer_risk(name: str, description: str) -> tuple[str, bool]:
    text = f"{name} {description}".lower()
    high_markers = (
        "production",
        "生产",
        "delete",
        "删除",
        "publish",
        "deploy",
        "send",
        "submit",
        "execute-once",
        "permission",
    )
    write_markers = ("create", "update", "write", "upload", "commit", "push", "trigger", "填写", "创建", "修改")
    if any(marker in text for marker in high_markers):
        return "high", True
    if any(marker in text for marker in write_markers):
        return "write", False
    return "readonly", False


def infer_tags(name: str, description: str) -> list[str]:
    text = f"{name} {description}".lower()
    groups = {
        "database": ("database", "sql", "postgres", "clickhouse", "dbauto"),
        "logs": ("log", "trace", "日志"),
        "backend": ("backend", "spring", "django", "java", "python", "api"),
        "testing": ("test", "tdd", "verification", "regression", "测试"),
        "delivery": ("release", "deploy", "pipeline", "delivery", "发布", "流水线"),
        "collaboration": ("lark", "feishu", "dingtalk", "alidocs", "飞书", "钉钉"),
        "documents": ("document", "spreadsheet", "pdf", "obsidian", "文档"),
        "agents": ("agent", "mcp", "skill", "openspec"),
        "github": ("github", "git ", "pull request"),
        "research": ("research", "search", "研究", "调研"),
        "media": ("image", "video", "audio", "youtube", "图片", "视频"),
    }
    return sorted(tag for tag, markers in groups.items() if any(marker in text for marker in markers))


def build_registry() -> dict[str, Any]:
    skills: list[dict[str, Any]] = []
    for package in canonical_packages():
        metadata = frontmatter(package / "SKILL.md")
        descriptor = read_json(package / "skill.json", {}) or {}
        name = metadata.get("name") or descriptor.get("name") or package.name
        description = metadata.get("description", "")
        risk, inferred_manual = infer_risk(name, description)
        digest, file_count = package_hash(package)
        adapters = descriptor.get("adapters", {})
        skills.append(
            {
                "id": descriptor.get("id", name),
                "name": name,
                "description": description,
                "path": str(package),
                "instruction_path": str(package / "SKILL.md"),
                "sha256": digest,
                "file_count": file_count,
                "tags": sorted(set(descriptor.get("tags", [])) | set(infer_tags(name, description))),
                "risk": descriptor.get("risk", risk),
                "manual_only": bool(descriptor.get("manual_only", inferred_manual)),
                "source_runtimes": descriptor.get("source_runtimes", []),
                "source_variants": descriptor.get("source_variants", []),
                "adapters": adapters,
            }
        )
    payload = {
        "version": 3,
        "generated_at": now_iso(),
        "hub": str(HUB),
        "discovery_policy": {
            "initial_profile": "bootstrap",
            "registry_in_prompt": False,
            "top_k_default": 5,
        },
        "skills": sorted(skills, key=lambda item: item["name"]),
    }
    write_json(REGISTRY_FILE, payload)
    return payload


def build_manifest(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = registry or build_registry()
    payload = {
        "version": 3,
        "generated_at": now_iso(),
        "hub": str(HUB),
        "resources": [
            {
                "name": skill["name"],
                "path": skill["path"],
                "sha256": skill["sha256"],
                "file_count": skill["file_count"],
                "source_runtimes": skill["source_runtimes"],
                "adapters": skill["adapters"],
            }
            for skill in registry["skills"]
        ],
    }
    write_json(MANIFEST, payload)
    return payload


def registry_by_name() -> dict[str, dict[str, Any]]:
    payload = read_json(REGISTRY_FILE)
    if not payload:
        payload = build_registry()
    return {item["name"]: item for item in payload.get("skills", [])}


def instruction_for(skill: dict[str, Any], runtime: str | None) -> Path:
    if runtime:
        relative = skill.get("adapters", {}).get(runtime)
        if relative:
            return Path(skill["path"]) / relative
    return Path(skill["instruction_path"])


def verify_registry() -> list[str]:
    errors: list[str] = []
    payload = read_json(REGISTRY_FILE)
    if not payload:
        return [f"registry missing: {REGISTRY_FILE}"]
    names: set[str] = set()
    for item in payload.get("skills", []):
        name = item.get("name", "")
        if name in names:
            errors.append(f"duplicate registry name: {name}")
        names.add(name)
        package = Path(item.get("path", ""))
        if not (package / "SKILL.md").is_file():
            errors.append(f"canonical skill missing: {package}")
            continue
        digest, file_count = package_hash(package)
        if digest != item.get("sha256"):
            errors.append(f"registry hash mismatch: {package}")
        if file_count != item.get("file_count"):
            errors.append(f"registry file count mismatch: {package}")
        for runtime, relative in item.get("adapters", {}).items():
            adapter = package / relative
            if not adapter.is_file():
                errors.append(f"adapter missing for {name}/{runtime}: {adapter}")
    return errors


def verify_manifest() -> list[str]:
    payload = read_json(MANIFEST)
    if not payload:
        return [f"manifest missing: {MANIFEST}"]
    errors: list[str] = []
    for item in payload.get("resources", []):
        package = Path(item.get("path", ""))
        if not package.is_dir():
            errors.append(f"manifest package missing: {package}")
            continue
        digest, file_count = package_hash(package)
        if digest != item.get("sha256") or file_count != item.get("file_count"):
            errors.append(f"manifest mismatch: {package}")
    return errors


def verify_read_only() -> list[str]:
    errors: list[str] = []
    if not SKILLS.exists():
        return [f"skills directory missing: {SKILLS}"]
    for path in [SKILLS, *SKILLS.rglob("*")]:
        if path.is_symlink():
            continue
        if stat.S_IMODE(path.stat().st_mode) & 0o222:
            errors.append(f"hub entry is writable: {path}")
    return errors
