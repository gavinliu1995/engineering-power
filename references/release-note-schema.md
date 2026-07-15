# Release Note Report Contract

## Required metadata

- Release range or exact base and head
- Input mode, profile, authentication method, and cache status
- Evidence coverage and deadline limitations

## Required sections

### Decision summary

State what changed, who is affected, release risk, required action, and
confidence in no more than five bullets.

### User-facing release notes

Describe observable additions, changes, fixes, deprecations, or removals.
Include only evidence-supported claims. State `No supported user-facing change
identified` when appropriate.

### Technical release notes

Describe implementation, API, dependency, configuration, schema, migration,
deployment, observability, and operational effects relevant to engineers.

### Required actions

List consumer, operator, data, configuration, deployment, or rollback actions.
Use `None discovered` when evidence supports no action and `Unknown` when
coverage is insufficient.

### Validation status

Use three separate lists:

- Executed checks and their observed results
- Discovered relevant tests or commands that were not executed
- Recommended validation before release

### Risks and compatibility

For each item include likelihood, impact, affected audience, mitigation,
evidence, and residual unknowns.

### Evidence index

List all repository-relative citations and collection limitations.
