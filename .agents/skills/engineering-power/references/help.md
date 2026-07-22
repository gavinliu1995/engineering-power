# RepoLens help mode

Use this mode for `/repolens help`, `$repolens help`, `/repolens -h`, or
`/repolens --help`.

Return a concise command guide in the user's language. Do not collect a
repository, authenticate to GitHub, load the report schema, validate a report,
or create files.

Include these commands with short explanations:

```text
/repolens REPO_URL
/repolens deep REPO_URL
/repolens REPO_URL architecture
/repolens REPO_URL business logic
/repolens REPO_URL onboarding
/repolens REPO_URL migration TARGET
/repolens PR_URL
/repolens REPO_OR_PR_URL architecture business logic onboarding
/repolens /path/to/repository
/repolens deep /path/to/repository
/repolens /path/to/repository ref REF
/repolens /path/to/repository compare BASE HEAD
/repolens /path/to/repository working-tree [base BASE]
/repolens /path/to/repository patch /path/to/change.diff [base CONTEXT_REF]
/repolens doctor
/repolens doctor REPO_URL
/repolens doctor /path/to/repository
/repolens cache status
/repolens cache permissions
/repolens cache permissions --fix
/repolens cache prune
/repolens cache clean DAYS
/repolens cache clean all
/repolens help
```

Also state:

- Quick Report is the default and targets about 2 minutes with a 120-second
  hard deadline. It is capped at 10,000 Markdown characters, one representative
  business flow, and five prioritized risks.
- `deep` must be explicit and uses a larger evidence budget with a 300-second
  hard deadline.
- Exact commits and exact local working states reuse their existing evidence
  cache; the collector does not download or copy the same state again.
- Evidence is sampled by architecture layer (root docs/build, entry points,
  routes/UI, services, DAO/persistence, tests, and operations), not by one
  global Top-N list.
- When coverage or time is exhausted, RepoLens returns the available report and
  marks the limitation instead of continuing indefinitely.
- Every delivered report is finalized with citation/diagram validation and
  displays the measured total elapsed time. The validation badge is generated
  by the finalizer, not claimed by the model.
- A report that is structurally valid but finishes after its profile deadline is
  marked `passed-with-deadline-limit`, returned with the available evidence, and
  must not be presented as an unrestricted `passed` report.
- Repository URLs produce repository intelligence reports.
- URLs ending in `/pull/NUMBER` produce PR impact reports.
- A local path produces the same report workflow without network authentication.
- `compare`, `working-tree`, and `patch` produce local PR simulation reports.
- Downloaded Bitbucket repositories and patch files are supported offline; no
  Bitbucket API call is made.
- Multiple focus terms may be combined.
- Reports render inline by default; save only on explicit request.
- Public repositories need no installation. Private repositories must be
  selected in the GitHub App installation.
- `doctor` checks the runtime, authentication, private cache permissions, and
  optional repository access without exposing credentials.
- Evidence-cache directories use mode `700` and files use mode `600`.
  `cache permissions` audits existing snapshots; add `--fix` to repair only
  permissions without deleting or changing evidence content.
- Cache cleanup always shows a dry run and requires confirmation before deleting
  evidence snapshots.
- `cache prune` applies the configured age and per-target snapshot limits, also
  with dry-run and explicit confirmation.
- RepoLens is read-only and does not modify, checkout, apply patches to, or
  comment on target repositories.

End with two copy-ready examples: one placeholder GitHub URL and one local
base/head comparison. Do not ask for a target while in help mode.
