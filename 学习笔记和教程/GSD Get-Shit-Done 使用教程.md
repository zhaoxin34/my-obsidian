> **一个轻量但强大的元提示、上下文工程与规格驱动开发系统**

GSD 是一个专为 AI 代码助手设计的开发工作流框架，支持 Claude Code、OpenCode、Gemini CLI、Kilo、Codex、Copilot、Cursor、Windsurf、Antigravity、Augment、Trae、Qwen Code、Cline 和 CodeBuddy 等多种运行时。

**解决的核心问题：Context Rot** — 随着 AI 上下文窗口被填满，输出质量逐步劣化的问题。

[![npm version](https://img.shields.io/npm/v/get-shit-done-cc?style=flat-square)](https://www.npmjs.com/package/get-shit-done-cc)
[![GitHub stars](https://img.shields.io/github/stars/gsd-build/get-shit-done?style=flat-square)](https://github.com/gsd-build/get-shit-done)

---

## 目录

- [核心概念](#核心概念)
- [安装](#安装)
- [快速开始](#快速开始)
- [标准工作流](#标准工作流)
- [快速模式](#快速模式)
- [核心命令详解](#核心命令详解)
- [Wave 执行机制](#wave-执行机制)
- [项目文件结构](#项目文件结构)
- [配置与自定义](#配置与自定义)
- [安全注意事项](#安全注意事项)
- [故障排查](#故障排查)

---

## 核心概念

### Context Engineering（上下文工程）

GSD 的核心思想是：**给 AI 完整的上下文，让它稳定地产出高质量代码**。

传统开发中，AI 代码助手质量下降的原因是：
- 上下文窗口被历史对话填满
- 缺少项目整体架构认知
- 决策和边界条件没有文档化

GSD 通过结构化的文件体系维护项目上下文：

| 文件 | 作用 |
|------|------|
| `PROJECT.md` | 项目愿景，始终加载 |
| `REQUIREMENTS.md` | 带 phase 可追踪性的 v1/v2 范围定义 |
| `ROADMAP.md` | 路线图：要去哪、已完成哪些 |
| `STATE.md` | 决策、阻塞项、当前位置 — 跨会话记忆 |
| `PLAN.md` | 带 XML 结构和验证步骤的原子任务 |
| `SUMMARY.md` | 做了什么、改了什么、已提交 |
| `research/` | 生态知识（技术栈、功能、架构、坑点） |

### 元提示（Meta-Prompting）

不是给 AI 命令，而是给它**完整的背景、约束和验收标准**，让它自己推理出最佳方案。

### 多代理编排（Multi-Agent Orchestration）

每个阶段由一个轻量 orchestrator 协调多个专用代理：

```
┌─────────────────────────────────────────────────────┐
│ Stage        │ Orchestrator 做什么    │ Agents 做什么          │
├──────────────┼────────────────────────┼──────────────────────── ┤
│ Research     │ 协调并展示研究发现      │ 4 个并行研究代理分别调查 │
│              │                        │ 技术栈、功能、架构、坑点  │
│ Planning     │ 校验并管理迭代          │ Planner 生成计划，       │
│              │                        │ checker 验证，循环直到通过 │
│ Execution    │ 按 wave 分组并跟踪进度   │ Executors 并行实现，      │
│              │                        │ 每个都有全新的 20 万上下文 │
│ Verification │ 呈现结果并决定下一步    │ Verifier 对照目标检查代码库 │
└─────────────────────────────────────────────────────┘
```

---

## 安装

### 一键安装

```bash
npx get-shit-done-cc@latest
```

安装器会提示选择：
1. **运行时**：选择你使用的 AI 代码助手
2. **安装位置**：全局（所有项目）或本地（仅当前项目）

### 支持的运行时

| 运行时 | 全局路径 | 本地路径 |
|--------|----------|----------|
| Claude Code | `~/.claude/` | `./.claude/` |
| OpenCode | `~/.config/opencode/` | `./.opencode/` |
| Gemini CLI | `~/.gemini/` | `./.gemini/` |
| Kilo | `~/.config/kilo/` | `./.kilo/` |
| Codex | `~/.codex/` | `./.codex/` |
| Copilot | `~/.github/` | `./.github/` |
| Cursor CLI | `~/.cursor/` | `./.cursor/` |
| Windsurf | `~/.codeium/windsurf/` | `./.windsurf/` |
| Cline | `~/.cline/` | `./.clinerules` |

### 非交互式安装

```bash
# 指定运行时和全局安装
npx get-shit-done-cc --claude --global

# 指定运行时和本地安装
npx get-shit-done-cc --claude --local

# 安装到所有运行时
npx get-shit-done-cc --all --global
```

### 验证安装

安装完成后，运行以下命令验证：

```bash
# Claude Code / Gemini / Copilot / Antigravity / Qwen Code
/gsd-help

# OpenCode / Kilo / Augment / Trae / CodeBuddy
/gsd-help

# Codex
$gsd-help

# Cline
# 检查 .clinerules 文件是否存在
```

### 推荐：跳过权限确认模式

GSD 设计为无摩擦自动化，建议配合以下方式运行：

```bash
claude --dangerously-skip-permissions
```

> [!TIP]
> 这才是 GSD 的预期用法。如果连 `date` 和 `git commit` 都要来回确认 50 次，整个体验就废了。

---

## 快速开始

### 1. 初始化新项目

```bash
/gsd-new-project
```

系统会引导你完成：
1. **提问** — 一直问到彻底理解你的想法（目标、约束、技术偏好、边界情况）
2. **研究** — 并行调研领域知识（可选，强烈建议启用）
3. **需求梳理** — 区分 v1、v2 和范围外
4. **路线图** — 创建与需求映射的阶段规划

**生成文件**：`PROJECT.md`、`REQUIREMENTS.md`、`ROADMAP.md`、`STATE.md`、`.planning/research/`

### 2. 已有代码库？

先运行代码库映射，让 GSD 理解你的项目：

```bash
/gsd-map-codebase
```

然后再运行 `/gsd-new-project`，此时它已经理解你的代码库，提问会聚焦在你要新增的部分。

---

## 标准工作流

GSD 的核心是一个循环：**讨论 → 规划 → 执行 → 验证 → 发布**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Discuss     │ -> │ Plan        │ -> │ Execute     │ -> │ Verify      │ -> │ Ship        │
│ Phase N     │    │ Phase N     │    │ Phase N     │    │ Work N      │    │ Phase N     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 完整流程示例

```bash
# 阶段 1：讨论 — 在规划前收集实现决策
/gsd-discuss-phase 1

# 阶段 1：规划 — 研究 + 制定计划 + 验证
/gsd-plan-phase 1

# 阶段 1：执行 — 按 wave 并行执行所有计划
/gsd-execute-phase 1

# 阶段 1：验证 — 人工验收测试
/gsd-verify-work 1

# 阶段 1：发布 — 创建 PR
/gsd-ship 1

# 重复到阶段 2...
```

### 或使用自动推进

```bash
# 自动检测并执行下一步
/gsd-next
```

---

## 快速模式

对于不需要完整规划的临时任务，使用快速模式：

```bash
/gsd-quick
```

快速模式保留 GSD 的核心保障（原子提交、状态跟踪），但路径更短：

| 特点 | 说明 |
|------|------|
| 相同代理体系 | Planner + executor，质量不降 |
| 跳过可选步骤 | 默认不启用 research、plan checker、verifier |
| 独立跟踪 | 数据存放在 `.planning/quick/`，不和 phase 混在一起 |

### 快速模式参数

- `--discuss`：在规划前先进行轻量讨论，理清灰区
- `--research`：在规划前拉起研究代理，调查实现方式、库选型和潜在坑点
- `--full`：启用计划检查（最多 2 轮迭代）和执行后验证
- `--validate`：只启用计划检查和执行后验证

示例：

```bash
# 完整流程：讨论 + 研究 + 计划检查 + 验证
/gsd-quick --discuss --research --full

# 简单任务
/gsd-quick
> What do you want to do? "Add dark mode toggle to settings"
```

---

## 核心命令详解

### /gsd-new-project

完整初始化项目。

```bash
/gsd-new-project          # 交互式
/gsd-new-project --auto   # 自动模式，使用默认值
```

### /gsd-discuss-phase

在规划前收集实现决策。这是塑造实现方式的关键步骤。

```bash
/gsd-discuss-phase 1           # 讨论阶段 1
/gsd-discuss-phase 1 --batch   # 批量回答问题
/gsd-discuss-phase 1 --analyze # 增加权衡分析
/gsd-discuss-phase 1 --chain   # 自动链入规划和执行
```

系统会识别灰区并持续追问，直到你满意为止。最终输出 `CONTEXT.md`。

**讨论的灰区类型**：

- **视觉功能**：布局、信息密度、交互、空状态
- **API / CLI**：返回格式、flags、错误处理、详细程度
- **内容系统**：结构、语气、深度、流转方式
- **组织型任务**：分组标准、命名、去重、例外情况

### /gsd-plan-phase

为某个阶段执行研究 + 规划 + 验证。

```bash
/gsd-plan-phase 1           # 阶段 1
/gsd-plan-phase 1 --reviews # 加载代码库审查结果
```

**生成文件**：`{phase_num}-RESEARCH.md`、`{phase_num}-{N}-PLAN.md`

### /gsd-execute-phase

以并行 wave 执行全部计划，完成后验证。

```bash
/gsd-execute-phase 1
/gsd-execute-phase 1 --to 2  # 在完成阶段 2 后停止自主执行
```

**生成文件**：`{phase_num}-{N}-SUMMARY.md`、`{phase_num}-VERIFICATION.md`

### /gsd-verify-work

人工用户验收测试。

```bash
/gsd-verify-work 1
```

系统会：
1. 提取可测试的交付项
2. 逐项带你验证
3. 自动诊断失败
4. 创建验证过的修复计划

### /gsd-ship

从已验证的阶段工作创建 PR。

```bash
/gsd-ship 1           # 创建正式 PR
/gsd-ship 1 --draft    # 创建 Draft PR
```

### /gsd-complete-milestone

归档里程碑并打 release tag。

```bash
/gsd-complete-milestone
```

### /gsd-new-milestone

开启下一个版本 — 相同流程但面向现有代码库。

```bash
/gsd-new-milestone
/gsd-new-milestone v2.0
```

---

## Wave 执行机制

计划根据依赖关系被分组为不同的 "Wave"：

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE EXECUTION                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  WAVE 1 (parallel)    WAVE 2 (parallel)    WAVE 3                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │ Plan 01 │  │ Plan 02 │ → │ Plan 03 │  │ Plan 04 │ → │ Plan 05 │  │
│  │  User   │  │Product  │  │ Orders  │  │  Cart   │  │Checkout │  │
│  │  Model  │  │  Model  │  │   API   │  │   API   │  │   UI    │  │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │
│        │        │            ↑           ↑            ↑            │
│        └────────┴────────────┴───────────┴────────────┘             │
│                                                                     │
│  Dependencies:                                                      │
│  • Plan 03 needs Plan 01                                            │
│  • Plan 04 needs Plan 02                                            │
│  • Plan 05 needs Plans 03 + 04                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Wave 划分的原则**：

- **独立计划** → 同一 wave → 并行执行
- **有依赖的计划** → 更晚的 wave → 等依赖完成
- **文件冲突** → 顺序执行，或合并到同一个计划里

### 为什么垂直切片比水平分层更容易并行

| 方式 | 说明 |
|------|------|
| **垂直切片** ✅ | Plan 01：端到端完成用户功能 — 更容易并行 |
| **水平分层** ❌ | Plan 01：所有 model，Plan 02：所有 API — 依赖关系导致串行 |

---

## 项目文件结构

GSD 在项目中创建以下结构：

```
.
├── PROJECT.md              # 项目愿景
├── REQUIREMENTS.md         # 需求定义 (v1/v2/范围外)
├── ROADMAP.md             # 阶段路线图
├── STATE.md               # 状态、决策、阻塞项
└── .planning/
    ├── config.json        # GSD 配置
    ├── research/          # 领域研究
    │   ├── 01-stack-research.md
    │   ├── 02-features-research.md
    │   └── ...
    ├── phases/
    │   └── phase-01/
    │       ├── 01-CONTEXT.md
    │       ├── 01-RESEARCH.md
    │       ├── 01-01-PLAN.md
    │       ├── 01-01-SUMMARY.md
    │       └── 01-VERIFICATION.md
    └── quick/             # 快速模式任务
        └── 001-xxx/
            └── PLAN.md
```

---

## 配置与自定义

### 查看当前配置

```bash
/gsd-settings
```

### 模型 Profile

控制各代理使用哪种 Claude 模型：

| Profile | Planning | Execution | Verification |
|---------|----------|-----------|--------------|
| `quality` | Opus | Opus | Sonnet |
| `balanced`（默认） | Opus | Sonnet | Sonnet |
| `budget` | Sonnet | Sonnet | Haiku |
| `inherit` | 继承当前 | 继承当前 | 继承当前 |

切换：

```bash
/gsd-set-profile budget
```

### 工作流代理开关

| 设置 | 默认 | 说明 |
|------|------|------|
| `workflow.research` | `true` | 每个 phase 规划前先调研 |
| `workflow.plan_check` | `true` | 执行前验证计划 |
| `workflow.verifier` | `true` | 执行后确认交付 |
| `workflow.auto_advance` | `false` | 自动串联 discuss → plan → execute |

单次命令覆盖：

```bash
/gsd-plan-phase 1 --skip-research
/gsd-plan-phase 1 --skip-verify
```

### Git 分支策略

```bash
# .planning/config.json
{
  "git": {
    "branching_strategy": "phase",  // none | phase | milestone
    "phase_branch_template": "gsd/phase-{phase}-{slug}",
    "milestone_branch_template": "gsd/{milestone}-{slug}"
  }
}
```

---

## 安全注意事项

### 保护敏感文件

GSD 的代码库映射会读取文件。**包含机密信息的文件应加入 Claude Code 的 deny list**：

```json
// .claude/settings.json
{
  "permissions": {
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(**/secrets/**)",
      "Read(**/*credential*)",
      "Read(**/*.pem)",
      "Read(**/*.key)"
    ]
  }
}
```

### 内置安全加固

GSD v1.27+ 内置多层安全防护：
- **路径遍历防护**：验证用户提供的文件路径在项目目录内
- **提示注入检测**：扫描用户输入中的注入模式
- **安全 JSON 解析**：防止畸形参数破坏状态
- **Shell 参数验证**：用户文本在 shell 插入前被清理

---

## 故障排查

### 命令找不到？

1. 重启运行时，让命令/skills 重新加载
2. 验证文件存在于正确路径
3. 运行 `/gsd-help` 确认安装成功
4. 重新执行 `npx get-shit-done-cc@latest`

### 更新到最新版本

```bash
npx get-shit-done-cc@latest
```

### Docker 环境

如果 `~/.claude/...` 路径读取失败：

```bash
CLAUDE_CONFIG_DIR=/home/youruser/.claude npx get-shit-done-cc --global
```

### 卸载

```bash
# 全局卸载
npx get-shit-done-cc --claude --global --uninstall

# 本地卸载
npx get-shit-done-cc --claude --local --uninstall
```

---

## 更多资源

- [官方 GitHub](https://github.com/gsd-build/get-shit-done)
- [Discord 社区](https://discord.gg/mYgfVNfA2r)
- [用户指南](https://github.com/gsd-build/get-shit-done/blob/main/docs/USER-GUIDE.md)
- [变更日志](https://github.com/gsd-build/get-shit-done/blob/main/CHANGELOG.md)

---

> **核心理念**：GSD 将复杂性隐藏在系统内部，而不是在你的工作流里。幕后是上下文工程、XML 提示格式、子代理编排、状态管理；你看到的是几个真能工作的命令。
>
> *— TCHES（GSD 作者）*
