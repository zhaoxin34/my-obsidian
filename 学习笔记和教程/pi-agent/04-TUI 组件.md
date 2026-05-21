# TUI Components

> 原文: https://pi.dev/docs/latest/tui

扩展和自定义工具可以渲染自定义 TUI 组件以实现交互式用户界面。本页涵盖组件系统和可用的构建块。

**源码:** [`@earendil-works/pi-tui`](https://github.com/earendil-works/pi-mono/tree/main/packages/tui)

## 组件接口

所有组件实现:

```typescript
interface Component {
  render(width: number): string[];
  handleInput?(data: string): void;
  wantsKeyRelease?: boolean;
  invalidate(): void;
}
```

| 方法                 | 描述                                                        |
| -------------------- | ----------------------------------------------------------- |
| `render(width)`      | 返回字符串数组 (每行一个)。每行**必须不超过 `width`**。     |
| `handleInput?(data)` | 当组件有焦点时接收键盘输入。                                |
| `wantsKeyRelease?`   | 如果为 true，组件接收键释放事件 (Kitty 协议)。默认: false。 |
| `invalidate()`       | 清除缓存的渲染状态。在主题更改时调用。                      |

TUI 在每个渲染行的末尾追加完整的 SGR 重置和 OSC 8 重置。样式不会跨行携带。如果发出带样式的多行文本，每行重新应用样式或使用 `wrapTextWithAnsi()` 以便为每个换行行保留样式。

## Focusable 接口 (IME 支持)

显示文本光标且需要 IME (输入法编辑器) 支持的组件应实现 `Focusable` 接口:

```typescript
import {
  CURSOR_MARKER,
  type Component,
  type Focusable,
} from "@earendil-works/pi-tui";

class MyInput implements Component, Focusable {
  focused: boolean = false; // TUI 焦点变化时设置

  render(width: number): string[] {
    const marker = this.focused ? CURSOR_MARKER : "";
    // 在假光标前发出标记
    return [
      `> ${beforeCursor}${marker}\x1b[7m${atCursor}\x1b[27m${afterCursor}`,
    ];
  }
}
```

当 `Focusable` 组件有焦点时，TUI:

1. 在组件上设置 `focused = true`
2. 在渲染输出中扫描 `CURSOR_MARKER` (零宽 APC 转义序列)
3. 在该位置定位硬件终端光标
4. 显示硬件光标

这使得 CJK 输入法的候选窗口出现在 IME 输入的正确位置。内置 `Editor` 和 `Input` 组件已实现此接口。

### 嵌入输入的容器组件

当容器组件 (对话框、选择器等) 包含 `Input` 或 `Editor` 子组件时，容器必须实现 `Focusable` 并将焦点状态传播到子组件。否则，硬件光标将无法为 IME 输入正确定位。

```typescript
import { Container, type Focusable, Input } from "@earendil-works/pi-tui";

class SearchDialog extends Container implements Focusable {
  private searchInput: Input;

  // Focusable 实现 - 传播到子输入以实现 IME 光标定位
  private _focused = false;
  get focused(): boolean {
    return this._focused;
  }
  set focused(value: boolean) {
    this._focused = value;
    this.searchInput.focused = value;
  }

  constructor() {
    super();
    this.searchInput = new Input();
    this.addChild(this.searchInput);
  }
}
```

没有此传播，使用 IME (中文、日文、韩文等) 输入时光标候选窗口会在屏幕上显示在错误位置。

## 使用组件

**在扩展中** 通过 `ctx.ui.custom()`:

```typescript
pi.on("session_start", async (_event, ctx) => {
  const handle = ctx.ui.custom(myComponent);
  // handle.requestRender() - 触发重新渲染
  // handle.close() - 恢复正常 UI
});
```

**在自定义工具中** 通过 `pi.ui.custom()`:

```typescript
async execute(toolCallId, params, onUpdate, ctx, signal) {
  const handle = pi.ui.custom(myComponent);
  // ...
  handle.close();
}
```

## 覆盖层

覆盖层在现有内容之上渲染组件而不清除屏幕。传递 `{ overlay: true }` 给 `ctx.ui.custom()`:

```typescript
const result = await ctx.ui.custom<string | null>(
  (tui, theme, keybindings, done) => new MyDialog({ onClose: done }),
  { overlay: true },
);
```

对于定位和大小，使用 `overlayOptions`:

```typescript
const result = await ctx.ui.custom<string | null>(
  (tui, theme, keybindings, done) => new SidePanel({ onClose: done }),
  {
    overlay: true,
    overlayOptions: {
      // 大小: 数字或百分比字符串
      width: "50%", // 终端宽度的 50%
      minWidth: 40, // 最小 40 列
      maxHeight: "80%", // 最大终端高度的 80%

      // 位置: 基于锚点 (默认: "center")
      anchor: "right-center", // 9 个位置: center, top-left, top-center 等
      offsetX: -2, // 从锚点的偏移
      offsetY: 0,

      // 边距
      margin: 2, // 所有边，或 { top, right, bottom, left }
    },
  },
);
```

### 覆盖层生命周期

覆盖层组件在关闭时释放。不要重用引用 - 创建新实例:

```typescript
// 错误 - 过时的引用
let menu: MenuComponent;
await ctx.ui.custom(
  (_, __, ___, done) => {
    menu = new MenuComponent(done);
    return menu;
  },
  { overlay: true },
);
setActiveComponent(menu); // 已释放

// 正确 - 重新调用以重新显示
const showMenu = () =>
  ctx.ui.custom((_, __, ___, done) => new MenuComponent(done), {
    overlay: true,
  });

await showMenu(); // 第一次显示
await showMenu(); // "返回" = 再次调用
```

## 内置组件

从 `@earendil-works/pi-tui` 导入:

```typescript
import { Text, Box, Container, Spacer, Markdown } from "@earendil-works/pi-tui";
```

### Text

带自动换行的多行文本。

```typescript
const text = new Text("Hello World", 1, 1, (s) => bgGray(s));
text.setText("Updated");
```

### Box

带填充和背景色的容器。

```typescript
const box = new Box(1, 1, (s) => bgGray(s));
box.addChild(new Text("Content", 0, 0));
box.setBgFn((s) => bgBlue(s));
```

### Container

垂直分组子组件。

```typescript
const container = new Container();
container.addChild(component1);
container.addChild(component2);
container.removeChild(component1);
```

### Spacer

空垂直空间。

```typescript
const spacer = new Spacer(2); // 2 个空行
```

### Markdown

带语法高亮的 markdown 渲染。

```typescript
const md = new Markdown("# Title\n\nSome **bold** text", 1, 1, theme);
md.setText("Updated markdown");
```

### Image

在支持的终端中渲染图像 (Kitty, iTerm2, Ghostty, WezTerm)。

```typescript
const image = new Image(base64Data, "image/png", theme, {
  maxWidthCells: 80,
  maxHeightCells: 24,
});
```

## 键盘输入

使用 `matchesKey()` 进行键检测:

```typescript
import { matchesKey, Key } from "@earendil-works/pi-tui";

handleInput(data: string) {
  if (matchesKey(data, Key.up)) {
    this.selectedIndex--;
  } else if (matchesKey(data, Key.enter)) {
    this.onSelect?.(this.selectedIndex);
  } else if (matchesKey(data, Key.escape)) {
    this.onCancel?.();
  } else if (matchesKey(data, Key.ctrl("c"))) {
    // Ctrl+C
  }
}
```

**键标识符**:

- 基本键: `Key.enter`, `Key.escape`, `Key.tab`, `Key.space`, `Key.backspace`, `Key.delete`, `Key.home`, `Key.end`
- 方向键: `Key.up`, `Key.down`, `Key.left`, `Key.right`
- 带修饰符: `Key.ctrl("c")`, `Key.shift("tab")`, `Key.alt("left")`, `Key.ctrlShift("p")`
- 字符串格式: `"enter"`, `"ctrl+c"`, `"shift+tab"`, `"ctrl+shift+p"`

## 行宽

**关键:** `render()` 的每行必须不超过 `width` 参数。

```typescript
import { visibleWidth, truncateToWidth } from "@earendil-works/pi-tui";

render(width: number): string[] {
  // 截断长行
  return [truncateToWidth(this.text, width)];
}
```

工具:

- `visibleWidth(str)` - 获取显示宽度 (忽略 ANSI 代码)
- `truncateToWidth(str, width, ellipsis?)` - 带可选省略号的截断
- `wrapTextWithAnsi(str, width)` - 自动换行保留 ANSI 代码

## 创建自定义组件

示例: 交互式选择器

```typescript
import { matchesKey, Key, truncateToWidth } from "@earendil-works/pi-tui";

class MySelector {
  private items: string[];
  private selected = 0;
  private cachedWidth?: number;
  private cachedLines?: string[];

  public onSelect?: (item: string) => void;
  public onCancel?: () => void;

  constructor(items: string[]) {
    this.items = items;
  }

  handleInput(data: string): void {
    if (matchesKey(data, Key.up) && this.selected > 0) {
      this.selected--;
      this.invalidate();
    } else if (
      matchesKey(data, Key.down) &&
      this.selected < this.items.length - 1
    ) {
      this.selected++;
      this.invalidate();
    } else if (matchesKey(data, Key.enter)) {
      this.onSelect?.(this.items[this.selected]);
    } else if (matchesKey(data, Key.escape)) {
      this.onCancel?.();
    }
  }

  render(width: number): string[] {
    if (this.cachedLines && this.cachedWidth === width) {
      return this.cachedLines;
    }

    this.cachedLines = this.items.map((item, i) => {
      const prefix = i === this.selected ? "> " : "  ";
      return truncateToWidth(prefix + item, width);
    });
    this.cachedWidth = width;
    return this.cachedLines;
  }

  invalidate(): void {
    this.cachedWidth = undefined;
    this.cachedLines = undefined;
  }
}
```

在扩展中使用:

```typescript
pi.registerCommand("pick", {
  description: "Pick an item",
  handler: async (args, ctx) => {
    const items = ["Option A", "Option B", "Option C"];
    const selector = new MySelector(items);

    let handle: { close: () => void; requestRender: () => void };

    await new Promise<void>((resolve) => {
      selector.onSelect = (item) => {
        ctx.ui.notify(`Selected: ${item}`, "info");
        handle.close();
        resolve();
      };
      selector.onCancel = () => {
        handle.close();
        resolve();
      };
      handle = ctx.ui.custom(selector);
    });
  },
});
```

## 主题

组件接受用于样式的主题对象。

**在 `renderCall`/`renderResult`** 中，使用 `theme` 参数:

```typescript
renderResult(result, options, theme, context) {
  // 使用 theme.fg() 获取前景色
  return new Text(theme.fg("success", "Done!"), 0, 0);

  // 使用 theme.bg() 获取背景色
  const styled = theme.bg("toolPendingBg", theme.fg("accent", "text"));
}
```

**前景色** (`theme.fg(color, text)`):

| 类别     | 颜色                                                         |
| -------- | ------------------------------------------------------------ |
| 通用     | `text`, `accent`, `muted`, `dim`                             |
| 状态     | `success`, `error`, `warning`                                |
| 边框     | `border`, `borderAccent`, `borderMuted`                      |
| 消息     | `userMessageText`, `customMessageText`, `customMessageLabel` |
| 工具     | `toolTitle`, `toolOutput`                                    |
| Markdown | `mdHeading`, `mdLink`, `mdCode`, 等                          |

**背景色** (`theme.bg(color, text)`):

`selectedBg`, `userMessageBg`, `customMessageBg`, `toolPendingBg`, `toolSuccessBg`, `toolErrorBg`

**对于 Markdown**，使用 `getMarkdownTheme()`:

```typescript
import { getMarkdownTheme } from "@earendil-works/pi-coding-agent";
import { Markdown } from "@earendil-works/pi-tui";

renderResult(result, options, theme, context) {
  const mdTheme = getMarkdownTheme();
  return new Markdown(result.details.markdown, 0, 0, mdTheme);
}
```

## 性能

尽可能缓存渲染输出:

```typescript
class CachedComponent {
  private cachedWidth?: number;
  private cachedLines?: string[];

  render(width: number): string[] {
    if (this.cachedLines && this.cachedWidth === width) {
      return this.cachedLines;
    }
    // ... 计算行 ...
    this.cachedWidth = width;
    this.cachedLines = lines;
    return lines;
  }

  invalidate(): void {
    this.cachedWidth = undefined;
    this.cachedLines = undefined;
  }
}
```

状态更改时调用 `invalidate()`，然后 `handle.requestRender()` 触发重新渲染。

## 失效和主题更改

当主题更改时，TUI 调用所有组件上的 `invalidate()` 以清除它们的缓存。组件必须正确实现 `invalidate()` 以确保主题更改生效。

### 问题

如果组件将主题颜色预烘焙成字符串 (通过 `theme.fg()`、`theme.bg()` 等) 并缓存它们，缓存的字符串包含来自旧主题的 ANSI 转义代码。简单地清除渲染缓存是不够的如果组件单独存储主题内容。

### 解决方案

使用主题颜色构建内容的组件必须在 `invalidate()` 时重建该内容:

```typescript
class GoodComponent extends Container {
  private message: string;
  private content: Text;

  constructor(message: string) {
    super();
    this.message = message;
    this.content = new Text("", 1, 0);
    this.addChild(this.content);
    this.updateDisplay();
  }

  private updateDisplay(): void {
    // 使用当前主题重建内容
    this.content.setText(theme.fg("accent", this.message));
  }

  override invalidate(): void {
    super.invalidate(); // 清除子缓存
    this.updateDisplay(); // 使用新主题重建
  }
}
```

### 模式: 在失效时重建

对于有复杂内容的组件:

```typescript
class ComplexComponent extends Container {
  private data: SomeData;

  constructor(data: SomeData) {
    super();
    this.data = data;
    this.rebuild();
  }

  private rebuild(): void {
    this.clear(); // 移除所有子组件

    // 使用当前主题构建 UI
    this.addChild(new Text(theme.fg("accent", theme.bold("Title")), 1, 0));
    this.addChild(new Spacer(1));

    for (const item of this.data.items) {
      const color = item.active ? "success" : "muted";
      this.addChild(new Text(theme.fg(color, item.label), 1, 0));
    }
  }

  override invalidate(): void {
    super.invalidate();
    this.rebuild();
  }
}
```

## 常见模式

这些模式涵盖扩展中最常见的 UI 需求。

### 模式 1: 选择对话框 (SelectList)

让用户从选项列表中选择。使用 `SelectList` 和 `DynamicBorder` 进行框架。

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { DynamicBorder } from "@earendil-works/pi-coding-agent";
import {
  Container,
  type SelectItem,
  SelectList,
  Text,
} from "@earendil-works/pi-tui";

pi.registerCommand("pick", {
  handler: async (_args, ctx) => {
    const items: SelectItem[] = [
      { value: "opt1", label: "Option 1", description: "First option" },
      { value: "opt2", label: "Option 2", description: "Second option" },
    ];

    const result = await ctx.ui.custom<string | null>(
      (tui, theme, _kb, done) => {
        const container = new Container();

        // 顶部边框
        container.addChild(
          new DynamicBorder((s: string) => theme.fg("accent", s)),
        );

        // 标题
        container.addChild(
          new Text(theme.fg("accent", theme.bold("Pick an Option")), 1, 0),
        );

        // 带主题的 SelectList
        const selectList = new SelectList(items, Math.min(items.length, 10), {
          selectedPrefix: (t) => theme.fg("accent", t),
          selectedText: (t) => theme.fg("accent", t),
          description: (t) => theme.fg("muted", t),
          scrollInfo: (t) => theme.fg("dim", t),
          noMatch: (t) => theme.fg("warning", t),
        });
        selectList.onSelect = (item) => done(item.value);
        selectList.onCancel = () => done(null);
        container.addChild(selectList);

        // 底部边框
        container.addChild(
          new DynamicBorder((s: string) => theme.fg("accent", s)),
        );

        return {
          render: (w) => container.render(w),
          invalidate: () => container.invalidate(),
          handleInput: (data) => {
            selectList.handleInput(data);
            tui.requestRender();
          },
        };
      },
    );

    if (result) {
      ctx.ui.notify(`Selected: ${result}`, "info");
    }
  },
});
```

### 模式 2: 带取消的异步操作 (BorderedLoader)

对于需要时间且应该可取消的操作。`BorderedLoader` 显示微调器并处理 escape 取消。

```typescript
import { BorderedLoader } from "@earendil-works/pi-coding-agent";

pi.registerCommand("fetch", {
  handler: async (_args, ctx) => {
    const result = await ctx.ui.custom<string | null>(
      (tui, theme, _kb, done) => {
        const loader = new BorderedLoader(tui, theme, "Fetching data...");
        loader.onAbort = () => done(null);

        // 做异步工作
        fetchData(loader.signal)
          .then((data) => done(data))
          .catch(() => done(null));

        return loader;
      },
    );

    if (result === null) {
      ctx.ui.notify("Cancelled", "info");
    } else {
      ctx.ui.setEditorText(result);
    }
  },
});
```

### 模式 3: 设置/切换 (SettingsList)

用于切换多个设置。使用 `SettingsList` 和 `getSettingsListTheme()`。

```typescript
import { getSettingsListTheme } from "@earendil-works/pi-coding-agent";
import {
  Container,
  type SettingItem,
  SettingsList,
  Text,
} from "@earendil-works/pi-tui";

pi.registerCommand("settings", {
  handler: async (_args, ctx) => {
    const items: SettingItem[] = [
      {
        id: "verbose",
        label: "Verbose mode",
        currentValue: "off",
        values: ["on", "off"],
      },
      {
        id: "color",
        label: "Color output",
        currentValue: "on",
        values: ["on", "off"],
      },
    ];

    await ctx.ui.custom((_tui, theme, _kb, done) => {
      const container = new Container();
      container.addChild(
        new Text(theme.fg("accent", theme.bold("Settings")), 1, 1),
      );

      const settingsList = new SettingsList(
        items,
        Math.min(items.length + 2, 15),
        getSettingsListTheme(),
        (id, newValue) => {
          ctx.ui.notify(`${id} = ${newValue}`, "info");
        },
        () => done(undefined),
        { enableSearch: true },
      );
      container.addChild(settingsList);

      return {
        render: (w) => container.render(w),
        invalidate: () => container.invalidate(),
        handleInput: (data) => settingsList.handleInput?.(data),
      };
    });
  },
});
```

### 模式 4: 持久状态指示器

在 footer 中显示持久的状态。适合模式指示器。

```typescript
// 设置状态 (显示在 footer)
ctx.ui.setStatus("my-ext", ctx.ui.theme.fg("accent", "● active"));

// 清除状态
ctx.ui.setStatus("my-ext", undefined);
```

### 模式 5: 编辑器上方/下方的 Widget

显示持久内容在输入编辑器上方或下方。适合待办列表、进度。

```typescript
// 简单字符串数组 (默认在编辑器上方)
ctx.ui.setWidget("my-widget", ["Line 1", "Line 2"]);

// 在编辑器下方渲染
ctx.ui.setWidget("my-widget", ["Line 1", "Line 2"], {
  placement: "belowEditor",
});

// 使用主题
ctx.ui.setWidget("my-widget", (_tui, theme) => {
  const lines = items.map((item, i) =>
    item.done
      ? theme.fg("success", "✓ ") + theme.fg("muted", item.text)
      : theme.fg("dim", "○ ") + item.text,
  );
  return { render: () => lines, invalidate: () => {} };
});

// 清除
ctx.ui.setWidget("my-widget", undefined);
```

### 模式 6: 自定义 Footer

替换 footer。`footerData` 公开否则无法访问的数据。

```typescript
ctx.ui.setFooter((tui, theme, footerData) => ({
  invalidate() {},
  render(width: number): string[] {
    return [`${ctx.model?.id} (${footerData.getGitBranch() || "no git"})`];
  },
  dispose: footerData.onBranchChange(() => tui.requestRender()),
}));

ctx.ui.setFooter(undefined); // 恢复默认
```

### 模式 7: 自定义编辑器 (vim 模式等)

用自定义实现替换主输入编辑器。适合模态编辑 (vim)、不同键绑定 (emacs) 或专业输入处理。

```typescript
import {
  CustomEditor,
  type ExtensionAPI,
} from "@earendil-works/pi-coding-agent";
import { matchesKey, truncateToWidth } from "@earendil-works/pi-tui";

type Mode = "normal" | "insert";

class VimEditor extends CustomEditor {
  private mode: Mode = "insert";

  handleInput(data: string): void {
    if (matchesKey(data, "escape")) {
      if (this.mode === "insert") {
        this.mode = "normal";
        return;
      }
      super.handleInput(data);
      return;
    }

    if (this.mode === "insert") {
      super.handleInput(data);
      return;
    }

    switch (data) {
      case "i":
        this.mode = "insert";
        return;
      case "h":
        super.handleInput("\x1b[D");
        return;
      case "j":
        super.handleInput("\x1b[B");
        return;
      case "k":
        super.handleInput("\x1b[A");
        return;
      case "l":
        super.handleInput("\x1b[C");
        return;
    }
    if (data.length === 1 && data.charCodeAt(0) >= 32) return;
    super.handleInput(data);
  }

  render(width: number): string[] {
    const lines = super.render(width);
    if (lines.length > 0) {
      const label = this.mode === "normal" ? " NORMAL " : " INSERT ";
      const lastLine = lines[lines.length - 1]!;
      lines[lines.length - 1] =
        truncateToWidth(lastLine, width - label.length, "") + label;
    }
    return lines;
  }
}

export default function (pi: ExtensionAPI) {
  pi.on("session_start", (_event, ctx) => {
    ctx.ui.setEditorComponent(
      (tui, theme, keybindings) => new VimEditor(theme, keybindings),
    );
  });
}
```

**关键点:**

- **扩展 `CustomEditor`** (不是基础 `Editor`) 以获取应用键绑定
- 调用 `super.handleInput(data)` 处理你未处理的键
- **工厂模式**: `setEditorComponent` 接收工厂函数获取 `tui`、`theme` 和 `keybindings`
- 传递 `undefined` 恢复默认编辑器: `ctx.ui.setEditorComponent(undefined)`

## 关键规则

1. **始终使用回调中的主题** - 不要直接导入主题。使用 `ctx.ui.custom((tui, theme, keybindings, done) => ...)` 中的 `theme`。
2. **始终为 DynamicBorder 颜色参数添加类型** - 写 `(s: string) => theme.fg("accent", s)`，而不是 `(s) => theme.fg("accent", s)`。
3. **状态更改后调用 tui.requestRender()** - 在 `handleInput` 中更新状态后调用。
4. **返回三方法对象** - 自定义组件需要 `{ render, invalidate, handleInput }`。
5. **使用现有组件** - `SelectList`、`SettingsList`、`BorderedLoader` 覆盖 90% 的情况。不要重建它们。

## 示例

- **选择 UI**: [preset.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/preset.ts)
- **带取消的异步**: [qna.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/qna.ts)
- **设置切换**: [tools.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/tools.ts)
- **状态指示器**: [plan-mode.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/plan-mode.ts)
- **工作指示器**: [working-indicator.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/working-indicator.ts)
- **自定义 footer**: [custom-footer.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/custom-footer.ts)
- **自定义编辑器**: [modal-editor.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/modal-editor.ts)
- **贪吃蛇游戏**: [snake.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/snake.ts)
- **自定义工具渲染**: [todo.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/examples/extensions/todo.ts)
