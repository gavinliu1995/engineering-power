# GitHub Copilot 20-Skill 完整迁移设计

## 背景

Engineering Power 当前同时包含两套入口：

- `skills/*`：Codex Plugin 使用的 20 个独立 Skills。
- `.agents/skills/engineering-power`：GitHub Copilot、Claude Code 和 Cursor
  可发现的单一总入口 Skill。

单一总入口可以调用共享证据脚本，但 GitHub Copilot 不会自动读取仓库根目录的
`skills/*`。因此它无法像 Codex 一样分别发现、选择和完整执行这 20 个 Skill。

## 目标

1. 让 GitHub Copilot、Claude Code 和 Cursor 分别发现 Engineering Power 的
   20 个独立 Skills。
2. 保留 `engineering-power` 总入口，继续承担路由、帮助和共享证据引擎职责。
3. 保留现有 Codex Plugin 结构和行为。
4. 根目录 `skills/*` 继续作为唯一人工维护的 Skill 源码，避免两套内容漂移。
5. 安装后提供 21 个可发现目录：20 个独立 Skills 加 1 个总入口。

## 架构

```text
skills/<name>/                         人工维护的 Canonical Skill
        │
        │ deterministic sync
        ▼
.agents/skills/<name>/                 Copilot/Claude/Cursor 可发现的生成物

.agents/skills/engineering-power/      总入口 + 共享证据引擎 + 共享报告规范
├── SKILL.md
├── scripts/repo_evidence/
└── references/
```

同步器负责从 `skills/*` 生成 20 个平台中立 Skills。生成物进入 Git，因此远程
GitHub 仓库、项目级安装和用户级安装都能直接使用，不依赖运行时生成步骤。

## 单一源码与生成规则

`skills/*` 是唯一人工维护源。`.agents/skills/<name>` 不允许手工修改，必须由
`scripts/sync_portable_agent_skill.py` 生成。

每个生成 Skill：

1. 保留源 `SKILL.md` 的 `name` 和 `description`。
2. 复制执行所需的同目录资源，例如 prompt、reference、脚本和示例。
3. 排除 Codex 专用 `agents/openai.yaml`、`__pycache__` 和 `*.pyc`。
4. 将 `engineering-power:<skill>` 改写成 Copilot 可发现的裸 Skill 名。
5. 将 `$PLUGIN_ROOT` 改写成 `$ENGINEERING_POWER_CORE`。
6. 将根级共享 reference 路径改写为
   `../engineering-power/references/<file>`。
7. 注入 Portable Runtime 说明，明确共享核心位于相邻的
   `../engineering-power`，仓库分析不得绕过共享证据引擎。

生成器必须是确定性的。`--check` 会比较 canonical source 与所有生成目录，
发现缺失、意外文件或内容差异时失败。

## 总入口职责

`.agents/skills/engineering-power` 继续存在，但角色收敛为：

- 用户不知道应选哪个 Skill 时的 router/orchestrator。
- `help`、`doctor`、缓存管理等统一入口。
- 共享 `repo_evidence` 脚本和报告规范的 runtime core。

它不再是 Copilot 唯一能够发现的 Engineering Power Skill。

## 安装模型

安装器把整个 Skill Suite 安装到宿主的 Skills 根目录：

| 宿主 | 安装根目录 |
| --- | --- |
| GitHub Copilot | `<target>/.agents/skills/` |
| Claude Code | `<target>/.claude/skills/` |
| Cursor | `<target>/.cursor/skills/` |

安装内容是 21 个受管目录。安装器不得删除目标 Skills 根目录，也不得影响用户的
其他 Skills。

- 默认模式：任一受管目标已存在时，在复制前整体失败。
- `--force`：只替换 Engineering Power 的 21 个受管目录。
- `--dry-run`：列出全部目标，不创建或删除文件。

## 路径与宿主兼容

平台中立 Skill 不依赖：

- Codex `agents/openai.yaml`
- Codex marketplace
- Codex Plugin cache
- GitHub App 才能完成的本地分析

仓库分析 Skill 通过相邻 core 使用共享脚本：

```text
../engineering-power/scripts/repo_evidence/
../engineering-power/references/
```

本地 Git、commit range、working tree 和 patch 是 Bitbucket/VPN 离线场景的
主路径。GitHub URL/PR 仍可使用现有认证策略。

## 测试合同

自动化测试必须验证：

1. `.agents/skills` 的受管目录集合等于 20 个 canonical Skills 加总入口。
2. 20 个生成 Skills 都有有效 frontmatter。
3. 生成内容不包含 `$PLUGIN_ROOT`、`engineering-power:` 或错误的
   `../../references`。
4. 源 Skill 的必要辅助资源被复制，`agents/openai.yaml` 被排除。
5. `sync --check` 能发现 SKILL、资源和目录级漂移。
6. 三种宿主都能安装完整 21-Skill Suite。
7. 安装器保留无关 Skills，并且冲突处理不会产生半安装状态。
8. 所有生成 Skill 通过 Skill Creator 的 `quick_validate.py`。
9. 既有证据引擎、脱敏、缓存、只读和报告校验测试继续通过。

## 文档与使用体验

README 必须说明：

- Codex Plugin 与 Agent Skills 使用同一 canonical source。
- Copilot 用户可以单独选择 20 个 Skills，也可以选择总入口。
- 修改 `skills/*` 后必须运行同步器并提交生成物。
- 安装、刷新和验证命令。

## 非目标

- 不把 GitHub Copilot 变成 Codex Plugin 宿主。
- 不让 Copilot 云端 Agent 访问开发者本机或 VPN 内资源。
- 不自动修改目标仓库、评论 PR 或扩大 GitHub 权限。
- 不在 20 个 Skill 中复制 20 份证据引擎。
- 不在本次迁移中重写现有分析方法或报告内容。

## 验收标准

迁移完成后：

- Codex 仍显示和执行原有 20 个 Skills。
- Copilot/Claude/Cursor 安装目录包含 21 个可发现 Skills。
- Copilot 可以直接选择 `pr-impact-analysis`、
  `systematic-debugging`、`verification-before-completion` 等独立 Skill。
- 所有自动化测试与 21 个 Skill 校验通过。
- 工作区中不存在需要人工同步的第二套 Skill 内容。
