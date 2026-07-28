# Engineering Power — Agent Instructions

Canonical skills live as flat directories under `skills/`, one directory per
skill:

- Repository and change analysis (repo-intelligence, PR impact, etc.)
- Release notes and migration planning
- Development practices (brainstorming, TDD, debugging, review)
- Routers, meta-skills, and execution coordination

Every promoted skill has a `SKILL.md` and an `agents/openai.yaml` for Codex
metadata.

The top-level `skills/` directory is both the single canonical source and the
Codex Plugin validation entrypoint. Edit skills directly under `skills/`.

The shared evidence engine lives at `scripts/repo_evidence/`. Reference schemas
live at `references/`. Skills resolve these paths relative to the repository
root (development) or relative to the installed `engineering-power` core skill
(distribution).

To link all skills into local agent harnesses for development:

```bash
scripts/link-skills.sh
```

To install into a target project:

```bash
python3 scripts/install_agent_skill.py --host copilot --target-root /path/to/project
python3 scripts/install_agent_skill.py --host claude --target-root /path/to/project
python3 scripts/install_agent_skill.py --host cursor --target-root /path/to/project
```
