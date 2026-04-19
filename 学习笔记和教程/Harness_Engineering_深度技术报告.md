**技术深度研究报告**

> **报告日期**: 2026年4月7日
> **目标读者**: 软件工程师、AI/ML从业者、技术决策者
> **研究主题**: Harness Engineering（驾驭工程）——2026年AI圈最火热的技术话题

---

## 执行摘要

Harness Engineering（驾驭工程）是2026年AI领域最重要的工程范式突破。它源于一个核心发现：**决定AI Agent表现的关键不是模型本身，而是包裹在模型外围的那套系统**。

OpenAI的标志性实验证明了这一点：仅3名工程师借助Codex Agent，在5个月内完全通过AI生成的方式构建了一个包含约**100万行代码**的生产级应用，合并了约1500个Pull Request，全程零行人工手写代码，开发效率提升约**10倍**[1]。更令人震惊的是，LangChain的实验显示：同一个模型，仅通过优化Harness架构，其在Terminal Bench 2.0上的通过率就从52.8%飙升至66.5%——底层模型权重**一个字节都没改**[2]。

这揭示了一个深刻的技术真相：**模型是马力，Harness是缰绳**。同一匹马，配上不同的驾驭系统，表现天差地别。

---

## 一、引言：从"调模型"到"搭系统"

### 1.1 技术背景

2026年的AI圈出现了一个耐人寻味的现象：大模型能力以近乎失控的速度跃迁，从GPT-3到GPT-5，从Claude 3到Claude 4，参数规模、推理能力、多模态水平不断刷新纪录。然而，德勤发布的《2026年企业AI现状》报告显示，尽管80%的受访企业声称已部署AI工具，但真正能够实现规模化应用并产生显著商业价值的企业仅占**15%**[3]。

这形成了一个技术进步与落地效果之间的鲜明反差：**AI越强，企业反而越用不好、不敢用。**

### 1.2 问题的本质

当AI从"会说话"走向"能干活"，从单轮问答进化到自主执行多步骤复杂任务时，一类全新的失败模式开始浮现[4]：

- **上下文侵蚀**：随着对话历史膨胀，模型对早期决策的记忆模糊，在第50轮对话中做出的选择可能与第5轮的架构决策完全矛盾
- **自我评估失灵**：模型天然倾向于对自己的输出给予正面评价，难以保持批判距离
- **架构约束缺失**：Agent忽视团队规范，生成违反架构约束的代码
- **技术债加速累积**：AI代码易混乱，无人review时技术债以10倍速度增长

这些问题的根源不在于"模型够不够聪明"，而在于**"环境够不够好"**。

### 1.3 概念的诞生

2025年底，HashiCorp联合创始人、Terraform作者Mitchell Hashimoto首次明确命名了这一工程实践[5]：

> **"每当发现Agent犯错，就花时间工程化一个解决方案，确保它永远不再犯同样的错误。"**

2026年2月5日，OpenAI发表《Harness Engineering: Leveraging Codex in an Agent-First World》，将这一理念推向高潮[1]。随后，Anthropic、LangChain、Google DeepMind等头部厂商纷纷跟进，逐渐收敛到一个行业共识公式：

```
Agent = Model + Harness
```

---

## 二、核心概念辨析：三层工程范式的演进

### 2.1 概念层次关系

Harness Engineering并非凭空出现，它是Prompt Engineering和Context Engineering的自然延伸，三者构成嵌套关系[6]：

| 层次 | 关注焦点 | 核心问题 | 类比 |
|------|----------|----------|------|
| **Prompt Engineering** | 如何向模型提问 | "该怎么问？" | 指令措辞 |
| **Context Engineering** | 给模型看什么 | "该让它看到什么？" | 工作内存管理 |
| **Harness Engineering** | 给模型怎样的环境 | "怎么让它稳定工作？" | 操作系统 |

### 2.2 各层详解

#### 2.2.1 Prompt Engineering（2020-2023）

这是AI工程的1.0阶段，聚焦于"如何说清楚"。典型技术包括角色设定、思维链（CoT）、Few-shot示例、ReAct框架[7]。

**核心局限**：
- 无法注入私域知识（如团队规范）
- 无法感知外部状态（如系统日志）
- 无法处理多轮任务中的目标漂移

当任务从"答对一道题"变为"完成一个PR"（Pull Request），仅靠Prompt已力不从心。

#### 2.2.2 Context Engineering（2024-2025）

2.0阶段的核心是信息编排——决定模型在关键时刻能看到什么。Andrej Karpathy指出，此时Context Engineering比Prompt更重要[8]。

**三大支柱**：
- **RAG ≠ 万能**：企业知识问答用向量检索有效，但代码调试用grep/git log更精准
- **工具即感官**：接入Bash、文件系统、LSP，让AI像开发者一样操作环境
- **记忆外置化**：用CLAUDE.md等持久化文件存储长期记忆

**仍存缺口**：工具权限失控、缺乏验证闭环、无过程追溯。

#### 2.2.3 Harness Engineering（2026-）

3.0阶段的本质是**系统设计**——把AI放进一个可运行、可纠错、可追溯的工程闭环[9]。

用比喻来说明三层关系：
- Prompt Engineering是"向右转"的口令
- Context Engineering是地图、路标和可见地形
- **Harness Engineering是缰绳、马鞍、围栏和道路本身**——确保马能安全奔跑的整套基础设施

---

## 三、技术架构：Harness的核心组件

### 3.1 Agent Harness的定义

Agent Harness是包裹在AI模型外围的所有非模型代码：提示、工具、中间件、状态管理、反馈回路的总和[10]。

用计算机系统的经典类比来理解[11]：

| 层级 | 类比 | 说明 |
|------|------|------|
| Model | CPU | 提供原始算力 |
| Context Window | RAM | 有限的工作记忆 |
| Agent Harness | 操作系统 | 管理上下文、处理启动流程、提供标准驱动 |
| Agent | 应用程序 | 运行在操作系统上的具体逻辑 |

### 3.2 五大核心模块

一个完整的Harness由五个核心模块构成[12]：

#### 3.2.1 Tools（工具）—— 给模型"双手"

```
原子化工具设计原则：
├── 文件读写 (Read/Write/Grep)
├── Shell执行 (Bash)
├── 网络请求 (HTTP API)
├── 数据库操作
└── 自定义业务逻辑

每个工具必须：
- 原子化：单一职责
- 可组合：能与其他工具协同
- 可描述：有清晰的工具定义（schema）
```

#### 3.2.2 Knowledge（知识）—— 给模型"领域经验"

```
知识管理策略：
├── 产品文档
├── API规范
├── 架构设计决策记录
├── 代码风格指南
└── 按需加载而非一次性塞给模型
```

#### 3.2.3 Observation（观察）—— 给模型"眼睛"

```
可观测性建设：
├── Git变更追踪
├── 错误日志实时感知
├── 浏览器状态监控
├── 环境信息暴露
└── 执行轨迹记录
```

#### 3.2.4 Action Interfaces（执行接口）—— 给模型"行动通道"

```
统一动作输出格式：
├── CLI命令规范
├── API调用标准
├── UI交互协议
└── 权限边界定义
```

#### 3.2.5 Permissions（权限体系）—— 给模型"边界"

```
安全防护机制：
├── 沙箱隔离（文件系统、网络、权限）
├── 危险操作拦截
├── 人工审批流程
└── 资源使用限制
```

### 3.3 四大核心动作

OpenAI将Harness抽象为四个闭环动作[13]：

```
┌─────────────────────────────────────────────────────────────┐
│                     Harness 四大核心动作                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │   CONSTRAIN   │    │    INFORM    │                      │
│  │    (约束)     │───▶│    (告知)    │                      │
│  └──────┬───────┘    └──────┬───────┘                      │
│         │                   │                              │
│         ▼                   ▼                              │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │    VERIFY    │◀───│   CORRECT    │                      │
│  │   (验证)      │    │    (纠正)     │                      │
│  └──────┬───────┘    └──────┬───────┘                      │
│         │                   │                              │
│         └───────────────────┘                              │
│              反馈循环                                       │
└─────────────────────────────────────────────────────────────┘
```

#### 3.3.1 Constrain（约束）

给Agent设定硬边界：
- 架构规则：分层依赖约束
- 权限隔离：禁止危险操作
- 沙箱环境：物理隔离执行

#### 3.3.2 Inform（告知）

提供精确、机器可读的上下文：
- AGENTS.md：项目入口指南
- 架构地图：docs/目录结构
- API合约：接口规范文档

**关键原则**：只给"目录索引"，不给全文，防止注意力稀释。

#### 3.3.3 Verify（验证）

自动质检三层验证：
- **格式层**：Lint规则、格式校验
- **执行层**：单元测试、集成测试
- **质量层**：结果评审、人工审核

#### 3.3.4 Correct（纠正）

反馈闭环机制：
- 错误即修复指南：Lint错误信息直接包含修复方法
- 自动回滚：异常时恢复到稳定状态
- 人工介入兜底：关键节点人工审批

---

## 四、关键技术实践

### 4.1 AGENTS.md：Agent的"新员工手册"

AGENTS.md是Harness工程中最关键的文档实践，它解决了三个关键问题[14]：

1. **规范可视化**：将散落在README、Wiki、口头约定的规则集中管理
2. **约束可执行**：Codex/Claude会主动遵守文件中定义的边界条件
3. **知识可继承**：新成员通过AGENTS.md快速掌握项目约定

**OpenAI的核心教训**：

团队最初尝试把所有规范、约定、历史决策都塞进一个巨大的AGENTS.md文件，结果失败了[1]：

| 失败原因 | 说明 |
|----------|------|
| Context资源竞争 | 臃肿的指令文件挤掉任务和代码的空间 |
| 规则过载失效 | 当所有内容都被标注为"重要"，反而没有重点 |
| 文档快速腐烂 | 旧的规则会失效，没人及时更新 |

**正确的做法**：

AGENTS.md只做100行导航索引，真正的知识在docs/目录中分层存储：

```markdown
# AGENTS.md - 项目导航索引

## 架构规范
- 分层架构: docs/architecture/layers.md
- 命名约定: docs/architecture/naming.md

## 代码规范
- TypeScript风格: docs/coding/typescript-style.md
- 测试要求: docs/coding/test-standards.md

## 开发流程
- PR流程: docs/process/pull-request.md
- 发布流程: docs/process/release.md

## 工具链
- 构建命令: docs/tools/build-commands.md
- 环境配置: docs/tools/env-setup.md
```

### 4.2 三Agent架构：Generator-Evaluator分离

Anthropic从深度学习的GAN（生成对抗网络）中借鉴了一个核心洞见[15]：

> **将做工作的智能体与评判工作的智能体分离，是一个强有力的杠杆。**

让评估者变得更怀疑，远比让生成者变得更加自我批判要容易得多。

```
┌────────────────────────────────────────────────────────────┐
│                    三Agent系统架构                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│     ┌─────────────┐         ┌─────────────┐                │
│     │  Generator  │────────▶│  Evaluator  │                │
│     │   (生成者)   │         │   (评估者)   │                │
│     └──────┬──────┘         └──────┬──────┘                │
│            │                      │                        │
│            │   反馈循环           │                        │
│            │◀─────────────────────┘                        │
│            │                                               │
│            ▼                                               │
│     ┌─────────────┐                                        │
│     │   Reporter  │                                        │
│     │   (报告者)   │                                        │
│     └─────────────┘                                        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**实践验证**：Anthropic发现planner和evaluator的设计比prompt的措辞对产出质量影响更大[16]。

### 4.3 Lint规则即修复指令

OpenAI的自定义Lint不仅标记违规，还在错误消息中直接包含修复方法[1]：

```python
# 自定义Lint规则示例
class ArchitectureLayerLinter:
    """
    架构分层约束：
    - Domain层禁止直接调用数据库
    - Service层禁止直接操作UI
    - 违规代码直接拒收
    """

    def check_violation(self, code_block, context):
        if self.is_domain_layer(context):
            if self.has_db_call(code_block):
                return LintError(
                    message="Domain层不能直接调用数据库",
                    # 错误消息直接包含修复指引
                    fix_hint="请通过Repository接口访问数据",
                    suggested_pattern="self.repository.find_by_id(id)"
                )
```

**效果**：Agent在遇到违规时同时获得了"教学"，不需要再去查找文档。

### 4.4 记忆治理与状态持久化

#### 4.4.1 记忆的三大层次

| 层次 | 存储位置 | 生命周期 | 作用 |
|------|----------|----------|------|
| **工作记忆** | Context Window | 单次调用 | 当前任务上下文 |
| **短期记忆** | 对话历史 | 会话级 | 跨工具调用 |
| **长期记忆** | 文件系统/Git | 持久化 | 项目级知识 |

#### 4.4.2 持久化原则

核心原则：**进度持久化在文件系统上，而非上下文窗口中**[17]。

```markdown
# 进度文件机制
每次Context重置后，Agent通过以下文件恢复状态：

1. harness-progress.txt - 当前任务进度
2. harness-tasks.json - 任务清单状态
3. git log - 版本历史决策
4. docs/design/*.md - 架构决策记录

读取顺序：10秒内恢复完整会话上下文
```

#### 4.4.3 记忆治理策略

Anthropic提出的"进化引擎"概念[18]：

```
未验证的知识 ──▶ 不能进入共享库
     │
     ▼
单点幻觉 ──▶ 不能污染全系统
     │
     ▼
信号 ──▶ 验证后 ──▶ 基因（可复用的经验）
```

**关键数据**：3行Prompt加上记忆系统，效果可媲美200行精心编写的专家Prompt。

### 4.5 可观测性体系

OpenAI通过Chrome DevTools给Agent装上"眼睛"[1]：

```javascript
// Agent视觉验证系统
class AgentVisionSystem {
    async verifyUI() {
        // 1. Agent生成UI代码
        const changes = await agent.writeCode(spec);

        // 2. 自动截图
        const screenshot = await devtools.captureScreenshot();

        // 3. AI视觉分析
        const analysis = await vision.analyze(screenshot, spec);

        // 4. 发现问题自动修复
        if (analysis.hasMismatch()) {
            await agent.selfCorrect(analysis.differences);
        }
    }
}
```

**反馈闭环**：Agent写完代码 → 运行测试 → 看截图 → 发现问题 → 自己修复

---

## 五、实战案例：OpenAI Codex项目深度解析

### 5.1 项目背景

2025年8月，OpenAI内部一个三人小组承接了一个新产品开发任务[1]：

- **团队规模**：3人（后扩展到7人）
- **约束条件**：所有代码必须由Codex AI Agent生成，人类工程师不动键盘写代码
- **时间跨度**：5个月
- **最终成果**：
  - 代码库约**100万行**
  - 合并约**1500个Pull Request**
  - 人均日处理**3.5个PR**
  - 整体效率提升约**10倍**

### 5.2 核心技术实践

#### 5.2.1 AGENTS.md的演进

初始方案失败后，团队重构了AGENTS.md策略：

```markdown
# ❌ 初始方案（失败）
- 500+行的巨型AGENTS.md
- 包含所有规范、约定、历史决策
- 结果：Agent无法分辨优先级，规则快速腐烂

# ✅ 改进方案（成功）
- 100行的导航索引
- 真正的知识在docs/目录下
- 类似代码库的README，但服务对象是Agent
```

#### 5.2.2 架构约束机制

```yaml
# 分层架构约束配置
architecture:
  layers:
    - name: Domain      # 领域层：核心业务逻辑
      can_call: [Domain, SharedKernel]
      forbidden: [Database, ExternalAPI, UI]
    - name: Application  # 应用层：用例编排
      can_call: [Domain, Infrastructure]
    - name: Infrastructure # 基础设施层：技术实现
      can_call: [Database, ExternalAPI]

lint_rules:
  - id: no-cross-layer-violation
    error_message: "违反分层架构约束"
    auto_fix: false  # 人工review
```

#### 5.2.3 反馈回路设计

```
                    ┌─────────────────┐
                    │  用户需求/任务    │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │   Codex Agent   │
                    │   (生成代码)     │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │   自动测试/CI   │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │   结果验证      │
                    └────────┬────────┘
                             ▼
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
      ┌───────────────┐           ┌───────────────┐
      │   通过验证     │           │   失败/需要修复 │
      └───────┬───────┘           └───────┬───────┘
              │                           │
              ▼                           ▼
      ┌───────────────┐           ┌─────────────────┐
      │  合并PR/交付   │           │  自动修复 + 重试 │
      └───────────────┘           └────────┬────────┘
                                           │
                                           └────────────────┘
```

### 5.3 "无聊技术栈"策略

团队刻意选择"无聊"（well-established）的技术栈[1]：

**原因**：训练数据里出现越多的库和框架，Codex对它的理解就越准确，出错率越低。

```python
# ✅ 选择：成熟的、训练数据丰富的
tech_stack = {
    "language": "TypeScript",      # 训练数据丰富
    "framework": "React",          # 生态完善
    "orm": "Prisma",               # 类型安全
    "testing": "Jest + Playwright", # 标准工具链
}

# ❌ 避免：过于新颖的
avoid_stack = {
    "language": "RUST",            # 可能过于底层
    "framework": "Experimental",   # 缺乏训练数据
}
```

### 5.4 "垃圾回收"机制

后台周期性运行一个Agent，扫描代码库里的技术债[1]：

```python
class TechDebtCollector:
    """
    定期扫描和清理：
    1. 未使用的导入
    2. 重复代码片段
    3. 过时的注释
    4. 废弃的API调用
    5. 架构违规
    """

    def run_periodically(self, interval_hours=24):
        # 扫描任务
        issues = self.scan_tech_debt()

        # 分类处理
        auto_fixable = [i for i in issues if i.auto_fixable]
        manual_review = [i for i in issues if not i.auto_fixable]

        # 自动修复简单问题
        for issue in auto_fixable:
            self.auto_fix(issue)

        # 提交需要人工review的问题
        for issue in manual_review:
            self.create_review_task(issue)
```

---

## 六、评估体系：Evaluation Harness

### 6.1 评估驱动开发

Anthropic提倡的核心理念：**Agent不能自我评价，需由独立评估器基于明确标准打分**[15]。

```
┌────────────────────────────────────────────────────────────┐
│                    评估闭环流程                             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. 定义评估标准 (Eval Definition)                         │
│     └── 明确"什么是对的"                                   │
│                                                            │
│  2. 独立评估器 (Independent Evaluator)                     │
│     └── 不依赖Agent自评                                    │
│                                                            │
│  3. 自动化执行 (Automated Execution)                      │
│     └── Playwright等工具实际操作产品                       │
│                                                            │
│  4. 反馈改进 (Feedback Loop)                              │
│     └── 发现问题 → 改进Harness → 再次评估                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 6.2 评估标准的设计

```python
# 评估用例设计原则
class EvaluationCriteria:
    """
    好的评估标准应具备：
    1. 可自动化执行
    2. 结果无歧义（通过/失败）
    3. 覆盖核心功能路径
    4. 包含边界情况和错误处理
    """

    examples = [
        "代码能通过所有单元测试",
        "lint检查无警告",
        "类型检查通过",
        "UI渲染符合设计规范",
        "API响应时间 < 200ms"
    ]
```

### 6.3 评估Bug的发现与修复

Anthropic的一个关键发现[15]：

> 修复评估本身的bug后，模型得分从**42%提升至95%**。

这说明评估标准的设计与验证本身也需要工程化。

---

## 七、与DevOps CI/CD的融合

### 7.1 Harness在CI/CD中的定位

Harness Engineering与传统的DevOps实践有天然的融合点[19]：

| DevOps实践 | Harness对应 |
|------------|-------------|
| CI Pipeline | 自动化验证管道 |
| Code Review | Evaluator Agent评审 |
| Feature Flags | Agent行为约束 |
| Rollback | 状态恢复机制 |
| Monitoring | 可观测性体系 |

### 7.2 自动化验证管道

```yaml
# Agent提交代码后的自动化验证
agent_pr_pipeline:
  stages:
    - name: lint_and_format
      tools: [eslint, prettier, custom_arch_linter]
      fail_on_error: true

    - name: type_check
      tools: [typescript_check, mypy]
      fail_on_error: true

    - name: unit_tests
      coverage_threshold: 80%

    - name: integration_tests
      tools: [playwright, api_tests]

    - name: security_scan
      tools: [snyk, bandit]

    - name: architecture_validation
      tools: [dependency_check, layer_linter]

  gate:
    all_stages_pass: true
    human_review_required: true
```

---

## 八、技术挑战与应对

### 8.1 主要挑战

#### 8.1.1 熵增问题

AI代码以10倍速度累积技术债[20]：

```
挑战：随着时间推移，系统越来越难回答基本问题
- 谁在推进状态？
- 谁在发布边界？
- 谁在定义当前真值？

表现：
- helper、adapter、fallback逻辑无序增长
- 状态歧义升级为ownership问题
- 层次界限（authority、contract、handoff）模糊
```

#### 8.1.2 上下文窗口限制

复杂项目无法在单个会话内完成，Agent像"失忆"了一样[4]：

```
症状：
- 第50轮对话的选择与第5轮的决策矛盾
- 早期确定的架构规范被遗忘
- 代码风格一致性显著下降
```

#### 8.1.3 安全风险

当Agent获得高授权后，风险急剧放大[21]：

```
事件记录：
- 恶意skill渗透：341个恶意skill占注册表12%
- 数据泄露：35,000个邮件地址 + 150万API tokens
- 高危漏洞：CVE-2026-25253，毫秒级攻击链
```

### 8.2 应对策略

#### 8.2.1 七大支柱体系

| 支柱 | 核心策略 |
|------|----------|
| **仓库即唯一事实源** | 所有知识必须版本化、可发现、存在于repo中 |
| **AGENTS.md导航化** | 地图而非手册，索引而非百科 |
| **Lint规则即指令** | 错误信息直接包含修复指引 |
| **评估独立化** | Generator与Evaluator角色分离 |
| **记忆持久化** | 进度存储在文件系统，非Context Window |
| **熵治理** | 周期性技术债扫描和清理 |
| **安全边界** | 沙箱隔离 + 权限分层 |

#### 8.2.2 解析优于校验原则

OpenAI借鉴了19年的技术博客"Parse, don't validate"[22]：

```python
# ❌ 校验模式（不稳健）
def validate_and_process(data):
    # 先接收混沌数据
    # 用时校验
    # 问题：校验逻辑容易遗漏，且不能传递到下一层
    if validate(data):
        process(data)

# ✅ 解析模式（推荐）
def parse_and_process(data: TypedData):
    # 在系统边界定义清晰的数据类型
    # 让数据"准备好被使用"
    # 问题在前端解决，而非层层传递
    validated = parse_to_typed(data)
    process(validated)
```

---

## 九、实践建议：从0到1构建Harness

### 9.1 五步起步法

#### 第一步：创建AGENTS.md

```markdown
# 项目根目录/AGENTS.md

# [项目名称] Agent指南

## 快速开始
- 环境设置：docs/setup.md
- 构建命令：docs/build.md

## 架构规范
- 分层架构：docs/arch/layers.md
- 命名规范：docs/arch/naming.md

## 代码标准
- 风格指南：docs/code/style.md
- 测试要求：docs/code/tests.md

## 约束规则
- 禁止删除：/legacy目录
- 禁止修改：/config/prod.yaml
- 必须review：涉及数据库schema的变更

## 工具链
- 测试：npm test
- Lint：npm run lint
- 构建：npm run build
```

#### 第二步：配置Lint规则

```javascript
// .eslintrc.agents.js
module.exports = {
  rules: {
    // 自定义架构约束
    'no-cross-layer-db': {
      // Domain层禁止直接调用数据库
      create(context) {
        return {
          CallExpression(node) {
            if (isInDomainLayer(context) && isDBOperation(node)) {
              context.report({
                node,
                message: 'Domain层禁止直接调用数据库。使用Repository接口。',
                fix: '通过注入的Repository访问数据'
              });
            }
          }
        };
      }
    }
  }
};
```

#### 第三步：建立评估管道

```python
# eval_pipeline.py
class AgentEvaluationPipeline:
    def evaluate(self, agent_output):
        results = {
            "format": self.check_format(agent_output),
            "syntax": self.check_syntax(agent_output),
            "tests": self.run_tests(agent_output),
            "lint": self.run_lint(agent_output),
            "arch": self.check_architecture(agent_output)
        }

        score = sum(results.values()) / len(results)
        return EvaluationResult(score=score, details=results)
```

#### 第四步：实现记忆持久化

```python
# memory_manager.py
class AgentMemoryManager:
    def save_checkpoint(self, state, task_id):
        checkpoint = {
            "task_id": task_id,
            "timestamp": datetime.now(),
            "context": self.extract_context(state),
            "progress": state.progress,
            "decisions": state.key_decisions
        }

        # 持久化到文件系统
        path = f".agent-memory/{task_id}/checkpoint.json"
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def restore(self, task_id):
        path = f".agent-memory/{task_id}/checkpoint.json"
        if Path(path).exists():
            with open(path) as f:
                return json.load(f)
        return None
```

#### 第五步：配置安全边界

```yaml
# harness_config.yaml
permissions:
  file_system:
    read: ["src/**", "docs/**", "tests/**"]
    write: ["src/**", "tests/**"]
    delete: false  # 禁止删除

  network:
    allowed_hosts: ["api.example.com"]
    blocked_paths: ["/admin", "/internal"]

  shell:
    max_duration_seconds: 300
    allowed_commands: ["npm", "git", "pytest", "docker"]
    blocked_commands: ["rm -rf /", "curl | sh"]

  escalation:
    dangerous_ops_require_approval: true
    approval_roles: ["senior_engineer", "tech_lead"]
```

### 9.2 常见误区

| 误区 | 真相 |
|------|------|
| "模型够强了，Harness不重要" | 同一模型，Harness差→12%成功率；Harness好→76%成功率[23] |
| "Harness就是写好Prompt" | Harness包含工具、验证、记忆、安全等完整系统 |
| "AGENTS.md越大越好" | 应做导航索引，不做百科全书 |
| "Harness建好就不用维护" | Harness需要持续迭代，适应项目演化 |
| "Agent能自我评估" | Generator和Evaluator必须分离 |

---

## 十、未来展望

### 10.1 演进方向

1. **标准化**：Harness规范和最佳实践将形成行业标准
2. **自动化**：从手动配置到自动发现和生成Harness
3. **智能化**：AI辅助的Harness优化和建议
4. **安全化**：内置安全扫描和合规检查

### 10.2 技术融合趋势

```
Harness Engineering
        │
        ├── DevOps ──▶ 持续验证管道
        │
        ├── MLOps ──▶ 模型生命周期管理
        │
        ├── FinOps ──▶ AI成本优化
        │
        └── SecOps ──▶ AI安全治理
```

### 10.3 工程师角色转变

| 传统角色 | 新角色 |
|----------|--------|
| 代码编写者 | Agent环境设计师 |
| PR Reviewer | Harness系统架构师 |
| 手动测试者 | 评估体系构建者 |
| 运维工程师 | AI工作流编排者 |

---

## 结论

Harness Engineering代表了AI软件工程的一次根本性范式转变：**从"优化模型"到"设计环境"**。

其核心价值在于：

1. **突破模型天花板**：同样的模型，优化Harness可带来显著的性能提升
2. **实现规模化部署**：通过约束、验证、反馈闭环，让AI Agent稳定运行
3. **重新定义工程师角色**：从"写代码"到"设计让AI能可靠工作的环境"

正如OpenAI工程师Ryan Lopopolo所言[1]：

> **"Agents aren't hard; the Harness is hard."**
> （Agent不难，难的是Harness。）

这是一场静悄悄的软件工程革命，它正在重新定义我们构建AI系统的方式。

---

## 参考文献

[1] OpenAI. "Harness Engineering: Leveraging Codex in an Agent-First World." OpenAI Blog, February 2026. https://openai.com/index/harness-engineering/

[2] LangChain. "Terminal Bench 2.0 Evaluation Results." LangChain Research, March 2026.

[3] Deloitte. "Enterprise AI Adoption Report 2026." Deloitte Insights, 2026.

[4] 腾讯新闻. "深度解析Harness Engineering." 腾讯新闻科技, April 2026. https://news.qq.com/rain/a/20260403A06K3U00

[5] Hashimoto, M. "Harness Engineering Principles." Mitchell Hashimoto Blog, December 2025.

[6] CSDN. "Harness Engineering深度解析:AI Agent时代的工程范式革命." 2026. https://blog.csdn.net/qhvssonic/article/details/159475751

[7] 什么值得买. "AI工程范式三次跃迁:从Prompt到Context,再到Harness." 2026. https://post.smzdm.com/p/aqr37rxv

[8] Karpathy, A. "Context Engineering vs Prompt Engineering." State of AI, 2025.

[9] 知乎. "Harness工程:Agent终于有了自己的工程学." 2026. https://zhuanlan.zhihu.com/p/2015142041282163260

[10] 稀土掘金. "所有人都在说Harness Engineering,所以它到底是啥?" 2026. https://aicoding.juejin.cn/post/7621066583953031202

[11] 知乎. "Harness Engineering:2026年最值得程序员搞懂的新词." 2026. https://www.163.com/dy/article/KPIBUDPE0531O21B.html

[12] 百家号. "硅谷流行的Harness Engineering是什么?" 2026. https://baijiahao.baidu.com/s?id=1861043534597326326

[13] 知乎. "Harness工程,为AI烈马套上缰绳." 2026. https://zhuanlan.zhihu.com/p/2020772553333941162

[14] CSDN. "Codex驯服手册:用AGENTS.md实现精准代码生成." 2026. https://blog.csdn.net/weixin_29304985/article/details/159186296

[15] 知乎. "Harness Engineering:AI时代的新基础设施." 2026. https://zhuanlan.zhihu.com/p/2022008610239070273

[16] CloudTencent. "Harness Engineering最佳实践." 2026. https://cloud.tencent.com/developer/article/2647567

[17] CSDN. "harness engineering学习笔记." 2026. https://blog.csdn.net/qqqahhh/article/details/159648180

[18] 什么值得买. "Harness Engineering:构建Agent持续稳定运行的操作系统." 2026. https://post.smzdm.com/p/a26w09vq/

[19] CSDN. "Harness CI/CD平台深度解析." 2026. https://blog.csdn.net/m0_50709695/article/details/159773586

[20] 腾讯网. "万字长文:从Vibe Coding到Harness Engineering的实践与思考." 2026. https://news.qq.com/rain/a/20260405A02UN000

[21] 腾讯新闻. "OpenClaw之后,聊聊多智能体系统Harness Engineering架构设计思考." 2026. https://new.qq.com/rain/a/20260322A0563L00

[22] 知乎. "AI 写了 100 万行代码,靠的不是更聪明——Harness Engineering 是什么?" 2026. https://zhuanlan.zhihu.com/p/2022368702125876986

[23] CloudTencent. "OpenAI的Agent神器揭秘." 2026. https://blog.csdn.net/2301_80239908/article/details/159514636

---

*本报告基于2026年4月7日前的公开技术资料综合整理，力求准确反映Harness Engineering的核心概念与技术实践。*
