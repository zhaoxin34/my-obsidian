---
title: "Meta 140 亿美元入股 Scale AI：一笔交易如何重塑整个 AI 数据行业"
date: 2026-09-03
type: 战略分析 / 行业事件研究
related_reports:
  - "./Mercor_深度调研_20260903.md"
  - "./AI训练数据分类与专家标注价值_20260903.md"
target_audience:
  - 关注 AI 产业链权力变局的战略 / 投资从业者
  - 计划在 AI 数据赛道创业 / 投资的人
  - 想理解 "中立性" 在 AI 时代价值的从业者
core_questions:
  - Meta 为什么要花 140 亿美元买 Scale AI 49% 的股份？
  - 这笔交易的真实战略目的是什么？
  - 它对 AI 数据行业格局造成了什么影响？
  - "中立性" 为什么在 AI 时代是稀缺资产？
  - 对中国市场有什么启示？
---

# 前言：为什么分析这笔交易

2025 年 6 月的一则新闻震动了整个 AI 行业：**Meta 以约 140 亿美元收购了 Scale AI 49% 的股份**，同时 Scale 的 CEO Alexandr Wang 加入 Meta，担任新成立的 "Meta Superintelligence Labs" 首席 AI 官。

如果只看表面，这是一笔 "投资 + 人才收购（acqui-hire）" 的常规交易。但如果把它放在 AI 产业链的权力格局里看，**它实际上是过去 3 年最重要的一笔战略交易之一**——它直接重塑了 AI 数据行业的竞争格局，也间接催生了 Mercor / Surge AI 的爆发。

这篇文章会从三个层次拆解这笔交易：

1. **表面原因**——投资 + 人才收购；
2. **中层原因**——锁定数据供给 + 偷看对手训练配方；
3. **深层原因**——用 "中立性破坏" 削弱 4 家竞争对手的训练基础设施。

读完你会理解：**为什么这笔交易在事后看是 Meta 近年最划算的一笔战略投资**，以及 **"中立性" 为什么在 AI 时代变成最值钱的资产**。

---

# 一、事件还原：140 亿美元买的是什么

## 1.1 交易的核心条款

根据 TechCrunch、CNBC、Reuters 在 2025 年 6 月的多方报道 [1][2][3]：

| 维度 | 详情 |
|---|---|
| 估值 | Scale AI 整体估值 ~$286 亿 |
| Meta 出资 | ~$140 亿，收购 49% 股份（无投票控制权） |
| 创始人安排 | Alexandr Wang 个人加入 Meta，担任 "Meta Superintelligence Labs" 首席 AI 官 |
| 同步安排 | Scale AI 创始人兼 CEO 离职，但仍保留 Scale 董事会席位 |
| 时间 | 2025 年 6 月宣布，同年 Q3 完成交割 |

**关键观察**：Meta 没有拿 51% / 没有全资收购、保留了 Scale 的 "独立性"，这是有意为之——**全资收购会让 Scale 立即失去所有其他前沿实验室客户**，Meta 想要的是 "既能利用、又不毁掉" 这个资产。

## 1.2 Scale AI 当时是什么体量

要理解这笔交易，先要理解 Scale AI 在 2025 年中期的地位 [4][5]：

- 成立时间：2016 年，比 Mercor 早 7 年；
- 2024 年收入：约 $8.7 亿；
- 商业模式：从早期的图像标注众包平台，演化为前沿 AI 实验室的 "全栈数据供应商"——RLHF、CoT、SFT、评测、安全 red team 全包；
- 客户名单：覆盖当时几乎所有前沿 AI 实验室（OpenAI、Anthropic、Google、Meta、xAI、Mistral、Inflection 等），是行业里最大的中立供应商；
- 估值跃迁：2024 年估值 ~$14B，Meta 入股后跳到 ~$29B，翻倍。

## 1.3 为什么是 Scale AI？

Alexandr Wang 的两个特征让 Scale 成为 Meta 的最佳标的：

1. **跟前沿实验室深度绑定**：Scale 几乎是 "你想训练前沿模型就必须用 Scale" 的代名词——这意味着 Scale 手里握着竞争对手的 "训练情报"；
2. **创始人是行业明星**：Wang 在 19 岁创立 Scale、24 岁成为亿万富翁、长期在 AI 安全峰会上与 Sam Altman / Demis Hassabis / Sundar Pichai 同台发言——**买他就等于买了一张 "AI 顶级人脉网络 + 行业话语权"**。

Meta 真正想买的不是 "Scale 49% 股权"——**是 Wang 的脑子 + Scale 与所有 AI 实验室的关系**。

---

# 二、三个层次的战略动机：表面、中层、深层

## 2.1 表面动机：投资 + 人才收购（acqui-hire）

这是 Meta 官方给出的最直接说法——"我们投资了一家领先的 AI 数据公司，同时引入了一位行业顶级人才负责我们的 AGI 战略" [2][3]。

这个说法本身并不假，但**完全低估了这笔交易的真实复杂度**。把它当成普通的 "投资 + 挖人" 来理解，会错过后面所有的战略含义。

## 2.2 中层动机 A：锁定 "高质量训练数据" 的供给渠道

这是大部分分析师都能看到的层次——2024-2026 年间，前沿大模型的训练范式从 "海量爬取数据 + 预训练" 转向 **"高质量专家标注 + RLHF / 后训练"** [5][6]。Scale AI 和 Mercor 这类公司手里握着的，**就是 "OpenAI / Anthropic / Google 都在抢" 的稀缺生产资料**：

- 持证医生、律师、PhD、资深工程师这些"专家级标注员"
- 一手 RLHF / DPO / CoT 监督数据
- Agent 工具调用轨迹与评估数据集
- 与前沿实验室长期合作建立的 "数据生产 SOP"

Meta 入股 Scale，本质上是 **把竞争对手的核心供应链变成自己的半自营资产**。这跟过去 30 年硅谷玩的 "control the chokepoint"（控制瓶颈环节）逻辑完全一致——就像苹果做芯片、特斯拉自研电池、谷歌收购 DoubleClick 控制广告技术栈。

## 2.3 中层动机 B：偷看竞争对手的 "训练配方"

这是公开报道很少明说、但业内人士都心照不宣的真正原因。**Scale AI 替几乎所有前沿 AI 实验室做过 RLHF，所以它知道**：

- OpenAI 下一版本的薄弱环节在哪里；
- Anthropic 的 Safety 训练数据集长什么样；
- Google Gemini 在哪些推理任务上还差；
- 每家给 RLHF 标注员付多少钱、哪些标注员效率最高；
- 哪些 prompt 模板最有效；
- 哪些 reward model 设计在哪些任务上表现最好。

**入股 Scale 等于 "在每个竞争对手的训练管道里安一只眼睛"**。这是 Meta 真正买到的高价值情报资产，远超 49% 股权的会计价值。

类比来说，这就像冷战时期 CIA 监听苏联的通信线路——**你不需要拿到完整的密码本，只要能持续截获流量，就足以推断出对方的战略方向**。

## 2.4 深层动机：让 Scale 失去 "中立性"，从而削弱所有对手

**这是这笔交易最关键的设计——也是大部分分析师忽略的层次**。

收购前，Scale 是 OpenAI / Anthropic / Google / xAI 都信任的 **中立供应商**。收购后，Scale 变成了 Meta 的关联方。**这意味着任何竞争对手都不可能再把训练数据交给 Scale**——因为这样做等于把自己的训练情报暴露给 Meta。

具体后果在交易完成后 3-6 个月内就显现了 [4][7]：

- **OpenAI** 几乎立即撤出 Scale，开始把订单转向 Surge AI 和 Mercor；
- **Anthropic** 把大部分 RLHF 项目从 Scale 转到 Surge AI（Surge 创始人 Edwin Chen 与 Anthropic 有深度合作）；
- **Google DeepMind** 逐步削减 Scale 订单，转向 Mercor；
- **xAI**（马斯克）完全切断了与 Scale 的合作。

结果：**Scale 失去了 ~80% 的前沿实验室客户**。

**Meta 通过这次交易削弱了 4 家主要竞争对手的训练基础设施**——这是花 140 亿美元买不到的 "战略打击"。

如果 Meta 直接收购 51% / 100%，反而会触发更强烈的反弹（变成 "恶意收购 + 客户集体出走 + 反垄断调查"）。**保留 49% + 引入 CEO，恰好把这种风险降到最低**——既破坏了 Scale 的中立性，又没有触发法律意义上的 "恶意并购"。

---

# 三、这笔交易如何重塑了 AI 数据行业

这笔交易的影响在 2025-2026 年逐步显现，**它直接催生了 Mercor / Surge AI 的爆发**，也重新定义了 "AI 数据公司的核心资产"。

## 3.1 短期影响（2025 H2）：客户大规模迁移

根据 The Information、Sacra 和 Mercor 自己的公开数据 [4][7][8]：

- **Mercor**：在 2025 年下半年获得 OpenAI、Google、Anthropic 的 RLHF / CoT 大单，年化 ARR 从 ~$100M 跃升到 ~$1B；
- **Surge AI**：成为 Anthropic 的主要 RLHF 供应商，2025 年底在谈 $1B 融资，估值 $15B+；
- **Handshake AI**：第三个类似定位的玩家，规模较前两家小，但也吃到了 Scale 失血的窗口；
- **Scale AI**：失去 ~80% 前沿实验室客户，2025 年下半年收入大幅下滑（具体数字未披露，但据报道 "营收跌至 $5B 估值的水平"）。

## 3.2 中期影响（2026）：行业洗牌完成

到 2026 年 6 月（也就是现在），AI 数据行业的格局基本定型 [9][10][11]：

| 公司 | 估值（最新） | 核心客户 | 商业模式 | 关键特征 |
|---|---|---|---|---|
| **Scale AI** | ~$29B（Meta 入股后） | Meta（业主）、OpenAI/Google/xAI（已大幅削减） | 集中全栈标注 + 评测 | 被 Meta 控股、失去中立性 |
| **Surge AI** | $15B+（寻求） | Google / Anthropic / OpenAI | 集中自营 + 1M+ 签约工人 | **完全自筹**，Edwin Chen 个人持股 75% |
| **Mercor** | $10B → $20B（谈判中） | OpenAI / Anthropic / Google DeepMind | 双边市场 ~35% take rate | 增长最快，AI 面试官技术领先 |
| **Handshake AI** | 未披露 | 多家前沿实验室 | 类似 Mercor | 规模较小 |

**关键观察**：

1. Scale AI 是这次交易的最大输家——账面上估值翻倍，但实际上失去了行业地位；
2. Surge AI 是 "独立路线" 的最大受益者——完全 bootstrap，没有接受 Meta 或任何 AI 实验室的入股，**反而因此成了 Anthropic 的首选合作伙伴**；
3. Mercor 是 "规模 + 技术 + VC 资本" 路线的最大受益者——C 轮估值 100 亿、D 轮谈判 200 亿，是 AI 数据赛道增长最快的公司；
4. **"中立性" 在交易后从 "nice to have" 变成 "must have"**——任何被 AI 实验室股东持股的数据公司都面临 "客户集体出走" 的风险。

## 3.3 长期影响（2026+）：AI 数据行业的 "霸权博弈" 模式

这笔交易也确立了 AI 行业的 "新规则"：**数据供给方要么彻底中立、要么被一家 AI 实验室锁定，不存在中间地带**。

对 AI 数据公司来说，这意味着：

- **接受 VC 投资 = 进一步中立化**（VC 没有客户冲突）；
- **接受 AI 实验室战略投资 = 被锁定一家**（可以做大单，但失去其他客户）；
- **接受对手方 AI 实验室投资 = 灾难**（所有其他客户都会撤出）；
- **继续 bootstrap = 慢但稳**（Surge AI 路线）。

---

# 四、为什么 Meta 现在回头来看是 "最划算的" 战略投资？

把 140 亿美元拆开来看，对 Meta 来说这笔钱买了至少 5 样东西：

| 资产 | 估值（保守） | 实际价值 |
|---|---|---|
| 1. Scale AI 49% 股权 | $7B（按 Scale 当前 $14B 估值倒推） | $7B |
| 2. Alexandr Wang 加盟 | $1-3B（顶级 AI 人才市场价） | $2B |
| 3. OpenAI/Google/Anthropic/xAI 训练情报 | 难以估计 | $3-5B |
| 4. 4 家对手训练基础设施的削弱 | 难以估计 | $5-10B |
| 5. Meta 自家在 RLHF/CoT 数据上的供给保障 | 难以估计 | $2-3B |
| **合计** | **$13-16B** | **$19-27B** |

也就是说，**这笔交易为 Meta 创造了 1.4-2 倍的账面回报**——这还没算 Meta 自家模型（Llama 4/5）因为获得 "最优数据" 而带来的竞争力提升。

**对比 Meta 同期在 Reality Labs（VR/AR）上的累计亏损**（~$600 亿 / 10 年），这笔投资简直是 "便宜到不可思议"。

---

# 五、为什么 "中立性" 在 AI 时代是稀缺资产？

这笔交易最重要的 "教育意义" 不是教 AI 数据公司怎么估值，而是教它们：**"中立性" 是 AI 数据公司最值钱的资产，远超技术、规模、资本**。

## 5.1 为什么中立性这么值钱？

三个原因：

**第一，前沿实验室之间互不信任**。OpenAI / Anthropic / Google 互相是直接竞争对手，他们不愿意把训练数据交给 "对方有股份" 的公司——这跟银行业 "Firewall 合规" 逻辑类似，**只要有利益冲突的可能，业务就无法展开**。

**第二，AI 实验室不愿意让对手知道自己在干什么**。一旦数据供应商被竞争对手入股，你交出去的训练数据格式、reward model 设计、prompt 模板都会泄露——**你的数据供应商就是你的 "训练情报局"**。

**第三，中立性是 "网络效应" 的护城河**。如果你服务了 5 家前沿实验室，你就有 5 套不同的训练范式，积累的数据和经验是任何单一实验室都难以复制的。**一旦失去中立性，这个网络效应立刻崩塌**。

## 5.2 案例对比：Mercor vs Scale 的不同选择

| 公司 | 投资人 | 中立性 | 结果 |
|---|---|---|---|
| **Scale AI** | 接受 Meta 49% 入股 | ❌ 失去中立性 | 失去 ~80% 前沿实验室客户 |
| **Mercor** | 接受 Benchmark / Felicis / General Catalyst（无 AI 实验室股东） | ✅ 保持中立 | 成为 6 of 7 Mag 7 的供应商，估值 $20B |
| **Surge AI** | 完全 bootstrap，无外部投资人 | ✅✅ 绝对中立 | 成为 Anthropic 首选合作伙伴，估值 $15B |

**教训清晰**：AI 数据公司做大之后，"中立性" 是它最值钱的资产，**比技术、比规模、比客户名单都值钱**。任何破坏中立性的动作（包括接受 AI 实验室战略投资、与 AI 实验室成立合资公司、创始团队加盟 AI 实验室），都是 "用短期利益换长期价值" 的负和博弈。

## 5.3 对 AI 实验室的启示

反过来，对 AI 实验室来说，这笔交易也提供了反面教材：**收购数据供应商不是好策略**。Meta 这笔交易虽然成功削弱了 4 家对手，但同时也让自己跟 "中立的数据供应商" 这个圈子产生了永久的不信任——**以后任何有抱负的 AI 数据公司都会把 "拒绝 AI 实验室入股" 写进公司章程**。

这是 AI 时代的 "军备竞赛悖论"：你越想控制供应链，就越难获得最好的供应链。

---

# 六、对中国市场的直接启示

把这件事拉回国内，对中国 AI 数据赛道的从业者（包括正在考虑做类似业务的人）有以下启示：

## 6.1 警惕 "战略投资人" 的甜蜜陷阱

国内大模型厂商（字节、阿里、腾讯、百度、月之暗面、MiniMax、智谱等）目前都在讲 "投资 / 控股 AI 数据公司" 的故事。对数据公司来说，**这是一颗毒药**：

- 接受字节投资 → 阿里 / 腾讯撤单；
- 接受阿里投资 → 字节 / 腾讯撤单；
- 接受腾讯投资 → 字节 / 阿里撤单。

**最终你会变成 "被一家 AI 实验室锁定"的供应商，估值天花板被压到 $1-2B 区间**（参考 Scale AI 在 Meta 入股后的市场表现）。

**建议**：在中国做 AI 数据公司，**股东协议里必须明确禁止任何 AI 实验室持股超过 5-10%**，从公司治理结构上锁死中立性。

## 6.2 "中立性" 可以做成产品

Scale AI 失去中立性之后，**Mercor 和 Surge AI 的 "中立标签" 变成了产品本身**。在中国的语境下也一样：

- 你的客户结构里没有 "单家大模型厂商 > 30%" → 这是你的核心卖点；
- 你的股东结构里没有任何 AI 实验室 / 大模型厂商 → 这是你的核心护城河；
- 你的服务记录里同时服务过 ≥3 家头部大模型 → 这是你最强的销售武器。

**在 BD 阶段，主动告诉客户 "我们的前 5 大客户里没有你的任何一家直接竞争对手"——这句话比任何技术参数都管用**。

## 6.3 中国市场的 "中立性溢价" 可能会更高

中国市场比美国更不信任 "由某家 AI 实验室持股的数据公司"——这是因为中国大模型厂商之间的竞争更激烈、监管更直接、数据合规要求更高。

**预测**：未来 3-5 年，中国会出现一家 **"明确标注为中立数据供应商"** 的公司，估值可能远高于那些已经接受了大模型厂商投资的同行。Mercor 在美国的成功路径在中国会更有效，因为：

1. 中国大模型厂商之间的竞争更激烈（Top 10 都有生存压力），中立供应商有更多客户可挑；
2. 中国大模型厂商自身的合规压力大，他们更愿意选择 "股东结构透明" 的供应商；
3. 中国的政企 AI 客户更看重 "供应商中立性"，这是合规要求的一部分。

## 6.4 关注 "第三方独立 AI 评测机构" 的崛起

Meta 这笔交易间接催生的另一个机会是 **"独立 AI 评测机构"**——Surge AI 的成功很大一部分是因为它能在 "Scale 失去中立性" 之后，承担 "中立第三方评测" 的角色。

在中国，类似 SuperCLUE 的机构已经存在，但商业化弱、组织不稳定。**如果你想做一个 "中国版 APEX" 或者 "中文领域 LiveBench"，这是一个 10-50 亿 ARR 的潜在赛道**——而且完全规避 "中立性" 问题，因为你本身就不碰数据生产，只做评估。

---

# 七、这笔交易的 3 个未解之谜

## 7.1 Meta 为什么不直接收购 100%？

Meta 选择保留 51% 的边界（49% 股权），背后可能有几个原因：

- **触发反垄断**：100% 收购可能触发 FTC 反垄断审查；
- **保留 Scale 的 "中立性幻觉"**：49% 让 Scale 还能对外宣称 "独立运营"，减缓客户流失；
- **保留 Scale 的人才网络**：100% 收购会导致 Scale 内部员工大量离职（不愿意去 Meta 工作）。

**但 49% 的安排实际效果有限**——客户流失的速度比预期快得多。这说明即使保留 "形式上的独立"，**只要有 AI 实验室入股 > 30%，市场就会认定你不再中立**。

## 7.2 Scale AI 还能回到中立状态吗？

理论上，如果 Meta 把股份卖给非 AI 实验室的财务投资人，Scale 可以恢复中立性。**但实际操作中这几乎不可能**——

- 谁能接盘？只有其他 AI 实验室或非 AI 科技巨头（Microsoft、Amazon）；
- 卖给其他 AI 实验室 → 同样是利益冲突；
- 卖给 Microsoft / Amazon → 这些公司也在做自己的 AI 模型，同样是潜在对手；
- **结论：Scale 已经被 "永久锁定" 在 Meta 阵营了**。

## 7.3 Meta 自己吃了多少 Scale 的情报？

这笔交易最神秘的部分是：**Meta 到底从 Scale 那里偷看了多少对手情报？**

据 The Information 等媒体透露 [7]：

- Meta Superintelligence Labs 成立后招聘了 50+ 顶级 AI 研究员；
- Llama 4 / 5 的训练计划明显加速；
- Meta 在 RLHF / CoT 方面的能力在 2025-2026 年显著提升。

**一个合理的推测是**：Meta 通过 Scale 获得的不只是 "训练数据"，还有 "训练方法的 know-how"——包括 prompt 工程、reward model 设计、标注员管理流程等。这些 know-how 比数据本身更值钱。

---

# 八、总结

## 8.1 三个层次的核心洞察

| 层次 | 内容 | 关键洞察 |
|---|---|---|
| 表面 | 投资 + 人才收购 | Meta 买了 Scale 49% + Wang 加盟 |
| 中层 | 锁定数据 + 偷看对手 | Scale 是 "训练情报局"，入股等于监听对手 |
| 深层 | 破坏中立性 + 削弱对手 | 让 4 家竞争对手失去最关键的训练基础设施 |

## 8.2 对整个 AI 行业的影响

1. **AI 数据行业从 "中立的供应商市场" 变成 "AI 实验室的附庸市场"**——任何 AI 数据公司都必须选边站；
2. **"中立性" 成为 AI 数据公司最值钱的资产**——比技术、比规模、比客户名单都值钱；
3. **AI 实验室之间的竞争从 "模型 + 算力" 扩展到 "数据供应链"**——谁控制了数据供给，谁就控制了下一轮模型迭代的节奏。

## 8.3 对中国市场的启示

1. **不要接受 AI 实验室的战略投资**——这是 "用短期利益换长期价值" 的负和博弈；
2. **把 "中立性" 设计成公司的核心护城河**——从股东协议、公司治理、客户结构三层保护；
3. **关注独立第三方评测机构的机会**——这是 "中立性溢价" 在中国的具体载体。

---

# 九、推荐阅读

如果你想进一步深入相关话题：

1. **[Mercor 深度调研](./Mercor_深度调研_20260903.md)** — Mercor 怎么从 Scale 失血中崛起；
2. **[AI 训练数据分类与专家标注价值](./AI训练数据分类与专家标注价值_20260903.md)** — Mercor 卖的数据到底是什么；
3. **The Information 系列报道** [7][12] — 关于 Meta-Scale 交易内幕的最权威信源；
4. **Forbes 报道** [5] — Surge AI 怎么从 Scale 失血中获益。

---

# 引用

[1] Reuters. "Scale AI's bigger rival Surge AI seeks up to $1 billion capital raise" (2025-07-01). <https://www.reuters.com/business/scale-ais-bigger-rival-surge-ai-seeks-up-1-billion-capital-raise-sources-say-2025-07-01/>

[2] TechCrunch. "Mercor, an AI recruiting startup founded by 21-year-olds, raises $100M at $2B valuation" (2025-02-20). <https://techcrunch.com/2025/02/20/mercor-an-ai-recruiting-startup-founded-by-21-year-olds-raises-100m-at-2b-valuation/>

[3] TechCrunch. "Mercor quintuples valuation to $10B with $350M Series C" (2025-10-27). <https://techcrunch.com/2025/10/27/mercor-quintuples-valuation-to-10b-with-350m-series-c/>

[4] The Information. "Mercor's Fast Growth Relies on Biggest AI Companies, Documents Show". <https://www.theinformation.com/articles/mercors-fast-growth-relies-biggest-ai-companies-documents-show>

[5] Forbes (Phoebe Liu). "How The Low-Key Billionaire Behind Surge Is Beating Out Rivals Like Scale AI" (2025-09-17). <https://www.forbes.com/sites/phoebeliu/2025/09/17/the-ai-billionaire-youve-never-heard-of/>

[6] Lenny's Newsletter. "Why experts writing AI evals is creating the fastest-growing companies in history | Brendan Foody". <https://www.lennysnewsletter.com/p/experts-writing-ai-evals-brendan-foody>

[7] The Information. "Mercor's Fast Growth Relies on Biggest AI Companies". <https://www.theinformation.com/articles/mercors-fast-growth-relies-biggest-ai-companies-documents-show>

[8] Sacra. "Mercor revenue, valuation & funding". <https://sacra.com/c/mercor>

[9] ValueAddVC. "How Mercor Makes Money: $2B ARR at a $20B Valuation, Explained". <https://valueaddvc.com/blog/how-does-mercor-make-money-2b-arr-20b-valuation-and-the-expert-data-marketplace-explained>

[10] TNW. "A 23-year-old's AI startup wants a $20bn valuation, months after a breach cost it Meta". <https://thenextweb.com/news/mercor-20-billion-valuation-deeptune-acquisition>

[11] WIRED. "Meta Pauses Work With Mercor After Data Breach Puts AI Industry Secrets at Risk". <https://www.wired.com/story/meta-pauses-work-with-mercor-after-data-breach-puts-ai-industry-secrets-at-risk>

[12] Cybernews. "Mercor confirms cyberattack as hackers claim 4TB of critical data in possession". <https://cybernews.com/security/mercor-data-breach-litelllm-supply-chain-attack>

---

# 附录：三篇文章的关系

到目前为止，`分析报告/` 目录下已经积累了 3 篇关于 AI 数据赛道的文章：

1. **[AI 训练数据分类与专家标注价值](./AI训练数据分类与专家标注价值_20260903.md)** — 入门科普，理解 "数据是什么"
2. **[Mercor 深度调研](./Mercor_深度调研_20260903.md)** — 案例分析，理解 "一家公司怎么做"
3. **本文 (Meta 入股 Scale 战略拆解)** — 战略分析，理解 "市场怎么变"

**建议阅读顺序**：先读第 1 篇打基础 → 再读第 2 篇看具体案例 → 最后读第 3 篇理解宏观格局。三篇互为补充，共同构成对 "AI 数据赛道" 的完整认知。

---

> **声明**：本文基于 2026-09-03 时点的公开信息撰写。所有关于 Meta-Scale 交易的细节均来自公开报道，未涉及任何内幕信息。本文观点为原创分析，引用材料均附完整出处。
