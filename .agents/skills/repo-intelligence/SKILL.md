---
name: repo-intelligence
description: Analyze a GitHub repository URL or local Git repository with evidence-backed architecture, business-flow, risk, build, and onboarding guidance. Use for repository understanding, technical discovery, and codebase intelligence.
---
## Portable runtime

This generated Agent Skill shares the adjacent `engineering-power` runtime core.
Resolve `$ENGINEERING_POWER_CORE` to `../engineering-power` relative to this
Skill directory. Run repository evidence tools from
`$ENGINEERING_POWER_CORE/scripts/repo_evidence/` and load shared report schemas
from `$ENGINEERING_POWER_CORE/references/`. Do not bypass the evidence engine
for repository, pull-request, comparison, working-tree, or patch analysis.


# Repository Intelligence

Collect exactly one bounded evidence snapshot with the shared engine. For a local
repository run `collect_local_context.py PATH --profile quick`; for GitHub run
`collect_github_context.py URL --profile quick`. Prepare one citation context,
then return an inline report with the repository commit, authentication method,
architecture diagram, representative business flow, risks, onboarding, and
evidence index. Keep the target repository read-only.

Resolve the plugin root from this skill directory, then call scripts under
`$ENGINEERING_POWER_CORE/scripts/repo_evidence/`. Use `deep` only when the user explicitly
requests it. Validate the temporary report with `finalize_report.py` before
delivery; disclose any deadline or collection limitation.
