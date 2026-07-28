#!/usr/bin/env python3

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


STATE_DIR = Path(
    os.environ.get(
        "HEYTEA_PROJECT_STACK_STATE_DIR",
        "~/.codex/state/heytea-project-stack",
    )
).expanduser()
PROJECT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
REPOSITORY_TYPES = {"maven_dependency", "deployable_service"}
SENSITIVE_KEY_PARTS = ("password", "secret", "token", "credential")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def manifest_path(project: str) -> Path:
    if not PROJECT_RE.fullmatch(project):
        fail(f"invalid project id: {project}")
    return STATE_DIR / f"{project}.json"


def load_manifest(project: str) -> Tuple[Path, Dict[str, Any]]:
    path = manifest_path(project)
    if not path.is_file():
        fail(f"project manifest not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read manifest {path}: {exc}")
    if not isinstance(data, dict):
        fail("manifest root must be an object")
    return path, data


def find_sensitive_keys(value: Any, prefix: str = "") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            current = f"{prefix}.{key}" if prefix else str(key)
            lowered = str(key).lower()
            if any(part in lowered for part in SENSITIVE_KEY_PARTS):
                yield current
            yield from find_sensitive_keys(child, current)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from find_sensitive_keys(child, f"{prefix}[{index}]")


def workspace_path(manifest: Dict[str, Any]) -> Path:
    workspace = manifest.get("workspace")
    if not isinstance(workspace, str) or not workspace:
        fail("manifest.workspace must be a non-empty string")
    return Path(workspace).expanduser()


def repositories(manifest: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    value = manifest.get("repositories")
    if not isinstance(value, dict) or not value:
        fail("manifest.repositories must be a non-empty object")
    for name, config in value.items():
        if not isinstance(config, dict):
            fail(f"repository config must be an object: {name}")
        repo_type = config.get("type")
        if repo_type not in REPOSITORY_TYPES:
            fail(f"invalid repository type for {name}: {repo_type}")
    return value


def direct_git_repositories(workspace: Path) -> List[str]:
    if not workspace.is_dir():
        fail(f"workspace not found: {workspace}")
    return sorted(
        child.name
        for child in workspace.iterdir()
        if child.is_dir() and (child / ".git").exists()
    )


def validate_data(manifest: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    sensitive = list(find_sensitive_keys(manifest))
    if sensitive:
        errors.append("sensitive manifest keys are forbidden: " + ", ".join(sensitive))

    workspace = workspace_path(manifest)
    registered = set(repositories(manifest))
    actual = set(direct_git_repositories(workspace))
    missing = sorted(actual - registered)
    stale = sorted(registered - actual)
    if missing:
        errors.append("unregistered repositories: " + ", ".join(missing))
    if stale:
        errors.append("registered repositories missing from workspace: " + ", ".join(stale))

    dependency_names = sorted(
        name
        for name, config in repositories(manifest).items()
        if config.get("type") == "maven_dependency"
    )
    declared = sorted(manifest.get("dependencyPackages", []))
    if declared != dependency_names:
        errors.append(
            "dependencyPackages does not match repository types: "
            f"declared={declared}, typed={dependency_names}"
        )
    return errors


def command_inventory(manifest: Dict[str, Any]) -> None:
    print(f"PROJECT: {manifest.get('project')} ({manifest.get('displayName')})")
    print(f"WORKSPACE: {workspace_path(manifest)}")
    print(f"{'REPOSITORY':34} {'TYPE':20} {'LOCAL':18} {'REMOTE'}")
    for name, config in sorted(repositories(manifest).items()):
        print(
            f"{name:34} {config['type']:20} "
            f"{config.get('localAction', '-'):18} {config.get('remoteAction', '-')}"
        )


def command_validate(manifest: Dict[str, Any]) -> None:
    errors = validate_data(manifest)
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("VALID: manifest matches the current direct child repositories")


def default_repository_config(manifest: Dict[str, Any]) -> Dict[str, Any]:
    repo_type = manifest.get("defaultRepositoryType")
    if repo_type != "deployable_service":
        fail("automatic sync requires defaultRepositoryType=deployable_service")
    return {
        "type": "deployable_service",
        "localAction": "local_start",
        "remoteAction": "service_deploy",
        "localRuntime": "discovery_required",
    }


def write_manifest_atomic(path: Path, manifest: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(path.parent),
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def command_sync(path: Path, manifest: Dict[str, Any], apply: bool) -> None:
    workspace = workspace_path(manifest)
    configured = repositories(manifest)
    actual = direct_git_repositories(workspace)
    missing = [name for name in actual if name not in configured]
    stale = [name for name in configured if name not in actual]
    if stale:
        fail("refusing sync because configured repositories are missing: " + ", ".join(stale))
    if not missing:
        print("SYNC: no new direct child repositories")
        return
    print("SYNC CANDIDATES:")
    for name in missing:
        print(f"- {name}: deployable_service (local runtime discovery required)")
    if not apply:
        print("DRY RUN: rerun with --apply after project classification is confirmed")
        return
    for name in missing:
        configured[name] = default_repository_config(manifest)
    manifest["repositories"] = dict(sorted(configured.items()))
    write_manifest_atomic(path, manifest)
    print(f"APPLIED: registered {len(missing)} repositories in {path}")


def action_for(config: Dict[str, Any], mode: str) -> str:
    key = "localAction" if mode == "local" else "remoteAction"
    value = config.get(key)
    if not isinstance(value, str) or not value:
        fail(f"missing {key}")
    return value


def command_plan(manifest: Dict[str, Any], mode: str, changed: List[str]) -> None:
    repo_configs = repositories(manifest)
    unknown = [name for name in changed if name not in repo_configs]
    if unknown:
        fail("unknown changed repositories: " + ", ".join(unknown))
    unique_changed = list(dict.fromkeys(changed))
    ordered = sorted(
        unique_changed,
        key=lambda name: 0 if repo_configs[name]["type"] == "maven_dependency" else 1,
    )
    print(f"PLAN: project={manifest.get('project')} mode={mode}")
    for index, name in enumerate(ordered, start=1):
        config = repo_configs[name]
        action = action_for(config, mode)
        command = config.get("commands", {}).get(mode)
        suffix = f" | {command}" if command else ""
        print(f"{index}. {name}: {action}{suffix}")
        if config["type"] == "maven_dependency":
            consumers = config.get("consumers", [])
            if consumers:
                print("   affected consumer candidates: " + ", ".join(consumers))
    if mode == "remote":
        print("NOTE: execute artifact_publish before affected service_deploy actions")


def launcher_script(manifest: Dict[str, Any]) -> Path:
    launcher = manifest.get("localLauncher")
    if not isinstance(launcher, dict):
        fail("local launcher is not registered")
    script = launcher.get("script")
    if not isinstance(script, str) or not script:
        fail("localLauncher.script must be a non-empty string")
    path = Path(script).expanduser()
    if not path.is_file() or not os.access(path, os.X_OK):
        fail(f"local launcher is not executable: {path}")
    return path


def command_status(manifest: Dict[str, Any]) -> None:
    result = subprocess.run([str(launcher_script(manifest)), "status"], check=False)
    raise SystemExit(result.returncode)


def command_start(manifest: Dict[str, Any], target: str, auth_bypass: bool) -> None:
    targets = manifest.get("localTargets", {})
    if target not in targets:
        fail(f"unknown local target {target}; registered targets: {', '.join(sorted(targets))}")
    command = [str(launcher_script(manifest)), "start", target]
    if auth_bypass:
        command.append("--auth-bypass")
    result = subprocess.run(command, check=False)
    raise SystemExit(result.returncode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage registered HeyTea project stacks")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("inventory", "validate", "status"):
        command = subparsers.add_parser(name)
        command.add_argument("project")
    sync = subparsers.add_parser("sync")
    sync.add_argument("project")
    sync.add_argument("--apply", action="store_true")
    plan = subparsers.add_parser("plan")
    plan.add_argument("project")
    plan.add_argument("--mode", choices=("local", "remote"), required=True)
    plan.add_argument("changed", nargs="+")
    start = subparsers.add_parser("start")
    start.add_argument("project")
    start.add_argument("target")
    start.add_argument("--auth-bypass", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    path, manifest = load_manifest(args.project)
    if args.command == "inventory":
        command_inventory(manifest)
    elif args.command == "validate":
        command_validate(manifest)
    elif args.command == "sync":
        command_sync(path, manifest, args.apply)
    elif args.command == "plan":
        command_plan(manifest, args.mode, args.changed)
    elif args.command == "status":
        command_status(manifest)
    elif args.command == "start":
        command_start(manifest, args.target, args.auth_bypass)


if __name__ == "__main__":
    main()

