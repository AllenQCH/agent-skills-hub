#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator
from zoneinfo import ZoneInfo


HUB = Path(__file__).resolve().parents[1]
HUB_SKILLS = HUB / "skills"
HERMES_SKILLS = Path("/Users/heytea/.hermes/skills")
USAGE_FILE = HERMES_SKILLS / ".usage.json"
RUNTIME_ROOT = Path("/Users/heytea/.codex/agent-catalog-runtime")
STATE_FILE = RUNTIME_ROOT / "skill_review_state.json"
QUEUE_FILE = RUNTIME_ROOT / "skill_review_queue.json"
REPORT_ROOT = RUNTIME_ROOT / "skill-quality-review"
LOCK_DIR = RUNTIME_ROOT / "skill_review.lock"
BACKUP_ROOT = Path("/Users/heytea/Documents/myHeytea/code/agent-skills-hub-backups/scheduled")
QUALITY_PACKAGE = HUB_SKILLS / "skill-quality-review"
AUDIT_SCRIPT = QUALITY_PACKAGE / "scripts" / "audit_skill_quality.py"
NORMALIZE_SCRIPT = QUALITY_PACKAGE / "scripts" / "normalize_skill_quality.py"
VALIDATOR = Path("/Users/heytea/.codex/skills/.system/skill-creator/scripts/quick_validate.py")
LOCK_STALE_AFTER = timedelta(hours=6)
IGNORED_TREE_NAMES = {".git", "reports", "__pycache__", ".DS_Store"}
REVIEW_TIMEZONE_NAME = "Asia/Shanghai"
REVIEW_TIMEZONE = ZoneInfo(REVIEW_TIMEZONE_NAME)
REVIEW_WEEKDAYS = (0, 4)
REVIEW_HOUR = 10
REVIEW_MINUTE = 0


class ReviewError(RuntimeError):
    pass


class ReviewBusy(ReviewError):
    pass


class CommandError(ReviewError):
    def __init__(self, command: list[str], returncode: int, output: str):
        self.command = command
        self.returncode = returncode
        self.output = output
        super().__init__(f"command failed ({returncode}): {' '.join(command)}")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def next_review_after(current: datetime) -> datetime:
    if current.tzinfo is None:
        raise ValueError("review schedule requires a timezone-aware datetime")
    local_current = current.astimezone(REVIEW_TIMEZONE)
    for day_offset in range(8):
        candidate = (local_current + timedelta(days=day_offset)).replace(
            hour=REVIEW_HOUR,
            minute=REVIEW_MINUTE,
            second=0,
            microsecond=0,
        )
        if candidate.weekday() in REVIEW_WEEKDAYS and candidate > local_current:
            return candidate.astimezone(timezone.utc)
    raise ReviewError("unable to calculate the next Skill review schedule")


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default
    return payload if isinstance(payload, dict) else default


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def local_skill_packages(root: Path = HERMES_SKILLS, hub: Path = HUB) -> list[Path]:
    result: list[Path] = []
    if not root.is_dir():
        return result
    hub_prefix = str(hub.resolve()) + os.sep
    for skill_file in root.rglob("SKILL.md"):
        relative = skill_file.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        package = skill_file.parent
        resolved = str(package.resolve())
        if package.is_symlink() or resolved.startswith(hub_prefix):
            continue
        result.append(package)
    return sorted(set(result))


def candidate_for(package: Path, usage: dict[str, Any], current: datetime, hub_skills: Path = HUB_SKILLS) -> dict[str, Any]:
    name = package.name
    record = usage.get(name, {})
    record = record if isinstance(record, dict) else {}
    last_used = parse_time(record.get("last_used_at"))
    age_days = (current - last_used).days if last_used else None
    use_count = int(record.get("use_count") or 0)
    if (hub_skills / name).exists():
        recommendation = "review-as-update-or-adapter"
    elif use_count >= 2:
        recommendation = "review-for-shared-hub"
    elif age_days is not None and age_days >= 30:
        recommendation = "keep-local-stale"
    else:
        recommendation = "keep-local-observe"
    return {
        "name": name,
        "path": str(package),
        "state": record.get("state", "untracked"),
        "use_count": use_count,
        "last_used_at": record.get("last_used_at"),
        "recommendation": recommendation,
        "promotion_target": str(hub_skills / name),
        "requires_human_approval": True,
    }


def due(state: dict[str, Any], current: datetime) -> bool:
    next_review = parse_time(state.get("next_review_at"))
    if next_review is not None:
        return current >= next_review
    last_review = parse_time(state.get("last_review_at"))
    return last_review is None or current >= next_review_after(last_review)


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def lock_is_stale(owner: dict[str, Any], current: datetime) -> bool:
    pid = int(owner.get("pid") or 0)
    started_at = parse_time(owner.get("started_at"))
    age_expired = started_at is None or current - started_at >= LOCK_STALE_AFTER
    return not process_is_alive(pid) and age_expired


@contextmanager
def review_lock(current: datetime) -> Iterator[None]:
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    try:
        LOCK_DIR.mkdir()
    except FileExistsError:
        owner = load_json(LOCK_DIR / "owner.json", {})
        if not lock_is_stale(owner, current):
            raise ReviewBusy(f"skill review already running: {owner}")
        shutil.rmtree(LOCK_DIR)
        LOCK_DIR.mkdir()
    write_json(LOCK_DIR / "owner.json", {"pid": os.getpid(), "started_at": current.isoformat()})
    try:
        yield
    finally:
        shutil.rmtree(LOCK_DIR, ignore_errors=True)


def run_command(
    command: list[str],
    cwd: Path,
    log_path: Path,
    allowed_returncodes: tuple[int, ...] = (0,),
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"$ {' '.join(command)}\n")
        if result.stdout:
            handle.write(result.stdout)
            if not result.stdout.endswith("\n"):
                handle.write("\n")
        if result.stderr:
            handle.write(result.stderr)
            if not result.stderr.endswith("\n"):
                handle.write("\n")
        handle.write(f"[exit={result.returncode}]\n\n")
    if result.returncode not in allowed_returncodes:
        output = (result.stderr or result.stdout).strip()
        raise CommandError(command, result.returncode, output)
    return result


def quality_command(
    script: Path,
    hub: Path,
    hermes_root: Path,
    extra: list[str],
    log_path: Path,
    allowed_returncodes: tuple[int, ...] = (0,),
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(script), "--hub", str(hub), "--hermes-root", str(hermes_root), *extra]
    return run_command(command, hub, log_path, allowed_returncodes)


def set_writable_tree(root: Path, writable: bool) -> int:
    changed = 0
    paths = [root, *root.rglob("*")]
    for path in sorted(paths, key=lambda item: len(item.parts), reverse=not writable):
        if path.is_symlink():
            continue
        mode = stat.S_IMODE(path.stat().st_mode)
        target = mode | stat.S_IWUSR if writable else mode & ~0o222
        if target != mode:
            path.chmod(target)
            changed += 1
    return changed


def ignored_path(path: Path) -> bool:
    return any(part in IGNORED_TREE_NAMES for part in path.parts) or path.suffix == ".pyc"


def tree_digest(hub: Path, hermes_root: Path) -> str:
    digest = hashlib.sha256()
    roots = [("hub", hub), *[(f"hermes:{package.relative_to(hermes_root).as_posix()}", package) for package in local_skill_packages(hermes_root, hub)]]
    for label, root in roots:
        if not root.exists():
            continue
        for path in sorted([root, *root.rglob("*")]):
            relative = path.relative_to(root)
            if ignored_path(relative):
                continue
            name = f"{label}/{relative.as_posix()}"
            digest.update(name.encode("utf-8"))
            digest.update(b"\0")
            if path.is_symlink():
                digest.update(b"link\0")
                digest.update(os.readlink(path).encode("utf-8"))
            elif path.is_file():
                digest.update(b"file\0")
                with path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(chunk)
            else:
                digest.update(b"dir\0")
            digest.update(b"\0")
    return digest.hexdigest()


def copy_for_staging(stage_root: Path) -> tuple[Path, Path]:
    stage_hub = stage_root / "hub"
    shutil.copytree(
        HUB,
        stage_hub,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git", "reports", "__pycache__", "*.pyc", ".DS_Store"),
    )
    stage_hermes = stage_root / "hermes-skills"
    stage_hermes.mkdir(parents=True)
    for package in local_skill_packages():
        relative = package.relative_to(HERMES_SKILLS)
        target = stage_hermes / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(package, target, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    set_writable_tree(stage_hub / "skills", True)
    set_writable_tree(stage_hermes, True)
    return stage_hub, stage_hermes


def skill_files(hub: Path, hermes_root: Path) -> list[Path]:
    files = sorted(path for path in (hub / "skills").rglob("SKILL.md") if path.is_file())
    for package in local_skill_packages(hermes_root, hub):
        files.append(package / "SKILL.md")
    return sorted(set(files))


def validate_skill_files(hub: Path, hermes_root: Path, log_path: Path) -> int:
    files = skill_files(hub, hermes_root)
    for path in files:
        run_command([sys.executable, str(VALIDATOR), str(path.parent)], hub, log_path)
    return len(files)


def assert_golden_searches(hub: Path, log_path: Path) -> None:
    cases = {
        "查询国内数据库": "dbauto-sql-query",
        "维护 multi-agent 和 skill hub": "multi-agent-framework-maintainer",
        "全量整理和审查 skills": "skill-quality-review",
    }
    for query, expected in cases.items():
        result = run_command(
            [sys.executable, str(hub / "bin" / "skillctl.py"), "search", "--query", query, "--limit", "5"],
            hub,
            log_path,
        )
        payload = json.loads(result.stdout)
        candidates = payload.get("candidates", [])
        actual = candidates[0].get("name") if candidates else None
        if actual != expected:
            raise ReviewError(f"golden search mismatch for {query!r}: expected {expected}, got {actual}")


def audit(
    hub: Path,
    hermes_root: Path,
    json_out: Path,
    markdown_out: Path,
    log_path: Path,
    fail_on_issues: bool = False,
) -> dict[str, Any]:
    extra = ["--json-out", str(json_out), "--markdown-out", str(markdown_out)]
    if fail_on_issues:
        extra.append("--fail-on-issues")
    quality_command(AUDIT_SCRIPT, hub, hermes_root, extra, log_path)
    return load_json(json_out, {})


def normalize(
    hub: Path,
    hermes_root: Path,
    json_out: Path,
    log_path: Path,
    apply: bool,
) -> dict[str, Any]:
    extra = ["--include-hermes", "--json-out", str(json_out)]
    if apply:
        extra.append("--apply")
    quality_command(NORMALIZE_SCRIPT, hub, hermes_root, extra, log_path, (0, 1))
    payload = load_json(json_out, {})
    if not payload:
        raise ReviewError(f"normalization report missing or invalid: {json_out}")
    return payload


def create_backup(timestamp: str, log_path: Path) -> Path:
    backup = BACKUP_ROOT / timestamp
    backup.mkdir(parents=True, exist_ok=False)
    with tarfile.open(backup / "hub-state.tar.gz", "w:gz") as archive:
        for relative in ("skills", "registry", "manifests"):
            archive.add(HUB / relative, arcname=relative, recursive=True)
    with tarfile.open(backup / "hermes-local-skills.tar.gz", "w:gz") as archive:
        for package in local_skill_packages():
            archive.add(package, arcname=package.relative_to(HERMES_SKILLS), recursive=True)
    status = run_command(["git", "status", "--short"], HUB, log_path)
    (backup / "git-status.txt").write_text(status.stdout, encoding="utf-8")
    head = run_command(["git", "rev-parse", "HEAD"], HUB, log_path)
    (backup / "git-head.txt").write_text(head.stdout, encoding="utf-8")
    return backup


def validate_staging(hub: Path, hermes_root: Path, run_dir: Path, log_path: Path) -> dict[str, Any]:
    run_command([sys.executable, str(hub / "bin" / "skillctl.py"), "build"], hub, log_path)
    after = audit(
        hub,
        hermes_root,
        run_dir / "staging-audit-after.json",
        run_dir / "staging-audit-after.md",
        log_path,
        fail_on_issues=True,
    )
    validated = validate_skill_files(hub, hermes_root, log_path)
    run_command([sys.executable, str(hub / "bin" / "skillctl.py"), "scan"], hub, log_path)
    run_command([sys.executable, "-m", "unittest", "tests.test_skill_quality", "-v"], hub, log_path)
    assert_golden_searches(hub, log_path)
    set_writable_tree(hub / "skills", False)
    run_command([sys.executable, str(hub / "bin" / "skill_hub.py"), "verify"], hub, log_path)
    return {"audit": after.get("summary", {}), "validated_surfaces": validated}


def validate_live(run_dir: Path, log_path: Path) -> dict[str, Any]:
    after = audit(
        HUB,
        HERMES_SKILLS,
        run_dir / "audit-after.json",
        run_dir / "audit-after.md",
        log_path,
        fail_on_issues=True,
    )
    validated = validate_skill_files(HUB, HERMES_SKILLS, log_path)
    run_command([sys.executable, str(HUB / "bin" / "skillctl.py"), "scan"], HUB, log_path)
    run_command([sys.executable, str(HUB / "bin" / "skillctl.py"), "verify"], HUB, log_path)
    run_command([sys.executable, str(HUB / "bin" / "skill_hub.py"), "verify"], HUB, log_path)
    run_command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], HUB, log_path)
    for runtime in ("codex", "claude", "hermes"):
        run_command([sys.executable, str(HUB / "bin" / "skillctl.py"), "doctor", "--runtime", runtime], HUB, log_path)
    assert_golden_searches(HUB, log_path)
    return {"audit": after.get("summary", {}), "validated_surfaces": validated}


def build_promotion_queue(current: datetime) -> dict[str, Any]:
    usage = load_json(USAGE_FILE, {})
    candidates = [candidate_for(package, usage, current) for package in local_skill_packages()]
    return {
        "version": 5,
        "generated_at": current.isoformat(),
        "schedule": {
            "timezone": REVIEW_TIMEZONE_NAME,
            "weekdays": ["monday", "friday"],
            "time": "10:00",
        },
        "mode": "quality-auto-local-no-vcs",
        "candidates": candidates,
    }


def quality_cycle(current: datetime, run_dir: Path, audit_only: bool) -> dict[str, Any]:
    log_path = run_dir / "commands.log"
    before = audit(HUB, HERMES_SKILLS, run_dir / "audit-before.json", run_dir / "audit-before.md", log_path)
    plan = normalize(HUB, HERMES_SKILLS, run_dir / "normalization-plan.json", log_path, apply=False)
    result: dict[str, Any] = {
        "before": before.get("summary", {}),
        "plan": {
            "action_count": int(plan.get("action_count") or 0),
            "manual_count": int(plan.get("manual_count") or 0),
            "action_types": plan.get("action_types", {}),
        },
        "artifact_paths": [str(run_dir)],
    }
    if audit_only:
        result.update({"status": "audit-only", "schedule_advanced": False})
        return result
    if result["plan"]["manual_count"]:
        result.update({"status": "pending", "reason": "manual-review-required"})
        return result
    if not result["plan"]["action_count"]:
        result["validation"] = validate_live(run_dir, log_path)
        result.update({"status": "no-changes", "backup": None})
        return result

    live_digest = tree_digest(HUB, HERMES_SKILLS)
    with tempfile.TemporaryDirectory(prefix="skill-quality-stage-") as temporary:
        stage_hub, stage_hermes = copy_for_staging(Path(temporary))
        try:
            stage_plan = normalize(stage_hub, stage_hermes, run_dir / "staging-normalization-plan.json", log_path, apply=False)
            if int(stage_plan.get("manual_count") or 0):
                result.update({"status": "pending", "reason": "staging-manual-review-required"})
                return result
            stage_result = normalize(stage_hub, stage_hermes, run_dir / "staging-normalization-result.json", log_path, apply=True)
            if int(stage_result.get("action_count") or 0) != result["plan"]["action_count"]:
                raise ReviewError("staging action count differs from the approved deterministic plan")
            result["staging_validation"] = validate_staging(stage_hub, stage_hermes, run_dir, log_path)
        finally:
            set_writable_tree(stage_hub / "skills", True)

    if tree_digest(HUB, HERMES_SKILLS) != live_digest:
        raise ReviewError("managed Skill inputs changed during staging; live apply aborted")

    timestamp = current.astimezone().strftime("%Y%m%dT%H%M%S%f%z")
    backup = create_backup(timestamp, log_path)
    result["backup"] = str(backup)
    try:
        set_writable_tree(HUB_SKILLS, True)
        applied = normalize(HUB, HERMES_SKILLS, run_dir / "normalization-result.json", log_path, apply=True)
        if int(applied.get("action_count") or 0) != result["plan"]["action_count"]:
            raise ReviewError("live action count differs from the staged deterministic plan")
        run_command([sys.executable, str(HUB / "bin" / "skillctl.py"), "build"], HUB, log_path)
    finally:
        set_writable_tree(HUB_SKILLS, False)
    result["validation"] = validate_live(run_dir, log_path)
    result.update({"status": "applied", "after_digest": tree_digest(HUB, HERMES_SKILLS)})
    return result


def state_after_result(state: dict[str, Any], current: datetime, result: dict[str, Any]) -> dict[str, Any]:
    next_review = next_review_after(current)
    updated = dict(state)
    updated.update(
        {
            "version": 5,
            "last_attempt_at": current.isoformat(),
            "last_review_at": current.isoformat(),
            "next_review_at": next_review.isoformat(),
            "last_status": result.get("status"),
            "last_artifact_paths": result.get("artifact_paths", []),
            "last_backup": result.get("backup"),
        }
    )
    if result.get("status") in {"applied", "no-changes"}:
        updated["last_success_at"] = current.isoformat()
    return updated


def state_after_failure(state: dict[str, Any], current: datetime, error: Exception, run_dir: Path) -> dict[str, Any]:
    updated = dict(state)
    updated.update(
        {
            "version": 5,
            "last_attempt_at": current.isoformat(),
            "next_review_at": next_review_after(current).isoformat(),
            "last_status": "failed",
            "last_error": str(error),
            "last_artifact_paths": [str(run_dir)],
        }
    )
    return updated


def run(force: bool, audit_only: bool) -> int:
    current = now_utc()
    state = load_json(STATE_FILE, {})
    if not force and not due(state, current):
        print(json.dumps({"status": "not-due", "next_review_at": state.get("next_review_at")}))
        return 0
    try:
        with review_lock(current):
            state = load_json(STATE_FILE, {})
            if not force and not due(state, current):
                print(json.dumps({"status": "not-due", "next_review_at": state.get("next_review_at")}))
                return 0
            timestamp = current.astimezone().strftime("%Y%m%dT%H%M%S%f%z")
            run_dir = REPORT_ROOT / timestamp
            run_dir.mkdir(parents=True, exist_ok=False)
            write_json(QUEUE_FILE, build_promotion_queue(current))
            try:
                result = quality_cycle(current, run_dir, audit_only)
                write_json(run_dir / "result.json", result)
                write_json(REPORT_ROOT / "latest.json", result)
                if not audit_only:
                    write_json(STATE_FILE, state_after_result(state, current, result))
                print(json.dumps(result, ensure_ascii=False))
                return 0
            except Exception as exc:
                failure = {
                    "status": "failed",
                    "error": str(exc),
                    "artifact_paths": [str(run_dir)],
                    "schedule_advanced": not audit_only,
                }
                write_json(run_dir / "result.json", failure)
                write_json(REPORT_ROOT / "latest.json", failure)
                if not audit_only:
                    write_json(STATE_FILE, state_after_failure(state, current, exc, run_dir))
                print(json.dumps(failure, ensure_ascii=False))
                return 1
    except ReviewBusy as exc:
        print(json.dumps({"status": "busy", "error": str(exc)}, ensure_ascii=False))
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the governed Monday/Friday shared Skill quality review.")
    parser.add_argument("--force", action="store_true", help="ignore the scheduled due gate")
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="generate audit and normalization-plan evidence without applying changes or advancing the schedule",
    )
    args = parser.parse_args()
    return run(args.force, args.audit_only)


if __name__ == "__main__":
    raise SystemExit(main())
