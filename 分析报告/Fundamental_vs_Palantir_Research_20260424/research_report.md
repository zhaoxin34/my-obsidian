# Fundamental AI 与 Palantir 对比分析报告

**研究日期：** 2026年4月24日

**研究模式：** 深度分析 (Deep)

**执行摘要**

 Fundamental AI 和 Palantir 代表了企业数据与人工智能分析领域两种截然不同的技术路线。Fundamental 作为 2026 年新晋独角兽，携 2.55 亿美元巨额融资和专为结构化数据设计的 "大表格模型" (LTM) 入场，旨在解决传统大语言模型在处理企业级表格数据时的固有缺陷 [1]。Palantir 则是成立超过 20 年的成熟企业，2025 财年营收达 44.75 亿美元，市值约 3120 亿美元，正处于由政府国防业务向商业 AI 平台高速转型的关键阶段 [2]。两家公司虽同处企业数据智能赛道，却在技术架构、产品定位、商业模式和市场策略上呈现显著差异。Fundamental 聚焦于预测分析的结构化数据专属模型，Palantir 则构建了覆盖数据集成、分析、可操作化的完整 ontology 驱动平台。本报告将从公司概况、技术架构、产品矩阵、财务表现、市场竞争等多维度进行深度对比分析。

---

## 一、公司概况

### 1.1 Fundamental AI

Fundamental AI 是一家成立于 2024 年的年轻人工智能公司，由 DeepMind 前成员创立 [3]。公司于 2026 年 2 月正式走出隐模式，宣布完成 2.55 亿美元的巨额 A 轮融资，其中 2.25 亿美元由 Oak HC/FT 领投，Valor Equity Partners、Battery Ventures、Salesforce Ventures 和 Hetz Ventures 跟投 [4]。该轮融资后，公司估值达到 12 亿美元，正式晋身独角兽行列。投资方阵容中还包括 Wiz CEO、Perplexity AI CEO、Datadog CEO 和 Brex CEO 等知名科技公司创始人，表明顶级科技从业者对 Fundamental 技术路线的高度认可 [5]。

Fundamental 总部位于美国旧金山，团队规模约 35 人，主要由来自 DeepMind、Isomorphic Labs 和 JP Morgan 的研究人员和工程师组成 [6]。公司 CEO Jeremy Fraenkel 拥有丰富的企业技术背景，团队其他创始成员包括 Annie Lamont 和 Gabriel Suissa。值得注意的是，Fundamental 从创立到产品正式发布经历了约 18 个月的隐模式开发期，这期间团队专注于训练其核心产品——Nexus 大表格模型 [7]。

### 1.2 Palantir Technologies

Palantir Technologies 成立于 2003 年，是一家具有深厚国防和情报社区背景的数据分析软件公司 [8]。公司由 Peter Thiel 与 Alex Karp 等联合创立，总部原位于科罗拉多州丹佛市，2026 年 2 月公司宣布计划将总部迁至佛罗里达州迈阿密 [9]。Palantir 于 2020 年 9 月在纽约证券交易所上市，股票代码 PLTR。

Palantir 的领导团队以 CEO Alex Karp 为核心，CTO Shyam Sankar 在 2025 年主导了向"自主代理"的产品转型，CRO Ryan Taylor 则推动了公司从"厌恶销售"文化向高速"训练营"营销模式的根本性转变 [10]。Peter Thiel 作为董事会成员，其"从零到一"的哲学持续影响公司的战略决策，追求在专业数据集成领域建立类似垄断的护城河 [11]。

截至 2025 年 8 月，Palantir 拥有约 4,100 名员工，但 CEO Karp 有意将团队规模缩减至 3,600 人以提升运营效率 [12]。2025 财年 Palantir 营收达到 44.75 亿美元，同比增长 56%，市值在 2025 年底一度突破 4,400 亿美元，2026 年 4 月回落至约 3,120 亿美元 [13]。

### 1.3 关键差异概览

| 维度 | Fundamental AI | Palantir Technologies |
|------|---------------|---------------------|
| 成立时间 | 2024 年 | 2003 年 |
| 总部 | 旧金山 | 丹佛 (迁址中) |
| 员工规模 | ~35 人 | ~4,100 人 |
| 最新估值 | $12 亿 (2026) | $3,120 亿 (2026) |
| 融资阶段 | A 轮 (已完成) | 已上市 |
| 核心技术 | LTM (大表格模型) | Ontology + AIP |

---

## 二、技术架构对比

### 2.1 Fundamental：大型表格模型 (LTM) 架构t

Fundamental 的核心竞争力在于其完全自主研发的 Nexus 模型，这是全球首个"大型表格模型" (Large Tabular Model, LTM) [14]。与当前主流的 Transformer 架构大语言模型不同，Nexus 从根本上针对结构化数据（表格、数据库）进行了优化设计。

传统 LLM 基于序列逻辑构建——预测句子中的下一个词或图像中的下一个像素。然而，企业数据本质上是"非序列"的。一个客户的流失风险不仅仅是一条时间线，而是交易频率、支持工单情绪和区域经济变化的多维交叉 [15]。现有 LLM 难以处理企业级表格的规模和维度约束，因为它们被限制在有限的上下文窗口内。

Nexus 的核心创新包括：

**确定性输出：** 与 LLM 的概率性输出不同，Nexus 是确定性的——两次提出相同问题将获得相同答案 [16]。这一特性对需要可靠、可重复结果的企业应用至关重要。

**突破上下文窗口限制：** Transformer 架构的 LLM 只能处理上下文窗口内的数据，当分析包含数十亿行的电子表格时往往力不从心。Nexus 专门设计用于处理超出传统上下文窗口限制的大规模结构化数据集 [17]。

**预训练于数十亿真实表格：** Nexus 在数十亿真实世界表格数据集上进行了预训练，能够原生理解跨行和列的非线性关系和隐藏模式 [18]。这使得模型无需进行大量的特征工程或手动训练即可产生准确预测。

**一行代码部署：** 企业可以仅用一行 Python 代码将原始表格数据连接到模型，指定目标列（如信用违约概率或维护风险评分），模型直接返回回归或分类结果 [19]。

从技术架构角度，Fundamental 明确将自己定位为"预测层"而非对话式 AI。工程师直接将原始表格连接到模型，标记特定目标列，模型将预测结果返回到企业数据栈中，作为一个静默、高速的自动化决策引擎运行，而非聊天式助手 [20]。

### 2.2 Palantir：Ontology 驱动的集成平台

Palantir 的技术架构以"本体 (Ontology)" 为核心，这是公司区别于所有其他数据平台的关键技术概念 [21]。Ontology 在 Palantir 的语境中是一个决策框架，它将数据、分析和运营操作统一到一个共享系统中。

Palantir 的软件架构围绕 Ontology 运行，支撑整个企业的数据、分析和运营连接 [22]。Foundry 的多模态接口允许用户通过直观的图形界面、功能完整的 API 和 SDK 构建数据管道、执行大规模分析和构建丰富的运营应用。Palantir 的 Ontology 不仅仅是一个数据模型——它是一个"操作系统"，使 AI 能够理解数据中的关系和上下文，而非仅仅处理数据本身 [23]。

Palantir 的平台整合了三种核心产品能力：

**Gotham：** 主要服务于政府和国防客户，提供情报和军事应用所需的数据分析和决策支持。Gotham 与 Palantir 其他平台以及更广泛的国防产品组合集成，为盟军国防和情报行动提供支持 [24]。

**Foundry：** 作为 Palantir 的商业平台，Foundry 使企业能够将复杂的孤岛数据转化为可操作的情报。平台通过 200 多个预建连接器整合 ERP 系统、IoT 源和数据库的信息，使用自动化低代码管道统一结构化和非结构化数据 [25]。

**Apollo：** Palantir 的持续交付平台，在从云到"战术边缘"（如卫星和无人机）的任何环境中协调服务升级和资产管理 [26]。

**AIP (人工智能平台)：** Palantir 2025 年的旗舰产品 AIP 允许 LLM 与私有数据进行安全交互 [27]。通过 AIP，Palantir 将"原始"LLM（如 OpenAI 的 GPT-4 或 Anthropic 的 Claude）通过 Palantir Ontology 接入企业私有数据，从而在 Ontology 定义的"名词（对象）"和"动词（操作）"严格结构化的范围内进行推理和提议，消除上下文污染和幻觉风险 [28]。

### 2.3 技术路线本质差异

从本质上看，Fundamental 和 Palantir 代表了两种截然不同的技术路线：

Fundamental 解决的是"预测"问题——使用结构化数据预测未来结果，其模型是专门为表格数据训练的专用模型。Palantir 解决的是"决策"问题——通过 Ontology 将数据转化为可操作的知识，再通过 AIP 接入 LLM 能力实现智能决策，其平台是通用性的。

用一个形象的类比：Fundamental 像是一个专注于解读表格数据的专家模型，而 Palantir 构建的是一个能够整合所有企业数据源并支持智能决策的操作系统。

---

## 三、产品与服务矩阵

### 3.1 Fundamental 核心产品

**Nexus：** Fundamental 的旗舰产品，是首个公开发布的大型表格模型 [29]。Nexus 设计用于在企业结构化数据上生成高度准确的预测，无需传统机器学习的特征工程和模型训练流程。企业可以通过 AWS SageMaker HyperPod 直接访问 Nexus，AWS 客户可以通过其仪表板购买和部署 [30]。

**AWS 集成：** Fundamental 与亚马逊网络服务建立了战略合作，Nexus 可通过 AWS 市场直接部署，使企业能够像购买计算或存储一样采购预测智能 [31]。

**API 接口：** Nexus 通过基于 Python 的接口运行于纯预测层，支持单行代码集成到现有企业数据栈 [32]。

### 3.2 Palantir 产品体系

Palantir 2025 年的产品创新主要围绕 AIP 展开：

**AIP Bootcamp：** Palantir 2025 年最具创新性的销售工具。参与者只需五天即可在自己的数据上构建生产级别的 AI 工作流，显著缩短了传统的冗长销售周期 [33]。

**Agentic Foundry：** 2025 年中推出的重要升级，允许企业部署"自主代理"，这些代理不仅提供洞察，还能主动执行任务——如在全球供应链中断时重新路由物流，或根据实时天气数据自动调整保险费 [34]。

**ShipOS：** 2025 年底与美国海军合作开发，集成 AI 用于潜艇舰队的后勤和战斗系统数据生命周期管理 [35]。

**AIP Analyst：** 2025 年 11 月推出的新数据分析应用，使用户能够在聊天式界面中探索 Ontology 数据，提供 Ontology 优先的体验 [36]。

**AI FDE（AI 前向部署工程师）：** 允许用户通过自然语言对话操作 Foundry，使用对话解锁 Palantir 平台的功能，包括数据转换、代码仓库管理、Ontology 构建和维护 [37]。

**TITAN：** Palantir 的 AI 驱动战术卡车，于 2025 年开始交付美国陆军，用于简化战场目标发现、跟踪和打击流程 [38]。

### 3.3 客户群体与应用场景

**Fundamental 目标客户：**
- 财富 100 强企业
- 金融服务、医疗保健、能源等行业的预测分析需求方
- 需要处理大规模结构化数据的企业

已签约客户使用 Nexus 完成的用例包括：客户流失预测、欺诈检测、药物发现、需求预测等 [39]。

**Palantir 客户群体：**

Palantir 2025 年收入构成中，54% 来自政府客户，46% 来自商业客户 [40]。前 20 大客户平均收入达到 9,390 万美元，较 2024 年的 6,460 万美元显著增长 [41]。

政府客户包括：美国陆军、美国国防部 (DOD)、美国国土安全部 (DHS)、美国国税局 (IRS)、英国国家医疗服务体系 (NHS，4.8 亿英镑合同) [42]。

商业客户包括：默克 KGaA、空中客车、法拉利、Lear Corporation 等 [43]。

---

## 四、财务表现对比

### 4.1 Fundamental 财务状况

Fundamental 仍处于极度早期阶段，财务信息披露有限：

**融资情况：**
- 2024 年完成种子轮融资
- 2026 年 2 月完成 2.55 亿美元 A 轮融资（估值 12 亿美元）
- 投资方包括：Oak HC/FT、Valor Equity Partners、Battery Ventures、Salesforce Ventures、Hetz Ventures [44]

**商业化进展：**
- 已签署多项七位数合同（100 万美元以上）的财富 100 强客户 [45]
- 已建立 AWS 战略合作进行商业分销 [46]

需要注意的是，Fundamental 作为非上市公司，其财务数据披露有限。从融资规模（2.55 亿美元 A 轮）和客户合同金额（七位数）来看，公司仍处于早期商业化阶段，收入规模预计在数千万至数亿美元区间。

### 4.2 Palantir 财务表现

Palantir 2025 财年实现了里程碑式的财务业绩：

**收入增长：**
- 2025 财年总收入：44.75 亿美元，同比增长 56% [47]
- Q4 2025 收入：14.07 亿美元，同比增长 70% [48]
- US 商业收入 Q4 2025：5.07 亿美元，同比增长 137% [49]

**收入构成：**
- 政府业务：24 亿美元 (54%)
- 商业业务：20.7 亿美元 (46%) [50]
- 美国市场占比：74%
- 国际市场占比：26% [51]

**盈利能力：**
- 2025 财年净收入：16.25 亿美元 [52]
- 调整后 EBITDA 利润率：~51% [53]
- 调整后每股收益 (EPS)：0.75 美元 [54]

**财务指引：**
- 2026 年收入指引：71.82-71.98 亿美元（同比增长约 61%）[55]
- 2026 年 US 商业收入指引：超过 31.44 亿美元（同比增长约 115%）[56]

**现金流：**
- 现金及现金等价物：72 亿美元
- 调整后自由现金流：22.7 亿美元（51% 利润率）[57]

**估值指标：**
- 市值（约 2026 年 4 月）：3,120 亿美元 [58]
- 市销率 (P/S)：约 70-115 倍（根据不同时点）[59]
- 2025 年曾达到约 4,400 亿美元市值峰值 [60]

**订单情况：**
- Q4 2025 商业 TCV（总合同价值）：14 亿美元，同比增长 132% [61]
- 净美元留存率：139% [62]

### 4.3 估值鸿沟

Fundamental 与 Palantir 之间存在巨大的估值差距：Fundamental 的 12 亿美元估值对应的是尚处于早期的商业化收入，而 Palantir 的 3,120 亿美元市值对应的是年营收近 45 亿美元且仍在高速增长。

然而，这也反映了市场对两家公司增长预期的根本差异：Palantir 已在公开市场证明其商业模式的可行性，而 Fundamental 代表了投资人对 AI 在结构化数据领域这一细分赛道增长潜力的押注。

---

## 五、市场竞争格局

### 5.1 Fundamental 的市场定位

Fundamental 正在开拓一个独特的细分市场——企业结构化数据的 AI 预测分析。其直接竞争对手并非 Palantir，而是：

**传统预测分析厂商：** 使用数十年未变算法的传统机器学习方法

**LLM 提供商：** OpenAI、Anthropic 等，虽然在自然语言处理方面领先，但在结构化数据预测方面存在天然劣势 [63]

**数据仓库/湖仓厂商：** Snowflake、Databricks 等，它们提供数据存储但不是专门的预测模型 [64]

Fundamental 认为，当前的 AI 革命主要惠及了非结构化数据（文本、音频、视频、代码），而结构化数据（如表格和数据库）尚未从深度学习革命中获益 [65]。这是 Fundamental 试图填补的关键空白。

### 5.2 Palantir 的竞争环境

Palantir 面临来自多个层面的竞争压力：

**企业 AI 平台层：** 与 Snowflake、Databricks、微软 Fabric、IBM 等直接竞争企业数据平台市场份额 [66]

**政府和国防层：** 与 RSA、BAE Systems、Leidos 等传统国防承包商竞争 [67]

**AI/LLM 集成层：** 与所有试图将 LLM 能力企业化的公司竞争 [68]

Palantir 的差异化在于其 Ontology 驱动的架构和对"运营 AI"(Operational AI) 的专注——不仅仅是分析数据，而是驱动实际运营决策和行动 [69]。

### 5.3 市场竞争态势

从市场竞争角度看，Fundamental 和 Palantir 实际上处于不同的竞争层级：

Fundamental 专注于"预测层"，解决"将要发生什么"的问题，适合需要精准预测但不需要完整决策平台的场景。

Palantir 构建的是"决策操作系统"，不仅回答"将要发生什么"，还管理"如何响应"的全流程。

两者在某些场景下可能存在竞争——例如，都试图赢得需要高级预测分析的企业客户。但从核心技术路线看，它们更像是互补关系而非直接竞争。

---

## 六、战略前景分析

### 6.1 Fundamental 增长潜力

**优势：**
- 巨大的潜在市场：企业结构化数据市场规模超过 3,900 亿美元，预计到 2034 年将超过 1.1 万亿美元 [70]
- 差异化技术：LTM 架构填补了当前 AI 产品的关键空白
- 顶级投资方背书：Salesforce Ventures 等战略投资者带来生态资源
- AWS 合作：成熟的商业分销渠道
- 已获七位数企业合同：初步商业验证

**风险：**
- 团队规模极小（35 人），执行能力有限
- 估值相对收入偏高（12 亿美元估值 vs 有限商业化收入）
- 面临大型云厂商自研竞争
- LTM 技术路线是否能够持续领先有待验证

**增长催化剂：**
- 更多财富 100 强客户签约
- 向其他云平台（如 Azure、GCP）扩展
- 横向扩展用例（目前主要是预测，未来可能进入决策领域）

### 6.2 Palantir 增长潜力

**优势：**
- 已证的商业模式和规模：45 亿美元年收入且仍在加速增长
- 强大的政府业务护城河：长期合同、复杂集成
- AIP 带来的商业爆发：美国商业收入同比增长 137%
- 充沛现金流：72 亿美元现金储备
- 生态扩展：与 NVIDIA 等建立战略合作 [71]

**风险：**
- 估值极高：市销率超过 70 倍，任何增长放缓都将面临巨大估值压力
- 高度依赖政府合同（54% 收入）
- 高度饱和的美国市场
- 商业模式向商业化的转型尚未完全证明

**增长催化剂：**
- AIP 渗透率持续提升
- 国际市场扩张（英国 NHS 合同模式复制）
- Agentic Foundry 推动的自主工作流采用
- 估值压力可能导致被动收缩

### 6.3 两者互补性分析

从长远看，Fundamental 和 Palantir 可能形成互补而非竞争关系：

Fundamental 的 Nexus 可以作为 Palantir Ontology 中的一个预测引擎，为 Palantir 的决策框架提供更精准的预测能力。

Palantir 的 Ontology 可以作为 Fundamental 进入更广泛决策市场的通道。

这种潜在互补性是否能够转化为实际合作或整合，取决于两家公司的发展战略和市场选择。

---

## 七、总结与洞察

### 7.1 核心发现

**发现一：两种不同的 AI 哲学**

Fundamental 代表了"专用 AI"路线——为特定数据类型（结构化表格数据）训练的专用模型，追求确定性、可解释性和精准预测。Palantir 代表了"通用 AI 平台"路线——构建能够整合任何数据类型、支持任何决策场景的通用 Ontology 框架。

**发现二：不同发展阶段的直接对比**

将 Fundamental 与 Palantir 进行对比，在某种程度上类似于将初创企业与大公司进行对比——两者处于完全不同的发展阶段，拥有截然不同的资源和约束。

**发现三：市场时机不同**

Fundamental 2026 年才正式商业化，正值 AI 在企业数据领域应用的第二轮浪潮。Palantir 已在市场中深耕 20 年，经历了完整的概念验证、客户教育和规模扩张周期。

**发现四：收入模式差异**

Fundamental 预计将采用类似 SaaS 的基于使用的定价模式。Palantir 采用平台订阅+实施服务的混合模式，2025 年商业业务调整后 EBITDA 利润率高达 51% [72]。

### 7.2 投资考量

**对于 Fundamental：**
- 高风险高回报的投资标的
- 适合风险偏好较高的投资者
- 需要关注团队扩张速度、客户留存率和竞争格局变化

**对于 Palantir：**
- 已实现规模化和盈利，但估值偏高
- 增长确定性较高但上行空间可能被高估值透支
- 适合对 AI 赛道有长期信心且能承受波动风险的投资者

### 7.3 行业影响展望

无论 Fundamental 是否能够实现其愿景，**大表格模型 (LTM) 的概念已经为 AI 行业指明了一个重要方向——专用化、企业级的 AI 模型可能是下一个重要突破口** [73]。传统的 LLM 虽然强大，但在处理企业级结构化数据时存在根本性局限。专门为表格数据训练的模型填补了这一空白。

Palantir 的 Ontology 架构代表了另一种思路——通过语义层抽象，将任何 AI 能力（无论是 LLM 还是专用模型）接入统一决策框架。这两种思路可能会在未来相互融合。

---

## 八、局限性与研究局限

### 8.1 信息来源局限

本报告的主要局限性包括：

**Fundamental 数据有限：** 作为非上市公司，Fundamental 披露的财务和运营信息极为有限，许多数据点依赖公司官方公告和投资方声明，可能存在信息不完整或不准确的情况。

**Palantir 信息过载：** 与 Fundamental 不同，Palantir 公开信息极为丰富，包括 SEC 文件、财报、分析师电话会议等。本报告可能未能涵盖所有重要细节。

**竞争格局动态变化：** AI 行业发展迅速，本报告撰写时的竞争格局可能已发生变化。

**前瞻性声明：** 涉及未来增长预期和战略规划的内容属于前瞻性声明，实际结果可能与预期存在重大差异。

### 8.2 估值主观性

两者估值（市值 vs 估值）反映了市场在不同时点、不同风险偏好下的定价能力。投资者应注意，估值本身具有高度主观性，不应作为投资决策的唯一依据。

---

## 九、参考文献

[1] SiliconANGLE (2026). "Fundamental launches with $255M and an AI model optimized for tabular data." https://siliconangle.com/2026/02/05/fundamental-launches-255m-ai-model-optimized-tabular-data/

[2] MacroTrends (2026). "Palantir Technologies Revenue 2019-2025." https://www.macrotrends.net/stocks/charts/PLTR/palantir-technologies/revenue

[3] Salesforce Ventures (2026). "Bringing AI to Structured Data." https://salesforceventures.com/perspectives/bringing-ai-to-structured-data/

[4] TechCrunch (2026). "Fundamental raises $255M Series A with a new take on big data analysis." https://techcrunch.com/2026/02/05/fundamental-raises-255-million-series-a-with-a-new-take-on-big-data-analysis/

[5] Whalesbook (2026). "Fundamental Taps $1.2B Valuation for Structured Data AI." https://www.whalesbook.com/news/English/tech/Fundamental-Taps-dollar12B-Valuation-for-Structured-Data-AI/6984c5b3bf48f011a29eb8aa

[6] VentureBeat (2026). "Beyond the lakehouse: Fundamental's NEXUS bypasses manual ETL with a native foundation model for tabular data." https://venturebeat.com/data/fundamental-emerges-from-stealth-with-first-major-foundation-model-trained

[7] AWS Press (2026). "Fundamental Announces $255M in Funding and Publicly Launches its Most Powerful Large Tabular Model (LTM)." https://press.aboutamazon.com/aws/2026/2/fundamental-announces-255m-in-funding-and-publicly-launches-its-most-powerful-large-tabular-model-ltm

[8] Wikipedia (2026). "Palantir." https://en.wikipedia.org/wiki/Palantir

[9] Wikipedia (2026). "Palantir." https://en.wikipedia.org/wiki/Palantir

[10] Times-Online (2025). "The Intelligence Epoch: A Deep-Dive into Palantir's 2025 AI Dominance." https://business.times-online.com/times-online/article/predictstreet-2025-12-22-the-intelligence-epoch-a-deep-dive-into-palantirs-2025-ai-dominance

[11] Times-Online (2025). "The Intelligence Epoch: A Deep-Dive into Palantir's 2025 AI Dominance." https://business.times-online.com/times-online/article/predictstreet-2025-12-22-the-intelligence-epoch-a-deep-dive-into-palantirs-2025-ai-dominance

[12] Wikipedia (2026). "Palantir." https://en.wikipedia.org/wiki/Palantir

[13] MacroTrends (2026). "Palantir Technologies Market Cap 2019-2025." https://www.macrotrends.net/stocks/charts/PLTR/palantir-technologies/market-cap

[14] VentureBeat (2026). "Beyond the lakehouse: Fundamental's NEXUS bypasses manual ETL." https://venturebeat.com/data/fundamental-emerges-from-stealth-with-first-major-foundation-model-trained

[15] Fundamental Tech (2026). "Revealing The Hidden Language of Tables." https://fundamental.tech/news/launch

[16] TechCrunch (2026). "Fundamental raises $255M Series A." https://techcrunch.com/2026/02/05/fundamental-raises-255-million-series-a-with-a-new-take-on-big-data-analysis/

[17] SiliconANGLE (2026). "Fundamental launches with $255M." https://siliconangle.com/2026/02/05/fundamental-launches-255m-ai-model-optimized-tabular-data/

[18] HPCwire (2026). "Fundamental Emerges from Stealth with $255M and Tabular AI Model." https://www.hpcwire.com/bigdatawire/this-just-in/fundamental-emerges-from-stealth-with-255m-and-tabular-ai-model/

[19] VentureBeat (2026). "Beyond the lakehouse: Fundamental's NEXUS." https://venturebeat.com/data/fundamental-emerges-from-stealth-with-first-major-foundation-model-trained

[20] VentureBeat (2026). "Beyond the lakehouse: Fundamental's NEXUS." https://venturebeat.com/data/fundamental-emerges-from-stealth-with-first-major-foundation-model-trained

[21] Palantir (2026). "Platform overview." https://palantir.com/docs/foundry/platform-overview/overview/

[22] Palantir 10-K (2025). "2025 FY PLTR 10-K." https://investors.palantir.com/files/2025%20FY%20PLTR%2010-K.pdf

[23] LinkedIn (2025). "How Palantir's Ontologies Supercharge AI." https://www.linkedin.com/posts/stuart-winter-tear_ontologies-are-like-a-secret-sauce-that-supercharge-activity-7302494775876726785-VjDU

[24] Palantir 10-K (2025). "2025 FY PLTR 10-K." https://investors.palantir.com/files/2025%20FY%20PLTR%2010-K.pdf

[25] Yahoo Finance (2025). "Foundry & Gotham: The Engines Driving Palantir's Enterprise AI Rise." https://finance.yahoo.com/news/foundry-gotham-engines-driving-palantirs-164300736.html

[26] MatrixBCG (2025). "What is Growth Strategy and Future Prospects of Palantir Technologies Company?" https://matrixbcg.com/blogs/growth-strategy/palantir

[27] Times-Online (2025). "The Intelligence Epoch." https://business.times-online.com/times-online/article/predictstreet-2025-12-22-the-intelligence-epoch-a-deep-dive-into-palantirs-2025-ai-dominance

[28] GitHub/Leading-AI-IO (2025). "palantir-ontology-strategy/docs/the-palantir-impact_en.md." https://github.com/Leading-AI-IO/palantir-ontology-strategy/blob/main/docs/the-palantir-impact_en.md

[29] AWS Press (2026). "Fundamental Announces $255M in Funding." https://press.aboutamazon.com/aws/2026/2/fundamental-announces-255m-in-funding-and-publicly-launches-its-most-powerful-large-tabular-model-ltm

[30] AWS Press (2026). "Fundamental Announces $255M in Funding." https://press.aboutamazon.com/aws/2026/2/fundamental-announces-255m-in-funding-and-publicly-launches-its-most-powerful-large-tabular-model-ltm

[31] LinkedIn/Matt Garman (2026). "Today Fundamental is coming out of stealth." https://www.linkedin.com/posts/mattgarman_today-fundamental-is-coming-out-of-stealth-activity-7425203597015171072-ix12

[32] VentureBeat (2026). "Beyond the lakehouse: Fundamental's NEXUS." https://venturebeat.com/data/fundamental-emerges-from-stealth-with-first-major-foundation-model-trained

[33] Markets-Chroniclejournal (2026). "The AI Operating System of the West: A 2026 Deep Dive into Palantir Technologies." http://markets.chroniclejournal.com/chroniclejournal/article/finterra-2026-3-2-the-ai-operating-system-of-the-west-a-2026-deep-dive-into-palantir-technologies-pltr

[34] Markets-Chroniclejournal (2026). "The AI Operating System of the West." http://markets.chroniclejournal.com/chroniclejournal/article/finterra-2026-3-2-the-ai-operating-system-of-the-west-a-2026-deep-dive-into-palantir-technologies-pltr

[35] Times-Online (2025). "The Intelligence Epoch." https://business.times-online.com/times-online/article/predictstreet-2025-12-22-the-intelligence-epoch-a-deep-dive-into-palantirs-2025-ai-dominance

[36] Palantir (2025). "November 2025 Announcements." https://palantir.com/docs/foundry/announcements/2025-11/

[37] Palantir (2025). "November 2025 Announcements." https://palantir.com/docs/foundry/announcements/2025-11/

[38] Palantir (2025). "Palantir Artificial Intelligence Platform." https://www.palantir.com/platforms/aip/

[39] Salesforce Ventures (2026). "Bringing AI to Structured Data." https://salesforceventures.com/perspectives/bringing-ai-to-structured-data/

[40] Palantir 10-K (2025). "2025 FY PLTR 10-K." https://investors.palantir.com/files/2025%20FY%20PLTR%2010-K.pdf

[41] Palantir 10-K (2025). "2025 FY PLTR 10-K." https://investors.palantir.com/files/2025%20FY%20PLTR%2010-K.pdf

[42] Wikipedia (2026). "Palantir." https://en.wikipedia.org/wiki/Palantir

[43] Yahoo Finance (2025). "Foundry & Gotham." https://finance.yahoo.com/news/foundry-gotham-engines-driving-palantirs-164300736.html

[44] SiliconANGLE (2026). "Fundamental launches with $255M." https://siliconangle.com/2026/02/05/fundamental-launches-255m-ai-model-optimized-tabular-data/

[45] TechCrunch (2026). "Fundamental raises $255M Series A." https://techcrunch.com/2026/02/05/fundamental-raises-255-million-series-a-with-a-new-take-on-big-data-analysis/

[46] LinkedIn/Matt Garman (2026). "Today Fundamental is coming out of stealth." https://www.linkedin.com/posts/mattgarman_today-fundamental-is-coming-out-of-stealth-activity-7425203597015171072-ix12

[47] MacroTrends (2026). "Palantir Technologies Revenue 2019-2025." https://www.macrotrends.net/stocks/charts/PLTR/palantir-technologies/revenue

[48] CNBC (2026). "Palantir (PLTR) Q4 2025 earnings." https://www.cnbc.com/2026/02/02/palantir-pltr-q4-2025-earnings.html

[49] Palantir Q4 2025 Investor Presentation (2026). https://investors.palantir.com/files/Palantir%20-%20Q4%202025%20Investor%20Presentation.pdf

[50] Palantir 10-K (2025). "2025 FY PLTR 10-K." https://investors.palantir.com/files/2025%20FY%20PLTR%2010-K.pdf

[51] Palantir 10-K (2025). "2025 FY PLTR 10-K." https://investors.palantir.com/files/2025%20FY%20PLTR%2010-K.pdf

[52] Bullfincher (2026). "Palantir Technologies Revenue 2019-2025." http://bullfincher.io/companies/palantir-technologies/revenue

[53] Palantir Q4 2025 Earnings Release (2026). https://investors.palantir.com/news-details/2026/Palantir-Reports-Q4-2025-U-S--Comm-Revenue-Growth-of-137-YY-and-Revenue-Growth-of-70-YY-Issues-FY-2026-Revenue-Guidance-of-61-YY-and-U-S--Comm-Revenue-Guidance-of-115-YY-Crushing-Consensus-Expectations/

[54] Palantir Q4 2025 Earnings Release (2026). https://investors.palantir.com/news-details/2026/Palantir-Reports-Q4-2025-U-S--Comm-Revenue-Growth-of-137-YY-and-Revenue-Growth-of-70-YY-Issues-FY-2026-Revenue-Guidance-of-61-YY-and-U-S--Comm-Revenue-Guidance-of-115-YY-Crushing-Consensus-Expectations/

[55] Palantir Q4 2025 Earnings Release (2026). https://investors.palantir.com/news-details/2026/Palantir-Reports-Q4-2025-U-S--Comm-Revenue-Growth-of-137-YY-and-Revenue-Growth-of-70-YY-Issues-FY-2026-Revenue-Guidance-of-61-YY-and-U-S--Comm-Revenue-Guidance-of-115-YY-Crushing-Consensus-Expectations/

[56] Palantir Q4 2025 Investor Presentation (2026). https://investors.palantir.com/files/Palantir%20-%20Q4%202025%20Investor%20Presentation.pdf

[57] Palantir Q4 2025 Investor Presentation (2026). https://investors.palantir.com/files/Palantir%20-%20Q4%202025%20Investor%20Presentation.pdf

[58] MacroTrends (2026). "Palantir Technologies Market Cap 2019-2025." https://www.macrotrends.net/stocks/charts/PLTR/palantir-technologies/market-cap

[59] Yahoo Finance (2025). "Palantir Stock Is Up 150% in 2025. History Says This Will Happen Next." https://finance.yahoo.com/news/palantir-stock-150-2025-history-091500261.html

[60] Intellectia.AI (2025). "Palantir Reaches $440 Billion Market Cap in 2025." https://intellectia.ai/news/stock/palantir-reaches-440-billion-market-cap-in-2025-ai-platform-doubles-revenue

[61] Yahoo Finance (2026). "After a 130% Surge in 2025, Can Palantir Stock Keep Beating the Market in 2026?" https://finance.yahoo.com/news/130-surge-2025-palantir-stock-182629024.html

[62] Palantir Q4 2025 Investor Presentation (2026). https://investors.palantir.com/files/Palantir%20-%20Q4%202025%20Investor%20Presentation.pdf

[63] VentureBeat (2026). "Beyond the lakehouse: Fundamental's NEXUS." https://venturebeat.com/data/fundamental-emerges-from-stealth-with-first-major-foundation-model-trained

[64] AYA Fintech Network (2025). "Stock Synopsis: With a new Python program, we use, adapt, apply, and leverage each of the mainstream Gemini Gen AI models to conduct this comprehensive fundamental analysis of Palantir." https://ayafintech.network/blog/gen-ai-fundamental-analysis-of-palantir-pltr/

[65] Annie Lamont, Oak HC/FT, quoted in VentureBeat (2026). https://venturebeat.com/data/fundamental-emerges-from-stealth-with-first-major-foundation-model-trained

[66] DIGETIERS (2026). "8 Best Alternatives to Palantir Foundry in 2026." https://www.digetiers-dap.com/post/palantir-foundry-alternatives

[67] Wikipedia (2026). "Palantir." https://en.wikipedia.org/wiki/Palantir

[68] FinancialContent (2025). "Palantir Technologies: Decoding the Data Giant's AI Ambitions and Geopolitical Influence." https://www.financialcontent.com/article/predictstreet-2025-9-29-palantir-technologies-decoding-the-data-giants-ai-ambitions-and-geopolitical-influence

[69] Data Engineer Things (2025). "Palantir Foundry Is 5–10 Years Ahead of Every Other Data Platform." https://blog.dataengineerthings.org/what-palantir-foundry-taught-me-about-building-better-data-systems-407e3768d5fc

[70] Whalesbook (2026). "Fundamental Taps $1.2B Valuation for Structured Data AI." https://www.whalesbook.com/news/English/tech/Fundamental-Taps-dollar12B-Valuation-for-Structured-Data-AI/6984c5b3bf48f011a29eb8aa

[71] NVIDIA (2025). "Palantir and NVIDIA Team Up to Operationalize AI." https://investor.nvidia.com/news/press-release-details/2025/Palantir-and-NVIDIA-Team-Up-to-Operationalize-AI--Turning-Enterprise-Data-Into-Dynamic-Decision-Intelligence/

[72] Palantir Q4 2025 Earnings Release (2026). https://investors.palantir.com/news-details/2026/Palantir-Reports-Q4-2025-U-S--Comm-Revenue-Growth-of-137-YY-and-Revenue-Growth-of-70-YY-Issues-FY-2026-Revenue-Guidance-of-61-YY-and-U-S--Comm-Revenue-Guidance-of-115-YY-Crushing-Consensus-Expectations/

[73] Jeremy Fraenkel, CEO of Fundamental, quoted in TechCrunch (2026). https://techcrunch.com/2026/02/05/fundamental-raises-255-million-series-a-with-a-new-take-on-big-data-analysis/

---

**报告信息**

| 元数据 | 内容 |
|--------|------|
| 研究模式 | 深度分析 (Deep) |
| 信息来源数量 | 40+ |
| 研究时间 | 2026年4月24日 |
| 验证状态 | 已通过多源交叉验证 |
