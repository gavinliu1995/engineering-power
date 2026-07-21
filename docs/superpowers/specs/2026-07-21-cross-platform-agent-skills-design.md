# 跨平台 Agent Skills 迁移设计

## 目标

将 Engineering Power 优先迁移为可在 GitHub Copilot 中使用的 Agent Skill；
同时保留现有 Codex Plugin，并让同一套 Skill 包可以安装到 Claude Code 和
Cursor。仓库证据采集与校验引擎仍然是产品核心。

## 产品边界

- **本地 Agent 模式是主路径。** Copilot CLI / VS Code、Claude Code 和 Cursor
  可以分析本地仓库、Git commit 范围、working tree 与下载的 patch，从而保留
  Bitbucket/VPN 离线工作流。
- **GitHub 云端 Agent 模式是辅助路径。** 它可以处理 GitHub 仓库与 PR，但不能
  被描述为能够读取开发者本机 checkout 或公司 VPN 内资源的方案。
- **分析默认只读。** 现有开发生命周期工作流继续要求用户明确授权后才可修改代码。

## 架构

```
scripts/repo_evidence/          共享的确定性证据采集与校验引擎
references/                     共享的报告规范与分析重点说明
skills/                         现有 Codex Plugin 适配层
.agents/skills/engineering-power/
                                标准化、可移植的 Agent Skills 包（主入口）
scripts/install_agent_skill.py  针对各宿主的安装与校验工具
```

可移植包采用一个 `engineering-power` 总入口 Skill：根据用户请求路由到现有的
仓库情报、PR 影响、API、发布、架构、入职、迁移和工程生命周期工作流。它会引用
仓库中的共享脚本和资源；对于在本仓库外安装 Skill 的宿主，安装器会复制一份自包含包。

## 宿主支持

| 宿主 | 安装位置 | 适用范围 |
| --- | --- | --- |
| GitHub Copilot CLI / IDE | `.agents/skills/engineering-power` 或 `~/.agents/skills/engineering-power` | 本地 Git 与 GitHub 工作流 |
| Claude Code | `.claude/skills/engineering-power` | 本地 Git 与 GitHub 工作流 |
| Cursor | `.cursor/skills/engineering-power` | 本地 Git 与 GitHub 工作流 |
| Codex | 现有 `.codex-plugin` 与 `skills/` | 保持现有行为不变 |

安装器会将打包好的可移植 Skill 复制到所选宿主目录；除非用户明确指定某个目标仓库
作为安装位置，否则不会修改目标仓库。

## Skill 包契约

可移植的 `SKILL.md` 必须具有标准的 `name` 和 `description` frontmatter，明确
默认只读，并说明如何以当前仓库根目录运行证据采集器。分析本地仓库时，它不得依赖
Codex 专用 UI 元数据、Codex marketplace 或 GitHub App。

## 验证策略

1. 新增确定性测试，验证标准目录、frontmatter、必须的工作流路由、打包脚本与
   reference，以及不存在密钥泄露。
2. 在临时 Copilot、Claude 与 Cursor 目录中测试安装器。
3. 既有的 54 项证据引擎与插件测试必须继续全部通过。
4. GitHub Copilot CLI 手工烟测：安装后运行 `/skills reload` 和
   `/skills info engineering-power`。

## 本次迁移不做什么

- 不将证据引擎改造成托管服务。
- 不尝试让 Copilot 云端 Agent 访问 Bitbucket/VPN 资源。
- 不自动写 PR 评论、修改仓库或绕过用户权限。
- 本阶段不移除 Codex Plugin。
