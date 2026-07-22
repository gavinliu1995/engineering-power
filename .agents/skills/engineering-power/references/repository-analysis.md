# Repository analysis mode

Read this reference for repository URLs. Keep the shared report headings from
`report-schema.md`; use this file to decide what evidence to inspect and how to
connect it.

## Establish the system shape

Identify and cite:

1. Product purpose, principal users, and current maturity
2. Runtime, build, and deployment entry points
3. UI, route, handler, event, job, or CLI entry points
4. Orchestration modules and domain boundaries
5. State ownership, persistence, caches, queues, and external services
6. Configuration, feature flags, authentication, and trust boundaries
7. Existing build, lint, test, smoke, and operational paths

Prefer runtime entry points and call chains over filename-based guesses. Use
`tree.txt` to find missing areas, then read the smallest evidence set that proves
the architecture.

## Trace behavior

Select one to three journeys that explain the repository's primary value. For
each journey, trace:

- Trigger and preconditions
- Entry point and validation
- Decision rules and orchestration
- State transition or external effect
- User/system success feedback
- Failure, fallback, retry, and recovery behavior

Distinguish deterministic rules from model-generated, configuration-driven, or
external behavior when the repository mixes them.

## Review engineering quality

Evaluate only evidence-backed concerns. Prioritize shared boundaries, data
ownership, security, correctness, test gaps, operational failure modes, and
maintainability. Include onboarding guidance that maps common changes to the
responsible modules.
