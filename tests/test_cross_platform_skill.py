from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORTABLE_SKILL = ROOT / ".agents" / "skills" / "engineering-power"


class CrossPlatformSkillTests(unittest.TestCase):
    def test_portable_skill_contract(self):
        skill = PORTABLE_SKILL / "SKILL.md"
        self.assertTrue(skill.is_file(), skill)
        content = skill.read_text(encoding="utf-8")

        self.assertIn("name: engineering-power", content)
        self.assertIn("description:", content)
        self.assertIn("read-only", content.lower())
        for workflow in (
            "Repository Intelligence",
            "PR Impact Analysis",
            "Architecture Map",
            "API Contract",
            "Release Readiness",
            "Codebase Onboarding",
            "Migration Planner",
            "Systematic Debugging",
            "Verification Before Completion",
        ):
            self.assertIn(workflow, content)

    def test_portable_skill_is_self_contained_for_gh_skill_install(self):
        self.assertTrue(
            (PORTABLE_SKILL / "scripts" / "repo_evidence" / "collect_local_context.py").is_file()
        )
        self.assertTrue(
            (PORTABLE_SKILL / "scripts" / "repo_evidence" / "collect_github_context.py").is_file()
        )
        self.assertTrue((PORTABLE_SKILL / "references" / "report-schema.md").is_file())

    def test_portable_skill_resources_are_synchronized(self):
        completed = subprocess.run(
            ["python3", str(ROOT / "scripts" / "sync_portable_agent_skill.py"), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_installer_creates_host_specific_package(self):
        installer = ROOT / "scripts" / "install_agent_skill.py"
        self.assertTrue(installer.is_file(), installer)

        locations = {
            "copilot": (".agents", "skills", "engineering-power"),
            "claude": (".claude", "skills", "engineering-power"),
            "cursor": (".cursor", "skills", "engineering-power"),
        }
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            for host, parts in locations.items():
                with self.subTest(host=host):
                    completed = subprocess.run(
                        [
                            "python3",
                            str(installer),
                            "--host",
                            host,
                            "--target-root",
                            str(target_root),
                        ],
                        cwd=ROOT,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    destination = target_root.joinpath(*parts)
                    self.assertTrue((destination / "SKILL.md").is_file())
                    self.assertTrue((destination / "scripts" / "repo_evidence" / "collect_local_context.py").is_file())
                    self.assertTrue((destination / "references" / "report-schema.md").is_file())
                    self.assertFalse(any(destination.rglob("*.pem")))

    def test_installer_dry_run_does_not_create_destination(self):
        installer = ROOT / "scripts" / "install_agent_skill.py"
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            completed = subprocess.run(
                [
                    "python3",
                    str(installer),
                    "--host",
                    "copilot",
                    "--target-root",
                    str(target_root),
                    "--dry-run",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertFalse((target_root / ".agents").exists())

    def test_readme_documents_cross_platform_installation(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        for expected in (
            "GitHub Copilot",
            "Claude Code",
            "Cursor",
            "Bitbucket",
            "install_agent_skill.py",
            "sync_portable_agent_skill.py",
        ):
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
