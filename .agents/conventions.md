# Engineering Power Conventions

## Skill organization

Canonical skills are flat directories under `skills/`, one directory per skill.
They span repository/change analysis, release notes and migration planning,
development practices (brainstorming, TDD, debugging, review), and routers /
meta-skills / execution coordination.

## Skill structure

Every canonical skill directory contains at minimum:

```
skills/<skill-name>/
├── SKILL.md              # Skill definition (required)
├── agents/openai.yaml    # Codex UI metadata (required for promoted skills)
└── ...                   # Optional auxiliary resources
```

The `skills/` directory is both the single canonical source and the Codex Plugin
validation entrypoint (`skills/<skill-name>/SKILL.md`). There is no separate
source tree; edit skills in place.

## Invocation model

- **User-invoked**: reachable only when the human types the skill name.
  Set `disable-model-invocation: true` in SKILL.md frontmatter and
  `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.
- **Model-invoked**: reachable by model or user (default).
  The `description` uses rich trigger phrasing for auto-invocation.

A user-invoked skill may invoke model-invoked skills but never another
user-invoked skill.

## Evidence engine

Skills that produce evidence-backed reports use the shared engine at
`scripts/repo_evidence/`. They resolve the engine path as:

1. `../engineering-power/scripts/repo_evidence/` (installed package)
2. `<repo-root>/scripts/repo_evidence/` (development via symlink)

## Installation targets

| Host | Discovery path |
|------|----------------|
| Copilot / Codex | `.agents/skills/<skill-name>/SKILL.md` |
| Claude Code | `.claude/skills/<skill-name>/SKILL.md` |
| Cursor | `.cursor/skills/<skill-name>/SKILL.md` plus optional `.cursor/rules/*.mdc` governance |

For local development, `scripts/link-skills.sh` creates symlinks into
`~/.agents/skills`, `~/.claude/skills`, and `~/.cursor/skills`.
For distribution, `scripts/install_agent_skill.py` generates portable packages.
