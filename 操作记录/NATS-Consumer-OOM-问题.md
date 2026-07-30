# NATS Consumer OOM 问题排查

## 问题

agent-server dev 模式启动后 OOM 崩溃（FatalProcessOutOfMemory）。

## 根因

1. **FeedInbox/InquirerRegistry drain loop** 使用 `while (!this.stopped)` + `await fetch()` 循环。`await` 在循环中累积调用栈，每次 fetch 超时（5s）后重新开始，导致深度异步调用链。

2. **setImmediate 提前触发**：用 `setImmediate(() => consumeLoop())` 延迟启动。在 dev 模式 webpack HMR 初始化期间，GC 触发 `setImmediate` 提前执行，导致 NATS consumer + webpack 同时吃内存。

3. **真正的触发者**：bb-client（Chrome 扩展）连接后，pi agent 初始化吃大量内存。FeedInbox/InquirerRegistry 的 `setTimeout(8s/10s)` 延迟反而躲开了 webpack init，但 bb-client 触发的 pi agent 是躲不开的。

## 修复

### FeedInbox drain loop

**问题**：深度异步调用栈 + `while (!this.stopped)` 无限 await

**修复**：
```typescript
// 改用 setTimeout 调度，避免深度 async 调用栈
private drainLoop(): void {
    if (this.stopped || !this.consumer) return;
    this.consumer
        .fetch({ max_messages: 50, expires: 5_000 })
        .then(async (iter) => {
            for await (const m of iter) {
                if (this.stopped) break;
                // 处理消息...
            }
            // 调度下一批
            if (!this.stopped) setTimeout(() => this.drainLoop(), 0);
        })
        .catch((err) => {
            if (this.stopped) return;
            setTimeout(() => this.drainLoop(), 1_000); // 错误时延迟重试
        });
}
```

### InquirerRegistry consume loop

**问题**：`setImmediate` 在 GC 时提前触发

**修复**：
```typescript
// 用 setTimeout 延迟 8 秒，等 webpack HMR 完成
setTimeout(() => {
    if (this.stopped) return;
    void this.consumeLoop();
}, 8_000);
```

## 验证方法

```bash
cd agent-server
npm test  # 155 tests pass
npx tsc --noEmit  # no errors
```

## 关键文件

- `lib/proactive/observer/feed-queue.ts`：FeedInbox drain loop
- `lib/proactive/inquirer/registry.ts`：InquirerRegistry consume loop

## 经验教训

- `setImmediate` 不等于"延迟到下一轮事件循环"——GC 期间可能提前触发
- `while + await` 在循环中会累积调用栈，应该用 `setTimeout` 显式调度
- dev server OOM 不一定是代码 bug，可能是机器内存紧张 + pi agent 太重
