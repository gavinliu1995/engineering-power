# Dependency Impact Report Contract

## Required metadata

- Target and analysis mode
- Resolved commit, or exact base and head
- Profile and authentication method
- Cache status and coverage limitations

## Required sections

### Decision summary

State the affected capability, overall risk, highest-impact consumer, required
validation, and confidence in no more than five bullets.

### Changed or requested surface

List concrete modules, symbols, configuration, schemas, data stores, build
assets, or deployment assets in scope.

### Dependency propagation

Use a table with these fields:

| Source | Direction | Target | Effect | Classification | Evidence |
|---|---|---|---|---|---|

`Direction` is `depends-on` or `consumed-by`. `Classification` is `Fact`,
`Inference`, or `Unknown`.

### Transitive impact

Explain behavior, data, API, configuration, build, deployment, and operational
effects that cross more than one dependency edge. Do not repeat direct edges.

### Test impact

Separate executed tests, discovered relevant tests, and recommended validation.
Never imply that a discovered command or test was executed.

### Regression risks

For each risk record likelihood, impact, affected consumer, evidence,
mitigation, and residual unknowns.

### Evidence index

List cited repository-relative paths and line ranges. Include collection and
coverage limitations immediately before the evidence index.
