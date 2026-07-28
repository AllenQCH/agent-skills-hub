#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


HUB = Path(__file__).resolve().parents[1]
HUB_SKILLS = HUB / "skills"
HERMES_SKILLS = Path("/Users/heytea/.hermes/skills")
USAGE_FILE = HERMES_SKILLS / ".usage.json"
STATE_FILE = Path("/Users/heytea/.codex/agent-catalog-runtime/skill_review_state.json")
QUEUE_FILE = Path("/Users/heytea/.codex/agent-catalog-runtime/skill_review_queue.json")
INTERVAL = timedelta(hours=72)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def local_skill_packages() -> list[Path]:
    result = []
    for skill_file in HERMES_SKILLS.rglob("SKILL.md"):
        relative = skill_file.relative_to(HERMES_SKILLS)
        if any(part.startswith(".") for part in relative.parts):
            continue
        package = skill_file.parent
        resolved = str(package.resolve())
        if package.is_symlink() or resolved.startswith(str(HUB.resolve()) + os.sep):
            continue
        result.append(package)
    return sorted(set(result))


def candidate_for(package: Path, usage: dict, current: datetime) -> dict:
    name = package.name
    record = usage.get(name, {})
    last_used = parse_time(record.get("last_used_at"))
    age_days = (current - last_used).days if last_used else None
    use_count = int(record.get("use_count") or 0)
    if (HUB_SKILLS / name).exists():
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
        "promotion_target": str(HUB_SKILLS / name),
        "requires_human_approval": True,
    }


def due(state: dict, current: datetime) -> bool:
    last_review = parse_time(state.get("last_review_at"))
    return last_review is None or current - last_review >= INTERVAL


def run(force: bool) -> int:
    current = now_utc()
    state = load_json(STATE_FILE, {})
    if not force and not due(state, current):
        print(json.dumps({"status": "not-due", "next_review_at": state.get("next_review_at")}))
        return 0
    usage = load_json(USAGE_FILE, {})
    candidates = [candidate_for(package, usage, current) for package in local_skill_packages()]
    queue = {
        "version": 3,
        "generated_at": current.isoformat(),
        "interval_hours": 72,
        "mode": "read-only",
        "candidates": candidates,
    }
    next_review = current + INTERVAL
    STATE_FILE.write_text(
        json.dumps({"last_review_at": current.isoformat(), "next_review_at": next_review.isoformat()}, indent=2) + "\n",
        encoding="utf-8",
    )
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "generated", "queue": str(QUEUE_FILE), "candidates": len(candidates)}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a read-only shared-Hub promotion queue.")
    parser.add_argument("--force", action="store_true", help="ignore the 72-hour interval")
    args = parser.parse_args()
    return run(args.force)


if __name__ == "__main__":
    raise SystemExit(main())
