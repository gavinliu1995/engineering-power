import json
from pathlib import Path
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

    def write_snapshot(self, files):
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


if __name__ == "__main__":
    unittest.main()
