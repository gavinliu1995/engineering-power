import json
import os
from pathlib import Path
import subprocess
import stat
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock


SCRIPTS_DIR = (
    Path(__file__).resolve().parents[1] / "scripts" / "repo_evidence"
)
sys.path.insert(0, str(SCRIPTS_DIR))

import collect_github_context as collector  # noqa: E402
import collect_local_context as local_collector  # noqa: E402
import finalize_report  # noqa: E402
import manage_cache  # noqa: E402
import prepare_analysis_context  # noqa: E402
import redact_context  # noqa: E402
import validate_report  # noqa: E402


class TargetParsingTests(unittest.TestCase):
    def test_repository_url(self):
        self.assertEqual(
            collector.parse_target("https://github.com/openai/codex"),
            ("openai", "codex", None),
        )

    def test_pull_request_url(self):
        self.assertEqual(
            collector.parse_target("https://github.com/openai/codex/pull/123"),
            ("openai", "codex", 123),
        )

    def test_rejects_non_github_url(self):
        with self.assertRaises(RuntimeError):
            collector.parse_target("https://example.com/openai/codex")

    def test_runtime_profiles_have_release_deadlines(self):
        quick = SimpleNamespace(
            profile="quick",
            max_files=None,
            max_bytes=None,
            max_file_bytes=None,
            workers=None,
            deadline_seconds=None,
        )
        deep = SimpleNamespace(
            profile="deep",
            max_files=None,
            max_bytes=None,
            max_file_bytes=None,
            workers=None,
            deadline_seconds=None,
        )
        collector.apply_profile(quick)
        collector.apply_profile(deep)
        self.assertEqual(
            collector.PROFILE_DEFAULTS["quick"]["report_deadline_seconds"], 120
        )
        self.assertEqual(
            collector.PROFILE_DEFAULTS["deep"]["report_deadline_seconds"], 300
        )
        self.assertLess(quick.max_files, deep.max_files)
        self.assertLess(quick.deadline_seconds, deep.deadline_seconds)


class LocalConfigTests(unittest.TestCase):
    def test_loads_json_object(self):
        with tempfile.TemporaryDirectory() as temporary:
            config_path = Path(temporary) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "github_app_id": "123",
                        "github_private_key": "~/app.pem",
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ, {"REPOLENS_CONFIG": str(config_path)}, clear=False
            ):
                self.assertEqual(
                    collector.load_local_config()["github_app_id"], "123"
                )

    def test_rejects_non_object_config(self):
        with tempfile.TemporaryDirectory() as temporary:
            config_path = Path(temporary) / "config.json"
            config_path.write_text("[]", encoding="utf-8")
            with mock.patch.dict(
                os.environ, {"REPOLENS_CONFIG": str(config_path)}, clear=False
            ):
                with self.assertRaises(RuntimeError):
                    collector.load_local_config()

    def test_token_skips_malformed_local_config(self):
        with tempfile.TemporaryDirectory() as temporary:
            config_path = Path(temporary) / "config.json"
            config_path.write_text("not-json", encoding="utf-8")
            with mock.patch.dict(
                os.environ,
                {
                    "REPOLENS_CONFIG": str(config_path),
                    "REPOLENS_GITHUB_TOKEN": "test-token",
                },
                clear=True,
            ):
                self.assertEqual(
                    collector.resolve_github_app_settings(), (None, None)
                )

    def test_complete_cli_settings_skip_malformed_local_config(self):
        with tempfile.TemporaryDirectory() as temporary:
            config_path = Path(temporary) / "config.json"
            config_path.write_text("not-json", encoding="utf-8")
            with mock.patch.dict(
                os.environ, {"REPOLENS_CONFIG": str(config_path)}, clear=True
            ):
                self.assertEqual(
                    collector.resolve_github_app_settings("123", "~/app.pem"),
                    ("123", "~/app.pem"),
                )


class AccessErrorTests(unittest.TestCase):
    def test_github_app_error_explains_repository_selection(self):
        message = collector.repository_access_error(
            "owner", "private-repo", "github-app"
        )
        self.assertIn("repository selection", message)
        self.assertIn("owner/private-repo", message)

    def test_token_error_explains_sso(self):
        message = collector.repository_access_error(
            "owner", "private-repo", "environment-token"
        )
        self.assertIn("SSO", message)


class LocalCollectionTests(unittest.TestCase):
    def test_remote_url_sanitization_removes_credentials_and_query(self):
        self.assertEqual(
            local_collector.sanitize_remote(
                "https://user:token@example.test/team/repo.git?access_token=secret"
            ),
            "https://example.test/team/repo.git",
        )

    def git(self, repository, *arguments):
        return subprocess.run(
            ["git", "-C", str(repository), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()

    def create_repository(self, root):
        repository = root / "local-product"
        repository.mkdir()
        self.git(repository, "init", "-b", "main")
        self.git(repository, "config", "user.email", "repolens@example.test")
        self.git(repository, "config", "user.name", "RepoLens Test")
        (repository / "README.md").write_text(
            "# Local Product\n\nA local fixture.\n", encoding="utf-8"
        )
        (repository / "app.py").write_text(
            "def price(total):\n    return total\n", encoding="utf-8"
        )
        self.git(repository, "add", ".")
        self.git(repository, "commit", "-m", "initial product")
        base_sha = self.git(repository, "rev-parse", "HEAD")

        self.git(repository, "switch", "-c", "feature/tax")
        (repository / "app.py").write_text(
            "def price(total, tax_rate=0.1):\n"
            "    return total * (1 + tax_rate)\n",
            encoding="utf-8",
        )
        tests = repository / "tests"
        tests.mkdir()
        (tests / "test_app.py").write_text(
            "from app import price\n\n"
            "def test_tax():\n    assert price(100) == 110\n",
            encoding="utf-8",
        )
        self.git(repository, "add", ".")
        self.git(repository, "commit", "-m", "add tax calculation")
        head_sha = self.git(repository, "rev-parse", "HEAD")
        return repository, base_sha, head_sha

    def args(self, repository, output, **overrides):
        values = {
            "repository": str(repository),
            "ref": None,
            "base": None,
            "head": None,
            "working_tree": False,
            "patch": None,
            "output": None if output is None else str(output),
            "profile": "quick",
            "max_files": 250,
            "max_bytes": 4_000_000,
            "max_file_bytes": 200_000,
            "max_patch_bytes": 10_000_000,
            "workers": None,
            "deadline_seconds": 50,
            "no_cache": False,
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_repository_ref_collects_exact_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, base_sha, _ = self.create_repository(root)
            output, manifest = local_collector.collect(
                self.args(repository, root / "snapshot", ref="main")
            )

            self.assertEqual(manifest["mode"], "repository")
            self.assertEqual(manifest["resolved_ref"], base_sha)
            self.assertEqual(
                manifest["authentication"]["method"], "local-filesystem"
            )
            self.assertTrue((output / "files" / "app.py").is_file())
            self.assertFalse((output / "files" / "tests" / "test_app.py").exists())

    def test_collected_snapshot_is_private_without_changing_explicit_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _, _ = self.create_repository(root)
            explicit_parent = root / "exports"
            explicit_parent.mkdir(mode=0o755)
            explicit_parent.chmod(0o755)

            output, _ = local_collector.collect(
                self.args(repository, explicit_parent / "snapshot", ref="main")
            )

            self.assertEqual(stat.S_IMODE(explicit_parent.stat().st_mode), 0o755)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((output / "files").stat().st_mode), 0o700)
            for path in output.rglob("*"):
                if path.is_symlink():
                    continue
                expected = 0o700 if path.is_dir() else 0o600
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), expected, str(path))

    def test_git_range_collects_changed_tex_release_notes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, base_sha, _ = self.create_repository(root)
            notes = repository / "docs" / "release-notes.tex"
            notes.parent.mkdir()
            notes.write_text("\\section{Release}\n", encoding="utf-8")
            self.git(repository, "add", str(notes.relative_to(repository)))
            self.git(repository, "commit", "-m", "add release notes")

            output, _ = local_collector.collect(
                self.args(
                    repository,
                    root / "snapshot",
                    base=base_sha,
                    head="HEAD",
                )
            )

            self.assertTrue((output / "files" / "docs" / "release-notes.tex").is_file())
            manifest = json.loads(
                (output / "manifest.json").read_text(encoding="utf-8")
            )
            collected = {
                item["path"]: item for item in manifest["collected_files"]
            }
            self.assertTrue(
                collected["docs/release-notes.tex"]["changed_in_pull_request"]
            )

    def test_layered_sampling_keeps_each_architecture_layer(self):
        candidates = [
            {"path": f"src/generated/Noise{index}.java", "size": 100, "sha": str(index)}
            for index in range(1000)
        ]
        required = [
            "README.md",
            "pom.xml",
            "module/src/main/java/AppApplication.java",
            "module/src/main/java/web/HomePage.java",
            "module/src/main/java/service/BillingService.java",
            "module/src/main/java/dao/InvoiceDao.java",
            "module/src/test/java/BillingServiceTest.java",
            ".github/workflows/ci.yml",
        ]
        candidates.extend(
            {"path": path, "size": 100, "sha": path} for path in required
        )

        selected, coverage = collector.select_candidates(
            candidates, set(), max_files=40, max_bytes=100_000
        )
        selected_paths = {item["path"] for item in selected}

        for path in required:
            self.assertIn(path, selected_paths)
        for layer in (
            "core",
            "entrypoint",
            "route",
            "service",
            "persistence",
            "test",
            "operations",
        ):
            self.assertGreater(coverage["layer_selected"][layer], 0)

    def test_same_commit_reuses_cache_and_new_commit_misses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _, _ = self.create_repository(root)
            cache = root / "cache"
            with mock.patch.dict(
                os.environ, {"REPOLENS_CACHE_DIR": str(cache)}, clear=False
            ):
                first_output, first = local_collector.collect(
                    self.args(repository, None)
                )
                second_output, second = local_collector.collect(
                    self.args(repository, None)
                )
                self.assertFalse(first["cache"]["hit"])
                self.assertTrue(second["cache"]["hit"])
                self.assertEqual(first_output, second_output)

                (repository / "new.txt").write_text("new commit\n", encoding="utf-8")
                self.git(repository, "add", "new.txt")
                self.git(repository, "commit", "-m", "new commit")
                third_output, third = local_collector.collect(
                    self.args(repository, None)
                )
                self.assertFalse(third["cache"]["hit"])
                self.assertNotEqual(first_output, third_output)

    def test_working_tree_cache_fingerprint_changes_with_edits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _, _ = self.create_repository(root)
            cache = root / "cache"
            (repository / "app.py").write_text("value = 1\n", encoding="utf-8")
            with mock.patch.dict(
                os.environ, {"REPOLENS_CACHE_DIR": str(cache)}, clear=False
            ):
                first_output, _ = local_collector.collect(
                    self.args(
                        repository,
                        None,
                        working_tree=True,
                        base="HEAD",
                    )
                )
                (repository / "app.py").write_text("value = 2\n", encoding="utf-8")
                second_output, second = local_collector.collect(
                    self.args(
                        repository,
                        None,
                        working_tree=True,
                        base="HEAD",
                    )
                )
                self.assertFalse(second["cache"]["hit"])
                self.assertNotEqual(first_output, second_output)

    def test_analysis_context_contains_layered_exact_line_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _, _ = self.create_repository(root)
            snapshot, manifest = local_collector.collect(
                self.args(repository, root / "snapshot")
            )
            output = snapshot / "analysis-context-quick.md"
            result = prepare_analysis_context.build_context(
                snapshot, "quick", output, deadline_seconds=20
            )
            context = output.read_text(encoding="utf-8")

            self.assertEqual(result["profile"], "quick")
            self.assertEqual(
                result["context_policy_version"],
                prepare_analysis_context.CONTEXT_POLICY_VERSION,
            )
            self.assertEqual(result["files_included"], 3)
            self.assertEqual(result["collected_files"], 3)
            self.assertIn("## Layer Coverage", context)
            self.assertIn("## Reasoning Anchors", context)
            self.assertIn("`README.md`", context)
            self.assertIn("`app.py`", context)
            self.assertIn("Citation: `README.md:1-3`", context)
            self.assertIn("     1 | # Local Product", context)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertLessEqual(
                len(context), prepare_analysis_context.CONTEXT_DEFAULTS["quick"]["max_chars"]
            )

    def test_shared_redactor_covers_supported_secret_shapes_and_preserves_lines(self):
        synthetic_secret = "synthetic-secret-value"
        source = "\n".join(
            [
                f"password={synthetic_secret}",
                f'TOKEN: "{synthetic_secret}"',
                f'{{"apiKey": "{synthetic_secret}"}}',
                f"<password>{synthetic_secret}</password>",
                f'<server password="{synthetic_secret}" />',
                f"tool --token {synthetic_secret} --mode safe",
                f"tool --password={synthetic_secret}",
                f"Authorization: Bearer {synthetic_secret}",
                f"Authorization: Basic {synthetic_secret}",
                f"https://user:{synthetic_secret}@example.test/path",
                "-----BEGIN PRIVATE KEY-----",
                synthetic_secret,
                "-----END PRIVATE KEY-----",
                f'<user username="demo" password="{synthetic_secret}" roles="reader" />',
            ]
        )

        redacted = redact_context.redact_text(source)

        self.assertNotIn(synthetic_secret, redacted)
        self.assertGreaterEqual(redacted.count("[REDACTED]"), 10)
        self.assertEqual(len(source.splitlines()), len(redacted.splitlines()))
        self.assertIn("-----BEGIN PRIVATE KEY-----", redacted)
        self.assertIn("-----END PRIVATE KEY-----", redacted)

    def test_analysis_context_redacts_before_rendering_numbered_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _, _ = self.create_repository(root)
            synthetic_secret = "analysis-context-dummy-secret"
            (repository / "app.py").write_text(
                f'password = "{synthetic_secret}"\nvalue = 1\n',
                encoding="utf-8",
            )
            self.git(repository, "add", "app.py")
            self.git(repository, "commit", "-m", "add synthetic credential fixture")
            snapshot, _ = local_collector.collect(
                self.args(repository, root / "snapshot")
            )
            output = snapshot / "analysis-context-quick.md"

            prepare_analysis_context.build_context(
                snapshot, "quick", output, deadline_seconds=20
            )
            context = output.read_text(encoding="utf-8")

            self.assertNotIn(synthetic_secret, context)
            self.assertIn('password = "[REDACTED]"', context)
            self.assertIn("     2 | value = 1", context)

    def test_analysis_context_discloses_layers_with_no_candidates(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _, _ = self.create_repository(root)
            snapshot, _ = local_collector.collect(
                self.args(repository, root / "snapshot")
            )
            output = snapshot / "analysis-context-quick.md"

            result = prepare_analysis_context.build_context(
                snapshot, "quick", output, deadline_seconds=20
            )

            self.assertIn("route", result["unavailable_layers"])
            self.assertIn("service", result["unavailable_layers"])
            self.assertIn("persistence", result["unavailable_layers"])
            self.assertIn("operations", result["unavailable_layers"])
            context = output.read_text(encoding="utf-8")
            self.assertIn("No candidates were available for layers", context)

    def test_reasoning_anchors_prefer_source_over_configuration_files(self):
        anchors = prepare_analysis_context.reasoning_anchors(
            [
                {
                    "path": "config/services.properties",
                    "layer": "service",
                },
                {
                    "path": "src/main/java/example/OrderService.java",
                    "layer": "service",
                },
            ]
        )
        self.assertEqual(
            anchors["service"],
            [
                "src/main/java/example/OrderService.java",
                "config/services.properties",
            ],
        )

    def test_collector_deadline_returns_partial_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _, _ = self.create_repository(root)
            output, manifest = local_collector.collect(
                self.args(
                    repository,
                    root / "snapshot",
                    deadline_seconds=0.000001,
                )
            )
            self.assertTrue(manifest["selection"]["deadline_reached"])
            self.assertEqual(manifest["stats"]["collected_files"], 0)
            self.assertTrue((output / "manifest.json").is_file())
            self.assertTrue(
                any("deadline" in warning.lower() for warning in manifest["warnings"])
            )

    def test_pull_request_report_accepts_allowlisted_snapshot_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = root / "snapshot"
            files = snapshot / "files"
            files.mkdir(parents=True)
            (files / "app.py").write_text("one\ntwo\nthree\n", encoding="utf-8")
            (snapshot / "pull-request.patch").write_text(
                "diff --git a/app.py b/app.py\n-old\n+new\n", encoding="utf-8"
            )
            (snapshot / "manifest.json").write_text(
                json.dumps(
                    {
                        "mode": "pull-request",
                        "resolved_ref": "abc123",
                    }
                ),
                encoding="utf-8",
            )
            report = root / "report.md"
            report.write_text(
                "# RepoLens Pull Request Intelligence Report\n\n"
                "Head commit: abc123\n\n"
                "## Change Summary\n\n`app.py:1`\n\n"
                "## Change Propagation\n\n"
                "```mermaid\nflowchart LR\nA --> B\n```\n\n"
                "`@snapshot/pull-request.patch:1-2`\n\n"
                "## Business Logic Impact\n\nConfidence: High\n\n"
                "## Test Impact\n\n`app.py:2-3`\n\n"
                "## Regression Risk\n\nLow. Confidence: High\n\n"
                "## Architecture Review\n\nNo boundary change.\n\n"
                "## Evidence Index\n\nEvidence above.\n",
                encoding="utf-8",
            )

            mode, diagrams, citations, errors, warnings = validate_report.validate(
                SimpleNamespace(report=str(report), snapshot=str(snapshot))
            )
            self.assertEqual(mode, "pull-request")
            self.assertEqual(len(diagrams), 1)
            self.assertEqual(citations, 3)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_git_range_creates_pull_request_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, base_sha, head_sha = self.create_repository(root)
            output, manifest = local_collector.collect(
                self.args(
                    repository,
                    root / "snapshot",
                    base="main",
                    head="feature/tax",
                )
            )

            self.assertEqual(manifest["mode"], "pull-request")
            self.assertEqual(manifest["simulation"]["kind"], "git-range")
            self.assertEqual(manifest["pull_request"]["base_sha"], base_sha)
            self.assertEqual(manifest["pull_request"]["head_sha"], head_sha)
            changed = json.loads(
                (output / "pull-request-files.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {item["filename"] for item in changed}, {"app.py", "tests/test_app.py"}
            )
            patch = (output / "pull-request.patch").read_text(encoding="utf-8")
            self.assertIn("tax_rate", patch)
            self.assertTrue((output / "files" / "tests" / "test_app.py").is_file())

            report = root / "full-pr-report.md"
            report.write_text(
                "# RepoLens Pull Request Intelligence Report\n\n"
                "Analyzed PR: Local git-range simulation  \n"
                f"Base commit: {base_sha}  \n"
                f"Head commit: {head_sha}  \n"
                "Authentication: local-filesystem\n\n"
                "## Change Summary\n\n"
                "The change adds a tax parameter and a focused test. "
                "`app.py:1-2`\n\n"
                "## Change Propagation\n\n"
                "```mermaid\nflowchart LR\n"
                "Input[\"Order total\"] --> Price[\"price(total, tax_rate)\"]\n"
                "Price --> Result[\"Tax-inclusive result\"]\n"
                "Test[\"Tax scenario\"] --> Price\n```\n\n"
                "The diff connects the implementation and test additions. "
                "`@snapshot/pull-request.patch:1-3`\n\n"
                "## Business Logic Impact\n\n"
                "Inference: callers now receive a tax-inclusive price by default. "
                "Confidence: High. `app.py:1-2`\n\n"
                "## Test Impact\n\n"
                "The new test covers the default tax calculation. No tests were "
                "executed as part of this report fixture. `tests/test_app.py:1-4`\n\n"
                "## Regression Risk\n\n"
                "Medium: the default changes return values for existing callers. "
                "Confidence: High. `app.py:1-2`\n\n"
                "## Architecture Review\n\n"
                "The calculation remains isolated in the existing module. "
                "Confidence: High. `tests/test_app.py:1-4`\n\n"
                "## Evidence Index\n\n"
                "- `app.py:1-2`: changed calculation.\n"
                "- `tests/test_app.py:1-4`: added regression scenario.\n",
                encoding="utf-8",
            )
            _, diagrams, citations, errors, warnings = validate_report.validate(
                SimpleNamespace(report=str(report), snapshot=str(output))
            )
            self.assertEqual(len(diagrams), 1)
            self.assertGreaterEqual(citations, 3)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_working_tree_includes_tracked_and_untracked_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _, _ = self.create_repository(root)
            (repository / "app.py").write_text(
                "def price(total):\n    return total * 2\n", encoding="utf-8"
            )
            (repository / "notes.md").write_text(
                "working tree evidence\n", encoding="utf-8"
            )
            output, manifest = local_collector.collect(
                self.args(
                    repository,
                    root / "snapshot",
                    base="HEAD",
                    working_tree=True,
                )
            )

            self.assertEqual(manifest["simulation"]["kind"], "working-tree")
            changed = json.loads(
                (output / "pull-request-files.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {item["filename"] for item in changed}, {"app.py", "notes.md"}
            )
            patch = (output / "pull-request.patch").read_text(encoding="utf-8")
            self.assertIn("working tree evidence", patch)
            self.assertTrue((output / "files" / "notes.md").is_file())

    def test_downloaded_patch_uses_context_without_mutating_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, base_sha, _ = self.create_repository(root)
            patch_path = root / "change.diff"
            patch_path.write_bytes(
                subprocess.run(
                    ["git", "-C", str(repository), "diff", "main", "feature/tax"],
                    check=True,
                    stdout=subprocess.PIPE,
                ).stdout
            )
            before = self.git(repository, "status", "--porcelain")
            output, manifest = local_collector.collect(
                self.args(
                    repository,
                    root / "snapshot",
                    base="main",
                    patch=str(patch_path),
                )
            )
            after = self.git(repository, "status", "--porcelain")

            self.assertEqual(manifest["simulation"]["kind"], "patch-file")
            self.assertEqual(manifest["resolved_ref"], base_sha)
            self.assertEqual(before, after)
            changed = json.loads(
                (output / "pull-request-files.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {item["filename"] for item in changed}, {"app.py", "tests/test_app.py"}
            )
            self.assertFalse((output / "files" / "tests" / "test_app.py").exists())


class ReportFinalizationTests(unittest.TestCase):
    def create_snapshot_and_report(self, root):
        snapshot = root / "snapshot"
        files = snapshot / "files"
        files.mkdir(parents=True)
        (files / "app.py").write_text("one\ntwo\nthree\n", encoding="utf-8")
        (snapshot / "manifest.json").write_text(
            json.dumps({"mode": "repository", "resolved_ref": "abc123"}),
            encoding="utf-8",
        )
        draft = root / "draft.md"
        draft.write_text(
            "# RepoLens Repository Intelligence Report\n\n"
            "Analyzed target: local fixture  \n"
            "Analyzed commit: abc123  \n"
            "Authentication: local-filesystem  \n"
            "Profile: Quick  \n"
            "Collection: cache hit  \n"
            "Coverage: 1/1 candidates; reasoning evidence 1  \n"
            "Missing layers: none  \n"
            "Tests executed: no  \n"
            f"Report validation: {finalize_report.VALIDATION_PLACEHOLDER}  \n"
            f"Total elapsed: {finalize_report.ELAPSED_PLACEHOLDER}\n\n"
            "## Executive Summary\n\nFixture. `app.py:1`\n\n"
            "## Repository Map\n\nFixture map. `app.py:1-2`\n\n"
            "## Architecture Diagram\n\n"
            "```mermaid\nflowchart LR\nA --> B\n```\n\n"
            "Evidence: `app.py:1`\n\n"
            "## Business Logic Flows\n\nRepresentative flow. Confidence: High.\n\n"
            "```mermaid\nsequenceDiagram\nA->>B: Call\n```\n\n"
            "Evidence: `app.py:2`\n\n"
            "## Developer Onboarding\n\nRead app. `app.py:1-3`\n\n"
            "## Build, Test, and Operations\n\nTests not executed.\n\n"
            "## Risks and Recommendations\n\n1. Low. Confidence: High.\n\n"
            "## Evidence Index\n\n"
            "- `app.py:1`\n- `app.py:2`\n- `app.py:3`\n"
            "- `app.py:1-2`\n- `app.py:2-3`\n- `app.py:1-3`\n"
            "- `app.py:1`\n- `app.py:2`\n",
            encoding="utf-8",
        )
        return snapshot, draft

    def test_finalizer_injects_validation_and_elapsed_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot, draft = self.create_snapshot_and_report(root)
            output = root / "final.md"
            result = finalize_report.finalize(
                draft,
                snapshot,
                "quick",
                time.time() - 2,
                output,
            )
            report = output.read_text(encoding="utf-8")

            self.assertEqual(result["validation"], "passed")
            self.assertFalse(result["deadline_exceeded"])
            self.assertIn("Report validation: passed", report)
            self.assertRegex(report, r"Total elapsed: 2\.\d seconds")
            self.assertNotIn(finalize_report.VALIDATION_PLACEHOLDER, report)

    def test_finalizer_marks_deadline_exceeded_report_as_limited(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot, draft = self.create_snapshot_and_report(root)
            output = root / "final.md"

            result = finalize_report.finalize(
                draft,
                snapshot,
                "quick",
                time.time() - 121,
                output,
            )
            report = output.read_text(encoding="utf-8")

            self.assertEqual(result["validation"], "passed-with-deadline-limit")
            self.assertTrue(result["deadline_exceeded"])
            self.assertIn(
                "Report validation: passed-with-deadline-limit", report
            )
            self.assertTrue(
                any("deadline" in warning.lower() for warning in result["warnings"])
            )

    def test_finalizer_rewrites_coverage_from_manifest_statistics(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot, draft = self.create_snapshot_and_report(root)
            manifest_path = snapshot / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["stats"] = {
                "collected_files": 360,
                "text_candidates": 2866,
                "tree_entries": 3608,
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            content = draft.read_text(encoding="utf-8").replace(
                "Coverage: 1/1 candidates; reasoning evidence 1",
                "Coverage: 2866/3608 text candidates",
            )
            draft.write_text(content, encoding="utf-8")
            output = root / "final.md"

            finalize_report.finalize(
                draft,
                snapshot,
                "quick",
                time.time() - 1,
                output,
            )
            report = output.read_text(encoding="utf-8")

            self.assertIn("Coverage: 360/2866 text candidates", report)
            self.assertIn("Tree entries: 3608", report)
            self.assertNotIn("2866/3608 text candidates", report)

    def test_validator_rejects_coverage_that_disagrees_with_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot, report = self.create_snapshot_and_report(root)
            manifest_path = snapshot / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["stats"] = {
                "collected_files": 360,
                "text_candidates": 2866,
                "tree_entries": 3608,
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            content = report.read_text(encoding="utf-8").replace(
                "Coverage: 1/1 candidates; reasoning evidence 1",
                "Coverage: 2866/3608 text candidates\nTree entries: 3608",
            )
            report.write_text(content, encoding="utf-8")

            _, _, _, errors, _ = validate_report.validate(
                SimpleNamespace(
                    report=str(report), snapshot=str(snapshot), report_type="repository"
                )
            )

            self.assertTrue(any("Coverage" in error for error in errors))

    def test_quick_profile_rejects_long_report(self):
        report = "Profile: Quick\n" + (
            "x" * finalize_report.PROFILE_RULES["quick"]["max_chars"]
        )
        errors = finalize_report.profile_errors(report, "quick")
        self.assertTrue(any("exceeds" in error for error in errors))

    def create_specialized_report(self, root, report_type):
        snapshot = root / "snapshot"
        files = snapshot / "files"
        files.mkdir(parents=True)
        (files / "app.py").write_text("one\ntwo\nthree\n", encoding="utf-8")
        (snapshot / "manifest.json").write_text(
            json.dumps({"mode": "pull-request", "resolved_ref": "abc123"}),
            encoding="utf-8",
        )
        sections = {
            "dependency-impact": (
                "## Decision Summary\n\nConfidence: High. `app.py:1`\n\n"
                "## Changed or Requested Surface\n\n`app.py:1`\n\n"
                "## Dependency Propagation\n\n"
                "| Source | Direction | Target | Effect | Classification | Evidence |\n"
                "|---|---|---|---|---|---|\n"
                "| app | consumed-by | test | behavior | Fact | `app.py:1` |\n\n"
                "## Transitive Impact\n\nNone observed. `app.py:2`\n\n"
                "## Test Impact\n\nExecuted: none. Discovered: app test. Recommended: run it.\n\n"
                "## Regression Risks\n\nLow. `app.py:3`\n\n"
                "## Evidence Index\n\n- `app.py:1`\n- `app.py:2`\n- `app.py:3`\n"
            ),
            "api-contract": (
                "## Decision Summary\n\nConfidence: High. `app.py:1`\n\n"
                "## Contract Sources\n\nFact: route source. `app.py:1`\n\n"
                "## Operations\n\n"
                "| Change | Method or kind | Path or name | Input | Output | Authentication | Compatibility | Evidence |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| added | GET | /v1/x | Unknown | value | Unknown | compatible | `app.py:1` |\n\n"
                "## Schemas and Validation\n\nUnknown. `app.py:2`\n\n"
                "## Compatibility Findings\n\nCompatible. `app.py:3`\n\n"
                "## Verification\n\nExecuted: none. Discovered: route test. Recommended: contract test.\n\n"
                "## Evidence Index\n\n- `app.py:1`\n- `app.py:2`\n- `app.py:3`\n"
            ),
            "release-notes": (
                "## Decision Summary\n\nConfidence: High. `app.py:1`\n\n"
                "## User-facing Release Notes\n\nNo supported user-facing change. `app.py:1`\n\n"
                "## Technical Release Notes\n\nInternal behavior changed. `app.py:2`\n\n"
                "## Required Actions\n\nNone discovered.\n\n"
                "## Validation Status\n\nExecuted: none.\n\nDiscovered: app test.\n\nRecommended: run app test.\n\n"
                "## Risks and Compatibility\n\nLow. `app.py:3`\n\n"
                "## Evidence Index\n\n- `app.py:1`\n- `app.py:2`\n- `app.py:3`\n"
            ),
        }
        draft = root / f"{report_type}.md"
        draft.write_text(
            "# Specialized Report\n\n"
            "Analyzed commit: abc123  \n"
            "Profile: Quick  \n"
            "Collection: cache hit  \n"
            "Coverage: bounded snapshot  \n"
            "Missing layers: none  \n"
            "Tests executed: no  \n"
            f"Report validation: {finalize_report.VALIDATION_PLACEHOLDER}  \n"
            f"Total elapsed: {finalize_report.ELAPSED_PLACEHOLDER}\n\n"
            + sections[report_type],
            encoding="utf-8",
        )
        return snapshot, draft

    def test_specialized_report_types_pass_their_quality_gates(self):
        for report_type in ("dependency-impact", "api-contract", "release-notes"):
            with self.subTest(report_type=report_type), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                snapshot, report = self.create_specialized_report(root, report_type)
                kind, diagrams, citations, errors, _ = validate_report.validate(
                    SimpleNamespace(
                        report=str(report), snapshot=str(snapshot), report_type=report_type
                    )
                )
                self.assertEqual(kind, report_type)
                self.assertEqual(diagrams, [])
                self.assertGreaterEqual(citations, 3)
                self.assertEqual(errors, [])

    def test_specialized_report_rejects_missing_semantic_contract(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot, report = self.create_specialized_report(root, "dependency-impact")
            content = report.read_text(encoding="utf-8").replace(
                "| Source | Direction | Target | Effect | Classification | Evidence |",
                "| Source | Target | Evidence |",
            )
            report.write_text(content, encoding="utf-8")
            _, _, _, errors, _ = validate_report.validate(
                SimpleNamespace(
                    report=str(report),
                    snapshot=str(snapshot),
                    report_type="dependency-impact",
                )
            )
            self.assertTrue(any("Dependency Propagation" in error for error in errors))

    def test_finalizer_records_specialized_report_type(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot, draft = self.create_specialized_report(root, "api-contract")
            result = finalize_report.finalize(
                draft,
                snapshot,
                "quick",
                time.time() - 1,
                root / "final.md",
                report_type="api-contract",
            )
            self.assertEqual(result["report_type"], "api-contract")
            self.assertEqual(result["validation"], "passed")


class CacheManagementTests(unittest.TestCase):
    def create_snapshot(
        self,
        root,
        name,
        modified_at,
        target_url="https://github.com/owner/repo",
        group="owner-repo",
    ):
        snapshot = root / group / name
        snapshot.mkdir(parents=True)
        manifest = snapshot / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "target_url": target_url,
                    "mode": "repository",
                }
            ),
            encoding="utf-8",
        )
        (snapshot / "tree.txt").write_text("blob\t1\tREADME.md\n", encoding="utf-8")
        os.utime(manifest, (modified_at, modified_at))
        return snapshot

    def test_status_and_confirmed_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "cache"
            now = time.time()
            old_snapshot = self.create_snapshot(
                root, "repository-old", now - (40 * 86400)
            )
            new_snapshot = self.create_snapshot(
                root, "repository-new", now - (2 * 86400)
            )

            snapshots = manage_cache.find_snapshots(root)
            self.assertEqual(len(snapshots), 2)
            selected = manage_cache.select_snapshots(
                snapshots, older_than_days=30, now=now
            )
            self.assertEqual(len(selected), 1)

            deleted, reclaimed = manage_cache.delete_snapshots(
                root, selected, confirm=False
            )
            self.assertEqual(deleted, [])
            self.assertEqual(reclaimed, 0)
            self.assertTrue(old_snapshot.exists())

            deleted, reclaimed = manage_cache.delete_snapshots(
                root, selected, confirm=True
            )
            self.assertEqual(len(deleted), 1)
            self.assertGreater(reclaimed, 0)
            self.assertFalse(old_snapshot.exists())
            self.assertTrue(new_snapshot.exists())

    def test_retention_policy_combines_age_and_per_target_limits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "cache"
            now = time.time()
            old = self.create_snapshot(root, "old", now - (40 * 86400))
            excess = self.create_snapshot(root, "excess", now - (3 * 86400))
            kept_one = self.create_snapshot(root, "kept-one", now - (2 * 86400))
            kept_two = self.create_snapshot(root, "kept-two", now - 86400)
            other_target = self.create_snapshot(
                root,
                "other",
                now - (4 * 86400),
                target_url="local:/tmp/other",
                group="local-other",
            )
            policy = {
                "max_age_days": 30,
                "max_snapshots_per_target": 2,
            }

            selected = manage_cache.select_by_retention_policy(
                manage_cache.find_snapshots(root), policy, now=now
            )
            selected_by_path = {
                item["path"]: set(item["retention_reasons"]) for item in selected
            }
            self.assertEqual(
                selected_by_path[str(old.resolve())], {"max-age", "max-per-target"}
            )
            self.assertEqual(
                selected_by_path[str(excess.resolve())], {"max-per-target"}
            )
            self.assertNotIn(str(kept_one.resolve()), selected_by_path)
            self.assertNotIn(str(kept_two.resolve()), selected_by_path)
            self.assertNotIn(str(other_target.resolve()), selected_by_path)

    def test_loads_cache_retention_from_config_and_allows_overrides(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary) / "config.json"
            config.write_text(
                json.dumps(
                    {
                        "github_app_id": "123",
                        "cache_retention": {
                            "max_age_days": 14,
                            "max_snapshots_per_target": 3,
                        },
                    }
                ),
                encoding="utf-8",
            )
            policy = manage_cache.retention_policy(config, {"max_age_days": 7})
            self.assertEqual(policy["max_age_days"], 7)
            self.assertEqual(policy["max_snapshots_per_target"], 3)
            self.assertTrue(policy["config_exists"])

    def test_does_not_follow_directory_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "cache"
            outside = base / "outside"
            self.create_snapshot(outside, "repository-external", time.time())
            root.mkdir()
            (root / "external-link").symlink_to(outside, target_is_directory=True)
            self.assertEqual(manage_cache.find_snapshots(root), [])

    def test_permission_audit_and_fix_secure_existing_cache_without_following_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "cache"
            snapshot = self.create_snapshot(root, "repository-old", time.time())
            outside = base / "outside.txt"
            outside.write_text("do not touch", encoding="utf-8")
            outside.chmod(0o644)
            (snapshot / "outside-link").symlink_to(outside)
            root.chmod(0o755)
            snapshot.chmod(0o755)
            (snapshot / "manifest.json").chmod(0o644)

            audit = manage_cache.audit_cache_permissions(root)
            self.assertGreater(audit["insecure_entries"], 0)
            fixed = manage_cache.secure_cache_permissions(root)
            self.assertEqual(fixed["remaining_insecure_entries"], 0)
            self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(snapshot.stat().st_mode), 0o700)
            self.assertEqual(
                stat.S_IMODE((snapshot / "manifest.json").stat().st_mode), 0o600
            )
            self.assertEqual(stat.S_IMODE(outside.stat().st_mode), 0o644)


if __name__ == "__main__":
    unittest.main()
