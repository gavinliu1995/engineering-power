---
name: migration-planner
description: Build an evidence-backed migration plan for a GitHub repository or local Git repository toward a user-specified target such as Java 21, a framework upgrade, cloud platform, or dependency replacement.
---
## Portable runtime

This generated Agent Skill shares the adjacent `engineering-power` runtime core.
Resolve `$ENGINEERING_POWER_CORE` to `../engineering-power` relative to this
Skill directory. Run repository evidence tools from
`$ENGINEERING_POWER_CORE/scripts/repo_evidence/` and load shared report schemas
from `$ENGINEERING_POWER_CORE/references/`. Do not bypass the evidence engine
for repository, pull-request, comparison, working-tree, or patch analysis.


# Migration Planner

Require an explicit migration target. Collect one shared repository snapshot,
then inventory target-sensitive modules, APIs, build plugins, configuration, and
tests. Return dependency-ordered migration waves, validation gates, rollback
points, and unresolved compatibility questions. Separate required changes,
recommended cleanup, and hypotheses. Use citations for every inventory claim.
