# Product Manager Skills 项目调研报告

> 来源: [deanpeters/Product-Manager-Skills](https://github.com/deanpeters/product-manager-skills)
> 版本: v0.75 (2026-03-17)
> 许可证: CC BY-NC-SA 4.0

## 概述

Product Manager Skills 是一个为 AI Agent 打造的产品管理技能框架，包含 **47 个可立即使用的 PM Skills + 6 个命令工作流**。这些技能教会你和你的 AI 代理如何以专业水平执行产品管理工作——PM 理解「为什么」，Agent 执行「怎么做」。

它与多种 AI Agent 兼容：Claude Code、Cowork、OpenAI Codex、ChatGPT、Gemini 以及任何能读取结构化知识的 AI Agent。

## 核心价值

| 对比项 | 传统 Prompts | PM Skills |
|--------|-------------|-----------|
| 复用性 | 每次任务单独指令 | 一次学习，重复使用 |
| 输出质量 | "写个 PRD"——结果随机 | Agent 知道 PRD 结构，会问智能问题 |
| 一致性 | 输出参差不齐 | 专业、一致的结果 |
| 教育性 | 无 | 每个技能都让使用者学到背后的框架原理 |

## 设计哲学

项目强调 **ABC — Always Be Coaching**（始终在指导）原则：
- 每个技能使用后，使用者应该比开始时懂得更多
- 删除解释性内容来精简输出是缺陷，不是改进
- 技能同时服务于两个目标：让 AI Agent 更能干，让人类 PM 更专业

## 三层架构

```
┌───────────────────────────────────────────────────────────┐
│ WORKFLOW SKILLS (6)                                      │
│ 完整端到端 PM 流程                                        │
│ 例如："运行产品策略会议"                                   │
│ 周期: 2-4 周                                             │
└───────────────────────────────────────────────────────────┘
                         ↓ 编排
┌───────────────────────────────────────────────────────────┐
│ INTERACTIVE SKILLS (20)                                  │
│ 带自适应问题的引导式发现                                   │
│ 例如："我该用哪个优先级框架？"                             │
│ 周期: 30-90 分钟                                         │
└───────────────────────────────────────────────────────────┘
                         ↓ 使用
┌───────────────────────────────────────────────────────────┐
│ COMPONENT SKILLS (21)                                    │
│ 特定 PM 可交付物的模板                                     │
│ 例如："写一个用户故事"                                     │
│ 周期: 10-30 分钟                                         │
└───────────────────────────────────────────────────────────┘
```

## 技能分类详情

### Component Skills（21个）—— 模板与产出物

| 技能 | 用途 |
|------|------|
| `user-story` | 用验收标准写用户故事 (Mike Cohn + Gherkin) |
| `positioning-statement` | 定义目标用户、问题、差异化 (Geoffrey Moore 框架) |
| `press-release` | 写未来新闻稿澄清产品愿景 (Amazon Working Backwards) |
| `problem-statement` | 用证据框定客户问题，避免直接跳到解决方案 |
| `epic-hypothesis` | 将模糊举措转化为可测试假设 |
| `customer-journey-map` | 跨所有触点映射客户体验 (NNGroup 框架) |
| `jobs-to-be-done` | 理解客户试图完成什么 (JTBD 框架) |
| `user-story-splitting` | 用 8 种成熟模式拆分大故事 |
| `user-story-mapping` | 按用户工作流组织故事 (Jeff Patton 框架) |
| `proto-persona` | 在完整研究前创建基于假设的画像 |
| `storyboard` | 用 6 帧叙事故事板可视化用户旅程 |
| `pestel-analysis` | 分析外部因素 (政治、经济、社会、技术、环境、法律) |
| `company-research` | 深入竞争对手/公司分析 |
| `eol-message` | 优雅地传达产品/功能弃用 |
| `pol-probe` | 定义轻量级、可丢弃的验证实验来测试假设 |
| `product-sense-interview-answer` | 结构化口述产品感觉答案 |
| `saas-economics-efficiency-metrics` | 评估单位经济学和资本效率 |
| `saas-revenue-growth-metrics` | 计算收入、留存、增长指标 |
| `finance-metrics-quickref` | 32+ SaaS 财务指标快速查询表 |
| `altitude-horizon-framework` | PM→总监心态转变框架 |
| `recommendation-canvas` | 记录 AI 产品推荐 |

### Interactive Skills（20个）—— 引导式发现

| 技能 | 功能 |
|------|------|
| `prioritization-advisor` | 根据情况推荐优先级框架 (RICE/ICE/Kano 等) |
| `discovery-interview-prep` | 基于研究目标规划客户访谈 (Mom Test 风格) |
| `epic-breakdown-advisor` | 用 Richard Lawrence 的 9 种模式拆分史诗 |
| `positioning-workshop` | 通过自适应问题引导定位定义 |
| `business-health-diagnostic` | 用关键指标诊断 SaaS 业务健康状况 |
| `acquisition-channel-advisor` | 用单位经济学评估获客渠道 |
| `feature-investment-advisor` | 评估特征投资的收入影响、成本结构、ROI |
| `finance-based-pricing-advisor` | 用财务影响分析评估定价变化 |
| `tam-sam-som-calculator` | 用真实数据和引用预测市场规模 |
| `ai-shaped-readiness-advisor` | 评估你是"AI-first"还是"AI-shaped" |
| `context-engineering-advisor` | 诊断上下文填充 vs 上下文工程 |
| `lean-ux-canvas` | 设置基于假设的规划 (Jeff Gothelf Lean UX Canvas v2) |
| `opportunity-solution-tree` | 生成机会和解决方案，推荐最佳概念验证测试 |
| `pol-probe-advisor` | 推荐 5 种原型类型中的一种来测试假设 |
| `customer-journey-mapping-workshop` | 引导旅程映射+痛点识别 |
| `user-story-mapping-workshop` | 引导创建带骨干和发布切片的story maps |
| `context-engineering-advisor` | 诊断上下文问题 |
| `director-readiness-advisor` | 教练 PM 和新总监渡过转型期 |
| `vp-cpo-readiness-advisor` | 教练总监和高管渡过 VP/CPO 转型 |
| `workshop-facilitation` | 为工作流技能添加逐步引导 |

### Workflow Skills（6个）—— 端到端流程

| 技能 | 功能 | 周期 |
|------|------|------|
| `product-strategy-session` | 完整策略: 定位→问题框定→方案探索→路线图 | 2-4周 |
| `discovery-process` | 完整发现周期: 框定问题→研究→综合→验证方案 | 3-4周 |
| `roadmap-planning` | 战略路线图: 收集输入→定义史诗→优先级→排序→沟通 | 1-2周 |
| `prd-development` | 结构化 PRD: 问题→人物画像→方案→指标→用户故事 | 2-4天 |
| `executive-onboarding-playbook` | VP/CPO 过渡的 30-60-90 天诊断 playbook | 90天 |
| `skill-authoring-workflow` | 元工作流: 创建→验证→更新文档→打包发布 | 30-90分钟 |

## 使用方法

### 快速选择指南

不熟悉技术？先读：
- `docs/Using PM Skills 101.md` — 新手入门
- `docs/Platform Guides for PMs.md` — 平台选择器

记住一件事：
1. 选**一个技能**
2. 给**一个真实业务问题**
3. 先让 AI 问**澄清问题**

### A) 非技术用户（聊天即可）

**Claude Desktop / ChatGPT Desktop**

复制粘贴这个 starter prompt：
```
Use the uploaded PM skill as my framework. Ask up to 3 clarifying questions first.
Then produce the final output in markdown. End with assumptions, risks, and next steps.
```

### B) 会用终端（更高控制力）

**Claude Code:**
```bash
npx skills find <query>
npx skills add deanpeters/Product-Manager-Skills --list
```

使用示例：
```
Using skills/prioritization-advisor/SKILL.md, help me choose a framework for 12
requests and one sprint. Ask questions one at a time, then give numbered recommendations.
```

**Claude /slash commands:**
- `/discover` — 发现流程
- `/write-prd` — 写 PRD
- `/plan-roadmap` — 规划路线图
- `/prioritize` — 优先级排序
- `/leadership-transition` — 领导力过渡

### C) 需要可重复工作流（自动化）

支持平台：n8n、LangFlow、Python Agents、OpenClaw、Claude Cowork

### D) 实验性替代 Agent 栈

支持：Cursor、Windsurf、Bolt、Replit Agent、Make.com、Devin、CrewAI、Gemini

## 配套工具

### Streamlit (beta) 界面

本地快速测试技能的 Web 界面：
```bash
streamlit run app/main.py
```
功能：Learn / Find My Skill / Run Skills

### 脚本工具

| 脚本 | 用途 |
|------|------|
| `find-a-skill.sh` | 按关键词查找技能 |
| `find-a-command.sh` | 查找命令 |
| `run-pm.sh` | 运行 PM 工作流 |
| `test-library.sh` | 测试整个库 |
| `test-a-skill.sh` | 测试单个技能 |
| `add-a-skill.sh` | 添加新技能 |
| `build-a-skill.sh` | 构建技能 |
| `zip-a-skill.sh` | 打包技能为 .zip |
| `generate-catalog.py` | 生成目录索引 |

## 使用场景示例

### "我需要对齐干系人的产品策略"
→ **Workflow:** `product-strategy-session` (2-4周)

### "我需要在构建前验证客户问题"
→ **Workflow:** `discovery-process` (3-4周)

### "我想快速测试一个假设再投入开发"
→ **Interactive:** `pol-probe-advisor` (推荐原型类型)
→ **Component:** `pol-probe` (记录验证实验)

### "我要写一个新功能的 PRD"
→ **Workflow:** `prd-development` (2-4天)

### "我要创建 Q2 路线图"
→ **Workflow:** `roadmap-planning` (1-2周)

### "我该用哪个优先级框架？"
→ **Interactive:** `prioritization-advisor`

### "我需要拆分一个大型史诗"
→ **Interactive:** `epic-breakdown-advisor`

## 项目结构

```
product-manager-skills/
├── skills/               # 47个技能（每个skill-name/SKILL.md）
│   ├── user-story/
│   ├── prioritization-advisor/
│   ├── prd-development/
│   └── ...
├── commands/             # 6个命令工作流
├── catalog/              # 自动生成的浏览索引
├── docs/                 # 使用指南和公告
│   ├── Using PM Skills 101.md
│   ├── Platform Guides for PMs.md
│   ├── announcements/
│   └── ...
├── app/                  # Streamlit beta 界面
├── scripts/              # 工具脚本
└── research/             # 研究资料
```

## 技能标准格式

每个技能文件包含：
1. **Purpose** — 技能功能和适用场景
2. **Key Concepts** — 核心框架、定义、反模式
3. **Application** — 逐步指导（含示例）
4. **Examples** — 真实案例（好的和坏的）
5. **Common Pitfalls** — 要避免什么及原因
6. **References** — 相关技能和外部框架

## 框架来源

项目整合了多位大师的方法论：
- **Teresa Torres** — 持续发现、机会解决方案树
- **Geoffrey Moore** — 定位、跨越鸿沟
- **Jeff Patton** — 用户故事映射
- **Mike Cohn** — 用户故事、敏捷估计
- **Amazon** — Working Backwards 新闻稿
- **MITRE** — 问题框定
- **Richard Lawrence** — 史诗拆分模式
- **Jeff Gothelf** — Lean UX Canvas
- **Dean Peters** — PoL 框架等原创贡献

## 优缺点分析

### 优点
- 框架经过真实客户工作验证（医疗、金融、制造、科技行业）
- Agent 优化格式——不是博客、不是书、不是课程，是**可执行框架**
- 无废话，每个词都有用
- 示例丰富（含好的和坏的）
- 支持平台广泛
- 教育性与实用性并重

### 缺点
- 目前更多是 Markdown 文件，需要一定配置才能在部分平台使用
- 某些 Skills 可能需要根据具体业务场景调整
- 许可证是 CC BY-NC-SA 4.0，商用需注意

## 总结

Product Manager Skills 是一个非常实用的 PM+AI 集成框架。它的价值不仅在于提供了 47 个可直接使用的技能模板，更在于：

1. **教育性** — 每个技能都让人学到背后的框架原理
2. **系统性** — 三层架构覆盖从组件到端到端流程的所有场景
3. **兼容性** — 支持几乎所有主流 AI Agent 平台
4. **实战性** — 基于 decades 的 PM 咨询经验

对于希望利用 AI 提升 PM 效率的个人或团队，这是一个值得深入研究的资源。
