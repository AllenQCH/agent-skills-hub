#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata"}
AUXILIARY_ROOT_FILES = {"README.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md", "CHANGELOG.md"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"(!?\[[^\]]*\]\()([^\n)]+)(\))")
TRIGGER_RE = re.compile(
    r"\buse\s+(?:this\s+skill\s+)?when\b|\bwhen\s+(?:the\s+)?user\b|"
    r"适用|当用户|用户(?:需要|请求)|触发",
    re.IGNORECASE,
)
UI_KEYS = {
    "display_name",
    "short_description",
    "icon_small",
    "icon_large",
    "brand_color",
    "default_prompt",
}


@dataclass(frozen=True)
class Surface:
    kind: str
    path: Path
    package: Path
    mutable: bool


def default_hub() -> Path:
    return Path(__file__).resolve().parents[3]


def read_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, str | None]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.DOTALL)
    if not match:
        return {}, text, "missing-or-invalid-frontmatter"
    try:
        payload = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return {}, text[match.end() :], f"invalid-yaml: {exc}"
    if not isinstance(payload, dict):
        return {}, text[match.end() :], "frontmatter-is-not-a-mapping"
    return payload, text[match.end() :], None


def render_skill(frontmatter: dict[str, Any], body: str) -> str:
    yaml_text = yaml.safe_dump(
        frontmatter,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
        default_flow_style=False,
    ).rstrip()
    return f"---\n{yaml_text}\n---\n\n{body.lstrip()}".rstrip() + "\n"


def canonical_packages(hub: Path) -> list[Path]:
    root = hub / "skills"
    if not root.is_dir():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file())


def collect_surfaces(hub: Path, hermes_root: Path) -> list[Surface]:
    result: list[Surface] = []
    hub_resolved = hub.resolve()
    for package in canonical_packages(hub):
        result.append(Surface("canonical", package / "SKILL.md", package, True))
        for adapter in sorted(package.glob("adapters/*/SKILL.md")):
            result.append(Surface("adapter", adapter, package, True))
    if hermes_root.is_dir():
        for path in sorted(hermes_root.rglob("SKILL.md")):
            if path.is_symlink():
                continue
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved == hub_resolved or hub_resolved in resolved.parents:
                continue
            if any(part.startswith(".") for part in path.relative_to(hermes_root).parts):
                continue
            result.append(Surface("hermes-local", path, path.parent, True))
    return result


def inventory_surfaces(system_root: Path, plugin_root: Path) -> list[Surface]:
    result: list[Surface] = []
    for kind, root in (("system", system_root), ("plugin", plugin_root)):
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("SKILL.md")):
            if path.is_file():
                result.append(Surface(kind, path, path.parent, False))
    return result


def line_count(text: str) -> int:
    return len(text.splitlines())


def has_trigger(description: str) -> bool:
    return bool(TRIGGER_RE.search(description))


def split_destination(raw: str) -> tuple[str, str]:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        end = value.index(">")
        return value[1:end], value[end + 1 :]
    match = re.match(r"(\S+)(.*)$", value, re.DOTALL)
    return (match.group(1), match.group(2)) if match else (value, "")


def is_external_destination(destination: str) -> bool:
    lowered = destination.lower()
    return (
        not destination
        or lowered in {"url", "link", "path"}
        or destination.startswith(("#", "/"))
        or re.match(r"^[a-z][a-z0-9+.-]*:", lowered) is not None
        or destination.startswith("$")
    )


def destination_path(base: Path, destination: str) -> Path | None:
    if is_external_destination(destination):
        return None
    path_part = destination.split("#", 1)[0]
    if not path_part:
        return None
    return (base / path_part).resolve(strict=False)


def broken_links(path: Path, text: str) -> list[str]:
    broken: list[str] = []
    visible_lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            visible_lines.append("")
            continue
        visible_lines.append("" if in_fence else re.sub(r"`[^`]*`", "", line))
    visible_text = "\n".join(visible_lines)
    for match in LINK_RE.finditer(visible_text):
        destination, _ = split_destination(match.group(2))
        target = destination_path(path.parent, destination)
        if target is not None and not target.exists():
            broken.append(destination)
    return sorted(set(broken))


def openai_metadata_issues(package: Path, name: str) -> list[str]:
    path = package / "agents" / "openai.yaml"
    if not path.is_file():
        return ["missing-openai-yaml"]
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return ["invalid-openai-yaml"]
    if not isinstance(payload, dict):
        return ["invalid-openai-yaml"]
    issues: list[str] = []
    if any(key in payload for key in UI_KEYS):
        issues.append("legacy-openai-yaml-shape")
    interface = payload.get("interface")
    if not isinstance(interface, dict):
        return issues + ["missing-openai-interface"]
    if not interface.get("display_name"):
        issues.append("missing-display-name")
    short = interface.get("short_description")
    if not isinstance(short, str) or not 25 <= len(short.strip()) <= 64:
        issues.append("invalid-short-description")
    prompt = interface.get("default_prompt")
    if not isinstance(prompt, str) or f"${name}" not in prompt:
        issues.append("default-prompt-missing-skill-token")
    return issues


def audit_surface(surface: Surface) -> dict[str, Any]:
    text = surface.path.read_text(encoding="utf-8")
    metadata, _, parse_error = parse_frontmatter(text)
    issues: list[str] = []
    if parse_error:
        issues.append(parse_error)
    name = metadata.get("name")
    description = metadata.get("description")
    if not isinstance(name, str) or not name.strip():
        issues.append("missing-or-invalid-name")
        name = surface.package.name
    elif len(name) > 64 or not NAME_RE.fullmatch(name):
        issues.append("invalid-name-format")
    if surface.kind == "canonical" and name != surface.package.name:
        issues.append("canonical-name-folder-mismatch")
    if not isinstance(description, str) or not description.strip():
        issues.append("missing-or-invalid-description")
        description = ""
    else:
        if len(description.strip()) > 1024:
            issues.append("description-over-1024")
        if "<" in description or ">" in description:
            issues.append("description-angle-brackets")
        if not has_trigger(description):
            issues.append("description-missing-trigger")
    unsupported = sorted(set(metadata) - ALLOWED_FRONTMATTER)
    if unsupported:
        issues.append("unsupported-frontmatter")
    if line_count(text) > 500:
        issues.append("skill-md-over-500-lines")
    links = broken_links(surface.path, text)
    if links:
        issues.append("broken-relative-links")
    if surface.kind in {"canonical", "hermes-local"}:
        issues.extend(openai_metadata_issues(surface.package, str(name)))
    auxiliary = []
    if surface.kind in {"canonical", "hermes-local"}:
        auxiliary = sorted(path.name for path in surface.package.iterdir() if path.is_file() and path.name in AUXILIARY_ROOT_FILES)
        if auxiliary:
            issues.append("package-root-auxiliary-doc")
    return {
        "kind": surface.kind,
        "path": str(surface.path),
        "package": str(surface.package),
        "mutable": surface.mutable,
        "name": name,
        "lines": line_count(text),
        "unsupported_frontmatter": unsupported,
        "broken_links": links,
        "auxiliary_root_files": auxiliary,
        "issues": sorted(set(issues)),
    }


def audit_all(
    hub: Path,
    hermes_root: Path,
    system_root: Path,
    plugin_root: Path,
) -> dict[str, Any]:
    managed = [audit_surface(surface) for surface in collect_surfaces(hub, hermes_root)]
    inventory = [audit_surface(surface) for surface in inventory_surfaces(system_root, plugin_root)]
    counts = Counter(issue for item in managed for issue in item["issues"])
    inventory_counts = Counter(item["kind"] for item in inventory)
    kinds = Counter(item["kind"] for item in managed)
    return {
        "version": 1,
        "hub": str(hub),
        "scope": {
            "managed": dict(sorted(kinds.items())),
            "inventory_only": dict(sorted(inventory_counts.items())),
        },
        "summary": {
            "managed_surfaces": len(managed),
            "managed_with_issues": sum(bool(item["issues"]) for item in managed),
            "issue_counts": dict(sorted(counts.items())),
            "inventory_surfaces": len(inventory),
        },
        "managed": managed,
        "inventory_only": inventory,
    }


def markdown_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Skill Quality Audit",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Managed surfaces | {summary['managed_surfaces']} |",
        f"| Managed surfaces with issues | {summary['managed_with_issues']} |",
        f"| Inventory-only surfaces | {summary['inventory_surfaces']} |",
        "",
        "## Managed Scope",
        "",
        "| Kind | Count |",
        "| --- | ---: |",
    ]
    for kind, count in report["scope"]["managed"].items():
        lines.append(f"| {kind} | {count} |")
    lines.extend(["", "## Issue Counts", "", "| Issue | Count |", "| --- | ---: |"])
    for issue, count in summary["issue_counts"].items():
        lines.append(f"| `{issue}` | {count} |")
    lines.extend(["", "## Affected Surfaces", ""])
    for item in report["managed"]:
        if not item["issues"]:
            continue
        lines.append(f"- `{item['path']}`: " + ", ".join(f"`{value}`" for value in item["issues"]))
    lines.extend(["", "## Inventory Only", "", "| Kind | Count |", "| --- | ---: |"])
    for kind, count in report["scope"]["inventory_only"].items():
        lines.append(f"| {kind} | {count} |")
    return "\n".join(lines).rstrip() + "\n"


def title_name(name: str) -> str:
    special = {
        "ai": "AI",
        "api": "API",
        "cli": "CLI",
        "css": "CSS",
        "db": "DB",
        "dws": "DWS",
        "github": "GitHub",
        "html": "HTML",
        "mcp": "MCP",
        "pdf": "PDF",
        "qa": "QA",
        "sql": "SQL",
        "tdd": "TDD",
        "ui": "UI",
        "url": "URL",
    }
    return " ".join(special.get(part, part.capitalize()) for part in name.split("-"))


def generated_short_description(display_name: str) -> str:
    value = f"Use {display_name} workflows and resources"
    if len(value) < 25:
        value += " for agent tasks"
    if len(value) > 64:
        value = f"Use the documented {display_name} workflow"
    if len(value) > 64:
        value = value[:61].rstrip() + "..."
    return value


def normalized_openai(package: Path, name: str) -> tuple[str, str]:
    path = package / "agents" / "openai.yaml"
    existing_text = path.read_text(encoding="utf-8") if path.is_file() else ""
    try:
        payload = yaml.safe_load(existing_text) if existing_text else {}
    except yaml.YAMLError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    payload = dict(payload)
    interface = payload.get("interface")
    interface = dict(interface) if isinstance(interface, dict) else {}
    payload.pop("interface", None)
    for key in UI_KEYS:
        if key in payload and key not in interface:
            interface[key] = payload.pop(key)
        elif key in payload:
            payload.pop(key)
    display_name = interface.get("display_name")
    if not isinstance(display_name, str) or not display_name.strip():
        display_name = title_name(name)
    interface["display_name"] = display_name.strip()
    short = interface.get("short_description")
    if not isinstance(short, str) or not 25 <= len(short.strip()) <= 64:
        short = generated_short_description(interface["display_name"])
    interface["short_description"] = short.strip()
    prompt = interface.get("default_prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        prompt = f"Use ${name} for this task and follow its documented workflow."
    elif f"${name}" not in prompt:
        prompt = f"Use ${name}. {prompt.strip()}"
    interface["default_prompt"] = prompt
    normalized = {"interface": interface, **payload}
    text = yaml.safe_dump(normalized, allow_unicode=True, sort_keys=False, width=1000).rstrip() + "\n"
    return existing_text, text


def trigger_description(name: str, description: str) -> str:
    prefix = f"Use when the user explicitly needs the {name} workflow: "
    if len(prefix) + len(description) <= 1024:
        return prefix + description.strip()
    return description.strip()


def normalize_description_placeholders(description: str) -> str:
    value = re.sub(r"<([A-Za-z][A-Za-z0-9_-]{0,40})>", r"[\1]", description)
    value = re.sub(r"<(\d)", r"less than \1", value)
    return value.replace("<", "[").replace(">", "]")


def heading_positions(text: str) -> list[int]:
    positions: list[int] = []
    in_fence = False
    for index, line in enumerate(text.splitlines()):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#{2,3}\s+\S", line):
            positions.append(index)
    return positions


def anchor_for_heading(value: str) -> str:
    value = re.sub(r"[`*_]", "", value.strip().lower())
    value = re.sub(r"[^\w\-\u4e00-\u9fff ]+", "", value)
    return re.sub(r"\s+", "-", value).strip("-")


def reference_contents(text: str) -> str:
    rows: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if not match:
            continue
        heading = re.sub(r"\s+#+$", "", match.group(2)).strip()
        anchor = anchor_for_heading(heading)
        if anchor:
            indent = "  " if len(match.group(1)) == 3 else ""
            rows.append(f"{indent}- [{heading}](#{anchor})")
        if len(rows) >= 60:
            break
    if not rows:
        return ""
    return "## Contents\n\n" + "\n".join(rows) + "\n\n"


def rewrite_links_for_move(text: str, old_base: Path, new_base: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        destination, suffix = split_destination(match.group(2))
        target = destination_path(old_base, destination)
        if target is None or not target.exists():
            return match.group(0)
        fragment = "#" + destination.split("#", 1)[1] if "#" in destination else ""
        relative = os.path.relpath(target, new_base.resolve(strict=False)).replace(os.sep, "/")
        return f"{match.group(1)}{relative}{fragment}{suffix}{match.group(3)}"

    return LINK_RE.sub(replace, text)


def split_long_skill(text: str, surface: Surface) -> tuple[str, Path, str] | None:
    if line_count(text) <= 500:
        return None
    metadata, body, error = parse_frontmatter(text)
    if error:
        return None
    body_lines = body.splitlines()
    frontmatter_lines = line_count(render_skill(metadata, ""))
    maximum_body_index = 440 - frontmatter_lines
    candidates = [position for position in heading_positions(body) if 80 <= position <= maximum_body_index]
    if not candidates:
        return None
    split_at = max(candidates)
    retained = "\n".join(body_lines[:split_at]).rstrip()
    moved = "\n".join(body_lines[split_at:]).rstrip() + "\n"
    reference = surface.path.parent / "references" / "extended-guidance.md"
    if reference.exists():
        return None
    moved = rewrite_links_for_move(moved, surface.path.parent, reference.parent)
    reference_text = "# Extended Guidance\n\n" + reference_contents(moved) + moved.lstrip()
    relative = os.path.relpath(reference, surface.path.parent).replace(os.sep, "/")
    retained += (
        "\n\n## Extended Guidance\n\n"
        f"Read [extended guidance]({relative}) for detailed procedures, examples, and reference material."
    )
    normalized = render_skill(metadata, retained)
    if line_count(normalized) > 500:
        return None
    return normalized, reference, reference_text.rstrip() + "\n"


def candidate_link_targets(surface: Surface, destination: str, hub: Path) -> list[Path]:
    path_part = destination.split("#", 1)[0]
    if not path_part:
        return []
    stripped = re.sub(r"^(?:\.\./)+", "", path_part)
    values = [
        surface.package / path_part,
        surface.package / "references" / Path(path_part).name,
        hub / "skills" / stripped,
    ]
    if surface.kind == "adapter":
        values.extend([surface.package / stripped, hub / "skills" / stripped])
    unique: list[Path] = []
    for value in values:
        resolved = value.resolve(strict=False)
        if resolved.exists() and resolved not in unique:
            unique.append(resolved)
    return unique


def repair_unique_links(text: str, surface: Surface, hub: Path) -> tuple[str, list[dict[str, str]]]:
    repairs: list[dict[str, str]] = []

    def replace(match: re.Match[str]) -> str:
        destination, suffix = split_destination(match.group(2))
        current = destination_path(surface.path.parent, destination)
        if current is None or current.exists():
            return match.group(0)
        candidates = candidate_link_targets(surface, destination, hub)
        if len(candidates) != 1:
            return match.group(0)
        fragment = "#" + destination.split("#", 1)[1] if "#" in destination else ""
        relative = os.path.relpath(candidates[0], surface.path.parent).replace(os.sep, "/")
        repairs.append({"from": destination, "to": relative + fragment})
        return f"{match.group(1)}{relative}{fragment}{suffix}{match.group(3)}"

    return LINK_RE.sub(replace, text), repairs


def descriptor_for(package: Path) -> dict[str, Any]:
    payload = read_json(package / "skill.json", {}) or {}
    return dict(payload) if isinstance(payload, dict) else {}


def normalize_frontmatter(
    surface: Surface,
    text: str,
    descriptor: dict[str, Any],
) -> tuple[str, list[str]]:
    metadata, body, error = parse_frontmatter(text)
    if error:
        return text, [f"manual:{error}"]
    actions: list[str] = []
    unsupported = {key: metadata[key] for key in metadata if key not in ALLOWED_FRONTMATTER}
    if unsupported:
        metadata = {key: value for key, value in metadata.items() if key in ALLOWED_FRONTMATTER}
        if surface.kind == "adapter":
            relative = surface.path.relative_to(surface.package).as_posix()
            adapter_metadata = descriptor.setdefault("adapter_metadata", {})
            entry = adapter_metadata.setdefault(relative, {})
            legacy = entry.setdefault("legacy_frontmatter", {})
            legacy.update(unsupported)
        else:
            legacy = descriptor.setdefault("legacy_frontmatter", {})
            legacy.update(unsupported)
        actions.append("move-legacy-frontmatter")
    name = metadata.get("name")
    description = metadata.get("description")
    if isinstance(description, str) and ("<" in description or ">" in description):
        metadata["description"] = normalize_description_placeholders(description)
        description = metadata["description"]
        actions.append("normalize-description-placeholders")
    if isinstance(name, str) and isinstance(description, str) and description.strip() and not has_trigger(description):
        updated = trigger_description(name, description)
        if updated != description:
            metadata["description"] = updated
            actions.append("add-description-trigger")
    rendered = render_skill(metadata, body)
    return rendered, actions


def normalize_auxiliary_root_file(
    surface: Surface,
    skill_text: str,
) -> tuple[str, list[tuple[Path, Path, str]]]:
    if surface.kind not in {"canonical", "hermes-local"}:
        return skill_text, []
    moves: list[tuple[Path, Path, str]] = []
    for source in sorted(surface.package.iterdir()):
        if not source.is_file() or source.name not in AUXILIARY_ROOT_FILES:
            continue
        stem = source.stem.lower().replace("_", "-")
        target = surface.package / "references" / f"{stem}-notes.md"
        if target.exists():
            continue
        content = source.read_text(encoding="utf-8")
        content = rewrite_links_for_move(content, source.parent, target.parent)
        moves.append((source, target, content.rstrip() + "\n"))
        relative = os.path.relpath(target, surface.path.parent).replace(os.sep, "/")
        label = source.stem.replace("_", " ").title()
        skill_text = skill_text.rstrip() + f"\n\n## Additional Reference\n\nRead [{label} notes]({relative}) when the packaged examples or background details are needed.\n"
    return skill_text, moves


def normalize_all(hub: Path, hermes_root: Path, include_hermes: bool, apply: bool) -> dict[str, Any]:
    effective_hermes = hermes_root if include_hermes else Path("/__skill_quality_no_hermes__")
    surfaces = collect_surfaces(hub, effective_hermes)
    descriptors = {surface.package: descriptor_for(surface.package) for surface in surfaces}
    actions: list[dict[str, Any]] = []
    manual: list[dict[str, str]] = []
    for surface in surfaces:
        original = surface.path.read_text(encoding="utf-8")
        descriptor = descriptors[surface.package]
        updated, frontmatter_actions = normalize_frontmatter(surface, original, descriptor)
        for action in frontmatter_actions:
            if action.startswith("manual:"):
                manual.append({"path": str(surface.path), "reason": action.removeprefix("manual:")})
            else:
                actions.append({"action": action, "path": str(surface.path)})
        updated, repairs = repair_unique_links(updated, surface, hub)
        for repair in repairs:
            actions.append({"action": "repair-relative-link", "path": str(surface.path), **repair})
        updated, moves = normalize_auxiliary_root_file(surface, updated)
        for source, target, content in moves:
            actions.append({"action": "move-auxiliary-doc", "path": str(source), "target": str(target)})
            if apply:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                source.unlink()
        split = split_long_skill(updated, surface)
        if split:
            updated, reference, reference_text = split
            actions.append({"action": "split-long-skill", "path": str(surface.path), "target": str(reference)})
            if apply:
                reference.parent.mkdir(parents=True, exist_ok=True)
                reference.write_text(reference_text, encoding="utf-8")
        elif line_count(updated) > 500:
            manual.append({"path": str(surface.path), "reason": "no-safe-heading-for-progressive-disclosure"})
        if updated != original:
            actions.append({"action": "rewrite-skill", "path": str(surface.path)})
            if apply:
                surface.path.write_text(updated, encoding="utf-8")
        if surface.kind in {"canonical", "hermes-local"}:
            metadata, _, _ = parse_frontmatter(updated)
            name = metadata.get("name") if isinstance(metadata.get("name"), str) else surface.package.name
            previous, normalized = normalized_openai(surface.package, name)
            if previous != normalized:
                openai_path = surface.package / "agents" / "openai.yaml"
                actions.append({"action": "normalize-openai-yaml", "path": str(openai_path)})
                if apply:
                    openai_path.parent.mkdir(parents=True, exist_ok=True)
                    openai_path.write_text(normalized, encoding="utf-8")
    for package, descriptor in descriptors.items():
        if not descriptor:
            skill_text = (package / "SKILL.md").read_text(encoding="utf-8")
            metadata, _, _ = parse_frontmatter(skill_text)
            name = metadata.get("name") if isinstance(metadata.get("name"), str) else package.name
            descriptor.update(
                {
                    "version": 1,
                    "id": name,
                    "name": name,
                    "source_runtimes": ["hermes-local"],
                    "source_variants": [],
                    "adapters": {},
                }
            )
        descriptor_path = package / "skill.json"
        previous = descriptor_path.read_text(encoding="utf-8") if descriptor_path.is_file() else ""
        normalized = json.dumps(descriptor, ensure_ascii=False, indent=2) + "\n"
        if previous != normalized:
            actions.append({"action": "update-skill-json", "path": str(descriptor_path)})
            if apply:
                descriptor_path.write_text(normalized, encoding="utf-8")
    return {
        "version": 1,
        "hub": str(hub),
        "apply": apply,
        "include_hermes": include_hermes,
        "surface_count": len(surfaces),
        "action_count": len(actions),
        "manual_count": len(manual),
        "action_types": dict(sorted(Counter(item["action"] for item in actions).items())),
        "actions": actions,
        "manual": manual,
    }


def paths_from_args(hub: Path | None = None) -> tuple[Path, Path, Path, Path]:
    selected_hub = (hub or default_hub()).expanduser().resolve()
    return (
        selected_hub,
        Path("/Users/heytea/.hermes/skills"),
        Path("/Users/heytea/.codex/skills/.system"),
        Path("/Users/heytea/.codex/plugins/cache"),
    )


def ensure_parent(paths: Iterable[Path]) -> None:
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
