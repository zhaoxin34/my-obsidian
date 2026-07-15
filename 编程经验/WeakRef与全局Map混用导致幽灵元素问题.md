# WeakRef 与全局 Map 混用导致幽灵元素问题

## 使用场景

当使用 WeakRef 追踪对象身份，同时用全局 Map 持有对象引用时适用本经验：

1. 使用 `WeakRef` + Map 做"ID → 对象"映射
2. 对象从 DOM 移除后，仍能通过 ID 找到它
3. 操作（如 click）返回成功但实际无效
4. 调试时发现"元素还在 Map 里"但"不在 DOM 里"

典型错误关键字：`WeakRef`, `deref`, `element not in DOM`, `stale reference`, `click returns ok but does nothing`

---

## 核心经验

### 1. 问题根源：WeakRef 保护对象不被 GC，但 Map 持有强引用

```typescript
// 增量 Snapshot 的设计
class IncrementalSnapshot {
  private byId = new Map<NodeId, BaselineEntry>();  // 强引用！
  private byElement = new Map<Element, NodeId>();
  
  // BaselineEntry 中使用了 WeakRef
  // 但 Map<NodeId, BaselineEntry> 持有强引用！
}

interface BaselineEntry {
  id: NodeId;
  elementRef: WeakRef<Element>;  // WeakRef 只是备用
  snapshot: SnapshotNode;
}
```

### 2. 症状：元素被移除，但 ID 仍可用

```javascript
// 第一次 snapshot
const r1 = inc.take();
// r1.nodes[0].id = "e5"

// 模拟 DOM 更新：元素被移除
document.getElementById("some-element").remove();

// 第二次 snapshot
const r2 = inc.take();
// r2.diff.removed 包含 "e5" ✓ 正确识别

// 但全局 Map 仍持有引用
BT.getElementById("e5")  // 返回元素对象（非 null）
element.closest("body")   // 返回 null ！元素不在 DOM 中

// click 看似成功，但实际无效
BT.click("e5")  // 返回 { ok: true }  ← 陷阱！
```

### 3. 为什么 click 返回 ok=true

```typescript
// click.ts 中的检查
function clickLegacy(id: NodeId, nodes?: NodesInput): OperationResult {
  // 只检查 id 是否在 Map 中，不检查元素是否在 DOM 中
  if (!getElementById(id)) {  // Map.get() 永远返回非 null
    return { ok: false, message: `找不到` };
  }
  // ...
  return { ok: true, id };  // 永远返回 ok！
}
```

### 4. 后果：事件触发，但框架状态不更新

即使 click 事件处理器被触发，对于 Vue/React 组件：
- 事件处理器绑定了旧组件实例
- DOM 更新后，新组件实例是不同对象
- 点击触发旧处理器，但不会更新新组件的状态

---

## 解决方案

### 方案 1：在 API 层面检查元素是否在 DOM 中

```typescript
function clickLegacy(id: NodeId, nodes?: NodesInput): OperationResult {
  const el = getElementById(id);
  if (!el) {
    return { ok: false, message: `id=${id} 找不到对应的元素` };
  }
  
  // 新增检查：元素是否在 DOM 中
  if (!el.closest("body")) {
    return { ok: false, message: `id=${id} 元素已不在 DOM 中` };
  }
  
  // ... 继续 click
}
```

### 方案 2：增量 Snapshot 清理时同步清理全局引用

```typescript
class IncrementalSnapshot {
  // 需要访问 refs.ts 的 unregisterElement
  private onElementRemoved(el: Element, id: NodeId) {
    unregisterElement(id);  // 新增：清理全局引用
    this.byElement.delete(el);
  }
}
```

### 方案 3：使用前检查 diff.removed

```javascript
const r = inc.take();
if (r.diff.removed.includes(targetId)) {
  console.log("Element was removed, cannot click");
  return;
}
await BT.click(targetId);
```

---

## 架构决策总结

| 决策 | 权衡 |
|------|------|
| 使用 WeakRef 追踪元素 | 允许 GC，内存不会泄漏 |
| 使用 Map 持有 BaselineEntry | BaselineEntry 包含完整 snapshot，不能 GC |
| 全局 Map 持有元素强引用 | API 简单，但会导致幽灵元素 |
| 点击前不检查 DOM 在场 | 性能好，但语义不正确 |

---

## 设计建议

如果重新设计，应该：

1. **分离关注点**：
   - 元素身份追踪（WeakRef）
   - 元素引用持有（按需）
   - 全局 ID 注册（可选，非必须）

2. **API 语义清晰**：
   - `getElementById(id)` 返回 `Element | null`
   - 如果元素不在 DOM 中，返回 `null` 而不是幽灵引用

3. **或者接受当前行为**：
   - 在文档中明确说明"返回成功不代表元素有效"
   - 让调用方负责检查 `diff.removed`
