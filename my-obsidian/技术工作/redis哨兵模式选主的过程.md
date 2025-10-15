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