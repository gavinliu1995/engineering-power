# Copilot Quality Hardening Implementation Plan

> **For agentic workers:** Execute this plan sequentially in the current session. Follow Engineering Power Test-Driven Development for every behavior change and Verification Before Completion before any completion claim.

**Goal:** Remove secret values from all model-facing evidence, make report coverage deterministic, add a strict Architecture Map report contract, and make inline delivery and Quick-mode time limits explicit across Copilot, Codex, Claude, and Cursor.

**Architecture:** Keep raw evidence snapshots private and unchanged. Introduce one shared redaction boundary between snapshots and all model-facing contexts. Treat manifest statistics as the single source of truth for final report coverage. Model Architecture Map as a first-class report type with its own validator/finalizer rules. Keep portable Agent Skill instructions synchronized with the shared scripts and references.

**Tech stack:** Python 3 standard library, `unittest`, Markdown Agent Skills, Mermaid, Git.

## Global constraints

- Do not print or copy real credential values into tests, logs, reports, or commits.
- Preserve source line count and line numbers during redaction.
- Do not alter raw snapshot files under `files/`; only derived contexts and reports are sanitized.
- Default repository analysis remains read-only.
- Keep local cache semantics unchanged: default output may hit shared cache; explicit `--output` remains an intentional cache miss.
- Empty patch remains a valid safe no-op collection, not proof that non-empty patch analysis passed.

---

## Task 1: Add one shared model-context redaction boundary

**Files:**

- Create: `scripts/repo_evidence/redact_context.py`
- Modify: `scripts/repo_evidence/prepare_analysis_context.py`
- Modify: `scripts/repo_evidence/prepare_workflow_context.py`
- Modify: `tests/test_repo_evidence.py`
- Modify: `tests/test_workflow_context.py`

### Step 1: Write failing unit and integration tests

Add table-driven tests for synthetic values in:

- shell/properties assignments (`password=value`, `TOKEN: value`)
- JSON/YAML (`"apiKey": "value"`, `secret: value`)
- XML elements and attributes (`<password>value</password>`, `password="value"`)
- CLI flags (`--token value`, `--password=value`)
- authorization headers (`Bearer value`, `Basic value`)
- URL user-info (`https://user:value@example.test/path`)
- private-key blocks
- compound user records containing password-like fields

Add one integration test for `prepare_analysis_context.build_context` and one for `prepare_workflow_context.build_workflow_context`. Each test must assert:

```python
self.assertNotIn("synthetic-secret-value", context)
self.assertIn("[REDACTED]", context)
self.assertEqual(original_line_count, redacted_line_count)
```

Run:

```bash
python3 -m unittest tests.test_repo_evidence tests.test_workflow_context -v
```

Expected: FAIL because the shared module does not exist or full patterns are not redacted.

### Step 2: Implement minimal shared redaction

Create `redact_context.py` with public functions:

```python
def redact_text(text: str) -> str: ...
def redact_lines(lines: list[str]) -> list[str]: ...
```

Implementation rules:

- replace only values, not keys or surrounding syntax;
- preserve every newline;
- replace private-key body lines with `[REDACTED]` while keeping BEGIN/END markers and line count;
- use deterministic `[REDACTED]` markers;
- never log the matched value.

Use this module in both context builders before rendering numbered excerpts. Bump `CONTEXT_POLICY_VERSION` and `WORKFLOW_CONTEXT_VERSION` so old unredacted derived contexts cannot be reused.

### Step 3: Run focused tests

```bash
python3 -m unittest tests.test_repo_evidence tests.test_workflow_context -v
```

Expected: PASS.

### Step 4: Commit

```bash
git add scripts/repo_evidence/redact_context.py scripts/repo_evidence/prepare_analysis_context.py scripts/repo_evidence/prepare_workflow_context.py tests/test_repo_evidence.py tests/test_workflow_context.py
git commit -m "fix: redact model-facing repository evidence"
```

---

## Task 2: Make coverage metadata deterministic

**Files:**

- Modify: `scripts/repo_evidence/finalize_report.py`
- Modify: `scripts/repo_evidence/validate_report.py`
- Modify: `references/report-schema.md`
- Modify: `tests/test_repo_evidence.py`

### Step 1: Write failing coverage tests

Add fixtures whose manifest contains:

```json
{"stats": {"collected_files": 360, "text_candidates": 2866, "tree_entries": 3608}}
```

Test that finalization rewrites any draft coverage to exactly:

```text
Coverage: 360/2866 text candidates
Tree entries: 3608
```

Test that direct report validation rejects `Coverage: 2866/3608 text candidates` against that manifest.

Run:

```bash
python3 -m unittest tests.test_repo_evidence.ReportFinalizationTests -v
```

Expected: FAIL because finalization currently trusts draft coverage and validation does not compare it to the manifest.

### Step 2: Implement manifest-owned coverage

In `finalize_report.py`:

- load the manifest before draft validation;
- replace or insert `Coverage:` and `Tree entries:` from `manifest.stats`;
- validate the normalized draft;
- keep reasoning-evidence counts separate from collection coverage.

In `validate_report.py`:

- parse `Coverage:` and `Tree entries:`;
- when manifest statistics are present, reject mismatches;
- retain compatibility with small legacy fixtures that omit `stats`.

Update `report-schema.md` so every report uses deterministic coverage fields and never uses `tree_entries` as the text-candidate denominator.

### Step 3: Run focused tests

```bash
python3 -m unittest tests.test_repo_evidence.ReportFinalizationTests -v
```

Expected: PASS.

### Step 4: Commit

```bash
git add scripts/repo_evidence/finalize_report.py scripts/repo_evidence/validate_report.py references/report-schema.md tests/test_repo_evidence.py
git commit -m "fix: derive report coverage from snapshot manifests"
```

---

## Task 3: Add Architecture Map as a strict report type

**Files:**

- Modify: `scripts/repo_evidence/validate_report.py`
- Modify: `scripts/repo_evidence/finalize_report.py`
- Modify: `references/architecture-focus.md`
- Modify: `references/report-schema.md`
- Modify: `tests/test_repo_evidence.py`

### Step 1: Write failing Architecture contract tests

Add a valid Architecture report fixture with exact headings:

```text
Target and Evidence
System Context and Runtime Units
Module Boundaries and Dependencies
Architecture Diagram
Concrete Feature Flow
Trust, State, and External Boundaries
Risks and Incremental Target State
Unknowns
Evidence Index
```

Require two Mermaid diagrams and a concrete chain that names at least three stages such as Page/Route, Provider/Service, and Client/DAO. Add negative tests for:

- missing concrete feature flow;
- only one Mermaid diagram;
- more than five Quick risks;
- Quick report longer than 7,000 characters.

Run:

```bash
python3 -m unittest tests.test_repo_evidence.ReportFinalizationTests -v
```

Expected: FAIL because `architecture` is not a report type.

### Step 2: Implement Architecture validation and profile rules

Add `architecture` to `REPORT_TYPES`. Enforce the exact headings, two Mermaid diagrams, minimum citation count, and a concrete feature chain. In `finalize_report.py`, use a 7,000-character Quick limit for `architecture`; Deep retains the shared wider limit. Require 1–5 prioritized risks in Quick.

Expand `architecture-focus.md` with:

- runtime/deployable units;
- dependency direction;
- state ownership;
- trust and external boundaries;
- one concrete `Page/Route → Provider/Service → Client/DAO` chain;
- incremental target state;
- 100–110 second active composition guidance and no late evidence expansion.

Add the formal Architecture Map template to `report-schema.md`.

### Step 3: Run focused tests

```bash
python3 -m unittest tests.test_repo_evidence.ReportFinalizationTests -v
```

Expected: PASS.

### Step 4: Commit

```bash
git add scripts/repo_evidence/validate_report.py scripts/repo_evidence/finalize_report.py references/architecture-focus.md references/report-schema.md tests/test_repo_evidence.py
git commit -m "feat: enforce architecture map report contract"
```

---

## Task 4: Harden the portable router and delivery contract

**Files:**

- Modify: `.agents/skills/engineering-power/SKILL.md`
- Modify: `tests/test_cross_platform_skill.py`
- Modify: `tests/test_repo_evidence.py`

### Step 1: Write failing portable-contract tests

Require the portable Skill to state that:

- Architecture Map loads both `references/architecture-focus.md` and `references/report-schema.md`;
- the formal report and Mermaid diagrams are inline by default;
- artifact files are supplemental only;
- Quick stops broad evidence expansion when 30 seconds or less remain;
- Architecture reports use `--report-type architecture`;
- secret-like evidence is redacted before the model sees it.

Add/retain cache semantics tests proving:

- default output gets a cache hit on unchanged state;
- explicit `--output` intentionally does not claim a shared cache hit.

Keep the empty-patch test description explicit: it verifies safe no-op handling only.

Run:

```bash
python3 -m unittest tests.test_cross_platform_skill tests.test_repo_evidence -v
```

Expected: FAIL on the new router/delivery assertions.

### Step 2: Update portable instructions

Add explicit routing, time-budget, redaction, architecture, and inline-delivery rules to `.agents/skills/engineering-power/SKILL.md`. Do not duplicate full references in the router.

### Step 3: Synchronize shared resources and run focused tests

```bash
python3 scripts/sync_portable_agent_skill.py
python3 -m unittest tests.test_cross_platform_skill tests.test_repo_evidence -v
```

Expected: PASS and portable package in sync.

### Step 4: Commit

```bash
git add .agents/skills/engineering-power tests/test_cross_platform_skill.py tests/test_repo_evidence.py
git commit -m "fix: harden cross-platform architecture delivery"
```

---

## Task 5: Full verification, packaging, and smoke tests

**Files:**

- Verify: `skills/*/SKILL.md`
- Verify: `.agents/skills/engineering-power/`
- Verify: `.codex-plugin/plugin.json`
- Modify only if required by the verified packaging workflow: `.codex-plugin/plugin.json`

### Step 1: Run all automated checks

```bash
python3 -m unittest discover -s tests -v
python3 scripts/sync_portable_agent_skill.py --check
python3 /Users/gavin.liu/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/engineering-power
python3 /Users/gavin.liu/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Expected: all tests and validators PASS.

### Step 2: Run deterministic redaction and report smoke tests

Use a temporary synthetic Git repository containing dummy credentials. Collect evidence, prepare both generic and workflow contexts, and assert the dummy literal is absent while `[REDACTED]` remains.

Finalize a synthetic Architecture report with an intentionally wrong coverage line and assert the final report contains manifest-derived coverage, two Mermaid diagrams, valid citations, and `report_type=architecture`.

### Step 3: Reinstall cross-platform packages locally

```bash
python3 scripts/install_agent_skill.py --host copilot --target-root /Users/gavin.liu --force
python3 scripts/install_agent_skill.py --host claude --target-root /Users/gavin.liu --force
python3 scripts/install_agent_skill.py --host cursor --target-root /Users/gavin.liu --force
```

Refresh the Codex plugin cachebuster and reinstall using the verified Plugin Creator workflow. Open a new task for UI metadata validation.

### Step 4: Run one real read-only Architecture smoke test

Use `/Users/gavin.liu/Downloads/DevOps/mbba-admintool` in Quick mode. Verify:

- target repository HEAD/status unchanged;
- correct `collected_files/text_candidates` coverage;
- two inline Mermaid diagrams;
- at least one concrete feature flow;
- no secret literals in model-facing context or final report;
- deadline/coverage limitation accurately reported.

### Step 5: Final repository verification

```bash
git status --short
git log -5 --oneline
```

Do not push without explicit user authorization.
