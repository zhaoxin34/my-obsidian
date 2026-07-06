# Chrome Extension MV3 消息通信调试经验

## 使用场景

调试 Chrome Extension MV3 时，以下场景适用本经验：

1. Side Panel 与 Content Script 通信时响应丢失
2. Service Worker 中 `sendResponse` callback 收不到
3. 消息发送后 Promise 永远 pending
4. Side Panel 打开后无法获取正确的 active tab

典型错误关键字：`sendResponse`, `sendMessage`, `tabs.sendMessage`, `sidePanel`, `service worker`, `MV3`, `No response from background`

---

## 核心经验

### 1. Service Worker 生命周期导致 `sendResponse` 不可靠

MV3 Service Worker 在 idle 时会被 freeze，**Promise chain 中的 `sendResponse` 可能在消息送达前 SW 就已经休眠了**。

```
Side Panel ──sendMessage──► Background (SW) ──tabs.sendMessage──► Content Script
                    ▲                                                        │
                    └──────────────── sendResponse ─────────────────────────┘
```

```typescript
// ❌ 不可靠：SW 可能在 sendResponse 前 freeze
browser.tabs.sendMessage(tabId, msg).then(reply => {
  sendResponse({ ok: true, result: reply }); // 消息可能丢失
});

// ✅ 可靠：用主动 push 消息 + callId 路由
browser.tabs.sendMessage(tabId, msg).then(reply => {
  // 通过 callId 路由到正确的 Promise
  browser.runtime.sendMessage({ kind: "BT_RESULT", callId, result: reply });
});

// Side Panel 端注册 permanent listener
chrome.runtime.onMessage.addListener((raw) => {
  const msg = raw as { kind?: string; callId?: string; result?: unknown };
  if (msg?.kind === "BT_RESULT" && msg.callId) {
    const pending = pendingMap.get(msg.callId);
    pending?.resolve(msg.result);
  }
});
```

### 2. Side Panel 打开后 `active tab` 变成自身

点击扩展图标 → Chrome 先把焦点切到 side panel → `tabs.query({active: true})` 返回 side panel 自己而非目标网页。

```typescript
browser.action.onClicked.addListener(async (tab) => {
  lastClickedTabId = tab.id;  // 先保存 tab.id
  await browser.sidePanel.open({ tabId: tab.id });  // 再打开 panel（此时焦点已变）
  
  // 主动把 tabId 推送给 side panel
  browser.runtime.sendMessage({ kind: "BT_INIT_TAB", tabId: tab.id });
});
```

### 3. React Hook 中 `useCallback` 依赖变化导致无限循环

`useCallback` 的依赖是对象（如 `options`）时，每次渲染对象引用都不同，导致 hook 无限重建。

```typescript
// ❌ 死循环：options 每次渲染都是新引用
const fireReadyOnce = useCallback(() => {
  options.onReady?.(); // 这里又用 options
}, [options]);

// ✅ 用 ref 持有最新值
const onReadyRef = useRef(options.onReady);
const fireReadyOnce = useCallback(() => {
  onReadyRef.current?.();  // 读取 ref
}, []);  // 无依赖，永远稳定
```

### 4. Headless Chrome 无法测试 content script 注入

`--load-extension` 在 headless 模式下不自动注入 content scripts，且 `chrome.scripting` API 在 service worker 中不可用。

**只能用真实 Chrome 测试 extension**。

### 5. IIFE 与 Content Script 的 MAIN/ISOLATED world 隔离通信

Content Script 运行在 ISOLATED world，注入的 IIFE 运行在 MAIN world。两者通过 `window.postMessage` 通信最可靠。

```typescript
// Content Script（ISOLATED world）
window.addEventListener("message", (e) => {
  if (e.data?.type === "BT_CALL") {
    // 转发给 IIFE（MAIN world）
    window.postMessage({ type: "BT_REQUEST", action: e.data.action, payload: e.data.payload }, "*");
  }
});

// IIFE（MAIN world）
window.addEventListener("message", (e) => {
  if (e.data?.type === "BT_REQUEST") {
    const result = dispatch(e.data.action, e.data.payload);
    window.postMessage({ type: "BT_REPLY", id: e.data.id, result }, "*");
  }
});
```

---

## 架构决策总结

| 决策 | 原因 |
|------|------|
| 主动 push 消息 > sendResponse callback | SW 生命周期不可靠，可能在消息送达前 freeze |
| callId + Map 做路由 | 支持同一 action 并发调用 |
| BT_INIT_TAB 主动推送 tabId | 解决 side panel 打开后 active tab 变化问题 |
| Ref 而非闭包捕获 options | 避免 React 重渲染导致的无限循环 |
| IIFE 通过 window.postMessage 通信 | MAIN/ISOLATED world 隔离，postMessage 是最安全通道 |
