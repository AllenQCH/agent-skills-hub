from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml


HUB = Path(__file__).resolve().parents[1]
QUALITY_SCRIPTS = HUB / "skills" / "skill-quality-review" / "scripts"
sys.path.insert(0, str(QUALITY_SCRIPTS))

from qualitylib import (  # noqa: E402
    Surface,
    broken_links,
    line_count,
    normalize_frontmatter,
    normalized_openai,
    parse_frontmatter,
    split_long_skill,
)


class SkillQualityTests(unittest.TestCase):
    def test_frontmatter_normalization_preserves_legacy_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "sample-skill"
            package.mkdir()
            path = package / "SKILL.md"
            text = """---
name: sample-skill
description: Train <1% of parameters for <model-name>.
version: 1.2.3
license: MIT
---

# Sample
"""
            descriptor: dict = {}
            surface = Surface("canonical", path, package, True)

            normalized, actions = normalize_frontmatter(surface, text, descriptor)
            metadata, _, error = parse_frontmatter(normalized)

            self.assertIsNone(error)
            self.assertIn("move-legacy-frontmatter", actions)
            self.assertIn("normalize-description-placeholders", actions)
            self.assertIn("add-description-trigger", actions)
            self.assertEqual("MIT", metadata["license"])
            self.assertNotIn("version", metadata)
            self.assertEqual("1.2.3", descriptor["legacy_frontmatter"]["version"])
            self.assertNotIn("<", metadata["description"])

    def test_long_skill_splits_at_heading_and_preserves_tail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "sample-skill"
            references = package / "references"
            references.mkdir(parents=True)
            (references / "existing.md").write_text("existing\n", encoding="utf-8")
            path = package / "SKILL.md"
            body = ["# Sample", ""]
            for section in range(12):
                body.append(f"## Section {section}")
                body.extend(f"line {section}-{index}" for index in range(48))
            body.append("[Existing](references/existing.md)")
            text = "---\nname: sample-skill\ndescription: Use when testing a long sample Skill.\n---\n\n" + "\n".join(body) + "\n"
            surface = Surface("canonical", path, package, True)

            result = split_long_skill(text, surface)

            self.assertIsNotNone(result)
            normalized, reference, reference_text = result  # type: ignore[misc]
            self.assertLessEqual(line_count(normalized), 500)
            self.assertEqual(references / "extended-guidance.md", reference)
            self.assertIn("## Contents", reference_text)
            self.assertIn("line 11-47", reference_text)
            self.assertIn("[Existing](existing.md)", reference_text)

    def test_openai_normalization_preserves_policy_and_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            agents = package / "agents"
            agents.mkdir()
            path = agents / "openai.yaml"
            path.write_text(
                "display_name: Sample\n"
                "short_description: too short\n"
                "default_prompt: Run the workflow.\n"
                "policy:\n  allow_implicit_invocation: false\n"
                "dependencies:\n  tools:\n    - type: mcp\n      value: sample\n",
                encoding="utf-8",
            )

            _, normalized = normalized_openai(package, "sample-skill")
            payload = yaml.safe_load(normalized)

            self.assertIn("$sample-skill", payload["interface"]["default_prompt"])
            self.assertGreaterEqual(len(payload["interface"]["short_description"]), 25)
            self.assertFalse(payload["policy"]["allow_implicit_invocation"])
            self.assertEqual("sample", payload["dependencies"]["tools"][0]["value"])

    def test_openai_normalization_updates_existing_interface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            agents = package / "agents"
            agents.mkdir()
            (agents / "openai.yaml").write_text(
                "interface:\n"
                "  display_name: Sample Skill\n"
                "  short_description: Apply the existing sample skill workflow\n"
                "  default_prompt: Run the existing workflow.\n",
                encoding="utf-8",
            )

            _, normalized = normalized_openai(package, "sample-skill")
            payload = yaml.safe_load(normalized)

            self.assertIn("$sample-skill", payload["interface"]["default_prompt"])

    def test_broken_link_scan_ignores_code_and_url_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SKILL.md"
            text = """[Example](url) and `![image](missing-inline.png)`

```python
model["name"](checkpoint="missing.pth")
```
"""
            self.assertEqual([], broken_links(path, text))


if __name__ == "__main__":
    unittest.main()
