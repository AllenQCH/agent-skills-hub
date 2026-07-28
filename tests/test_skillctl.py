from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


HUB = Path(__file__).resolve().parents[1]
SKILLCTL = HUB / "bin" / "skillctl.py"
REGISTRY = HUB / "registry" / "skills.json"
sys.path.insert(0, str(HUB / "bin"))

import skillctl  # noqa: E402


def run_json(*args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [sys.executable, str(SKILLCTL), *args],
        cwd=HUB,
        check=False,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    return result, payload


class SkillCtlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.by_name = {item["name"]: item for item in cls.registry["skills"]}

    def test_registry_has_219_unique_names(self) -> None:
        names = [item["name"] for item in self.registry["skills"]]
        self.assertEqual(219, len(names))
        self.assertEqual(len(names), len(set(names)))

    def test_golden_search_prompts(self) -> None:
        cases = {
            "查询国内数据库": "dbauto-sql-query",
            "维护 multi-agent 和 skill hub": "multi-agent-framework-maintainer",
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                result, payload = run_json("search", "--query", query, "--limit", "5")
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(expected, payload["candidates"][0]["name"])

    def test_runtime_adapter_selection(self) -> None:
        _, codex = run_json("get", "dws", "--runtime", "codex")
        _, hermes = run_json("get", "dws", "--runtime", "hermes")
        self.assertEqual(str(HUB / "skills" / "dws" / "SKILL.md"), codex["instruction_path"])
        self.assertIn("/skills/dws/adapters/hermes/", hermes["instruction_path"])

    def test_high_risk_metadata_requires_manual_review(self) -> None:
        skill = self.by_name["dbauto-sql-query"]
        self.assertEqual("high", skill["risk"])
        self.assertTrue(skill["manual_only"])

    def test_router_only_deployment_is_valid(self) -> None:
        self.assertEqual([], skillctl.verify_deployment())

    def test_runtime_context_budgets(self) -> None:
        for runtime in ("codex", "claude", "hermes"):
            with self.subTest(runtime=runtime):
                result, payload = run_json("doctor", "--runtime", runtime)
                self.assertEqual(0, result.returncode, result.stdout)
                self.assertTrue(payload["within_budget"])

    def test_secret_scan(self) -> None:
        result, payload = run_json("scan")
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual([], payload["high_confidence_findings"])


if __name__ == "__main__":
    unittest.main()
