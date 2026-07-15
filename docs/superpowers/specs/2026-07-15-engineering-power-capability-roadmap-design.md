# Engineering Power Capability Roadmap Design

## Goal

Evolve Engineering Power from a working repository-analysis demo into a
trusted internal engineering plugin and, finally, a self-service product used
across engineering teams.

The product must cover the ten assigned capabilities:

1. Repository refactoring assistance
2. API contract generation
3. Release note generation
4. Dependency impact analysis
5. Runtime incident triage
6. Architecture review support
7. Test impact analysis
8. Regression risk detection
9. Migration planning
10. Repository-specific onboarding

## Product principle

Engineering credibility is the primary design constraint. Management-facing
clarity is a derived presentation layer, not a replacement for technical
evidence.

Every material conclusion must be classified as one of:

- **Fact** — directly supported by collected repository or change evidence.
- **Inference** — a cross-file deduction with the reasoning stated.
- **Unknown** — information that cannot be established from the available
  source, history, configuration, logs, or executed checks.

Reports must retain exact repository state, source provenance, citations,
executed-versus-recommended test status, collection limitations, and runtime
metadata. Executive summaries may compress this information but may not weaken
or hide it.

## Delivery strategy

Development proceeds through three gated stages. A later stage starts only
after the previous stage meets its acceptance criteria.

### Stage 1: Demo MVP — prove usefulness

The demo centers on one coherent golden path:

```text
GitHub PR / repository / local Git comparison / downloaded patch
                              |
                              v
                 Shared evidence collection
                              |
                              v
             Architecture and dependency model
                              |
                              v
                   Change-impact reasoning
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
     Engineering report   API contract     Release notes
     - architecture       delta             - technical
     - dependencies       - endpoints        - user-facing
     - tests              - schemas          - risks
     - regression risk    - compatibility    - validation
```

The existing `repo-intelligence`, `pr-impact-analysis`, `architecture-map`,
`release-readiness`, `migration-planner`, and `codebase-onboarding` skills are
retained. Stage 1 adds:

- `dependency-impact-analysis`
- `api-contract-generator`
- `release-note-generator`

Stage 1 also strengthens `pr-impact-analysis` so the three new workflows can
reuse its exact base/head state and change evidence instead of recollecting the
same target.

#### Demo contract

- Accept a GitHub repository, GitHub pull request, local Git repository, local
  ref comparison, working tree, or downloaded patch with a base reference.
- Collect an exact repository or change snapshot once and reuse it by cache key.
- Produce a Quick result with a two-minute target and a Deep result only when
  explicitly requested.
- Stop collection at its configured deadline and return partial coverage rather
  than continuing silently.
- Cite file paths and line ranges for all important technical claims.
- Separate facts, inferences, and unknowns.
- Generate an API contract only from discoverable route, schema, controller,
  serialization, or specification evidence.
- Generate release notes with separate technical and user-facing sections;
  unsupported product claims are prohibited.
- Demonstrate the golden path against at least two repositories and three pull
  requests or equivalent local comparisons.

### Stage 2: Project validation — prove reliability

Stage 2 adds the two evidence-intensive workflows that require stronger runtime
and historical context:

- `refactoring-assistant`
- `runtime-incident-triage`

It also strengthens `migration-planner`, `dependency-impact-analysis`, and
`release-readiness` with validation gates and repository-specific policy.

#### Refactoring assistant boundaries

The assistant produces a staged proposal, dependency-aware edit order,
behavior-preservation checks, test plan, rollback points, and optionally a
reviewable patch when the user explicitly authorizes code changes. It must not
perform broad autonomous rewrites from a repository-level request.

#### Runtime incident triage boundaries

The workflow consumes a repository plus user-supplied symptoms such as logs,
stack traces, failing requests, alerts, deployment metadata, or observed time
windows. It correlates runtime evidence with code paths, configuration, recent
changes, and tests. It returns ranked hypotheses, supporting and contradicting
evidence, safe verification actions, and an escalation summary. Repository
inspection alone cannot establish a production root cause.

#### Validation program

- Pilot with at least three repositories spanning at least two technology
  stacks.
- Evaluate at least ten real changes, including five pull requests.
- Have repository maintainers score correctness, actionability, completeness,
  and time saved on a five-point scale.
- Record citation validity, material impact omissions, false-positive risks,
  cache hit rate, Quick runtime, Deep runtime, and report-validation failures.
- Require zero fabricated citations and zero claims that unexecuted tests passed.
- Require at least 80% of evaluated reports to receive a maintainer score of
  four or five for correctness and actionability before productization.

### Stage 3: Plugin product — prove scalability

Stage 3 turns independently useful skills into a discoverable, configurable,
and maintainable team product.

The plugin exposes a consistent command surface:

```text
/engineering-power help
/engineering-power repo <target>
/engineering-power pr <target>
/engineering-power architecture <target>
/engineering-power dependency-impact <target>
/engineering-power api-contract <target>
/engineering-power release-notes <target>
/engineering-power refactor <target>
/engineering-power incident <repository> <evidence>
/engineering-power migration <repository> <target-state>
/engineering-power onboarding <target>
```

Productization includes:

- Intent routing with explicit confirmation for ambiguous or mutating requests.
- Repository configuration through `.engineering-power.yml` for build commands,
  test commands, protected paths, architecture rules, ownership hints, report
  templates, and secret-exclusion patterns.
- Stable report schemas and backward-compatible plugin versioning.
- Installation, upgrade, rollback, doctor, help, and cache-management workflows.
- Local Git and downloaded Bitbucket patch support without requiring Codex to
  access the corporate VPN.
- Optional GitHub/CI delivery only after the local-first workflows are stable.
- Anonymized product metrics only when organizational policy and user consent
  permit collection.

## Architecture

The plugin keeps one flat user-facing `skills/` layer and one deterministic
shared engine:

```text
skills/
  lifecycle workflows
  repository intelligence workflows
  generated-artifact workflows
  operational workflows

scripts/repo_evidence/
  target resolution
  GitHub/local/diff collection
  exact-state cache
  layered evidence sampling
  citation context preparation
  report validation and finalization

references/
  evidence rules
  report schemas
  architecture and API conventions
  evaluation rubrics
  incident and release standards
```

All workflows consume a versioned `EvidenceSnapshot` contract. Derived
workflows may enrich a snapshot with an architecture graph, dependency graph,
API surface, or change model, but they may not independently recrawl the same
target. This keeps evidence consistent and runtime bounded.

## Shared contracts

### EvidenceSnapshot

The shared snapshot records:

- input type and normalized target
- authentication method
- resolved repository, commit, base, and head
- dirty working-tree state when applicable
- cache identity and cache-hit status
- collected files and layer coverage
- structured source excerpts with line ranges
- exclusions, errors, deadline status, and coverage limitations

### Derived models

- `ArchitectureModel` — modules, entry points, runtime boundaries, data stores,
  integrations, ownership hints, and cited edges.
- `ChangeModel` — changed symbols, callers, consumers, configuration, data paths,
  tests, deployment assets, and cited propagation edges.
- `ApiSurface` — endpoints, operations, inputs, outputs, schemas,
  authentication hints, versions, and evidence confidence.
- `RiskModel` — risk item, likelihood, impact, affected surface, supporting and
  contradicting evidence, tests, mitigation, and residual unknowns.

Schemas are versioned and validated before a skill formats its final response.

## Reporting layers

Every complete report has two layers:

1. **Engineering evidence report** — precise repository state, diagrams,
   affected symbols and paths, citations, test status, risks, and unknowns.
2. **Decision summary** — a short management-readable statement of behavior
   changed, delivery risk, readiness, required action, and confidence.

The decision summary must be generated from the validated engineering report,
not directly from raw repository context.

## Quality and performance gates

- Quick mode target: two minutes end to end.
- Deep mode target: five minutes end to end.
- Identical input state: reuse collected evidence.
- Deadline reached: finalize a partial report and disclose coverage.
- Citation validity: 100% for machine-validated citations.
- Test claims: explicitly distinguish executed, discovered, and recommended.
- Mutations: require explicit authorization and occur only in a user-approved
  working copy or branch.
- Source safety: never include detected secrets in generated context or reports.

## Testing strategy

- Unit tests for target parsing, cache identity, layer sampling, graph
  construction, contract extraction, validation, and deadline behavior.
- Fixture repositories for supported technology patterns and difficult cases.
- Golden-report tests for stable schema and citation behavior; prose wording is
  not snapshot-tested.
- Mutation tests ensuring source repositories remain unchanged during analysis.
- End-to-end tests for GitHub, local repository, working-tree, ref comparison,
  and patch inputs.
- Human evaluation records for Stage 2 correctness and actionability gates.

## Non-goals for the Demo MVP

- Automatic production incident root-cause claims.
- Autonomous repository-wide refactoring.
- Writing PR comments, merging changes, or deploying releases.
- Direct Bitbucket/VPN integration.
- Organization-wide telemetry or a hosted backend.
- Guaranteed API compatibility when the repository exposes no contract evidence.

## Stage exit criteria

### Demo MVP exits when

- The golden PR workflow works on the agreed demo fixtures.
- New API contract, release note, and dependency-impact skills validate.
- Reports meet evidence, runtime-disclosure, and source-safety rules.
- Both engineering and management presentation layers are demonstrated.

### Project validation exits when

- Pilot volume and technology-stack requirements are met.
- Evaluation metrics meet the correctness and actionability threshold.
- Known failure modes, unsupported stacks, and escalation paths are documented.
- Refactoring and incident workflows stay within their safety boundaries.

### Plugin product exits when

- A new engineer can install, diagnose, invoke, and update the plugin without
  author assistance.
- Configuration and report schemas are documented and versioned.
- Release packaging, compatibility checks, examples, and support ownership are
  established.
- Adoption is measured through an approved feedback mechanism.

