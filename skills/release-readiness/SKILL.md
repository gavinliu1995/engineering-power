---
name: release-readiness
description: Assess release readiness for a repository, PR, local comparison, working tree, or patch using repository evidence. Use for test coverage, configuration and deployment impact, rollback questions, operational risk, and release gates.
---

# Release Readiness

Collect one shared repository or change snapshot. Produce a release decision
brief: changed behavior or system scope, executed versus recommended tests,
configuration and deployment impact, observability and rollback evidence,
blocking risks, and a clear `go`, `go with conditions`, or `no-go` recommendation.
Never claim production readiness or test success without direct execution
evidence. Cite every gate and label unknowns as verification work.
