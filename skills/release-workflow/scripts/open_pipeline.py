#!/usr/bin/env python3
"""Resolve and open a configured pipeline URL."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


MAP_PATH = Path(__file__).parents[1] / "references/pipeline-map.json"


def resolve(mapping: dict, project: str, service: str | None, env: str | None, branch: str | None) -> str:
    project_cfg = mapping.get("projects", {}).get(project)
    if not project_cfg:
        raise SystemExit(f"No pipeline mapping for project: {project}")

    entry = None
    if service:
        entry = project_cfg.get("services", {}).get(service)
    if entry is None:
        entry = project_cfg.get("default")
    if not entry:
        raise SystemExit(f"No pipeline mapping for project/service: {project}/{service or '-'}")

    url = entry.get("url") or ""
    if not url:
        raise SystemExit(f"Pipeline URL is not configured for project/service: {project}/{service or '-'}")

    values = {
        "project": project,
        "service": service or "",
        "env": env or "",
        "branch": branch or "",
    }
    return url.format(**values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--service")
    parser.add_argument("--env")
    parser.add_argument("--branch")
    parser.add_argument("--print-only", action="store_true")
    args = parser.parse_args()

    mapping = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    url = resolve(mapping, args.project, args.service, args.env, args.branch)
    print(url)
    if not args.print_only:
        subprocess.run(["open", url], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
