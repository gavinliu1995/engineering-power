import json
from pathlib import Path
import re
import subprocess
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

DISPLAY_NAMES = {
    "api-contract-generator": "API Contract Generator",
    "architecture-map": "Architecture Map",
    "brainstorming": "Brainstorming",
    "codebase-onboarding": "Codebase Onboarding",
    "dependency-impact-analysis": "Dependency Impact Analysis",
    "executing-plans": "Executing Plans",
    "finishing-development-work": "Finishing Development Work",
    "migration-planner": "Migration Planner",
    "pr-impact-analysis": "PR Impact Analysis",
    "release-note-generator": "Release Note Generator",
    "release-readiness": "Release Readiness",
    "repo-intelligence": "Repo Intelligence",
    "requesting-code-review": "Requesting Code Review",
    "subagent-driven-development": "Subagent-Driven Development",
    "systematic-debugging": "Systematic Debugging",
    "test-driven-development": "Test-Driven Development",
    "using-engineering-power": "Using Engineering Power",
    "using-git-worktrees": "Using Git Worktrees",
    "verification-before-completion": "Verification Before Completion",
    "writing-plans": "Writing Plans",
}


def openai_interface(skill):
    path = ROOT / "skills" / skill / "agents" / "openai.yaml"
    if not path.is_file():
        return None, path
    values = dict(
        re.findall(
            r'^  (display_name|short_description|default_prompt): "([^"]*)"$',
            path.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    )
    return values, path


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

    def test_every_skill_has_unambiguous_engineering_power_ui_metadata(self):
        self.assertEqual(set(DISPLAY_NAMES), USER_WORKFLOWS | SUPPORT_WORKFLOWS)
        observed_display_names = set()
        for skill, title in DISPLAY_NAMES.items():
            with self.subTest(skill=skill):
                interface, path = openai_interface(skill)
                self.assertIsNotNone(interface, f"Missing {path}")
                expected_name = f"Engineering Power: {title}"
                self.assertEqual(interface.get("display_name"), expected_name)
                description = interface.get("short_description", "")
                self.assertGreaterEqual(len(description), 25)
                self.assertLessEqual(len(description), 64)
                self.assertIn(f"${skill}", interface.get("default_prompt", ""))
                self.assertNotIn("Superpowers", path.read_text(encoding="utf-8"))
                observed_display_names.add(interface.get("display_name"))
        self.assertEqual(len(observed_display_names), len(DISPLAY_NAMES))

    def test_plugin_source_has_no_nested_worktree_payload(self):
        self.assertFalse(
            (ROOT / ".worktrees").exists(),
            "Codex copies untracked source files into the installed plugin; "
            "move development worktrees outside the plugin root before packaging.",
        )
        tracked = subprocess.run(
            ["git", "ls-files", "--", ".worktrees"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        self.assertEqual(tracked, [], f"Nested worktree payload is tracked: {tracked}")


if __name__ == "__main__":
    unittest.main()
