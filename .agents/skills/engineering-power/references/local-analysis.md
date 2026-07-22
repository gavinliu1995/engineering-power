# Local repository and offline PR analysis

Read this reference when the target is a local Git repository. Local collection
does not require a GitHub App, a token, a Bitbucket API, or network access. It
must remain read-only: never checkout, reset, clean, stash, apply a patch, or
otherwise mutate the target repository.

## Choose the local evidence mode

- Repository snapshot: analyze `HEAD` or an explicit `--ref`.
- Git range: simulate a PR by comparing `--base BASE --head HEAD`. The collector
  uses the merge base and reads source files from the resolved head commit.
- Working tree: compare tracked, staged, unstaged, and untracked changes with
  `--working-tree`. The evidence is mutable, so disclose that rerunning may
  produce a different snapshot.
- Patch file: analyze a downloaded `.diff` or `.patch` with `--patch FILE` and a
  local context ref. The collector never applies the patch; `files/` represents
  the context commit and `pull-request.patch` represents the proposed changes.

Use the repository report schema for a repository snapshot. Use the pull-request
schema for Git range, working-tree, and patch-file simulations.

## Offline Bitbucket workflow

Do not call Bitbucket APIs. The user can obtain evidence while connected to the
company network, then run RepoLens after returning to an environment where Codex
is available:

1. Clone or update the repository locally.
2. Preserve both base and feature refs when possible, then use Git-range mode.
3. If only a PR download is available, save its `.diff` or `.patch` and use
   patch-file mode against the matching base/context ref.
4. If the proposed change exists only as local edits, use working-tree mode.

Report the local repository path, simulation kind, base/head refs and resolved
commit SHAs from `manifest.json`. For patch mode, explicitly state that no head
commit was available and that the patch was not applied.

## Evidence interpretation

- `manifest.json` records `authentication.method` as `local-filesystem` and the
  simulation metadata under `simulation`.
- `pull-request-files.json` records changed paths and Git status values.
- `pull-request.patch` is the authoritative change evidence.
- In Git-range mode, `files/` represents the head commit.
- In working-tree mode, `files/` represents the current working tree, including
  eligible untracked text files.
- In patch-file mode, `files/` represents the selected context commit. Do not
  cite it as proof that a patched implementation exists; cite the patch and
  frame post-change behavior as an inference where necessary.

The evidence bundle intentionally matches GitHub collection so report writing,
diagrams, risk analysis, and validation use the same downstream workflow.

## Runtime profiles and reuse

Local analysis defaults to the Quick profile. It samples root documentation and
build files, runtime entry points, routes/UI, services, persistence/DAO, tests,
and operations independently so a large test or generated-like source subtree
cannot hide an important layer. Use Deep only when the user explicitly requests
it.

Repository and Git-range snapshots reuse an existing cache entry for the same
resolved commits and profile. Working-tree and patch snapshots also include a
content hash in their cache identity, so editing the worktree or patch creates a
new snapshot. After collection, prepare `analysis-context-PROFILE.md` once and
reason from its line-numbered excerpts. Do not repeatedly scan the entire local
repository or recollect Quick with a larger limit.
