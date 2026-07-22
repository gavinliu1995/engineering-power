# Architecture focus

Load this reference when the user requests architecture, boundaries, design
review, dependencies, scalability, or maintainability.

Deepen the base report with:

1. Runtime containers and deployable units
2. Module boundaries and dependency direction
3. Public interfaces and data contracts
4. State ownership and consistency boundaries
5. Authentication, authorization, secrets, and trust boundaries
6. External services, queues, storage, retries, and failure containment
7. Cross-cutting concerns such as telemetry, configuration, and safety

Use one primary architecture diagram. Add a second diagram only when a trust,
deployment, or data-flow boundary is materially clearer separately.

Flag duplicated ownership, circular dependencies, hidden coupling, oversized
orchestration modules, and parallel legacy/new models only when direct evidence
supports them. Recommend an incremental target state, not a generic rewrite.
