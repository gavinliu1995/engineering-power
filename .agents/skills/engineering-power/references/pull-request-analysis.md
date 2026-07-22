# Pull-request analysis mode

Read this reference for URLs ending in `/pull/NUMBER` and for local Git-range,
working-tree, or patch-file simulations. Use the PR headings from
`report-schema.md`.

## Establish the change

Read `manifest.json`, `pull-request-files.json`, `pull-request.patch`, base/head
commits, changed files, and supporting source. Determine:

1. User-visible and technical behavior changes
2. Changed public interfaces, schemas, state, configuration, and invariants
3. Direct callers and indirect dependents
4. External effects, rollout constraints, and reversibility
5. Existing relevant tests and untested branches

Do not equate changed files with blast radius. Trace changed symbols to their
consumers and persistence or external boundaries.

For local patch mode, treat `pull-request.patch` as authoritative for proposed
lines and `files/` as context-only. For working-tree mode, note that staged,
unstaged, and untracked content can change after collection.

## Draw the smallest useful change diagram

Choose one:

- Change propagation for symbol-to-consumer impact
- Before/after flow for changed rules or state transitions
- Sequence diagram for changed request/event order
- Scope diagram for documentation-only or non-runtime changes

## Assess regression risk

Give an overall risk and individual findings. Separate:

- Confirmed implementation risk
- Cross-file inference
- Compatibility question or hypothesis

For tests, list existing coverage, commands supported by repository evidence,
and new scenarios. Never report a passing result unless the command ran.
