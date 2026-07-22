# Engineering Power Copilot 质量与安全加固设计

## 目标

修复 GitHub Copilot 验收发现的阻塞问题，同时保持 Codex Plugin、便携 Agent Skill 和共享 Evidence Engine 使用同一套实现：

1. Secret-like 源码内容不得进入 AI 分析 Context 或最终报告。
2. Coverage 必须由 `manifest.json` 确定性生成，不能由模型计算。
3. Architecture Map 必须加载专项规则、追踪具体业务链并内联交付 Mermaid。
4. Quick Architecture 报告必须紧凑并在时间预算不足时主动收束。
5. 缓存和 Patch 测试必须区分产品缺陷与无效测试输入。

## 非目标

- 不删除本地只读 Evidence Snapshot 中的原始源码；Snapshot 仍以 `600` 权限保存，用于精确引用与本地审计。
- 不改变 `--output` 的现有语义；显式输出目录继续表示一次独立采集，不参与共享缓存命中。
- 不把 Copilot 拆成多个用户可见 Skills。
- 不修改目标仓库，不自动运行目标仓库测试，也不接入 Bitbucket API。

## 设计

### 1. 统一 Context 脱敏

新增共享的文本脱敏模块，供 `prepare_analysis_context.py` 和 `prepare_workflow_context.py` 共同调用。脱敏发生在原始 Snapshot 被渲染到 AI Context 之前；普通凭据按行处理，private-key block 使用保留换行数的多行处理。

必须覆盖：

- `password=value`、`token: value`、带引号的 JSON/YAML assignment；
- `<secret>value</secret>`、`<client-secret>value</client-secret>` 等 XML/Maven 元素；
- `password="value"` 等 XML/配置属性；
- `--token value` 和 `--password=value` 等命令参数；
- URL user-info、Authorization/Bearer/Basic 值；
- private-key block；
- 已知的复合凭据字段，例如 servlet users/credentials 列表。

替换内容统一使用 `[REDACTED]`，并保持原文件行数不变，使 `path:line-line` 引用仍可定位到原文件。字段名、标签名和风险位置保留，Secret 值不保留。原始 Snapshot 不进入最终回复。

### 2. Coverage 确定性化

`finalize_report.py` 从 Snapshot Manifest 的以下字段生成 Coverage：

```text
Coverage: {stats.collected_files}/{stats.text_candidates} text candidates
Tree entries: stats.tree_entries
```

Finalizer 必须覆盖模型草稿中错误的 Coverage 数值；Validator 必须拒绝未 Finalize 且与 Manifest 不一致的报告。`tree_entries` 不得作为 text candidates 分母。

Reasoning evidence 文件数不是 Collector Coverage，不与上述分数混写；存在分析 Context metadata 时单独显示，否则写 `not recorded`。

### 3. Architecture 专项合同

便携 `engineering-power` Router 对 Architecture Map 使用硬路由：

1. 必须读取 `references/architecture-focus.md` 和 `references/report-schema.md`；
2. 必须运行 Architecture 专项报告类型；
3. 必须追踪至少一条有直接证据支持的 `Page/Route → Provider/Service → Client/DAO` 链；
4. 必须分析模块/运行单元、依赖方向、状态所有权、信任边界、外部系统和渐进式目标状态；
5. 不得用通用 Repository Intelligence、Onboarding 或 Build 说明填充 Architecture 报告。

新增 `architecture` report type。Quick 使用固定、紧凑结构：

```markdown
# Engineering Power Architecture Map

## Target and Evidence
## System Context and Runtime Units
## Module Boundaries and Dependencies
## Architecture Diagram
## Concrete Feature Flow
## Trust, State, and External Boundaries
## Risks and Incremental Target State
## Unknowns
## Evidence Index
```

Quick 必须包含一张系统架构 Mermaid 和一张具体 feature-flow Mermaid，最多五项风险，正文不超过 7,000 个 Markdown 字符。Deep 可扩大证据范围，但仍使用同一专项结构。

### 4. Inline 交付

GitHub Copilot、Codex、Claude 和 Cursor 的最终回复必须直接包含正式报告正文与 Mermaid。Artifact 只用于下载或保存副本，不能替代聊天中的报告。

如果界面长度限制阻止完整内联，至少内联：Target/Git state、Coverage、两张 Mermaid、主要风险、Validation 和 Unknowns，并明确说明 Artifact 中包含其余 Evidence Index。不得只回复文件路径。

### 5. Quick 时间收束

Collector 返回的 `report_deadline_epoch` 是整个 Quick 工作流的时间预算。Agent 在证据准备完成后、开始追加搜索前和正式成稿前检查剩余时间：

- 剩余超过 30 秒：允许一次针对具体 feature 链的定向检索；
- 剩余不超过 30 秒：停止扩大证据，立即按紧凑模板成稿；
- 已超时：基于已收集证据完成最小报告，并由 Finalizer 标记 `passed-with-deadline-limit`。

Finalizer 继续负责事后验证；它不能单独保证模型按时停止。7,000 字符上限和两阶段预算检查共同降低超时概率。

### 6. 测试语义

- Cache reuse 测试不得传 `--output`；连续两次默认采集相同精确 Git 状态，第二次必须命中。
- `--output` 测试必须预期 `cache_hit: false`，并说明这是独立快照语义。
- Patch 行为测试必须先断言 Patch 非空；空 Patch 只能验证安全边界，不能验证 changed-file 引用。

## 测试策略

严格使用 TDD，每一组实现前先加入失败测试并观察预期失败：

1. 单元测试覆盖 assignment、XML、JSON/YAML、CLI、URL、Authorization、private key 和复合凭据脱敏。
2. `prepare_analysis_context.py` 与 `prepare_workflow_context.py` 的真实 Context 中不得出现测试 Secret literal，且行号保持不变。
3. Finalizer 使用 Manifest 覆盖错误 Coverage；Validator 拒绝错误 Coverage。
4. Architecture report type 校验标题、九个章节、两张 Mermaid、具体 feature flow、引用和 7,000 字符上限。
5. Portable Skill 合同测试要求 Architecture 路由显式加载专项 reference，并要求 inline delivery。
6. Cache 测试覆盖默认命中和显式 `--output` 不命中。
7. Patch 测试拒绝将空 Patch 当作有效变更测试。
8. 完整测试、Skill 校验、Plugin 校验和便携包同步检查全部运行。

## 发布与验收

实现通过后：

1. 同步 `.agents/skills/engineering-power` 便携资源；
2. 更新 Plugin cachebuster；
3. 重新安装 Codex Plugin；
4. 重新安装/刷新 Copilot user Skill；
5. 对 `mbba-admintool` 重跑 Architecture Quick；
6. 确认 Context 不含已知 Secret literal、Coverage 正确、报告内联、包含具体业务链；
7. 记录总耗时。若仍超过 120 秒，则保留 `Go with conditions`，但安全修复不允许降级。

## 兼容性与回滚

- 脱敏模块只改变送入 AI 的 Context，不改变原始 Snapshot、Git 状态和引用路径。
- 新 `architecture` report type 是新增接口，不修改已有 repository、PR、dependency、API 和 release contract。
- 如安装验证失败，保留上一版本 Plugin cache；不直接修改已安装缓存，修复源码后重新打包。
