# GitHub Copilot 20-Skill Full Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use engineering-power:subagent-driven-development (recommended) or engineering-power:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate, install, and validate all 20 canonical Engineering Power Skills as individually discoverable Agent Skills while retaining the shared `engineering-power` runtime core and Codex Plugin.

**Architecture:** Root `skills/*` remains the only hand-maintained source. A deterministic synchronizer generates platform-neutral siblings under `.agents/skills/*`, rewriting Codex-only namespace and runtime paths to a shared adjacent `engineering-power` core. The installer copies the resulting 21-directory suite into each supported host without touching unrelated skills.

**Tech Stack:** Python 3 standard library, `unittest`, Markdown/YAML Skill files, GitHub Copilot Agent Skills directory conventions.

## Global Constraints

- Preserve all 20 canonical directories under `skills/*` unchanged.
- Generate 20 portable Skills plus the existing `engineering-power` core.
- Never duplicate `scripts/repo_evidence` into each individual Skill.
- Exclude `agents/openai.yaml`, `__pycache__`, and `*.pyc` from portable Skills.
- Preserve unrelated host Skills during install and force reinstall.
- Implement every production change through a failing regression test first.

---

### Task 1: Define the generated-suite contract

**Files:**
- Modify: `tests/test_cross_platform_skill.py`
- Test: `tests/test_cross_platform_skill.py`

**Interfaces:**
- Consumes: canonical skill directories from `skills/*`
- Produces: assertions for the expected 21 managed directories and platform-neutral content

- [ ] **Step 1: Write failing directory and transformation tests**

Add tests that derive canonical names from `skills/*`, require the same names under
`.agents/skills`, preserve frontmatter names, reject `$PLUGIN_ROOT`,
`engineering-power:` and `../../references`, and exclude `agents/openai.yaml`.

- [ ] **Step 2: Write failing auxiliary-resource tests**

Require representative resources such as
`requesting-code-review/code-reviewer.md`,
`subagent-driven-development/scripts/review-package.py`, and
`brainstorming/visual-companion.md`.

- [ ] **Step 3: Run focused tests and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_cross_platform_skill.CrossPlatformSkillTests.test_all_canonical_skills_are_generated_for_agent_hosts \
  tests.test_cross_platform_skill.CrossPlatformSkillTests.test_generated_skills_are_platform_neutral \
  tests.test_cross_platform_skill.CrossPlatformSkillTests.test_generated_skills_copy_auxiliary_resources
```

Expected: FAIL because only `.agents/skills/engineering-power` exists.

### Task 2: Generate the 20 portable Skills

**Files:**
- Modify: `scripts/sync_portable_agent_skill.py`
- Generated: `.agents/skills/<canonical-skill>/**`
- Test: `tests/test_cross_platform_skill.py`

**Interfaces:**
- Consumes: `skills/*`, `scripts/repo_evidence`, and `references`
- Produces: `canonical_skill_names()`, transformed SKILL content, synchronized portable directories, and drift diagnostics

- [ ] **Step 1: Implement canonical discovery and exclusions**

Discover directories containing `SKILL.md`, and copy all files except
`agents/`, `__pycache__`, and `*.pyc`.

- [ ] **Step 2: Implement deterministic SKILL transformation**

Rewrite namespace and runtime paths, then inject the portable-runtime block that
resolves `$ENGINEERING_POWER_CORE` to the adjacent `engineering-power` Skill.

- [ ] **Step 3: Extend `--check` to the complete suite**

Compare all expected generated files, report missing/different/unexpected entries,
and reject missing or extra managed Skill directories.

- [ ] **Step 4: Generate the suite and verify GREEN**

Run:

```bash
python3 scripts/sync_portable_agent_skill.py
python3 -m unittest tests.test_cross_platform_skill
```

Expected: all cross-platform tests implemented so far PASS.

### Task 3: Install the complete suite safely

**Files:**
- Modify: `scripts/install_agent_skill.py`
- Modify: `tests/test_cross_platform_skill.py`

**Interfaces:**
- Consumes: `.agents/skills` generated suite
- Produces: host Skills root resolution and atomic preflight for 21 managed directories

- [ ] **Step 1: Write failing installer-suite tests**

Require all 21 directories for Copilot, Claude, and Cursor; verify that an unrelated
`example-skill` survives; verify that a single collision fails before copying any
managed directory.

- [ ] **Step 2: Run installer tests and verify RED**

Run:

```bash
python3 -m unittest \
  tests.test_cross_platform_skill.CrossPlatformSkillTests.test_installer_creates_complete_host_suite \
  tests.test_cross_platform_skill.CrossPlatformSkillTests.test_installer_preserves_unrelated_skills \
  tests.test_cross_platform_skill.CrossPlatformSkillTests.test_installer_preflights_conflicts
```

Expected: FAIL because the installer currently copies only the core directory.

- [ ] **Step 3: Implement suite-root install and preflight**

Resolve the host Skills root, validate all managed sources, preflight collisions,
then copy or replace only the 21 managed directories.

- [ ] **Step 4: Verify installer GREEN**

Run:

```bash
python3 -m unittest tests.test_cross_platform_skill
```

Expected: all cross-platform tests PASS.

### Task 4: Document and validate host parity

**Files:**
- Modify: `README.md`
- Modify: `tests/test_cross_platform_skill.py`

**Interfaces:**
- Consumes: final generated and installation contracts
- Produces: user-facing Copilot/Claude/Cursor installation, selection, synchronization, and verification guide

- [ ] **Step 1: Write failing README contract assertions**

Require the README to state that Copilot receives 20 individual Skills plus the
router/core, and document sync, install, reload/list, and canonical-source rules.

- [ ] **Step 2: Update README**

Document suite structure, supported hosts, example individual Skill names, update
workflow, local Bitbucket flow, and Codex coexistence.

- [ ] **Step 3: Validate all generated Skills**

Run:

```bash
for skill in .agents/skills/*; do
  python3 /Users/gavin.liu/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$skill"
done
```

Expected: 21 successful validations.

### Task 5: Run complete regression and hand off

**Files:**
- Verify: repository-wide tests and generated package

**Interfaces:**
- Consumes: completed implementation
- Produces: evidence that Codex and portable Agent Skills remain compatible

- [ ] **Step 1: Verify generated content is current**

Run:

```bash
python3 scripts/sync_portable_agent_skill.py --check
```

Expected: `portable Agent Skill suite is in sync`.

- [ ] **Step 2: Run all automated tests**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all tests PASS with no errors.

- [ ] **Step 3: Inspect repository state**

Run:

```bash
git status --short
git diff --check
```

Expected: only intended source, generated Skill, test, design, plan, and README
changes; no whitespace errors or secrets.

- [ ] **Step 4: Commit**

```bash
git add \
  .agents/skills \
  README.md \
  scripts/install_agent_skill.py \
  scripts/sync_portable_agent_skill.py \
  tests/test_cross_platform_skill.py \
  docs/superpowers/specs/2026-07-23-copilot-full-skill-parity-design.md \
  docs/superpowers/plans/2026-07-23-copilot-full-skill-parity.md
git commit -m "feat: migrate all engineering power skills to copilot"
```

Expected: one clean feature commit on `copilot_use`.
