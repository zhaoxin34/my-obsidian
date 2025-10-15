## 哨兵模式的作用

Redis Sentinel 是 Redis 官方提供的 **高可用性（High Availability, HA）** 解决方案。  
它的核心作用有三点：

1. **监控（Monitoring）**  
    持续检查主节点和从节点是否正常工作。
    
2. **通知（Notification）**  
    当某个节点发生故障时，向管理员或其他程序发送通知。
    
3. **自动故障转移（Automatic Failover）**  
    如果主节点挂了，Sentinel 会自动选举一个从节点升级为新的主节点，并让其他从节点重新复制新主。

## 主从故障转移的流程

Sentinel 故障转移大致分为以下步骤：

### 1. 主观下线（Subjectively Down）

- 某个 Sentinel 检测到主节点在 `down-after-milliseconds` 时间内无响应，
- 它会认为主节点“主观下线”（SDOWN）。

### 2. 客观下线（Objectively Down）

- 当有 `quorum` 个 Sentinel 都认为主节点 SDOWN，
- 就会形成“客观下线”（ODOWN），
- 接下来会触发**领导者选举（Leader Election）**。
### 3. 领导者选举

- 所有 Sentinel 节点中，会通过 Raft 类似的投票机制选出一个“Leader Sentinel”。
- Leader 负责执行实际的主从切换操作。
### 4. 故障转移（Failover）

Leader Sentinel 执行以下步骤：

1. 从剩余的从节点中挑选一个“健康”的节点（复制落后最少的）。
2. 发送命令让它执行 `SLAVEOF NO ONE`，成为新的主节点。
3. 通知其他从节点执行 `SLAVEOF <new-master-ip> <new-master-port>`。
4. 更新监控信息，其他 Sentinel 也同步这个变更。
### 5. 客户端更新

- Sentinel 会更新 `mymaster` 的主节点 IP/端口。
- 客户端如果通过 Sentinel 获取连接信息，就能自动连接到新的主节点。

## 投票选主的过程

*假设一个3节点的集群，主节点挂了，剩下2个节点投票，为什么不会出现各投自己一票的现象*

### 1️⃣ 概念准备

- **epoch（纪元）**：每次故障转移的唯一编号（全局单调递增）。  
    每次有 Sentinel 发起新一轮选举时，epoch + 1。
- **Leader Sentinel**：在某个 epoch 中被多数（majority）Sentinel 认可的节点。
- **majority（多数派）**：  
    如果集群里有 N 个 Sentinel，则多数派数量为 `⌊N/2⌋ + 1`。  
### 2️⃣ 选举过程（逐步讲解）

以 3 个 Sentinel 为例：`Sentinel1、Sentinel2、Sentinel3 监控的 Master 挂掉了`

#### Step 1：主观下线

每个 Sentinel 各自检测到 Master 无响应，标记为 SDOWN。

#### Step 2：客观下线

每个 Sentinel 相互通信（通过 Pub/Sub 或命令），当有 `quorum` 个 Sentinel 也认为 Master SDOWN，就进入 ODOWN 状态。

> quorum 通常配置为 2，意味着至少两个 Sentinel 都认为主节点挂了。

#### Step 3：发起选举

此时每个 Sentinel 都可能发起“选主请求”（`is-master-down-by-addr` 命令）。

- 每个 Sentinel 在新的 epoch 中只能 **投一次票**。
- 投票给第一个请求它投票的 Sentinel。
- 之后即使再收到请求，也会拒绝（除非新一轮 epoch 开始）。

#### Step 4：统计投票

谁拿到了多数（>=2）票，谁就成为 Leader Sentinel。

#### Step 5：Leader Sentinel 执行 Failover

Leader 负责：

- 选择新的 master；
- 通知所有从节点；
- 更新配置；
- 同步其他 Sentinel。

---

### 3️⃣关键点：为什么不会出现“各投自己一票”？

这个是很多人误解的地方。  
Redis Sentinel 的选举是 **基于“请求投票”的一次性投票机制”**，不是“自己给自己打分”。

> 举个例子：

假设 3 个 Sentinel：A、B、C  
主节点挂了后，A 先发起 Failover：

1. A 增加自己的 epoch，比如 epoch=20。
2. A 请求 B、C 投票给自己。
3. B 和 C 如果还没投票过，会返回“YES”。
4. A 拿到 2 票（自己+1个他人）→ 成功成为 Leader。

如果 B 同时发起了选举：

- 因为 A 已经在 epoch=20 抢先发起，
- 其他节点 B、C 可能已经投票给 A，
- 所以 B 收不到足够票数（< majority），选举失败。

> 因此，选举是“先到先得 + 一轮一票”，而不是平票制。

---
## 总结表

| 场景     | 存活Sentinel数 | 多数派数 | 是否能选主      | 说明         |
| ------ | ----------- | ---- | ---------- | ---------- |
| 3台全活   | 3           | 2    | ✅          | 正常         |
| 3台中挂1台 | 2           | 2    | ✅          | 可以选出主      |
| 3台中挂2台 | 1           | 2    | ❌          | 无法形成多数派    |
| 2台部署   | 2           | 2    | ✅          | 理论上可以，但风险高 |
| 1台部署   | 1           | 1    | ✅（但失去HA意义） |            |

---

## 和 Raft 的区别（进阶）

Redis Sentinel 的投票逻辑与 Raft 相似，但更简单：

|特性|Sentinel|Raft|
|---|---|---|
|日志复制|❌ 无|✅ 有|
|Leader 任期号|✅ epoch|✅ term|
|选举过程|✅ 请求投票（一次性）|✅ 请求投票（带日志一致性检查）|
|多数派机制|✅|✅|
|一致性保证|弱一致（最终一致）|强一致（线性一致）|