# Engineering Power Demo MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the Stage 1 golden PR workflow with evidence-backed dependency impact, API contract generation, and release note generation on top of the existing RepoLens evidence snapshot.

**Architecture:** Keep collection, caching, and source safety in `scripts/repo_evidence/`. Add a deterministic workflow-context builder that prioritizes evidence already present in one snapshot without recrawling the target. Add three concise user-facing skills and reference contracts, then route `pr-impact-analysis` through the same evidence state.

**Tech Stack:** Python 3.9 standard library, Git CLI, Markdown Codex skills, JSON plugin manifest, `unittest`.

## Global Constraints

- Keep target repositories read-only.
- Reuse one exact-state evidence snapshot; derived workflows must not recrawl the same target.
- Quick mode target is two minutes; Deep mode target is five minutes.
- Facts, inferences, and unknowns must be distinguishable.
- Important technical claims require repository-relative file and line citations.
- Executed, discovered, and recommended tests must remain distinct.
- Do not expose credentials, tokens, private keys, or secret values.
- Direct Bitbucket/VPN integration is outside the Demo MVP.
- Stage 2 refactoring and incident-triage implementation is outside this plan.

---

### Task 1: Workflow-specific evidence context

**Files:**
- Create: `scripts/repo_evidence/prepare_workflow_context.py`
- Create: `tests/test_workflow_context.py`
- Modify: `tests/test_plugin_layout.py`

**Interfaces:**
- Consumes: a snapshot directory containing `manifest.json` and `files/`.
- Produces: `build_workflow_context(snapshot: Path, workflow: str, profile: str, output: Path) -> dict`.
- Workflow values: `dependency-impact`, `api-contract`, `release-notes`.
- CLI: `prepare_workflow_context.py SNAPSHOT --workflow NAME --profile quick|deep [--output PATH]`.

- [ ] **Step 1: Write the failing test**

```python
def test_api_contract_context_prioritizes_routes_and_schemas(self):
    snapshot = self.make_snapshot([
        ("src/OrderController.java", "@GetMapping(\"/orders\")\nOrderDto list() {}\n"),
        ("src/OrderDto.java", "record OrderDto(String id) {}\n"),
        ("README.md", "setup\n"),
    ])
    result = build_workflow_context(snapshot, "api-contract", "quick", snapshot / "api.md")
    text = Path(result["context"]).read_text(encoding="utf-8")
    self.assertIn("src/OrderController.java:L1-L2", text)
    self.assertIn("src/OrderDto.java:L1-L1", text)
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_workflow_context`

Expected: FAIL because `prepare_workflow_context` does not exist.

- [ ] **Step 3: Implement the bounded context builder**

Implement these public values and functions:

```python
WORKFLOW_PROFILES = {
    "dependency-impact": {"terms": ("dependency", "pom.xml", "build.gradle", "package.json", "requirements", "import", "client")},
    "api-contract": {"terms": ("controller", "route", "endpoint", "openapi", "swagger", "schema", "dto", "request", "response", "graphql")},
    "release-notes": {"terms": ("changelog", "release", "readme", "controller", "route", "service", "config", "deploy", "migration", "test")},
}

```

Validate inputs, read only manifest-listed files, reject paths escaping
`snapshot/files`, rank changed and term-matching files first, enforce Quick and
Deep budgets, and implement the three exact function signatures declared in the
Interfaces block. Return selected files, truncation state, and snapshot metadata.

- [ ] **Step 4: Verify GREEN and regression safety**

```bash
python3 -m unittest tests.test_workflow_context
python3 -m unittest tests.test_repo_evidence tests.test_plugin_layout
```

Expected: new tests pass and the existing 31-test baseline remains green.

- [ ] **Step 5: Commit**

```bash
git add scripts/repo_evidence/prepare_workflow_context.py tests
git commit -m "feat: add workflow-specific evidence contexts"
```

### Task 2: Dependency impact analysis workflow

**Files:**
- Create: `skills/dependency-impact-analysis/SKILL.md`
- Create: `skills/dependency-impact-analysis/agents/openai.yaml`
- Create: `references/dependency-impact-schema.md`
- Create: `tests/test_skill_contracts.py`
- Modify: `tests/test_plugin_layout.py`

**Interfaces:**
- Consumes: repository, PR, local comparison, working tree, or patch target.
- Produces: direct dependencies, reverse consumers, transitive effects, test impact, risks, and citations.

- [ ] **Step 1: Write the failing contract test**

```python
def test_dependency_impact_skill_contract(self):
    text = skill_text("dependency-impact-analysis")
    for phrase in ("prepare_workflow_context.py", "dependency-impact", "direct dependencies", "reverse consumers", "Fact", "Inference", "Unknown"):
        self.assertIn(phrase, text)
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_plugin_layout tests.test_skill_contracts`

Expected: FAIL because the skill does not exist.

- [ ] **Step 3: Initialize and implement the skill**

```bash
python3 /Users/gavin.liu/.codex/skills/.system/skill-creator/scripts/init_skill.py dependency-impact-analysis --path skills --interface display_name="Dependency Impact Analysis" --interface short_description="Trace dependency and change propagation from repository evidence." --interface default_prompt="Analyze dependency impact for this repository or change."
```

Replace generated instructions with a concise workflow requiring one snapshot,
the `dependency-impact` context, concrete dependency direction, changed symbols,
direct dependencies, reverse consumers, transitive effects, test impact, risk,
facts/inferences/unknowns, and citations. Put output headings and fields in
`references/dependency-impact-schema.md`.

- [ ] **Step 4: Validate, test, and commit**

```bash
python3 /Users/gavin.liu/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/dependency-impact-analysis
python3 -m unittest tests.test_plugin_layout tests.test_skill_contracts
git add skills/dependency-impact-analysis references/dependency-impact-schema.md tests
git commit -m "feat: add dependency impact analysis workflow"
```

Expected: validation and tests pass before the commit.

### Task 3: API contract generator workflow

**Files:**
- Create: `skills/api-contract-generator/SKILL.md`
- Create: `skills/api-contract-generator/agents/openai.yaml`
- Create: `references/api-contract-schema.md`
- Modify: `tests/test_plugin_layout.py`
- Modify: `tests/test_skill_contracts.py`

**Interfaces:**
- Consumes: one snapshot plus the `api-contract` workflow context.
- Produces: API surface or delta with operation, path, inputs, outputs, authentication evidence, compatibility classification, citations, and unknowns.

- [ ] **Step 1: Write and run the failing contract test**

```python
def test_api_contract_skill_contract(self):
    text = skill_text("api-contract-generator")
    for phrase in ("prepare_workflow_context.py", "api-contract", "compatibility", "authentication", "Do not invent"):
        self.assertIn(phrase, text)
```

Run: `python3 -m unittest tests.test_plugin_layout tests.test_skill_contracts`

Expected: FAIL because the API contract skill is absent.

- [ ] **Step 2: Initialize and implement the skill**

```bash
python3 /Users/gavin.liu/.codex/skills/.system/skill-creator/scripts/init_skill.py api-contract-generator --path skills --interface display_name="API Contract Generator" --interface short_description="Generate cited API surfaces and compatibility deltas." --interface default_prompt="Generate an evidence-backed API contract for this target."
```

Require explicit evidence from routes, controllers, schemas, DTOs,
serialization, GraphQL, protobuf, or OpenAPI. Emit unknowns when evidence is
incomplete. Classify changed operations as added, removed, compatible,
potentially breaking, or breaking. Define the exact output contract in
`references/api-contract-schema.md`.

- [ ] **Step 3: Validate, test, and commit**

```bash
python3 /Users/gavin.liu/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/api-contract-generator
python3 -m unittest tests.test_plugin_layout tests.test_skill_contracts tests.test_workflow_context
git add skills/api-contract-generator references/api-contract-schema.md tests
git commit -m "feat: add api contract generator workflow"
```

Expected: validation and tests pass before the commit.

### Task 4: Release note generator workflow

**Files:**
- Create: `skills/release-note-generator/SKILL.md`
- Create: `skills/release-note-generator/agents/openai.yaml`
- Create: `references/release-note-schema.md`
- Modify: `tests/test_plugin_layout.py`
- Modify: `tests/test_skill_contracts.py`

**Interfaces:**
- Consumes: one snapshot plus the `release-notes` workflow context.
- Produces: technical notes, user-facing notes, upgrade actions, validation status, risks, and citations.

- [ ] **Step 1: Write and run the failing contract test**

```python
def test_release_note_skill_contract(self):
    text = skill_text("release-note-generator")
    for phrase in ("prepare_workflow_context.py", "release-notes", "technical", "user-facing", "executed", "recommended"):
        self.assertIn(phrase, text)
```

Run: `python3 -m unittest tests.test_plugin_layout tests.test_skill_contracts`

Expected: FAIL because the release-note skill is absent.

- [ ] **Step 2: Initialize and implement the skill**

```bash
python3 /Users/gavin.liu/.codex/skills/.system/skill-creator/scripts/init_skill.py release-note-generator --path skills --interface display_name="Release Note Generator" --interface short_description="Generate technical and user-facing release notes from code evidence." --interface default_prompt="Generate evidence-backed release notes for this change."
```

Require exact base/head state, behavior change, technical notes, supported
user-visible effects, upgrade/configuration/data actions, executed versus
recommended validation, risks, and citations. Exclude commit-message-only
product claims. Define headings in `references/release-note-schema.md`.

- [ ] **Step 3: Validate, test, and commit**

```bash
python3 /Users/gavin.liu/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/release-note-generator
python3 -m unittest tests.test_plugin_layout tests.test_skill_contracts tests.test_workflow_context
git add skills/release-note-generator references/release-note-schema.md tests
git commit -m "feat: add release note generator workflow"
```

Expected: validation and tests pass before the commit.

### Task 5: Golden PR integration and final verification

**Files:**
- Modify: `skills/pr-impact-analysis/SKILL.md`
- Modify: `skills/release-readiness/SKILL.md`
- Modify: `.codex-plugin/plugin.json`
- Create: `references/demo-golden-path.md`
- Modify: `tests/test_skill_contracts.py`

**Interfaces:**
- PR analysis owns the common exact base/head snapshot.
- Derived workflows reuse that snapshot only when requested.
- Release readiness consumes completed derived reports without pretending uninvoked workflows ran.

- [ ] **Step 1: Write and run the failing integration test**

```python
def test_pr_golden_path_routes_to_derived_workflows(self):
    text = skill_text("pr-impact-analysis")
    for name in ("dependency-impact-analysis", "api-contract-generator", "release-note-generator"):
        self.assertIn(name, text)
    capabilities = " ".join(plugin_manifest()["interface"]["capabilities"]).lower()
    for phrase in ("dependency impact", "api contract", "release note"):
        self.assertIn(phrase, capabilities)
```

Run: `python3 -m unittest tests.test_skill_contracts`

Expected: FAIL because routing and capabilities are absent.

- [ ] **Step 2: Implement routing, plugin metadata, and demo guidance**

Update PR analysis to collect once and route only requested derived outputs.
Update release readiness to consume already-produced outputs. Add the three
capabilities to the manifest. Document the input, command sequence, engineering
report, decision summary, and expected limitations in
`references/demo-golden-path.md`.

- [ ] **Step 3: Run complete verification**

```bash
python3 -m unittest tests.test_plugin_layout tests.test_repo_evidence tests.test_workflow_context tests.test_skill_contracts
python3 /Users/gavin.liu/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
for skill in skills/*; do python3 /Users/gavin.liu/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"; done
python3 -m py_compile scripts/repo_evidence/*.py
git diff --check
```

Expected: all unit tests, all skill validators, plugin validation, Python
compilation, and whitespace checks succeed.

- [ ] **Step 4: Commit**

```bash
git add .codex-plugin/plugin.json skills/pr-impact-analysis skills/release-readiness references/demo-golden-path.md tests/test_skill_contracts.py
git commit -m "feat: integrate the golden pr analysis workflow"
```
