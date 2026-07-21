# Cross-Platform Agent Skills Design

## Goal

Make Engineering Power usable through GitHub Copilot first, while retaining the
existing Codex plugin and making the same skill package installable by Claude
Code and Cursor. The repository evidence engine remains the product core.

## Product boundary

- **Local-agent mode is primary.** Copilot CLI/VS Code, Claude Code, and Cursor
  can analyse local repositories, Git ranges, working trees, and downloaded
  patches. This preserves the Bitbucket/VPN workflow.
- **GitHub cloud-agent mode is secondary.** It can use GitHub repository/PR
  inputs but is not presented as a way to access a developer's local checkout
  or company VPN.
- **All analysis stays read-only by default.** Existing implementation
  workflows retain their explicit user-authorization rules.

## Architecture

```
scripts/repo_evidence/          Shared deterministic evidence engine
references/                     Shared report schemas and focus guides
skills/                         Existing Codex plugin adapter
.agents/skills/engineering-power/
                                Portable Agent Skills package (canonical)
scripts/install_agent_skill.py  Host-specific installer and verifier
```

The portable package is a single `engineering-power` umbrella skill. It routes
the user request to the existing repository-intelligence, PR-impact, API,
release, architecture, onboarding, migration, and engineering-lifecycle
workflows. It references the shared scripts and resources in the repository;
the installer copies a self-contained package for hosts that install a skill
outside this repository.

## Host support

| Host | Installation target | Scope |
| --- | --- | --- |
| GitHub Copilot CLI / IDE | `.agents/skills/engineering-power` or `~/.agents/skills/engineering-power` | Local Git and GitHub workflows |
| Claude Code | `.claude/skills/engineering-power` | Local Git and GitHub workflows |
| Cursor | `.cursor/skills/engineering-power` | Local Git and GitHub workflows |
| Codex | Existing `.codex-plugin` plus `skills/` | Existing behavior remains unchanged |

The installer will copy the bundled portable package to the selected host path;
it will not modify a target repository unless the user names that repository as
the installation target.

## Package contract

The portable `SKILL.md` must have standard `name` and `description`
frontmatter, be explicit about read-only defaults, and describe how to invoke
the evidence collector using the current repository root. It must not require
Codex-only UI metadata, a Codex marketplace, or a GitHub App when analysing a
local repository.

## Validation

1. A new deterministic test validates the standard skill location, frontmatter,
   required workflow routing, bundled scripts/references, and absence of secrets.
2. The installer is tested into temporary Copilot, Claude, and Cursor roots.
3. Existing 54-test evidence and plugin suite remains green.
4. A manual GitHub Copilot CLI smoke test uses `/skills reload` and
   `/skills info engineering-power` after installation.

## Non-goals for this migration

- Do not replace the evidence engine with a hosted service.
- Do not make Copilot cloud agent access Bitbucket/VPN resources.
- Do not automatically write PR comments, modify repositories, or bypass user
  permissions.
- Do not remove the Codex plugin during this phase.
