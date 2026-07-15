# Dependency Impact Report Contract

## Required metadata

- Target and analysis mode
- Resolved commit, or exact base and head
- `Profile: Quick` or `Profile: Deep`
- `Collection:`, `Coverage:`, `Missing layers:`, and `Tests executed:`
- `Report validation: {{REPOLENS_VALIDATION_STATUS}}`
- `Total elapsed: {{REPOLENS_TOTAL_ELAPSED}}`

## Required sections

## Decision Summary

State the affected capability, overall risk, highest-impact consumer, required
validation, and confidence in no more than five bullets.

## Changed or Requested Surface

List concrete modules, symbols, configuration, schemas, data stores, build
assets, or deployment assets in scope.

## Dependency Propagation

Use a table with these fields:

| Source | Direction | Target | Effect | Classification | Evidence |
|---|---|---|---|---|---|

`Direction` is `depends-on` or `consumed-by`. `Classification` is `Fact`,
`Inference`, or `Unknown`.

## Transitive Impact

Explain behavior, data, API, configuration, build, deployment, and operational
effects that cross more than one dependency edge. Do not repeat direct edges.

## Test Impact

Separate executed tests, discovered relevant tests, and recommended validation.
Never imply that a discovered command or test was executed.

## Regression Risks

For each risk record likelihood, impact, affected consumer, evidence,
mitigation, and residual unknowns.

## Evidence Index

List cited repository-relative paths and line ranges. Include collection and
coverage limitations immediately before the evidence index.
