# rrweb 回放架构 — Controller 与 UI 分离经验

## 使用场景

- 在 React/Next.js 等非 Svelte 项目中集成 rrweb-player（@rrweb/replay v2.0.0-alpha.x）做回放
- 需要自定义 UI（多倍速、跳过不活跃、全屏、键盘快捷键等），但不想 fork Svelte 组件
- 想保持 UI 跟主项目设计系统一致（dark theme、shadcn/tailwind 等），不被 Svelte 默认样式绑架
- 同一个回放能力要复用到多个 UI（设计稿对比、视频教学、远程调试回放等）

**相关关键词**：
- `@rrweb/replay` v2 alpha
- `Replayer` class
- `setConfig({ speed, skipInactive })`
- 控制器模式 (Controller pattern)
- 事件订阅 vs 轮询
- `getMetaData().totalTime`

## 核心架构

```
┌─────────────────────────────────────────┐
│  React UI (presentational)               │  ← 纯展示
│  - 倍速 / skip / 全屏 / 进度条 / 按钮    │
└──────────────┬──────────────────────────┘
               │ 调用方法 + 订阅事件
┌──────────────▼──────────────────────────┐
│  ReplayerController (logic)              │  ← 状态封装
│  - play/pause/seek/setSpeed/...          │
│  - EventTarget 转发 timeupdate/finish... │
└──────────────┬──────────────────────────┘
               │ 包装
┌──────────────▼──────────────────────────┐
│  @rrweb/replay v2 Replayer class         │  ← 不动
└─────────────────────────────────────────┘
```

## 关键经验点

### 1. 运行时改 config 用 `setConfig()`，别改 `r.config.x`

rrweb v2 的 Replayer 内部用 XState 状态机管播放，config 字段（speed、skipInactive 等）必须在状态机里走 action 才能生效。直接赋值 `r.config.speed = 4` **不生效**。

```typescript
// ❌ 错误：直接赋值
replayer.config.speed = 4;

// ✅ 正确：用 setConfig（内部会发 SET_SPEED 事件给 speedService）
replayer.setConfig({ speed: 4 });
replayer.setConfig({ skipInactive: true });
```

源码位置（v2.0.0-alpha.20）：`rrweb.js` 里 `setConfig` 方法（约 15740 行）会：
- `this.config[key] = config[key]` 写新值
- 对 `speed` 调 `speedService.send({ type: "SET_SPEED", payload })`
- 对 `skipInactive === false` 调 `backToNormal()`

### 2. Replayer 没有 per-frame timeupdate 事件，自己 rAF 轮询

rrweb v2 Replayer 暴露的事件：`Start` / `Pause` / `Resume` / `Finish` / `SkipStart` / `SkipEnd` / `Resize` / `StateChange` / `Destroy`。**没有 timeupdate**。

进度条要跟着时间走，最简单的办法是 rAF 轮询 `getCurrentTime()`，对比上次值变了就通知 UI：

```typescript
private startTimeLoop(): void {
  const tick = () => {
    if (this.destroyed) return;
    const t = this.getCurrentTime();
    if (t !== this.lastEmittedTime) {
      this.lastEmittedTime = t;
      this.emit("timeupdate");  // 转发给 React UI
    }
    this.rafId = requestAnimationFrame(tick);
  };
  this.rafId = requestAnimationFrame(tick);
}
```

rAF 在 60Hz 下足够顺滑；如果回放暂停了 `getCurrentTime()` 不会变，rAF 也几乎不耗 CPU（浏览器自动 throttle）。

### 3. Controller 用 EventTarget 转事件，不要把 Replayer 实例直接给 React

```typescript
class ReplayerController {
  private replayer: Replayer;
  private listeners: EventMap = { timeupdate: new Set(), ... };
  
  on(event: ControllerEvent, cb: () => void): () => void {
    this.listeners[event].add(cb);
    return () => this.off(event, cb);  // 返回 unsubscribe
  }
  
  private emit(event: ControllerEvent) {
    for (const cb of this.listeners[event]) cb();
  }
}
```

React 侧用 `useEffect` 订阅：
```tsx
useEffect(() => {
  const off = controller.on("timeupdate", () => setCurrentTime(controller.getCurrentTime()));
  return off;  // 卸载时自动取消订阅
}, [controller]);
```

### 4. isPlaying 不要用「time < total」推断，要追踪事件

`replayer.service.state.matches("playing")` 能拿到状态机状态，但耦合到内部字符串。可读性差。**推荐**：在 Controller 里维护 `playingFlag` 字段，订阅 `start` / `pause` / `finish` 事件翻转它。

```typescript
this.replayer.on("start", () => { this.playingFlag = true; this.emit("playing"); });
this.replayer.on("pause", () => { this.playingFlag = false; this.emit("pause"); });
this.replayer.on("finish", () => { this.playingFlag = false; this.emit("finish"); });

isPlaying(): boolean { return this.playingFlag; }
```

### 5. 容器 ref 用 callback ref + state，别用 useRef

```tsx
// ❌ 错误：useRef 不会触发重渲染，container 还没 mount 时 effect 就跑了
const containerRef = useRef<HTMLDivElement | null>(null);
useEffect(() => { new Replayer(events, { root: containerRef.current! }); }, [events]);
// 结果：replayer 构造时 container 是 null，或 effect 跑了但 div 还没挂载

// ✅ 正确：callback ref + state，setState 触发重渲染，container 一定就绪
const [containerEl, setContainerEl] = useState<HTMLDivElement | null>(null);
useEffect(() => {
  if (!containerEl) return;
  const c = new ReplayerController({ container: containerEl, events });
  return () => c.destroy();
}, [containerEl, events]);
// JSX: <div ref={setContainerEl} ... />
```

### 6. iframe 容器加 `min-width: 100%` 才能在窄容器内横向滚动

rrweb 录的页面宽度是固定的（比如 1280px），但播放器容器可能只有 800px。UA stylesheet 给 iframe 加了 `max-width: 100%`，把 iframe 挤到容器宽度内 → 永远不会横向溢出 → 看不到横向滚动条。

修复 CSS：
```css
.player-scroll .replayer-wrapper {
  display: inline-block;
  min-width: 100%;  /* wrapper 至少跟容器等宽 */
}
.player-scroll iframe {
  display: block;
  max-width: none !important;  /* 拒绝 UA 默认压缩 */
  max-height: none !important;
}
```

### 7. 横向 overflow 时 body 不要被撑大

如果 player 容器里有宽内容（比如 iframe 2560px）但被外层 `overflow: hidden` 裁了，**body 仍可能被撑大**。症状：滚动条出现、右侧控件被切、body.scrollWidth > viewport。

修复：在最外层 flex layout 的 main 元素加 `min-w-0 overflow-x-hidden`：

```tsx
// layout.tsx
<main className="flex-1 p-6 min-w-0 overflow-x-hidden">
  {children}
</main>
```

`min-w-0` 让 flex item 能缩到比内容固有宽度还小（默认是 `min-width: auto` = 内容最小宽度），配合 `overflow-x-hidden` 切掉溢出的视觉。

## 完整 Controller 骨架

```typescript
import { Replayer } from "@rrweb/replay";
import type { eventWithTime, playerMetaData } from "@rrweb/types";

export type ControllerEvent = 
  | "timeupdate" | "playing" | "pause" | "finish" 
  | "skipstart" | "skipend" | "resize" | "destroy";

export class ReplayerController {
  private replayer: Replayer;
  private listeners: Record<ControllerEvent, Set<() => void>>;
  private rafId: number | null = null;
  private lastEmittedTime = -1;
  private playingFlag = false;
  private destroyed = false;
  private opts: { container: HTMLElement; events: eventWithTime[]; 
                  speed: 1|2|4|8; skipInactive: boolean; 
                  timeupdateIntervalMs: number };
  
  constructor(opts: {
    container: HTMLElement;
    events: eventWithTime[];
    speed?: 1|2|4|8;
    skipInactive?: boolean;
  }) {
    this.opts = { 
      container: opts.container, 
      events: opts.events,
      speed: opts.speed ?? 1,
      skipInactive: opts.skipInactive ?? false,
      timeupdateIntervalMs: 16,
    };
    
    this.replayer = new Replayer(opts.events, {
      root: opts.container,
      mouseTail: false,
      speed: this.opts.speed,
      skipInactive: this.opts.skipInactive,
    });
    
    // 事件转发
    this.replayer.on("finish", () => { this.playingFlag = false; this.emit("finish"); });
    this.replayer.on("pause", () => { this.playingFlag = false; this.emit("pause"); });
    this.replayer.on("start", () => { this.playingFlag = true; this.emit("playing"); });
    this.replayer.on("skip-start", () => this.emit("skipstart"));
    this.replayer.on("skip-end", () => this.emit("skipend"));
    
    this.startTimeLoop();
  }
  
  play() { this.replayer.play(); }
  pause() { this.replayer.pause(); }
  togglePlay() { 
    if (this.isPlaying()) { this.pause(); return false; }
    this.play(); return true;
  }
  seek(ms: number) {
    const clamped = Math.max(0, Math.min(ms, this.getTotalTime()));
    this.replayer.pause();
    this.replayer.play(clamped);
  }
  getCurrentTime() { return this.replayer.getCurrentTime(); }
  getTotalTime() { return this.replayer.getMetaData().totalTime; }
  getMetaData(): playerMetaData { return this.replayer.getMetaData(); }
  isPlaying() { return this.playingFlag; }
  
  setSpeed(s: 1|2|4|8) {
    this.opts.speed = s;
    this.replayer.setConfig({ speed: s });
  }
  setSkipInactive(v: boolean) {
    this.opts.skipInactive = v;
    this.replayer.setConfig({ skipInactive: v });
  }
  
  // events
  on(event: ControllerEvent, cb: () => void): () => void {
    this.listeners[event].add(cb);
    return () => this.off(event, cb);
  }
  off(event: ControllerEvent, cb: () => void) {
    this.listeners[event].delete(cb);
  }
  private emit(event: ControllerEvent) {
    for (const cb of this.listeners[event]) cb();
  }
  
  private startTimeLoop() {
    if (typeof window === "undefined") return;
    const tick = () => {
      if (this.destroyed) return;
      const t = this.getCurrentTime();
      if (t !== this.lastEmittedTime) {
        this.lastEmittedTime = t;
        this.emit("timeupdate");
      }
      this.rafId = window.requestAnimationFrame(tick);
    };
    this.rafId = window.requestAnimationFrame(tick);
  }
  
  destroy() {
    if (this.destroyed) return;
    this.destroyed = true;
    if (this.rafId !== null) window.cancelAnimationFrame(this.rafId);
    try { this.replayer.destroy(); } catch {}
    for (const k of Object.keys(this.listeners)) {
      this.listeners[k as ControllerEvent].clear();
    }
  }
}
```

## 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **iframe 嵌入 rrweb-player（Svelte）** | 自带完整 UI | 跨 iframe 状态同步复杂、样式与主项目脱节、调试难 |
| **直接用 Replayer + 写 React UI（推荐）** | 跟主项目设计一致、状态可预测、调试容易、可扩展 | 需自己写 ~200 行 UI 壳 |
| **fork rrweb-player Svelte 源码改写** | 100% 控制 | 维护成本高，rrweb 升级时同步成本大 |

## 常见坑

| 症状 | 原因 | 修法 |
|------|------|------|
| 调了 setSpeed(4) 没反应 | 直接 `r.config.speed = 4` 绕过状态机 | 用 `r.setConfig({ speed: 4 })` |
| 进度条不动 | Replayer 没 timeupdate 事件 | 自己 rAF 轮询 `getCurrentTime()` |
| 切了 segment 但从头开始播 | `play(ms)` 没先 pause | `seek` 要 pause + play(ms) 两步 |
| 播放按钮灰色不可用 | container ref 用 useRef 时 div 还没 mount | 改 callback ref + state，effect 依赖 containerEl |
| iframe 被挤窄不溢出 | UA 把 iframe max-width 100% | wrapper `display:inline-block; min-width:100%` + iframe `max-width:none !important` |
| body 被撑大横向滚动 | flex item 内容固有宽度大 | main 加 `min-w-0 overflow-x-hidden` |
| 切换 segments 跳到中间但从头播 | 没区分 segment 时间 vs 全局时间 | 每个 segment 第一个 event.timestamp - 第一个 segment 第一个 event.timestamp = offsetMs |

## 扩展方向

- **annotation 系统**：在 `timeupdate` 里检查当前时间是否跨过 annotation 区间，弹 toast
- **多 segment 拼接连播**：把多个 segment 的 events flatten 后给 Replayer，annotation 用全局 ms
- **frame 索引**：`getEventAtTime(ms)` 二分搜索最近 event，把 event 索引存到 annotation 用于精确 seek
- **远程调试回放**：Controller 完全无 DOM 依赖（除了 container），可以把整个类抽到 worker 里做纯逻辑
