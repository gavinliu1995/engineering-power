# Cross-Platform Agent Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use engineering-power:subagent-driven-development (recommended) or engineering-power:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Engineering Power as a standard Agent Skills package for GitHub Copilot, Claude Code, and Cursor while retaining the existing Codex plugin.

**Architecture:** Keep `scripts/repo_evidence/` and `references/` as the source of truth. Add one portable umbrella skill under `.agents/skills/engineering-power/`, with an installer that builds a self-contained host-specific copy. The Codex plugin continues to use `skills/` unchanged.

**Tech Stack:** Python 3 standard library, Markdown Agent Skills, unittest, GitHub Copilot CLI-compatible directory structure.

## Global Constraints

- Default analysis remains read-only.
- Local Git, working-tree, compare, and patch modes remain supported without GitHub App access.
- The cloud-agent path is not presented as a Bitbucket/VPN solution.
- No private keys, tokens, or local user paths are included in portable packages.
- Existing Codex plugin behavior and 54 existing tests remain intact.

---

### Task 1: Define the portable umbrella Skill contract

**Files:**
- Create: `.agents/skills/engineering-power/SKILL.md`
- Test: `tests/test_cross_platform_skill.py`

**Consumes:** Existing workflow names in `skills/`, shared evidence scripts, and report references.

**Produces:** A standard Agent Skills entry point with required `name`/`description` frontmatter and explicit workflow routing.

- [ ] **Step 1: Write a failing package-contract test**

Assert that `.agents/skills/engineering-power/SKILL.md` exists, uses the name
`engineering-power`, routes repository, PR, architecture, API, release,
onboarding, migration, debugging, planning and verification requests, and
declares read-only defaults.

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `python3 -m unittest tests.test_cross_platform_skill.CrossPlatformSkillTests.test_portable_skill_contract -v`

Expected: FAIL because the portable `SKILL.md` does not exist.

- [ ] **Step 3: Add the minimal standard Skill**

Write standard YAML frontmatter and portable instructions. Reference resources
relative to the skill root; do not add Codex-only metadata or pre-approve shell
access.

- [ ] **Step 4: Run the focused test to verify it passes**

Run: `python3 -m unittest tests.test_cross_platform_skill.CrossPlatformSkillTests.test_portable_skill_contract -v`

Expected: PASS.

### Task 2: Build a safe host installer

**Files:**
- Create: `scripts/install_agent_skill.py`
- Test: `tests/test_cross_platform_skill.py`

**Consumes:** `.agents/skills/engineering-power/`, `scripts/repo_evidence/`, and `references/`.

**Produces:** A `--host copilot|claude|cursor` installer that copies a self-contained package to a selected target root.

- [ ] **Step 1: Write failing installer tests**

Use temporary directories. Assert the three host locations receive `SKILL.md`,
`scripts/repo_evidence/`, and `references/`; assert no source path, token, or
private-key payload is copied.

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python3 -m unittest tests.test_cross_platform_skill.CrossPlatformSkillTests.test_installer_creates_host_specific_package -v`

Expected: FAIL because no installer exists.

- [ ] **Step 3: Add minimal installer implementation**

Support `--host`, `--target-root`, `--force`, and `--dry-run`. Refuse an
existing destination unless `--force` is explicit. Copy only the standard
skill, evidence scripts, and references.

- [ ] **Step 4: Run focused tests to verify they pass**

Run: `python3 -m unittest tests.test_cross_platform_skill -v`

Expected: PASS.

### Task 3: Document and validate the migration

**Files:**
- Modify: `README.md`
- Modify: `tests/test_plugin_layout.py`
- Test: `tests/test_cross_platform_skill.py`

**Consumes:** Portable skill and installer behavior.

**Produces:** Explicit Copilot/Claude/Cursor installation and smoke-test guidance, plus regression coverage that Codex still remains available.

- [ ] **Step 1: Write failing documentation/compatibility tests**

Assert README names Copilot, Claude Code, Cursor, local Bitbucket/VPN mode, and
the installer command. Assert the Codex manifest and existing `skills/` remain.

- [ ] **Step 2: Run focused tests to verify they fail**

Run: `python3 -m unittest tests.test_cross_platform_skill.CrossPlatformSkillTests.test_readme_documents_cross_platform_installation -v`

Expected: FAIL until README documents the new flow.

- [ ] **Step 3: Document hosts and smoke tests**

Add concise examples for each host, with GitHub Copilot CLI `/skills reload` /
`/skills info engineering-power` verification. Clearly state cloud-agent limits.

- [ ] **Step 4: Run full verification**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 5: Commit**

Run: `git add .agents scripts/install_agent_skill.py tests README.md docs && git commit -m "feat: add cross-platform agent skills package"`
