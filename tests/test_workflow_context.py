import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts" / "repo_evidence"
sys.path.insert(0, str(SCRIPTS))

from prepare_workflow_context import build_workflow_context


class WorkflowContextTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.snapshot = Path(self.temporary.name) / "snapshot"
        (self.snapshot / "files").mkdir(parents=True)

    def tearDown(self):
        self.temporary.cleanup()

    def write_snapshot(self, files, declared_changed_paths=None):
        collected = []
        for path, content, changed in files:
            target = self.snapshot / "files" / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            collected.append(
                {
                    "path": path,
                    "size": len(content.encode("utf-8")),
                    "layer": "route" if "Controller" in path else "other",
                    "changed_in_pull_request": changed,
                }
            )
        manifest = {
            "mode": "pull-request",
            "target_url": "local-fixture",
            "resolved_ref": "a" * 40,
            "authentication": {"method": "local-filesystem"},
            "pull_request": {"base_sha": "b" * 40, "head_sha": "a" * 40},
            "selection": {"deadline_reached": False, "missing_layers": []},
            "collected_files": collected,
        }
        (self.snapshot / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        changed_paths = (
            declared_changed_paths
            if declared_changed_paths is not None
            else [path for path, _, changed in files if changed]
        )
        (self.snapshot / "pull-request-files.json").write_text(
            json.dumps(
                [
                    {"filename": path, "status": "modified"}
                    for path in changed_paths
                ]
            ),
            encoding="utf-8",
        )

    def test_api_contract_context_prioritizes_routes_and_schemas(self):
        self.write_snapshot(
            [
                (
                    "src/OrderController.java",
                    '@GetMapping("/orders")\nOrderDto list() {}\n',
                    True,
                ),
                ("src/OrderDto.java", "record OrderDto(String id) {}\n", False),
                ("README.md", "setup\n", False),
            ]
        )

        result = build_workflow_context(
            self.snapshot, "api-contract", "quick", self.snapshot / "api.md"
        )
        self.assertEqual(
            stat.S_IMODE((self.snapshot / "api.md").stat().st_mode), 0o600
        )

        text = Path(result["context"]).read_text(encoding="utf-8")
        self.assertIn("src/OrderController.java:L1-L2", text)
        self.assertIn("src/OrderDto.java:L1-L1", text)
        self.assertEqual(result["selected_files"][0], "src/OrderController.java")
        self.assertEqual(result["workflow"], "api-contract")

    def test_dependency_context_prioritizes_changed_build_files(self):
        self.write_snapshot(
            [
                ("src/Service.java", "import client.RemoteClient;\n", False),
                ("pom.xml", "<dependency>demo</dependency>\n", True),
                ("README.md", "dependency overview\n", False),
            ]
        )

        result = build_workflow_context(
            self.snapshot,
            "dependency-impact",
            "quick",
            self.snapshot / "dependency.md",
        )

        self.assertEqual(result["selected_files"][0], "pom.xml")
        self.assertFalse(result["truncated"])

    def test_quick_context_keeps_all_changed_files_before_support_budget(self):
        files = [
            (
                f"src/feature/Changed{index}.java",
                f"class Changed{index} {{}}\n",
                True,
            )
            for index in range(15)
        ]
        files.append(("README.md", "general setup only\n", False))
        self.write_snapshot(files)

        result = build_workflow_context(
            self.snapshot,
            "release-notes",
            "quick",
            self.snapshot / "release.md",
        )

        self.assertEqual(result["changed_files_total"], 15)
        self.assertEqual(result["changed_files_selected"], 15)
        self.assertEqual(result["changed_files_missing_from_snapshot"], [])
        self.assertTrue(
            all(path in result["selected_files"] for path, _, _ in files[:15])
        )

    def test_api_context_does_not_fill_budget_with_irrelevant_files(self):
        self.write_snapshot(
            [
                ("scripts/connect.sh", "ssh target\n", True),
                ("README.md", "general setup only\n", False),
                (".gitignore", "*.log\n", False),
            ]
        )

        result = build_workflow_context(
            self.snapshot, "api-contract", "quick", self.snapshot / "api.md"
        )

        self.assertEqual(result["selected_files"], ["scripts/connect.sh"])
        self.assertFalse(result["truncated"])
        self.assertEqual(result["relevant_supporting_candidates"], 0)

    def test_changed_symbol_affinity_prioritizes_related_test(self):
        self.write_snapshot(
            [
                (
                    "src/OrderController.java",
                    '@GetMapping("/orders")\nOrderDto list() {}\n',
                    True,
                ),
                ("src/AaaDto.java", "record AaaDto(String id) {}\n", False),
                (
                    "tests/ZzzOrderControllerTest.java",
                    "class ZzzOrderControllerTest {}\n",
                    False,
                ),
            ]
        )

        result = build_workflow_context(
            self.snapshot, "api-contract", "quick", self.snapshot / "api.md"
        )

        self.assertEqual(
            result["selected_files"][:2],
            ["src/OrderController.java", "tests/ZzzOrderControllerTest.java"],
        )

    def test_declared_changed_file_missing_from_snapshot_is_disclosed(self):
        self.write_snapshot(
            [("src/OrderController.java", "class OrderController {}\n", True)],
            declared_changed_paths=[
                "src/OrderController.java",
                "docs/release-notes.tex",
            ],
        )

        result = build_workflow_context(
            self.snapshot,
            "release-notes",
            "quick",
            self.snapshot / "release.md",
        )

        self.assertEqual(
            result["changed_files_missing_from_snapshot"],
            ["docs/release-notes.tex"],
        )
        self.assertTrue(
            any("not present" in item.lower() for item in result["limitations"])
        )

    def test_manifest_path_cannot_escape_snapshot_files(self):
        self.write_snapshot([])
        manifest_path = self.snapshot / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["collected_files"] = [{"path": "../outside.txt", "size": 6}]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        (self.snapshot / "outside.txt").write_text("secret", encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "outside snapshot files"):
            build_workflow_context(
                self.snapshot, "release-notes", "quick", self.snapshot / "release.md"
            )

    def test_invalid_workflow_is_rejected(self):
        self.write_snapshot([])
        with self.assertRaisesRegex(ValueError, "Unsupported workflow"):
            build_workflow_context(
                self.snapshot, "unknown", "quick", self.snapshot / "unknown.md"
            )

    def test_workflow_context_redacts_secret_values_before_rendering(self):
        synthetic_secret = "workflow-context-dummy-secret"
        self.write_snapshot(
            [
                (
                    "src/OrderController.java",
                    '@GetMapping("/orders")\n'
                    f'<server password="{synthetic_secret}" />\n'
                    'res.setHeader("Set-Cookie", [\n'
                    f'    "session={synthetic_secret}; HttpOnly",\n'
                    "]);\n"
                    "OrderDto list() {}\n",
                    True,
                )
            ]
        )

        result = build_workflow_context(
            self.snapshot, "api-contract", "quick", self.snapshot / "api.md"
        )
        context = Path(result["context"]).read_text(encoding="utf-8")

        self.assertNotIn(synthetic_secret, context)
        self.assertIn('password="[REDACTED]"', context)
        self.assertIn('"Set-Cookie", "[REDACTED]"', context)
        self.assertIn("     6 | OrderDto list() {}", context)


if __name__ == "__main__":
    unittest.main()
