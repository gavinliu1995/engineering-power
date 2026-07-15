---
name: dependency-impact-analysis
description: Trace dependency and change propagation for a GitHub repository, pull request, local Git comparison, working tree, or downloaded patch. Use when engineers need direct and transitive consumers, build or runtime dependency effects, test impact, or evidence-backed regression risk.
---

# Dependency Impact Analysis

Analyze dependency direction and change propagation from one bounded evidence
snapshot. Keep the source repository read-only.

## Workflow

1. Resolve the plugin root from this skill directory.
2. Reuse an exact-state snapshot when the target, base, head, mode, and profile
   match. Otherwise collect once with the shared engine under
   `$PLUGIN_ROOT/scripts/repo_evidence/`.
3. Run `prepare_analysis_context.py` once for general citation context, then run
   `prepare_workflow_context.py SNAPSHOT --workflow dependency-impact --profile
   quick`. Use `deep` only when explicitly requested.
4. Identify the changed component or requested dependency root. Trace:
   - direct dependencies it calls, imports, configures, reads, or writes;
   - reverse consumers that call, import, configure, deploy, or test it;
   - transitive behavior, data, configuration, build, and deployment effects.
5. Prioritize concrete symbols and dependency edges over directory-name
   speculation. Record direction for every edge.
6. Classify each material statement as **Fact**, **Inference**, or **Unknown**.
   Explain inference reasoning and turn unknowns into verification actions.
7. Use the output contract in
   `../../references/dependency-impact-schema.md`. Cite important claims with
   repository-relative `path:Lx-Ly` references.
8. Write the draft with the required runtime placeholders, then run
   `finalize_report.py DRAFT --snapshot SNAPSHOT --profile PROFILE
   --started-at-epoch START --report-type dependency-impact --output FINAL`.
   Return the finalized report only; if validation fails, correct the report
   contract rather than bypassing the validator.

## Guardrails

- Do not treat a manifest declaration as proof that a dependency is exercised
  at runtime.
- Do not describe every imported library; focus on the requested or changed
  surface and material propagation paths.
- Distinguish discovered tests, executed tests, and recommended tests.
- Disclose missing layers, truncated evidence, deadline status, and unsupported
  dependency mechanisms.
- Do not expose credentials or secret values found in source or configuration.
