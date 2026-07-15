# Engineering Power Design

## Goal

Create an installable Codex plugin that evolves the Superpowers development
lifecycle with evidence-backed repository intelligence from RepoLens.

## Product boundary

`engineering-power` is one plugin containing multiple user-invoked skills.
All user-facing workflows live directly under `skills/`; only deterministic,
shared implementation lives under `scripts/` and `references/`.

## V1 workflows

1. `repo-intelligence` — explain a repository, its runtime shape, business
   flows, risks, and onboarding path.
2. `pr-impact-analysis` — assess GitHub PRs, local commit ranges, working-tree
   changes, or downloaded patches.
3. `architecture-map` — produce evidence-backed architecture and ownership maps.
4. `codebase-onboarding` — provide an evidence-backed learning and local-run path.
5. `engineering-workflow` — route an engineering task through repository
   discovery, planning, implementation, test, review, and verification guidance.

The first four reuse the RepoLens evidence engine. `engineering-workflow` is an
adapted lifecycle workflow, not a second source collector.

## Shared engine

The plugin owns one private Python evidence engine for GitHub, local Git,
working-tree, and offline patch collection; cache management; citation-context
generation; report validation; and finalization. Skills invoke the engine with
their own profile and report instructions. Source targets remain read-only.

## Compatibility and scope

- Do not copy the installed Superpowers package verbatim. Recreate only the
  selected workflow behavior in Engineering Power's own instructions.
- Start with no MCP server, webhook, GitHub App automation, or hooks.
- Keep RepoLens compatible as a standalone project while the plugin is proven.
- V1 does not promise a hard interruption of model reasoning; runtime metadata
  must disclose deadline breaches.

## Plugin layout

```text
engineering-power/
├── .codex-plugin/plugin.json
├── skills/
│   ├── engineering-workflow/
│   ├── repo-intelligence/
│   ├── pr-impact-analysis/
│   ├── architecture-map/
│   └── codebase-onboarding/
├── scripts/repo_evidence/
├── references/
├── tests/
└── .agents/plugins/marketplace.json
```

## Acceptance criteria

- Plugin and personal marketplace validate successfully.
- Each V1 skill has a distinct trigger and a bounded output contract.
- Repo intelligence and PR analysis use one shared evidence API and pass unit
  tests against a local Git fixture.
- Installation/reinstall instructions work through a local personal marketplace.
