---
name: release-note-generator
description: Generate evidence-backed technical and user-facing release notes for a GitHub pull request, local Git comparison, working tree, downloaded patch, or repository release range. Use for changelogs, deployment briefs, upgrade notes, validation summaries, and release communication.
---

# Release Note Generator

Generate release communication from one exact code-change snapshot. Keep the
source repository read-only and make unsupported product claims explicit.

## Workflow

1. Resolve the plugin root from this skill directory.
2. Collect or reuse one exact base/head snapshot with the shared engine under
   `$PLUGIN_ROOT/scripts/repo_evidence/`.
3. Run `prepare_analysis_context.py`, then run
   `prepare_workflow_context.py SNAPSHOT --workflow release-notes --profile
   quick`. Use `deep` only when explicitly requested.
4. Determine the supported behavior change from changed routes, services,
   schemas, configuration, migrations, tests, build files, and deployment
   assets. Use commit or PR prose only as a lead that code evidence must confirm.
5. Produce two layers:
   - **technical** notes for engineers and operators;
   - **user-facing** notes only for observable effects supported by evidence.
6. Separate **executed** checks, discovered tests, and **recommended**
   validation. Never convert discovered commands into execution claims.
7. Include upgrade, configuration, data, deployment, rollback, compatibility,
   and risk information when supported. Mark missing evidence as **Unknown**.
8. Format the result with `../../references/release-note-schema.md` and cite
   important claims with repository-relative `path:Lx-Ly` references.

## Guardrails

- Do not repeat commit messages as facts without repository evidence.
- Do not invent customer value, performance improvements, fixed symptoms,
  compatibility, or release readiness.
- Omit internal implementation detail from the user-facing layer unless it
  changes how users integrate, configure, operate, or troubleshoot the product.
- Disclose collection deadlines, missing layers, and context truncation.
- Do not expose credentials, secret values, internal URLs, or personal data.
