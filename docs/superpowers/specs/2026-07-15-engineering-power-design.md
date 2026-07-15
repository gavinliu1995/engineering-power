# Engineering Power Design

## Goal

Create an installable Codex plugin that evolves the Superpowers development
lifecycle with evidence-backed repository intelligence from RepoLens.

## Product boundary

`engineering-power` is one plugin containing multiple user-invoked skills.
All user-facing workflows live directly under `skills/`; only deterministic,
shared implementation lives under `scripts/` and `references/`.

## V1 workflows

Engineering Power exposes one flat, user-facing workflow layer. The first seven
skills are adapted from Superpowers' engineering lifecycle; the next six add
RepoLens-style evidence-backed repository intelligence.

1. `brainstorming`
2. `writing-plans`
3. `test-driven-development`
4. `systematic-debugging`
5. `requesting-code-review`
6. `verification-before-completion`
7. `finishing-development-work`
8. `repo-intelligence` — explain a repository, its runtime shape, business
   flows, risks, and onboarding path.
9. `pr-impact-analysis` — assess GitHub PRs, local commit ranges, working-tree
   changes, or downloaded patches.
10. `architecture-map` — produce evidence-backed architecture and ownership maps.
11. `codebase-onboarding` — provide an evidence-backed learning and local-run path.
12. `release-readiness` — produce a cited go/no-go decision with conditions.
13. `migration-planner` — build a staged, reversible migration plan from real
    codebase evidence.

Support skills (`using-engineering-power`, `using-git-worktrees`,
`executing-plans`, and `subagent-driven-development`) exist only to coordinate
the direct workflows. The repository-intelligence workflows reuse one shared
RepoLens evidence engine; none owns a second collector.

## Shared engine

The plugin owns one private Python evidence engine for GitHub, local Git,
working-tree, and offline patch collection; cache management; citation-context
generation; report validation; and finalization. Skills invoke the engine with
their own profile and report instructions. Source targets remain read-only.

## Compatibility and scope

- Preserve the selected Superpowers workflow behavior in Engineering Power's
  own plugin namespace, while retaining clear provenance during development.
- Start with no MCP server, webhook, GitHub App automation, or hooks.
- Keep RepoLens compatible as a standalone project while the plugin is proven.
- V1 does not promise a hard interruption of model reasoning; runtime metadata
  must disclose deadline breaches.

## Plugin layout

```text
engineering-power/
├── .codex-plugin/plugin.json
├── skills/
│   ├── brainstorming/
│   ├── writing-plans/
│   ├── test-driven-development/
│   ├── systematic-debugging/
│   ├── requesting-code-review/
│   ├── verification-before-completion/
│   ├── finishing-development-work/
│   ├── repo-intelligence/
│   ├── pr-impact-analysis/
│   ├── architecture-map/
│   ├── codebase-onboarding/
│   ├── release-readiness/
│   └── migration-planner/
├── scripts/repo_evidence/
├── references/
├── tests/
└── docs/
```

## Acceptance criteria

- Plugin validates successfully.
- Each direct V1 skill has a distinct trigger and a bounded output contract.
- Repo intelligence and PR analysis use one shared evidence API and pass unit
  tests against a local Git fixture.
- A later packaging decision may add a personal marketplace without changing
  the plugin's root layout.
