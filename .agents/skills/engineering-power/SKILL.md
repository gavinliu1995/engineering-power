---
name: engineering-power
description: Run evidence-backed repository intelligence, PR impact, architecture, API contract, release, onboarding, migration, debugging, planning, review, and verification workflows. Use for GitHub repositories, local Git repositories, commit comparisons, working trees, and downloaded patches.
---

# Engineering Power

Use this router/orchestrator Agent Skill to select an Engineering Power
workflow while keeping every material conclusion traceable to a specific Git
state and source evidence. Keep workflow detail in the linked references rather
than expanding this entry point. Default to read-only analysis. Do not checkout,
reset, apply a patch, commit, or modify the target repository unless the user
explicitly requests an implementation workflow and authorizes writes.

## Locate the evidence engine

Set `SKILL_DIR` to this Skill directory. Use the first existing directory:

1. `$SKILL_DIR/scripts/repo_evidence` for a package installed by the
   Engineering Power installer.
2. `<engineering-power-repository>/scripts/repo_evidence` when this Skill is
   being used from the Engineering Power repository.

Before any report, use the appropriate collector and preserve its exact
repository state, cache status, coverage limits, and authentication method.

## Route the request

| User intent | Workflow |
| --- | --- |
| Understand a repository, its architecture, business flow, risks, or setup | Repository Intelligence |
| Review a PR, branch comparison, working tree, or patch | PR Impact Analysis |
| Map modules, trust boundaries, integrations, or data ownership | Architecture Map |
| Trace direct, reverse, build, runtime, or test effects | Dependency Impact Analysis |
| Inventory API contracts or assess compatibility changes | API Contract Generator |
| Produce technical or user-facing release notes | Release Note Generator |
| Decide Go / Go with conditions / No-go | Release Readiness |
| Prepare a new developer to work in the repository | Codebase Onboarding |
| Plan a framework, runtime, SDK, database, or platform move | Migration Planner |
| Investigate a test failure or unexpected behavior | Systematic Debugging |
| Design a feature before implementation | Brainstorming, then Writing Plans |
| Verify a completed implementation before claiming success | Verification Before Completion |

## Evidence workflow

1. For a local repository, use `collect_local_context.py`; for a GitHub URL or
   PR, use `collect_github_context.py`. Prefer local collection for a repository
   cloned from Bitbucket or only reachable over a corporate VPN.
2. Use `quick` unless the user explicitly requests `deep`.
3. For change analysis, collect one pull-request evidence snapshot, then reuse
   it for Dependency Impact Analysis, API Contract Generator, Release Note
   Generator, and Release Readiness. Do not recollect the same target per
   derived report.
4. Use `prepare_analysis_context.py` or `prepare_workflow_context.py` to create
   citation-ready context. These builders redact secret-like values before any
   evidence enters model context; never bypass them by pasting raw sensitive
   source into the conversation.
5. Distinguish facts, inferences, and unknowns. Distinguish executed tests from
   discovered and recommended tests.
6. Validate an inline Markdown report with `finalize_report.py` before delivery.
   If coverage is limited by a deadline or missing evidence, state that clearly.

For Architecture Map, load [Architecture focus](references/architecture-focus.md) and [Report schema](references/report-schema.md), trace a concrete Page/Route → Provider/Service → Client/DAO chain, and finalize with `--report-type architecture`.

Use the collector's `report_deadline_epoch` as an active budget. With more than
30 seconds remaining, perform at most one targeted search needed to close a
material evidence gap. With 30 seconds or less remaining, stop expanding
evidence and compose the smallest valid report from the bounded context.

## Platform rules

- **GitHub Copilot CLI / IDE:** After install, use `/skills reload`, then
  `/skills info engineering-power`. Invoke it explicitly with
  `/engineering-power` when required.
- **Claude Code and Cursor:** Use the installed `engineering-power` Skill from
  the project or user skill directory; give it a local repository path, GitHub
  URL, branch comparison, working tree, or patch.
- **GitHub cloud agents:** Use for GitHub repositories and PRs only. They cannot
  access a developer's local checkout or a company VPN/Bitbucket environment.

## Resources

Load only the resources required for the selected workflow:

- [Report schema](references/report-schema.md): evidence rules, exact formal
  report headings, diagrams, risk, confidence, and runtime metadata.
- [Architecture focus](references/architecture-focus.md): Architecture Map
  boundaries, concrete feature flow, target state, and Quick time budget.
- [Local analysis](references/local-analysis.md): local repository, Git range,
  working-tree, downloaded patch, and offline Bitbucket rules.
- [Pull request analysis](references/pull-request-analysis.md): change
  propagation, test impact, diagrams, and regression-risk analysis.

## Report contract

Include the target, exact commit or base/head state, profile, cache status,
collection coverage, citations, and the validation result. Never claim that a
test passed unless this session ran it and observed a successful result.

Deliver the validated formal report inline in the conversation, including its
Mermaid diagrams. A saved artifact is supplemental only and must never replace
the inline report. If a host imposes a response-length limit, inline at least
the target and Git state, manifest-backed coverage, both required diagrams,
prioritized risks, validation status, and Unknowns; then link the supplemental
artifact.

Use the following minimum structure for a generic workflow. When a linked
workflow schema defines exact headings, that schema takes precedence; preserve
the same information in its metadata and sections.

```markdown
## Target

## Git state

## Evidence coverage

## Findings

## Risks

## Validation

## Unknowns
```
