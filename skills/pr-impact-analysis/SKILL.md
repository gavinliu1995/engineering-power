---
name: pr-impact-analysis
description: Analyze GitHub pull requests, local commit ranges, working-tree changes, or downloaded patches. Return evidence-backed change propagation, test impact, regression risk, and architecture review.
---

# PR Impact Analysis

Analyze a change once, then reuse its exact evidence state for requested derived
engineering outputs. Never apply a patch or modify the target repository.

## Workflow

1. Accept a GitHub PR URL, local `compare BASE HEAD`, `working-tree`, or a
   downloaded patch with its base ref.
2. Collect exactly one shared evidence snapshot in pull-request mode. Record the
   exact base, head, authentication method, profile, cache status, and collection
   limitations.
3. Run `prepare_analysis_context.py` once. Report the user-visible behavior,
   changed symbols, affected callers and data paths, architecture effects,
   executed versus recommended tests, regression risks, unknowns, and evidence
   index.
4. Invoke derived workflows only when the user requests them or explicitly asks
   for the full golden-path report:
   - `dependency-impact-analysis` for direct, reverse, and transitive effects;
   - `api-contract-generator` for a discovered API delta;
   - `release-note-generator` for technical and user-facing release notes.
5. Pass the same snapshot directory and profile to every derived workflow. Each
   may run `prepare_workflow_context.py` for its focus, but none may recollect the
   repository or resolve a different base/head pair.
6. Present the evidence-backed engineering report first and a compact decision
   summary second. State when a derived workflow was not requested, unsupported,
   or incomplete.

Use `finalize_report.py` before returning the inline result. Distinguish direct
diff evidence from inferred impact and from runtime behavior not verified here.
Do not imply that a derived workflow ran merely because it is available.
