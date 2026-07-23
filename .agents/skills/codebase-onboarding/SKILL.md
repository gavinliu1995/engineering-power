---
name: codebase-onboarding
description: Create a practical evidence-backed onboarding guide for a GitHub repository or local Git repository. Use for reading order, local setup, common change locations, test paths, operational dependencies, and first-week engineering guidance.
---
## Portable runtime

This generated Agent Skill shares the adjacent `engineering-power` runtime core.
Resolve `$ENGINEERING_POWER_CORE` to `../engineering-power` relative to this
Skill directory. Run repository evidence tools from
`$ENGINEERING_POWER_CORE/scripts/repo_evidence/` and load shared report schemas
from `$ENGINEERING_POWER_CORE/references/`. Do not bypass the evidence engine
for repository, pull-request, comparison, working-tree, or patch analysis.


# Codebase Onboarding

Use one shared repository snapshot and citation context. Explain product purpose,
the recommended reading order from entry point to data boundary, local build and
run prerequisites, common modification locations, test and operational paths,
and questions a new engineer must clarify. Cite every command and configuration
claim from repository evidence; do not expose secrets or claim unexecuted tests
passed.
