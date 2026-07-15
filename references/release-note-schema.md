# Release Note Report Contract

## Required metadata

- Release range or exact base and head
- `Profile: Quick` or `Profile: Deep`
- `Collection:`, `Coverage:`, `Missing layers:`, and `Tests executed:`
- `Report validation: {{REPOLENS_VALIDATION_STATUS}}`
- `Total elapsed: {{REPOLENS_TOTAL_ELAPSED}}`

## Required sections

## Decision Summary

State what changed, who is affected, release risk, required action, and
confidence in no more than five bullets.

## User-facing Release Notes

Describe observable additions, changes, fixes, deprecations, or removals.
Include only evidence-supported claims. State `No supported user-facing change
identified` when appropriate.

## Technical Release Notes

Describe implementation, API, dependency, configuration, schema, migration,
deployment, observability, and operational effects relevant to engineers.

## Required Actions

List consumer, operator, data, configuration, deployment, or rollback actions.
Use `None discovered` when evidence supports no action and `Unknown` when
coverage is insufficient.

## Validation Status

Use three separate lists:

- Executed checks and their observed results
- Discovered relevant tests or commands that were not executed
- Recommended validation before release

## Risks and Compatibility

For each item include likelihood, impact, affected audience, mitigation,
evidence, and residual unknowns.

## Evidence Index

List all repository-relative citations and collection limitations.
