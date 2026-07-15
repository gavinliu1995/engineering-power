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


if __name__ == "__main__":
    unittest.main()
