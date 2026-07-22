# API Contract Report Contract

## Required metadata

- Target and input mode
- Resolved commit, or exact base and head
- `Profile: Quick` or `Profile: Deep`
- `Collection:`, `Coverage:`, `Missing layers:`, and `Tests executed:`
- `Report validation: {{REPOLENS_VALIDATION_STATUS}}`
- `Total elapsed: {{REPOLENS_TOTAL_ELAPSED}}`

## Required sections

## Decision Summary

State the API scope, compatibility decision, highest-risk operation, required
consumer action, and confidence.

## Contract Sources

List specifications, routes, controllers, schemas, DTOs, serializers,
authentication middleware, and tests used as evidence. Classify each as
`Fact`, `Inference`, or `Unknown`.

## Operations

Use one row per operation or message:

| Change | Method or kind | Path or name | Input | Output | Authentication | Compatibility | Evidence |
|---|---|---|---|---|---|---|---|

Use `Unknown` instead of an empty value when evidence is absent.

## Schemas and Validation

Describe cited field names, types, requiredness, validation, enums, defaults,
and serialization names. Do not infer unobserved fields from business prose.

## Compatibility Findings

Explain every `potentially breaking` or `breaking` classification, affected
consumers, mitigation, and unresolved compatibility questions.

## Verification

Separate executed checks, discovered API tests, and recommended contract or
consumer tests.

## Evidence Index

List repository-relative citations and all collection or contract limitations.
