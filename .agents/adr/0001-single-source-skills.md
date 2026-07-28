# ADR-0001: Single source of truth for skills

## Status

Accepted

## Context

The repository previously committed generated portable skill packages under
`.agents/skills/` (72 files) that duplicated the canonical skill source.
This caused maintenance burden: every change required running a sync script and
committing identical content twice.

## Decision

- `skills/` is the single canonical source: one flat directory per skill,
  containing real files (no category buckets, no symlinks).
- Codex Plugin validation consumes `skills/<skill-name>/SKILL.md` directly.
- `.agents/` contains only governance documents (conventions, ADRs).
- Local development uses `scripts/link-skills.sh` to symlink skills into host
  discovery directories (`~/.agents/skills/`, `~/.claude/skills/`).
- Distribution to other projects uses `scripts/install_agent_skill.py` which
  generates portable packages on-the-fly (bundling `repo_evidence/` and
  `references/` into the `engineering-power` core skill).
- No generated skill files are committed to the repository.

## Consequences

- Zero duplication in the source tree.
- `git pull` + symlinks = instant skill updates for local development.
- The installer remains the distribution path for non-symlink hosts.
- `scripts/sync_portable_agent_skill.py` is removed.
