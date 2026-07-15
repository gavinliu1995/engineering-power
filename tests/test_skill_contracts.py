import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def skill_text(name):
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def plugin_manifest():
    return json.loads(
        (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )


class SkillContractTests(unittest.TestCase):
    def test_dependency_impact_skill_contract(self):
        text = skill_text("dependency-impact-analysis")
        for phrase in (
            "prepare_workflow_context.py",
            "dependency-impact",
            "direct dependencies",
            "reverse consumers",
            "Fact",
            "Inference",
            "Unknown",
        ):
            self.assertIn(phrase, text)

    def test_api_contract_skill_contract(self):
        text = skill_text("api-contract-generator")
        for phrase in (
            "prepare_workflow_context.py",
            "api-contract",
            "compatibility",
            "authentication",
            "Do not invent",
        ):
            self.assertIn(phrase, text)

    def test_release_note_skill_contract(self):
        text = skill_text("release-note-generator")
        for phrase in (
            "prepare_workflow_context.py",
            "release-notes",
            "technical",
            "user-facing",
            "executed",
            "recommended",
        ):
            self.assertIn(phrase, text)

    def test_pr_golden_path_routes_to_derived_workflows(self):
        text = skill_text("pr-impact-analysis")
        for name in (
            "dependency-impact-analysis",
            "api-contract-generator",
            "release-note-generator",
        ):
            self.assertIn(name, text)

        capabilities = " ".join(
            plugin_manifest()["interface"]["capabilities"]
        ).lower()
        for phrase in ("dependency impact", "api contract", "release note"):
            self.assertIn(phrase, capabilities)

    def test_release_readiness_consumes_only_completed_derived_reports(self):
        text = skill_text("release-readiness")
        self.assertIn("completed derived", text.lower())
        self.assertIn("do not claim", text.lower())


if __name__ == "__main__":
    unittest.main()
