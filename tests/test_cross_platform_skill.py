import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PORTABLE_SKILL = ROOT / ".agents" / "skills" / "engineering-power"
PORTABLE_SKILLS_ROOT = PORTABLE_SKILL.parent


def canonical_skill_names() -> set[str]:
    return {
        path.name
        for path in (ROOT / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def frontmatter_value(content: str, key: str) -> str:
    self_contained_frontmatter = content.split("---", 2)[1]
    prefix = f"{key}:"
    for line in self_contained_frontmatter.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()
    raise AssertionError(f"missing frontmatter key {key!r}")


def load_script(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CrossPlatformSkillTests(unittest.TestCase):
    def test_all_canonical_skills_are_generated_for_agent_hosts(self):
        expected = canonical_skill_names() | {"engineering-power"}
        actual = {
            path.name
            for path in PORTABLE_SKILLS_ROOT.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        }

        self.assertEqual(actual, expected)
        for skill_name in canonical_skill_names():
            source = (ROOT / "skills" / skill_name / "SKILL.md").read_text(
                encoding="utf-8"
            )
            generated = (PORTABLE_SKILLS_ROOT / skill_name / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual(
                frontmatter_value(generated, "name"),
                frontmatter_value(source, "name"),
            )
            self.assertEqual(
                frontmatter_value(generated, "description"),
                frontmatter_value(source, "description"),
            )

    def test_generated_skills_are_platform_neutral(self):
        for skill_name in canonical_skill_names():
            with self.subTest(skill=skill_name):
                generated_root = PORTABLE_SKILLS_ROOT / skill_name
                content = (generated_root / "SKILL.md").read_text(encoding="utf-8")

                self.assertNotIn("$PLUGIN_ROOT", content)
                self.assertNotIn("engineering-power:", content)
                self.assertNotIn("../../references/", content)
                self.assertFalse((generated_root / "agents").exists())
                if "scripts/repo_evidence/" in content:
                    self.assertIn("$ENGINEERING_POWER_CORE", content)
                    self.assertIn("../engineering-power", content)

    def test_generated_skills_copy_auxiliary_resources(self):
        expected_resources = (
            PORTABLE_SKILLS_ROOT
            / "requesting-code-review"
            / "code-reviewer.md",
            PORTABLE_SKILLS_ROOT
            / "subagent-driven-development"
            / "scripts"
            / "review-package",
            PORTABLE_SKILLS_ROOT
            / "brainstorming"
            / "visual-companion.md",
            PORTABLE_SKILLS_ROOT
            / "test-driven-development"
            / "testing-anti-patterns.md",
        )
        for resource in expected_resources:
            self.assertTrue(resource.is_file(), resource)

    def test_portable_skill_redacts_cookie_values_before_model_context(self):
        """Exercise the exact redactor shipped to Copilot, not the source copy."""
        redactor_path = (
            PORTABLE_SKILL / "scripts" / "repo_evidence" / "redact_context.py"
        )
        spec = importlib.util.spec_from_file_location("portable_redactor", redactor_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        literal = "engineering-power-cookie-regression-test-12345"
        redacted = module.redact_text(
            "\n".join(
                (
                    f'COOKIE = "{literal}"',
                    f"Cookie: session={literal}; preference=dark",
                    f"Set-Cookie: session={literal}; HttpOnly; Secure",
                    f'"Set-Cookie": "session={literal}; HttpOnly; Secure"',
                    f'"Set-Cookie": ["session={literal}; HttpOnly; Secure"]',
                )
            )
        )

        self.assertNotIn(literal, redacted)
        self.assertIn('COOKIE = "[REDACTED]"', redacted)
        self.assertIn("Cookie: [REDACTED]", redacted)
        self.assertIn("Set-Cookie: [REDACTED]", redacted)
        self.assertIn('"Set-Cookie": "[REDACTED]"', redacted)

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

    def test_portable_skill_documents_router_resources_and_report_template(self):
        content = (PORTABLE_SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("router/orchestrator", content.lower())
        for resource in (
            "[Report schema](references/report-schema.md)",
            "[Architecture focus](references/architecture-focus.md)",
            "[Local analysis](references/local-analysis.md)",
            "[Pull request analysis](references/pull-request-analysis.md)",
        ):
            self.assertIn(resource, content)
        for section in (
            "## Target",
            "## Git state",
            "## Evidence coverage",
            "## Findings",
            "## Risks",
            "## Validation",
            "## Unknowns",
        ):
            self.assertIn(section, content)

    def test_portable_skill_enforces_architecture_and_inline_delivery_contracts(self):
        content = (PORTABLE_SKILL / "SKILL.md").read_text(encoding="utf-8")

        for expected in (
            "--report-type architecture",
            "Page/Route",
            "Provider/Service",
            "Client/DAO",
            "30 seconds or less",
            "inline",
            "supplemental",
            "redact",
        ):
            self.assertIn(expected, content)
        self.assertRegex(
            content,
            r"Architecture Map.*architecture-focus\.md.*report-schema\.md",
        )

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

    def test_sync_removes_stale_generated_skills_but_preserves_unrelated_skills(self):
        synchronizer = load_script(
            "portable_skill_sync_for_stale_test",
            ROOT / "scripts" / "sync_portable_agent_skill.py",
        )
        with tempfile.TemporaryDirectory() as temporary:
            sandbox = Path(temporary)
            canonical_root = sandbox / "skills"
            portable_root = sandbox / ".agents" / "skills"
            canonical = canonical_root / "current-skill"
            canonical.mkdir(parents=True)
            (canonical / "SKILL.md").write_text(
                "---\nname: current-skill\ndescription: Current.\n---\n",
                encoding="utf-8",
            )
            core = portable_root / "engineering-power"
            core.mkdir(parents=True)
            (core / "SKILL.md").write_text(
                "---\nname: engineering-power\ndescription: Core.\n---\n",
                encoding="utf-8",
            )
            stale = portable_root / "renamed-skill"
            stale.mkdir()
            (stale / "SKILL.md").write_text(
                "---\nname: renamed-skill\ndescription: Stale.\n---\n"
                "## Portable runtime\n",
                encoding="utf-8",
            )
            unrelated = portable_root / "unrelated-skill"
            unrelated.mkdir()
            (unrelated / "SKILL.md").write_text(
                "---\nname: unrelated-skill\ndescription: Preserve.\n---\n",
                encoding="utf-8",
            )

            with patch.object(
                synchronizer,
                "CANONICAL_SKILLS_ROOT",
                canonical_root,
            ), patch.object(
                synchronizer,
                "PORTABLE_SKILLS_ROOT",
                portable_root,
            ), patch.object(
                synchronizer,
                "RESOURCE_DIRECTORIES",
                {},
            ):
                synchronizer.sync()

            self.assertTrue((portable_root / "current-skill" / "SKILL.md").is_file())
            self.assertFalse(stale.exists())
            self.assertTrue((unrelated / "SKILL.md").is_file())
            self.assertTrue((core / "SKILL.md").is_file())

    def test_installer_creates_complete_host_suite(self):
        installer = ROOT / "scripts" / "install_agent_skill.py"
        self.assertTrue(installer.is_file(), installer)

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
                    skills_root = target_root.joinpath(*parts)
                    installed = {
                        path.name
                        for path in skills_root.iterdir()
                        if path.is_dir() and (path / "SKILL.md").is_file()
                    }
                    self.assertEqual(
                        installed,
                        canonical_skill_names() | {"engineering-power"},
                    )
                    core = skills_root / "engineering-power"
                    self.assertTrue(
                        (
                            core
                            / "scripts"
                            / "repo_evidence"
                            / "collect_local_context.py"
                        ).is_file()
                    )
                    self.assertTrue(
                        (core / "references" / "report-schema.md").is_file()
                    )
                    self.assertFalse(any(skills_root.rglob("*.pem")))

    def test_installer_preserves_unrelated_skills(self):
        installer = ROOT / "scripts" / "install_agent_skill.py"
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            skills_root = target_root / ".agents" / "skills"
            unrelated = skills_root / "example-skill" / "SKILL.md"
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text(
                "---\nname: example-skill\ndescription: Remain installed.\n---\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    "python3",
                    str(installer),
                    "--host",
                    "copilot",
                    "--target-root",
                    str(target_root),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(unrelated.is_file())
            self.assertTrue(
                (skills_root / "pr-impact-analysis" / "SKILL.md").is_file()
            )

    def test_installer_preflights_conflicts(self):
        installer = ROOT / "scripts" / "install_agent_skill.py"
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            skills_root = target_root / ".agents" / "skills"
            collision = skills_root / "pr-impact-analysis" / "SKILL.md"
            collision.parent.mkdir(parents=True)
            collision.write_text("existing content", encoding="utf-8")

            completed = subprocess.run(
                [
                    "python3",
                    str(installer),
                    "--host",
                    "copilot",
                    "--target-root",
                    str(target_root),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 2)
            self.assertIn("pr-impact-analysis", completed.stderr)
            self.assertEqual(
                collision.read_text(encoding="utf-8"),
                "existing content",
            )
            self.assertFalse((skills_root / "engineering-power").exists())
            self.assertFalse((skills_root / "repo-intelligence").exists())

    def test_installer_treats_dangling_symlink_as_preflight_conflict(self):
        installer = ROOT / "scripts" / "install_agent_skill.py"
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            skills_root = target_root / ".agents" / "skills"
            skills_root.mkdir(parents=True)
            collision = skills_root / "pr-impact-analysis"
            collision.symlink_to(target_root / "missing-skill-target")

            completed = subprocess.run(
                [
                    "python3",
                    str(installer),
                    "--host",
                    "copilot",
                    "--target-root",
                    str(target_root),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 2)
            self.assertIn("pr-impact-analysis", completed.stderr)
            self.assertTrue(collision.is_symlink())
            self.assertFalse((skills_root / "engineering-power").exists())
            self.assertFalse((skills_root / "repo-intelligence").exists())

    def test_installer_force_stages_complete_suite_before_replacing_existing(self):
        installer = load_script(
            "agent_skill_installer_for_atomic_test",
            ROOT / "scripts" / "install_agent_skill.py",
        )
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            installed = installer.install(
                "copilot",
                target_root,
                force=False,
                dry_run=False,
            )
            original = {
                destination.name: (destination / "SKILL.md").read_bytes()
                for destination in installed
            }

            with patch.object(
                installer.shutil,
                "copytree",
                side_effect=OSError("simulated staging failure"),
            ):
                with self.assertRaisesRegex(OSError, "simulated staging failure"):
                    installer.install(
                        "copilot",
                        target_root,
                        force=True,
                        dry_run=False,
                    )

            for destination in installed:
                self.assertEqual(
                    (destination / "SKILL.md").read_bytes(),
                    original[destination.name],
                )

    def test_installer_validates_exact_managed_skill_names(self):
        installer = load_script(
            "agent_skill_installer_for_name_test",
            ROOT / "scripts" / "install_agent_skill.py",
        )
        sources = list(installer.managed_sources())
        with tempfile.TemporaryDirectory() as temporary:
            rogue = Path(temporary) / "rogue-skill"
            rogue.mkdir()
            (rogue / "SKILL.md").write_text(
                "---\nname: rogue-skill\ndescription: Rogue.\n---\n",
                encoding="utf-8",
            )
            substituted = tuple(
                source
                for source in sources
                if source.name != "pr-impact-analysis"
            ) + (rogue,)

            with patch.object(
                installer,
                "managed_sources",
                return_value=substituted,
            ):
                with self.assertRaisesRegex(RuntimeError, "skill names"):
                    installer.validate_sources()

    def test_installer_dry_run_does_not_create_destination(self):
        installer = ROOT / "scripts" / "install_agent_skill.py"
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary) / "missing" / "project"
            self.assertFalse(target_root.exists())
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
            self.assertFalse(target_root.exists())
            self.assertFalse((target_root / ".agents").exists())
            self.assertIn("engineering-power", completed.stdout)
            self.assertIn("pr-impact-analysis", completed.stdout)

    def test_installer_preserves_backups_when_rollback_fails(self):
        installer = load_script(
            "agent_skill_installer_for_rollback_test",
            ROOT / "scripts" / "install_agent_skill.py",
        )
        with tempfile.TemporaryDirectory() as temporary:
            target_root = Path(temporary)
            installer.install(
                "copilot",
                target_root,
                force=False,
                dry_run=False,
            )
            original_rename = Path.rename

            def fail_install_and_rollback(path, target):
                if path.parent.name.startswith(".engineering-power-stage-"):
                    raise OSError("simulated install failure")
                if path.parent.name.startswith(".engineering-power-backup-"):
                    raise OSError("simulated rollback failure")
                return original_rename(path, target)

            with patch.object(Path, "rename", fail_install_and_rollback):
                with self.assertRaisesRegex(RuntimeError, "rollback incomplete"):
                    installer.install(
                        "copilot",
                        target_root,
                        force=True,
                        dry_run=False,
                    )

            backup_roots = tuple(
                target_root.glob(".engineering-power-backup-*")
            )
            self.assertEqual(len(backup_roots), 1)
            self.assertTrue(
                (backup_roots[0] / "engineering-power" / "SKILL.md").is_file()
            )

    def test_readme_documents_cross_platform_installation(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        for expected in (
            "GitHub Copilot",
            "Claude Code",
            "Cursor",
            "Bitbucket",
            "20 individual Skills",
            "21 directories",
            "canonical source",
            ".agents/skills/pr-impact-analysis",
            "/skills list",
            "install_agent_skill.py",
            "sync_portable_agent_skill.py",
        ):
            self.assertIn(expected, content)

    def test_readme_documents_team_release_governance(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        for expected in (
            "## Ownership and release governance",
            "Owner:",
            "Review cadence:",
            "Release checklist:",
        ):
            self.assertIn(expected, content)


if __name__ == "__main__":
    unittest.main()
