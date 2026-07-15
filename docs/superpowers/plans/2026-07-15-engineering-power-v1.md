# Engineering Power V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an installable Engineering Power plugin whose V1 workflows combine adapted engineering lifecycle guidance with a shared RepoLens evidence engine.

**Architecture:** Create a valid Codex plugin with five direct child skills. Move deterministic repository-evidence scripts into one shared package and expose a stable Python command interface. Keep each skill as an instruction layer that selects evidence mode, output contract, and report focus.

**Tech Stack:** Codex plugin manifest JSON, Markdown skills, Python 3.9 standard library, Git CLI, `unittest`.

## Global Constraints

- Keep target repositories read-only.
- Do not copy Superpowers files verbatim; use adapted workflow instructions.
- Do not add MCP servers, hooks, or automatic GitHub writes in V1.
- Preserve local Git, GitHub, working-tree, and patch evidence modes.
- Validate every plugin and skill before release.

---

### Task 1: Plugin foundation and marketplace

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `.agents/plugins/marketplace.json`
- Create: `skills/engineering-workflow/SKILL.md`
- Create: `tests/test_plugin_layout.py`

**Interfaces:**
- Produces a plugin named `engineering-power` discoverable from the local marketplace.
- `engineering-workflow` accepts an engineering task and optionally a repository or PR target.

- [ ] **Step 1: Write the failing layout test**

```python
def test_plugin_manifest_and_v1_skills_exist():
    assert (ROOT / ".codex-plugin/plugin.json").is_file()
    for name in V1_SKILLS:
        assert (ROOT / "skills" / name / "SKILL.md").is_file()
```

- [ ] **Step 2: Run the layout test**

Run: `python3 -m unittest tests.test_plugin_layout`

Expected: FAIL because plugin files do not exist.

- [ ] **Step 3: Scaffold the plugin and minimal workflow skill**

Use `plugin-creator`'s scaffold command with a repo-local marketplace. Set the
manifest name to `engineering-power`; create only `skills/` and marketplace
metadata. Write an adapted lifecycle skill that routes repository-aware work to
the evidence workflows without duplicating their collection commands.

- [ ] **Step 4: Verify the layout test and plugin validator**

Run: `python3 -m unittest tests.test_plugin_layout && python3 <plugin-creator>/scripts/validate_plugin.py .`

Expected: PASS and a valid plugin manifest.

- [ ] **Step 5: Commit**

Run: `git add .codex-plugin .agents skills/engineering-workflow tests/test_plugin_layout.py && git commit -m "feat: scaffold engineering power plugin"`

### Task 2: Shared Repo Evidence engine

**Files:**
- Create: `scripts/repo_evidence/__init__.py`
- Create: `scripts/repo_evidence/collect_local.py`
- Create: `scripts/repo_evidence/collect_github.py`
- Create: `scripts/repo_evidence/context.py`
- Create: `scripts/repo_evidence/report_validation.py`
- Create: `tests/test_repo_evidence.py`

**Interfaces:**
- Produces `collect_local(repository, profile) -> snapshot_metadata`.
- Produces `prepare_context(snapshot, profile) -> context_metadata`.
- Preserves exact commit, authentication method, cache status, and citations.

- [ ] **Step 1: Write failing local-fixture tests**

```python
def test_collect_local_returns_resolved_commit_and_layer_coverage():
    result = collect_local(FIXTURE_REPOSITORY, profile="quick")
    assert result["resolved_ref"]
    assert result["layer_coverage"]
```

- [ ] **Step 2: Run the test**

Run: `python3 -m unittest tests.test_repo_evidence`

Expected: FAIL because `collect_local` is not implemented.

- [ ] **Step 3: Port the deterministic RepoLens scripts behind the stable API**

Preserve current collection policy, cache identity, safe source-path handling,
context generation, and report citation validation. Do not import the old
repository at runtime.

- [ ] **Step 4: Run unit tests**

Run: `python3 -m unittest tests.test_repo_evidence`

Expected: PASS with a local Git fixture.

- [ ] **Step 5: Commit**

Run: `git add scripts/repo_evidence tests/test_repo_evidence.py && git commit -m "feat: add shared repository evidence engine"`

### Task 3: Repository and PR intelligence workflows

**Files:**
- Create: `skills/repo-intelligence/SKILL.md`
- Create: `skills/pr-impact-analysis/SKILL.md`
- Create: `references/repository-report-schema.md`
- Create: `references/pr-report-schema.md`
- Modify: `tests/test_plugin_layout.py`

**Interfaces:**
- `repo-intelligence` accepts a GitHub URL or local repository path.
- `pr-impact-analysis` accepts a PR URL, local compare, working tree, or patch.

- [ ] **Step 1: Write failing workflow contract checks**

```python
def test_repo_and_pr_skills_reference_shared_evidence_engine():
    assert "scripts/repo_evidence" in repo_skill_text
    assert "scripts/repo_evidence" in pr_skill_text
```

- [ ] **Step 2: Run the contract checks**

Run: `python3 -m unittest tests.test_plugin_layout`

Expected: FAIL until the two skills are created.

- [ ] **Step 3: Implement the two skills and report schemas**

Keep repository reports focused on product/system understanding and PR reports
focused on changed behavior, test impact, regression risk, and architecture
review. Require evidence citations and runtime disclosure in both.

- [ ] **Step 4: Verify skill and plugin validation**

Run: `python3 -m unittest tests.test_plugin_layout && python3 <skill-creator>/scripts/quick_validate.py skills/repo-intelligence && python3 <skill-creator>/scripts/quick_validate.py skills/pr-impact-analysis`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add skills/repo-intelligence skills/pr-impact-analysis references tests/test_plugin_layout.py && git commit -m "feat: add repository and pr intelligence workflows"`

### Task 4: Architecture and onboarding workflows

**Files:**
- Create: `skills/architecture-map/SKILL.md`
- Create: `skills/codebase-onboarding/SKILL.md`
- Create: `references/architecture-map-schema.md`
- Create: `references/onboarding-schema.md`
- Modify: `tests/test_plugin_layout.py`

**Interfaces:**
- Both skills consume an existing or freshly collected shared evidence snapshot.
- `architecture-map` outputs boundaries, data ownership, and business-flow diagrams.
- `codebase-onboarding` outputs a reading order, local-run path, and change map.

- [ ] **Step 1: Write failing per-skill contract checks**

```python
def test_architecture_and_onboarding_skills_have_distinct_outputs():
    assert "Architecture Diagram" in architecture_skill_text
    assert "Developer Onboarding" in onboarding_skill_text
```

- [ ] **Step 2: Run the checks**

Run: `python3 -m unittest tests.test_plugin_layout`

Expected: FAIL until both skills and references exist.

- [ ] **Step 3: Implement focused workflow instructions**

Require real component names, bounded Mermaid diagrams, cited business flows,
and explicit unknowns. Do not duplicate PR-report rules.

- [ ] **Step 4: Run all tests and validators**

Run: `python3 -m unittest && python3 <plugin-creator>/scripts/validate_plugin.py .`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add skills/architecture-map skills/codebase-onboarding references tests/test_plugin_layout.py && git commit -m "feat: add architecture and onboarding workflows"`

### Task 5: Installation and real-repository verification

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Create: `tests/test_install_contract.py`

**Interfaces:**
- Marketplace exposes `engineering-power` as `AVAILABLE` with `ON_INSTALL` authentication policy.

- [ ] **Step 1: Write failing marketplace contract test**

```python
def test_marketplace_exposes_engineering_power():
    entry = marketplace_plugin("engineering-power")
    assert entry["policy"]["installation"] == "AVAILABLE"
    assert entry["policy"]["authentication"] == "ON_INSTALL"
```

- [ ] **Step 2: Run the test**

Run: `python3 -m unittest tests.test_install_contract`

Expected: FAIL until marketplace metadata is complete.

- [ ] **Step 3: Complete marketplace metadata and test a local fixture invocation**

Run the shared evidence engine against a disposable local Git fixture. Verify
the output records a commit, local-filesystem authentication, citations, and no
target-repository mutation.

- [ ] **Step 4: Run final verification**

Run: `python3 -m unittest && python3 <plugin-creator>/scripts/validate_plugin.py . && git diff --check`

Expected: all commands succeed.

- [ ] **Step 5: Commit**

Run: `git add .agents tests && git commit -m "test: verify engineering power installation contract"`
