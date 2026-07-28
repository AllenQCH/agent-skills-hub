#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from qualitylib import audit_all, markdown_report, paths_from_args, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit shared and local Skill quality without changing files.")
    parser.add_argument("--hub", type=Path)
    parser.add_argument("--hermes-root", type=Path)
    parser.add_argument("--system-root", type=Path)
    parser.add_argument("--plugin-root", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--fail-on-issues", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hub, hermes, system, plugin = paths_from_args(args.hub)
    report = audit_all(
        hub,
        (args.hermes_root or hermes).expanduser(),
        (args.system_root or system).expanduser(),
        (args.plugin_root or plugin).expanduser(),
    )
    if args.json_out:
        write_json(args.json_out, report)
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 1 if args.fail_on_issues and report["summary"]["managed_with_issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
