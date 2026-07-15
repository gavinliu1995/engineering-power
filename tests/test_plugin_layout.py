import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
USER_WORKFLOWS = {
    "brainstorming",
    "writing-plans",
    "test-driven-development",
    "systematic-debugging",
    "requesting-code-review",
    "verification-before-completion",
    "finishing-development-work",
    "repo-intelligence",
    "pr-impact-analysis",
    "architecture-map",
    "codebase-onboarding",
    "release-readiness",
    "migration-planner",
    "dependency-impact-analysis",
    "api-contract-generator",
    "release-note-generator",
}
SUPPORT_WORKFLOWS = {
    "using-engineering-power",
    "using-git-worktrees",
    "executing-plans",
    "subagent-driven-development",
}


class PluginLayoutTests(unittest.TestCase):
    def test_manifest_and_all_workflows_exist(self):
        manifest = ROOT / ".codex-plugin" / "plugin.json"
        self.assertTrue(manifest.is_file())
        self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["name"], "engineering-power")
        for workflow in USER_WORKFLOWS | SUPPORT_WORKFLOWS:
            self.assertTrue((ROOT / "skills" / workflow / "SKILL.md").is_file())

    def test_repo_workflows_describe_shared_evidence_engine(self):
        for workflow in (
            "repo-intelligence",
            "pr-impact-analysis",
            "architecture-map",
            "codebase-onboarding",
            "release-readiness",
            "migration-planner",
        ):
            content = (ROOT / "skills" / workflow / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("shared", content.lower())

    def test_shared_evidence_scripts_are_present(self):
        scripts = ROOT / "scripts" / "repo_evidence"
        for filename in (
            "collect_github_context.py",
            "collect_local_context.py",
            "prepare_analysis_context.py",
            "prepare_workflow_context.py",
            "validate_report.py",
            "finalize_report.py",
            "manage_cache.py",
        ):
            self.assertTrue((scripts / filename).is_file())


if __name__ == "__main__":
    unittest.main()
