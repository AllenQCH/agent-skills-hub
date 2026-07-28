#!/usr/bin/env python3
"""Render a test-release Markdown document from JSON input."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FIELDS = [
    "title",
    "requirement",
    "background",
    "owner",
    "date",
    "project",
    "service",
    "branch",
    "commit_range",
    "change_summary",
    "impact_scope",
    "verification",
    "test_focus",
    "risk",
    "rollback",
    "config_data_migration",
    "pipeline_url",
    "environment",
    "open_questions",
]


def render(template: str, data: dict[str, object]) -> str:
    values = {field: str(data.get(field) or "待确认") for field in FIELDS}
    output = template
    for key, value in values.items():
        output = output.replace("{{" + key + "}}", value)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json", help="Path to JSON with release fields")
    parser.add_argument("--template", default=str(Path(__file__).parents[1] / "assets/templates/test-release-doc.md"))
    parser.add_argument("--output", help="Optional output Markdown path")
    args = parser.parse_args()

    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    template = Path(args.template).read_text(encoding="utf-8")
    markdown = render(template, data)

    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
