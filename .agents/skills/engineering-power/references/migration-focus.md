# Migration focus

Load this reference when the user requests `migration TARGET`, framework or
runtime upgrades, datastore moves, API transitions, or platform modernization.
Keep the repository base report and add the migration headings required by
`report-schema.md`.

## Inventory

Use deterministic search to identify:

- Direct dependencies and versions
- Runtime/build configuration
- Public and internal APIs affected
- Generated code, schemas, migrations, and data formats
- Deployment, CI, tests, scripts, and documentation
- External consumers and compatibility constraints

Classify each item as required change, recommended cleanup, or unknown.

## Waves

Order work by dependency direction and reversibility. Prefer:

1. Characterization tests and observability
2. Compatibility layer or dual-read/dual-write seam
3. Leaf-module migration
4. Shared boundary migration
5. Consumer cutover
6. Legacy removal

Adjust the waves to repository evidence; do not force this order when the
system's dependencies differ.

## Validation and rollback

For every wave specify validation, success criteria, rollback trigger, rollback
action, and irreversible operations. Separate commands available in the repo
from recommended new checks. Surface unresolved compatibility questions rather
than inventing target-platform behavior.
