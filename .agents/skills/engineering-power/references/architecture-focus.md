# Architecture focus

Load this reference when the user requests architecture, boundaries, design
review, dependencies, scalability, or maintainability.

Architecture Map is a first-class report type, not a generic Repository
Intelligence report with extra prose. Load `report-schema.md` with this file and
finalize with `--report-type architecture`.

Analyze:

1. Runtime containers and deployable units
2. Module boundaries and dependency direction
3. Public interfaces and data contracts
4. State ownership and consistency boundaries
5. Authentication, authorization, secrets, and trust boundaries
6. External services, queues, storage, retries, and failure containment
7. Cross-cutting concerns such as telemetry, configuration, and safety

Always trace at least one concrete feature through a repository-specific chain:

```text
Page/Route → Provider/Service → Client/DAO
```

Use the real class, module, or function names at each stage. If one stage does
not exist, say so as an Unknown rather than substituting a generic box.

Use exactly two Mermaid diagrams in Quick:

1. A system/module architecture diagram.
2. A concrete feature-flow or sequence diagram.

Deep uses the same report structure and may widen evidence coverage, but should
not add diagrams unless they materially change an engineering decision.

Flag duplicated ownership, circular dependencies, hidden coupling, oversized
orchestration modules, and parallel legacy/new models only when direct evidence
supports them. Recommend an incremental target state, not a generic rewrite.

## Quick time budget

Use the `report_deadline_epoch` supplied by the collector metadata.

- With more than 30 seconds remaining, permit at most one targeted search needed
  to complete the concrete feature chain.
- With 30 seconds or less remaining, stop expanding evidence and compose the
  report from the bounded context already collected.
- If the deadline has already passed, produce the smallest valid Architecture
  report and let the finalizer mark `passed-with-deadline-limit`.

Quick Architecture reports must stay within 7,000 Markdown characters, include
no more than five prioritized risks, and expose coverage limitations rather
than attempting an unbounded search.
