---
name: release-readiness
description: Assess release readiness for a repository, PR, local comparison, working tree, or patch using repository evidence. Use for test coverage, configuration and deployment impact, rollback questions, operational risk, and release gates.
---
## Portable runtime

This generated Agent Skill shares the adjacent `engineering-power` runtime core.
Resolve `$ENGINEERING_POWER_CORE` to `../engineering-power` relative to this
Skill directory. Run repository evidence tools from
`$ENGINEERING_POWER_CORE/scripts/repo_evidence/` and load shared report schemas
from `$ENGINEERING_POWER_CORE/references/`. Do not bypass the evidence engine
for repository, pull-request, comparison, working-tree, or patch analysis.


# Release Readiness

Collect one shared repository or change snapshot. Produce a release decision
brief: changed behavior or system scope, executed versus recommended tests,
configuration and deployment impact, observability and rollback evidence,
blocking risks, and a clear `go`, `go with conditions`, or `no-go` recommendation.
Never claim production readiness or test success without direct execution
evidence. Cite every gate and label unknowns as verification work.

Consume completed derived reports from dependency impact, API contract, and
release-note workflows when they share the same exact snapshot. Do not claim an
unrequested, failed, or incomplete derived workflow was performed. Treat its
absence as an explicit release-readiness unknown when the missing result is
material to the decision.
