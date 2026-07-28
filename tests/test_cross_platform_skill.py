"""Tests for the cross-platform skill installer and portable package generation."""

import importlib.util
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER_PATH = ROOT / "scripts" / "install_agent_skill.py"


def load_installer():
    spec = importlib.util.spec_from_file_location("installer", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_skill_names() -> set[str]:
    """Discover all skill names from the flat skills/ directory."""
    names = set()
    skills_root = ROOT / "skills"
    for skill_dir in skills_root.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        if (skill_dir / "SKILL.md").is_file():
            names.add(skill_dir.name)
    return names


class InstallerDiscoveryTests(unittest.TestCase):
    def test_discovers_all_canonical_skills(self):
        installer = load_installer()
        discovered = {skill.name for skill in installer.discover_skills()}
        expected = canonical_skill_names()
        self.assertEqual(discovered, expected)
        self.assertIn("engineering-power", discovered)

    def test_discovers_skills_in_flat_layout(self):
        installer = load_installer()
        skills = installer.discover_skills()
        parents = {skill.parent.name for skill in skills}
        self.assertEqual(parents, {"skills"})

    def test_codex_skills_directory_is_flat_real_entrypoints(self):
        for name in canonical_skill_names():
            skill_dir = ROOT / "skills" / name
            with self.subTest(skill=name):
                self.assertTrue(skill_dir.is_dir())
                self.assertFalse(skill_dir.is_symlink())
                self.assertTrue((skill_dir / "SKILL.md").is_file())


class InstallerGenerationTests(unittest.TestCase):
    def test_generates_complete_host_suite(self):
        locations = {
            "copilot": (".agents", "skills"),
            "claude": (".claude", "skills"),
            "cursor": (".cursor", "skills"),
        }
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            for host, parts in locations.items():
                with self.subTest(host=host):
                    completed = subprocess.run(
                        [
                            "python3", str(INSTALLER_PATH),
                            "--host", host,
                            "--target-root", str(target_root),
                        ],
                        cwd=ROOT, text=True, capture_output=True, check=False,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    skills_root = target_root.joinpath(*parts)
                    installed = {
                        path.name
                        for path in skills_root.iterdir()
                        if path.is_dir() and (path / "SKILL.md").is_file()
                    }
                    self.assertEqual(installed, canonical_skill_names())

    def test_core_skill_bundles_evidence_engine(self):
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            subprocess.run(
                ["python3", str(INSTALLER_PATH),
                 "--host", "copilot", "--target-root", str(target_root)],
                cwd=ROOT, check=True, capture_output=True,
            )
            core = target_root / ".agents" / "skills" / "engineering-power"
            self.assertTrue(
                (core / "scripts" / "repo_evidence" / "collect_local_context.py").is_file()
            )
            self.assertTrue(
                (core / "scripts" / "repo_evidence" / "collect_github_context.py").is_file()
            )
            self.assertTrue(
                (core / "scripts" / "repo_evidence" / "finalize_report.py").is_file()
            )
            self.assertTrue((core / "references" / "report-schema.md").is_file())
            self.assertFalse(any(core.rglob("*.pyc")))
            self.assertFalse(any(core.rglob("__pycache__")))

    def test_non_core_skills_have_portable_runtime_section(self):
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            subprocess.run(
                ["python3", str(INSTALLER_PATH),
                 "--host", "copilot", "--target-root", str(target_root)],
                cwd=ROOT, check=True, capture_output=True,
            )
            skills_root = target_root / ".agents" / "skills"
            for skill_dir in skills_root.iterdir():
                if skill_dir.name == "engineering-power" or not skill_dir.is_dir():
                    continue
                skill_md = skill_dir / "SKILL.md"
                if skill_md.is_file():
                    content = skill_md.read_text(encoding="utf-8")
                    self.assertIn(
                        "## Portable runtime", content,
                        f"{skill_dir.name} missing portable runtime section",
                    )

    def test_generated_skills_exclude_agents_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            subprocess.run(
                ["python3", str(INSTALLER_PATH),
                 "--host", "copilot", "--target-root", str(target_root)],
                cwd=ROOT, check=True, capture_output=True,
            )
            skills_root = target_root / ".agents" / "skills"
            for skill_dir in skills_root.iterdir():
                if skill_dir.is_dir():
                    self.assertFalse(
                        (skill_dir / "agents").exists(),
                        f"{skill_dir.name} should not have agents/ dir",
                    )

    def test_installer_preserves_unrelated_skills(self):
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            skills_root = target_root / ".agents" / "skills"
            unrelated = skills_root / "example-skill" / "SKILL.md"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text("---\nname: example\n---\n", encoding="utf-8")
            subprocess.run(
                ["python3", str(INSTALLER_PATH),
                 "--host", "copilot", "--target-root", str(target_root)],
                cwd=ROOT, check=True, capture_output=True,
            )
            self.assertTrue(unrelated.is_file())

    def test_installer_preflights_conflicts(self):
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            skills_root = target_root / ".agents" / "skills"
            collision = skills_root / "repo-intelligence" / "SKILL.md"
            collision.parent.mkdir(parents=True)
            collision.write_text("existing", encoding="utf-8")
            completed = subprocess.run(
                ["python3", str(INSTALLER_PATH),
                 "--host", "copilot", "--target-root", str(target_root)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("repo-intelligence", completed.stderr)

    def test_installer_dry_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary) / "missing"
            completed = subprocess.run(
                ["python3", str(INSTALLER_PATH),
                 "--host", "copilot", "--target-root", str(target_root),
                 "--dry-run"],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertFalse(target_root.exists())
            self.assertIn("engineering-power", completed.stdout)

    def test_installer_force_replaces_existing(self):
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            subprocess.run(
                ["python3", str(INSTALLER_PATH),
                 "--host", "copilot", "--target-root", str(target_root)],
                cwd=ROOT, check=True, capture_output=True,
            )
            completed = subprocess.run(
                ["python3", str(INSTALLER_PATH),
                 "--host", "copilot", "--target-root", str(target_root),
                 "--force"],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)


class PortableSkillRedactionTests(unittest.TestCase):
    def test_portable_redactor_is_bundled_and_functional(self):
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            subprocess.run(
                ["python3", str(INSTALLER_PATH),
                 "--host", "copilot", "--target-root", str(target_root)],
                cwd=ROOT, check=True, capture_output=True,
            )
            redactor_path = (
                target_root / ".agents" / "skills" / "engineering-power"
                / "scripts" / "repo_evidence" / "redact_context.py"
            )
            self.assertTrue(redactor_path.is_file())
            spec = importlib.util.spec_from_file_location("redactor", redactor_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            literal = "test-cookie-value-12345"
            redacted = module.redact_text(f'Cookie: session={literal}; pref=dark')
            self.assertNotIn(literal, redacted)
            self.assertIn("Cookie: [REDACTED]", redacted)


class LinkSkillsTests(unittest.TestCase):
    def test_link_script_exists_and_is_executable(self):
        import os
        script = ROOT / "scripts" / "link-skills.sh"
        self.assertTrue(script.is_file())
        self.assertTrue(os.access(script, os.X_OK))

    def test_link_script_targets_cursor_local_skills(self):
        script = ROOT / "scripts" / "link-skills.sh"
        content = script.read_text(encoding="utf-8")
        self.assertIn('$HOME/.cursor/skills', content)


class CursorGovernanceTests(unittest.TestCase):
    def test_cursor_rule_points_to_flat_skills(self):
        rule = ROOT / ".cursor" / "rules" / "engineering-power.mdc"
        self.assertTrue(rule.is_file())
        content = rule.read_text(encoding="utf-8")
        self.assertIn("skills/", content)
        self.assertIn(".cursor/skills", content)


if __name__ == "__main__":
    unittest.main()
