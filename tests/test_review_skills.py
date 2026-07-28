from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


HUB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HUB / "bin"))

import review_skills  # noqa: E402


class ReviewSkillsTests(unittest.TestCase):
    def test_due_prefers_explicit_next_review_time(self) -> None:
        current = datetime(2026, 7, 28, 8, 0, tzinfo=timezone.utc)
        future = current + timedelta(hours=1)
        past = current - timedelta(seconds=1)

        self.assertFalse(review_skills.due({"next_review_at": future.isoformat()}, current))
        self.assertTrue(review_skills.due({"next_review_at": past.isoformat()}, current))

    def test_local_packages_exclude_hidden_and_hub_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hub = root / "hub"
            hub_skill = hub / "skills" / "shared"
            hub_skill.mkdir(parents=True)
            (hub_skill / "SKILL.md").write_text("shared\n", encoding="utf-8")
            hermes = root / "hermes"
            local = hermes / "productivity" / "local-skill"
            local.mkdir(parents=True)
            (local / "SKILL.md").write_text("local\n", encoding="utf-8")
            hidden = hermes / ".hub" / "hidden"
            hidden.mkdir(parents=True)
            (hidden / "SKILL.md").write_text("hidden\n", encoding="utf-8")
            (hermes / "shared").symlink_to(hub_skill, target_is_directory=True)

            packages = review_skills.local_skill_packages(hermes, hub)

            self.assertEqual([local], packages)

    def test_audit_only_does_not_advance_schedule(self) -> None:
        current = datetime(2026, 7, 28, 8, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "runtime"
            state_file = runtime / "state.json"
            queue_file = runtime / "queue.json"
            report_root = runtime / "reports"
            lock_dir = runtime / "lock"
            original_state = {
                "last_review_at": "2026-07-28T05:49:33+00:00",
                "next_review_at": "2026-07-31T05:49:33+00:00",
            }
            review_skills.write_json(state_file, original_state)
            result = {
                "status": "audit-only",
                "schedule_advanced": False,
                "artifact_paths": [str(report_root)],
            }
            with (
                mock.patch.object(review_skills, "RUNTIME_ROOT", runtime),
                mock.patch.object(review_skills, "STATE_FILE", state_file),
                mock.patch.object(review_skills, "QUEUE_FILE", queue_file),
                mock.patch.object(review_skills, "REPORT_ROOT", report_root),
                mock.patch.object(review_skills, "LOCK_DIR", lock_dir),
                mock.patch.object(review_skills, "now_utc", return_value=current),
                mock.patch.object(review_skills, "build_promotion_queue", return_value={"candidates": []}),
                mock.patch.object(review_skills, "quality_cycle", return_value=result),
            ):
                exit_code = review_skills.run(force=True, audit_only=True)

            self.assertEqual(0, exit_code)
            self.assertEqual(original_state, json.loads(state_file.read_text(encoding="utf-8")))
            self.assertTrue(queue_file.is_file())
            self.assertFalse(lock_dir.exists())

    def test_failure_state_retries_after_six_hours(self) -> None:
        current = datetime(2026, 7, 28, 8, 0, tzinfo=timezone.utc)
        run_dir = Path("/tmp/review-evidence")

        state = review_skills.state_after_failure({}, current, RuntimeError("validation failed"), run_dir)

        self.assertEqual("failed", state["last_status"])
        self.assertEqual((current + timedelta(hours=6)).isoformat(), state["next_review_at"])
        self.assertEqual([str(run_dir)], state["last_artifact_paths"])

    def test_success_state_uses_72_hour_interval(self) -> None:
        current = datetime(2026, 7, 28, 8, 0, tzinfo=timezone.utc)
        result = {"status": "no-changes", "artifact_paths": ["/tmp/evidence"], "backup": None}

        state = review_skills.state_after_result({}, current, result)

        self.assertEqual((current + timedelta(hours=72)).isoformat(), state["next_review_at"])
        self.assertEqual(current.isoformat(), state["last_success_at"])

    def test_quality_cycle_stages_before_live_apply(self) -> None:
        current = datetime(2026, 7, 28, 8, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "run"
            run_dir.mkdir()
            backup = Path(directory) / "backup"

            def fake_stage(root: Path) -> tuple[Path, Path]:
                stage_hub = root / "hub"
                stage_hermes = root / "hermes"
                stage_hub.mkdir()
                stage_hermes.mkdir()
                return stage_hub, stage_hermes

            normalize_results = [
                {"action_count": 2, "manual_count": 0, "action_types": {"rewrite-skill": 2}},
                {"action_count": 2, "manual_count": 0},
                {"action_count": 2, "manual_count": 0},
                {"action_count": 2, "manual_count": 0},
            ]
            with (
                mock.patch.object(review_skills, "audit", return_value={"summary": {"managed_with_issues": 2}}),
                mock.patch.object(review_skills, "normalize", side_effect=normalize_results) as normalize_mock,
                mock.patch.object(review_skills, "copy_for_staging", side_effect=fake_stage),
                mock.patch.object(review_skills, "tree_digest", side_effect=["stable", "stable", "after"]),
                mock.patch.object(review_skills, "create_backup", return_value=backup) as backup_mock,
                mock.patch.object(review_skills, "validate_staging", return_value={"validated_surfaces": 2}),
                mock.patch.object(review_skills, "validate_live", return_value={"validated_surfaces": 2}),
                mock.patch.object(review_skills, "set_writable_tree"),
                mock.patch.object(review_skills, "run_command"),
            ):
                result = review_skills.quality_cycle(current, run_dir, audit_only=False)

            self.assertEqual("applied", result["status"])
            self.assertEqual(str(backup), result["backup"])
            self.assertEqual(4, normalize_mock.call_count)
            self.assertTrue(normalize_mock.call_args_list[2].kwargs["apply"])
            self.assertTrue(normalize_mock.call_args_list[3].kwargs["apply"])
            backup_mock.assert_called_once()

    def test_quality_cycle_keeps_manual_items_pending(self) -> None:
        current = datetime(2026, 7, 28, 8, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            with (
                mock.patch.object(review_skills, "audit", return_value={"summary": {"managed_with_issues": 1}}),
                mock.patch.object(
                    review_skills,
                    "normalize",
                    return_value={"action_count": 0, "manual_count": 1, "action_types": {}},
                ),
                mock.patch.object(review_skills, "create_backup") as backup_mock,
            ):
                result = review_skills.quality_cycle(current, run_dir, audit_only=False)

            self.assertEqual("pending", result["status"])
            self.assertEqual("manual-review-required", result["reason"])
            backup_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
