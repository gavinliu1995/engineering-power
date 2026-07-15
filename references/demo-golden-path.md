# Demo Golden Path

## Purpose

Demonstrate that one exact PR or local comparison can produce a trustworthy
engineering report and a concise management-readable decision summary without
recollecting the repository for each output.

## Recommended input

Choose a change with:

- at least one behavior change;
- a dependency or consumer edge;
- an API route, schema, DTO, or serialization effect;
- at least one relevant test;
- enough repository context to discuss release impact.

Use a local comparison when network access is unavailable:

```text
$pr-impact-analysis /path/to/repository compare BASE HEAD full golden path
```

Use a GitHub pull request when the installed GitHub App or authenticated GitHub
CLI can read the target:

```text
$pr-impact-analysis https://github.com/OWNER/REPOSITORY/pull/NUMBER full golden path
```

## Expected execution

1. Resolve and collect one exact base/head snapshot.
2. Produce the core PR impact analysis.
3. Reuse the snapshot for dependency impact, API contract delta, and release
   notes.
4. Validate citations and report limitations.
5. Present the engineering evidence report.
6. Present a decision summary containing behavior changed, affected audience,
   overall risk, required validation, and confidence.

## Expected engineering evidence

- Exact target, base, head, profile, authentication method, and cache status
- Changed behavior and concrete symbols
- Architecture and dependency propagation
- API surface delta or an explicit statement that none was evidenced
- Executed, discovered, and recommended tests
- Regression and compatibility risks
- Technical and evidence-supported user-facing release notes
- Facts, inferences, unknowns, citations, and collection limitations

## Demo integrity rules

- Do not substitute a commit message or PR description for source evidence.
- Do not claim a test was executed unless its output was observed in this run.
- Do not hide a missing layer, deadline, truncated context, or unsupported API
  mechanism.
- Do not change the source repository.
- If a derived workflow has no supported evidence, return that limitation rather
  than manufacturing an output for visual completeness.
