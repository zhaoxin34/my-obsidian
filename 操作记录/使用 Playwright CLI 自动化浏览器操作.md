---
title: "使用 Playwright CLI 自动化浏览器操作"
description: "通过命令行控制浏览器，学习录制用户操作并生成 Playwright 测试代码"
date: 2026-03-25
tags:
  - playwright
  - 浏览器自动化
  - CLI
  - 测试
---

# 使用 Playwright CLI 自动化浏览器操作

Playwright CLI 是微软出品的命令行浏览器自动化工具，可以帮助你通过终端控制浏览器、执行自动化测试、录制操作并生成 Playwright 测试代码。

本教程将带你从零开始，安装并掌握 Playwright CLI 的核心功能。

<Note>
本教程预计需要 **15-20 分钟** 完成。
你不需要有任何编程经验，所有操作都通过命令行完成。
</Note>

## 你将学到的内容

完成本教程后，你将能够：

- 在终端中打开浏览器并导航到任意网页
- 模拟用户操作：点击、输入文本、勾选复选框
- 截取网页截图和保存为 PDF
- 管理多个浏览器会话
- 使用快照功能查看页面元素引用

## 准备工作

在开始之前，确保你的电脑满足以下要求：

- **Node.js 18 或更高版本**
  ```bash
  node --version
  ```
  如果没有安装，请访问 [nodejs.org](https://nodejs.org) 下载安装。

- **npm 或 pnpm**（Node.js 自带）

- **Chrome、Firefox 或 Safari** 之一已安装在电脑上

<Tip>
不确定 Node.js 是否已安装？运行上面的命令查看版本号。如果显示 `v18.x.x` 或更高版本，说明已满足要求。
</Tip>

## 第一步：安装 Playwright CLI

打开终端，运行以下命令全局安装 Playwright CLI：

```bash
npm install -g @playwright/cli@latest
```

安装完成后，验证安装是否成功：

```bash
playwright-cli --help
```

你应该看到类似以下的输出：

```
playwright-cli

CLI for common Playwright actions

USAGE
  $ playwright-cli [COMMAND]

CORE COMMANDS
  open       open browser, optionally navigate to url
  goto       navigate to a url
  click      perform click on a web page
  type       type text into editable element
  ...

Run playwright-cli help [COMMAND] for more information on a command.
```

<Note>
如果终端提示 "command not found"，请重新打开一个新的终端窗口，让 PATH 环境变量生效。
</Note>

## 第二步：打开你的第一个网页

让我们从最基础的操作开始——打开一个网页。

```bash
playwright-cli open https://example.com
```

浏览器会以无头模式（headless）在后台打开，并自动导航到 example.com。

打开完成后，终端会显示当前页面信息：

```
### Page
- Page URL: https://example.com/
- Page Title: Example Domain

### Snapshot
[Snapshot](.playwright-cli/page-2026-03-25T10-00-00-000Z.yml)
```

这就是 Playwright CLI 的快照功能——每次命令执行后，它会自动记录页面的状态，包括 URL、标题，以及页面上所有可交互元素的引用（`e1`、`e2` 等）。

<Tip>
`screenshot` 命令可以抓取当前页面快照，生成 PNG 图片文件。
</Tip>

## 第三步：有界面模式查看浏览器

默认情况下，浏览器在后台以无头模式运行。如果你想看到浏览器的实际操作，可以使用 `--headed` 参数：

```bash
playwright-cli open https://example.com --headed
```

你会看到一个真实的浏览器窗口打开，显示目标网页。这对于调试和可视化理解自动化操作非常有帮助。

<Note>
有界面模式会占用屏幕空间。如果你在无界面服务器上运行，请省略 `--headed` 参数。
</Tip>

## 第四步：与页面交互

Playwright CLI 的强大之处在于可以模拟真实的用户操作。让我们以一个 Todo 应用为例进行练习。

### 打开 Todo 应用

```bash
playwright-cli open https://demo.playwright.dev/todomvc/ --headed
```

你应该看到浏览器打开了一个经典的 Todo 列表应用。

### 输入文本

在输入框中输入一些文字：

```bash
playwright-cli type "Buy groceries"
```

你应该看到输入框中出现了 "Buy groceries" 文本。

### 添加待办事项

按 Enter 键添加这个待办事项：

```bash
playwright-cli press Enter
```

你应该看到 "Buy groceries" 作为第一个待办事项出现在列表中。

### 再添加一个

```bash
playwright-cli type "Water flowers"
playwright-cli press Enter
```

现在列表中应该有两条待办事项。

### 勾选复选框

Playwright CLI 会自动为页面上的可交互元素分配引用 ID（如 `e1`、`e2`、`e21`、`e35` 等）。在 Todo 应用中，复选框通常使用 `e21`、`e35` 等引用。

```bash
playwright-cli check e21
```

你应该看到 "Buy groceries" 旁边的复选框被勾选了，文字上有删除线，表示已完成。

### 再勾选一个

```bash
playwright-cli check e35
```

现在两个待办事项都完成了。

<Note>
元素的引用 ID 可能会根据页面结构变化。每次执行命令后，终端都会显示最新的快照，其中包含所有可用的元素引用。
</Tip>

## 第五步：截取截图

截图是记录自动化操作结果的好方法。

### 截取整个页面

```bash
playwright-cli screenshot
```

Playwright CLI 会截取当前页面并保存为 PNG 文件。文件名类似 `screenshot-2026-03-25T10-05-00-000Z.png`。

### 指定文件名

如果你想使用自定义文件名：

```bash
playwright-cli screenshot --filename=my-todo-app.png
```

### 截取特定元素

你也可以只截取页面上的某个特定元素。首先获取元素的引用，然后用该引用截取：

```bash
playwright-cli snapshot
# 查看输出，找到你想要的元素的引用，比如 e3
playwright-cli screenshot e3
```

这对于只想保存某个组件或区域非常有用的。

## 第六步：保存为 PDF

除了截图，你还可以将页面保存为 PDF：

```bash
playwright-cli pdf
```

或者指定文件名：

```bash
playwright-cli pdf --filename=my-page.pdf
```

<Note>
PDF 功能仅在 Chromium 内核的浏览器（Chrome、Edge）中可用。
</Note>

## 第七步：管理浏览器会话

Playwright CLI 会记住你的浏览器状态，包括 cookies 和登录状态。这在多个项目之间切换时非常有用。

### 查看当前会话

```bash
playwright-cli list
```

你会看到当前所有打开的浏览器会话列表。

### 使用命名会话

如果你有多个项目，可以使用命名会话来区分：

```bash
playwright-cli -s=todo-app open https://demo.playwright.dev/todomvc/
playwright-cli -s=blog open https://example.com
playwright-cli list
```

通过 `-s=` 参数指定会话名称，每个会话的浏览器状态相互独立。

### 关闭所有浏览器

```bash
playwright-cli close-all
```

这会关闭所有浏览器会话。

### 强制终止所有进程

如果浏览器卡住了，可以强制终止：

```bash
playwright-cli kill-all
```

### 可视化监控

如果你的代码代理正在后台运行浏览器自动化，可以使用 `show` 命令查看实时进度：

```bash
playwright-cli show
```

这会打开一个监控面板，显示所有活动会话的实时画面。

## 第八步：理解快照和元素引用

每次执行命令后，Playwright CLI 都会生成一个快照文件，记录页面当前状态。这个快照包含：

- 当前 URL 和页面标题
- 页面上所有可交互元素的引用 ID
- 元素的详细信息（标签、文本、属性等）

### 查看快照内容

打开 `.playwright-cli` 目录，查看生成的快照文件：

```bash
ls .playwright-cli/
```

快照文件是 YAML 格式，可以直接用文本编辑器打开查看。

### 手动获取快照

你也可以随时手动获取快照：

```bash
playwright-cli snapshot
```

这对于调试和了解页面结构特别有用。

## 第九步：浏览器配置

Playwright CLI 支持通过配置文件或环境变量进行配置。

### 创建配置文件

在项目根目录创建 `.playwright/cli.config.json`：

```json
{
  "browser": {
    "browserName": "chromium"
  },
  "outputDir": "./output",
  "console": {
    "level": "info"
  }
}
```

现在每次运行 Playwright CLI 时都会自动读取这个配置文件。

### 命令行参数覆盖

你也可以在命令行直接指定参数：

```bash
playwright-cli open https://example.com --browser=firefox
```

这会使用 Firefox 而不是默认的 Chromium。

## 第十步：进阶操作

### 拖拽操作

在页面上执行拖拽：

```bash
playwright-cli drag e1 e2
```

这会将 `e1` 元素拖拽到 `e2` 元素的位置。

### 悬停和悬停菜单

```bash
playwright-cli hover e5
```

### 选择下拉选项

```bash
playwright-cli select e10 value
```

### 处理弹窗对话框

```bash
playwright-cli dialog-accept "确认文本"
# 或
playwright-cli dialog-dismiss
```

### 查看控制台消息

```bash
playwright-cli console
```

### 查看网络请求

```bash
playwright-cli network
```

## 你学到了什么

本教程中，你掌握了以下技能：

- 使用 `playwright-cli open` 在终端中打开浏览器
- 使用 `playwright-cli type`、`click`、`press` 模拟用户输入和操作
- 使用 `playwright-cli screenshot` 和 `pdf` 截取网页内容
- 使用 `playwright-cli list`、`close-all` 管理浏览器会话
- 使用 `playwright-cli snapshot` 了解页面元素结构
- 使用配置文件和环境变量定制浏览器行为

## 下一步

现在你已经掌握了 Playwright CLI 的基础，可以继续探索：

- **[Playwright CLI Skills](https://github.com/microsoft/playwright-cli)** - 深入学习高级功能，如网络请求拦截（Route）、视频录制、追踪调试
- **Playwright MCP** - 如果你正在开发 AI 代理，了解如何将 Playwright 集成到 AI 工作流中
- **Playwright 测试生成** - 使用 CLI 录制你的操作，自动生成 Playwright 测试代码

<Note>
完整的命令参考，请查看 [Playwright CLI 官方文档](https://github.com/microsoft/playwright-cli)。
</Note>
