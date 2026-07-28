#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from qualitylib import normalize_all, paths_from_args, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan or apply semantics-preserving Skill normalization.")
    parser.add_argument("--hub", type=Path)
    parser.add_argument("--hermes-root", type=Path)
    parser.add_argument("--include-hermes", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hub, hermes, _, _ = paths_from_args(args.hub)
    result = normalize_all(
        hub,
        (args.hermes_root or hermes).expanduser(),
        include_hermes=args.include_hermes,
        apply=args.apply,
    )
    if args.json_out:
        write_json(args.json_out, result)
    print(
        json.dumps(
            {
                "apply": result["apply"],
                "surface_count": result["surface_count"],
                "action_count": result["action_count"],
                "manual_count": result["manual_count"],
                "action_types": result["action_types"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if result["manual_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
