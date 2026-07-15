---
name: repo-intelligence
description: Analyze a GitHub repository URL or local Git repository with evidence-backed architecture, business-flow, risk, build, and onboarding guidance. Use for repository understanding, technical discovery, and codebase intelligence.
---

# Repository Intelligence

Collect exactly one bounded evidence snapshot with the shared engine. For a local
repository run `collect_local_context.py PATH --profile quick`; for GitHub run
`collect_github_context.py URL --profile quick`. Prepare one citation context,
then return an inline report with the repository commit, authentication method,
architecture diagram, representative business flow, risks, onboarding, and
evidence index. Keep the target repository read-only.

Resolve the plugin root from this skill directory, then call scripts under
`$PLUGIN_ROOT/scripts/repo_evidence/`. Use `deep` only when the user explicitly
requests it. Validate the temporary report with `finalize_report.py` before
delivery; disclose any deadline or collection limitation.
