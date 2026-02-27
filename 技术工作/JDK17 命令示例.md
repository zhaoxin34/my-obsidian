---
title: JDK 17 ZGC 启动命令示例
date: 2024-01-15
tags:
  - java
  - jdk17
  - zgc
  - 性能调优
---

# JDK 17 ZGC 启动命令

> [!tip] 适用场景
> ZGC 适用于需要低延迟、大内存（>8GB） 的应用，如实时系统、大数据处理等。

## 完整命令

```bash
java -Xms1g -Xmx2g \
     -XX:+UseZGC \
     -Xlog:gc*,gc+heap=trace,gc+ref=debug,gc+age=debug:file=/path/to/your/logs/gc-logs.txt \
     -XX:MaxGCPauseMillis=200 \
     -XX:InitiatingHeapOccupancyPercent=45 \
     -XX:ZAllocationSpikeTolerance=2.0 \
     -XX:ZCollectionInterval=5 \
     -XX:ZFragmentationLimit=25 \
     -XX:+ZProactive \
     -XX:+ZUncommit \
     -XX:ZUncommitDelay=300 \
     -jar your-application.jar
```

## 参数速查表

| 参数 | 默认值 | 说明 |
|:-----|:-------|:-----|
| `-Xms1g` | - | 初始堆大小 |
| `-Xmx2g` | - | 最大堆大小 |
| `-XX:+UseZGC` | - | 启用 ZGC 垃圾回收器 |
| `-XX:MaxGCPauseMillis=200` | 200 | 最大 GC 暂停目标（毫秒） |
| `-XX:InitiatingHeapOccupancyPercent=45` | 45 | 触发并发标记的堆占用阈值（%） |
| `-XX:ZAllocationSpikeTolerance=2.0` | 2.0 | 分配波动容忍度系数 |
| `-XX:ZCollectionInterval=5` | 0 | 最大 GC 间隔（秒），0 表示禁用 |
| `-XX:ZFragmentationLimit=25` | 25 | 最大碎片化限制（%） |
| `-XX:+ZProactive` | 开启 | 启用主动 GC 周期 |
| `-XX:+ZUncommit` | 开启 | 启用内存释放（取消提交） |
| `-XX:ZUncommitDelay=300` | 300 | 内存释放延迟（秒） |

## 详细说明

### 堆内存配置

- **`-Xms1g -Xmx2g`**: 设置堆的初始大小为 1GB，最大大小为 2GB。

### ZGC 核心配置

- **`-XX:+UseZGC`**: 启用 ZGC 作为垃圾回收器。
- **`-XX:+ZProactive`**: 启用 ZGC 的主动 GC 周期，提前触发垃圾回收。
- **`-XX:+ZUncommit`**: 启用 ZGC 的内存释放功能，回收未使用的堆内存。

### 性能调优

- **`-XX:MaxGCPauseMillis=200`**: 设置最大 GC 暂停时间为 200 毫秒。
- **`-XX:InitiatingHeapOccupancyPercent=45`**: 设置当堆占用率达到 45% 时开始并发标记过程。
- **`-XX:ZAllocationSpikeTolerance=2.0`**: 设置 ZGC 的分配波动容忍度。
- **`-XX:ZCollectionInterval=5`**: 设置 ZGC 最大收集间隔为 5 秒。
- **`-XX:ZFragmentationLimit=25`**: 设置 ZGC 最大碎片化限制为 25%。
- **`-XX:ZUncommitDelay=300`**: 设置 ZGC 取消提交内存的延迟时间为 300 秒（5 分钟）。

### GC 日志配置

- **`-Xlog:gc*`**: 启用 GC 日志，记录与 GC 相关的所有事件。
- **`gc+heap=trace,gc+ref=debug,gc+age=debug:file=/path/to/your/logs/gc-logs.txt`**: 将 GC 日志输出到文件，包含堆、引用和年龄相关详细信息。

> [!warning] 注意
> 确保将 `your-application.jar` 替换为您实际应用的 JAR 文件路径，并根据需要调整日志路径。

---

**相关文档**: [[JVM 性能调优]] |分析]] [[GC 日志