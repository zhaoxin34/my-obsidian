# rrweb 录制时长分段限制经验

## 使用场景

- 使用 rrweb 录制用户操作时，单个录像文件过大导致加载慢、传输困难
- 需要将长时间录制拆分为多个小文件，每隔固定时间自动生成新录像段
- 需要支持增量存储和传输，或更细粒度的回放控制

**相关关键词**：
- `rrweb.record`
- `checkoutEveryNms`
- `emit(event, isCheckout)`
- 录像分段、自动切割

## 问题背景

使用 rrweb 默认录制时，所有事件会累积在一个数组中，长时间录制会导致：
1. 内存占用持续增长
2. 最终文件过大（可能数百 MB）
3. 回放加载缓慢

## 解决方案

### 核心 API：`checkoutEveryNms`

rrweb 提供 `checkoutEveryNms` 配置选项，可以每隔 N 毫秒自动生成一个完整快照（checkout），触发新的录制段。

### 代码示例

```typescript
import { record } from '@rrweb/record';

interface SegmentManager {
  // 分段存储，每段独立管理
  segments: Map<string, event[]> = new Map();
  currentSegmentId: string = '';
  
  startNewSegment() {
    this.currentSegmentId = `segment_${Date.now()}`;
    this.segments.set(this.currentSegmentId, []);
  }
  
  addEvent(event: event) {
    const segment = this.segments.get(this.currentSegmentId);
    if (segment) {
      segment.push(event);
    }
  }
  
  async saveCurrentSegment() {
    const segment = this.segments.get(this.currentSegmentId);
    if (segment && segment.length > 0) {
      // 上传到后端或保存到 IndexedDB
      await this.saveToBackend(this.currentSegmentId, segment);
    }
  }
}

// 使用
const manager = new SegmentManager();
manager.startNewSegment(); // 初始化第一段

const stopFn = record({
  emit(event, isCheckout) {
    // isCheckout 为 true 时，表示进入了新的段落
    if (isCheckout) {
      // 保存上一段，开始新段
      manager.saveCurrentSegment();
      manager.startNewSegment();
    }
    manager.addEvent(event);
  },
  checkoutEveryNms: 10 * 60 * 1000, // 每10分钟生成新段落
});

// 回放时合并所有段
function mergeSegments(segments: event[][]): event[] {
  return segments.flat().sort((a, b) => a.timestamp - b.timestamp);
}
```

## 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| `checkoutEveryNms` | rrweb 原生支持，可靠性高 | 每段开始会有完整快照，数据略大 |
| 手动定时 stop/start | 控制更灵活 | 需要手动管理状态，可能丢事件 |
| 事件数量阈值 | 大小可控 | 时间不固定，可能过长或过短 |

## 额外优化建议

1. **压缩传输**：事件数据 gzip 压缩后再传输
2. **增量上传**：每段录制完成后立即上传，而非等全部结束后
3. **Metadata 记录**：记录每段的时间范围，方便随机访问
4. **内存控制**：定期清理已上传的段，避免内存持续增长

## 注意事项

- `checkoutEveryNms` 的实际触发时间会有一定误差（约 0-2 秒），因为依赖事件触发检测
- 每段开始时会生成一个完整快照（full snapshot），这是 rrweb 增量同步机制的要求
- 回放时需要按时间戳排序合并所有段的事件