> [!INFO]
> **Lightpanda** 是一个从零开始构建的无头浏览器，使用 Zig 语言编写，专门为 AI 代理和自动化场景设计。不是 Chromium 分支，不是 WebKit 补丁——是全新从头写的浏览器。

## 目录

- [项目介绍](#项目介绍)
- [安装方式](#安装方式)
  - [方式一：下载预编译二进制（推荐）](#方式一下载预编译二进制推荐)
  - [方式三：Docker](#方式三docker)
- [基础使用](#基础使用)
  - [快速抓取网页](#快速抓取网页)
  - [启动 CDP 服务器](#启动-cdp-服务器)
  - [与 Puppeteer 集成](#与-puppeteer-集成)
  - [与 Playwright 集成](#与-playwright-集成)
  - [与 chromedp 集成](#与-chromedp-集成)
- [进阶用法](#进阶用法)
  - [环境变量配置](#环境变量配置)
  - [代理支持](#代理支持)
  - [robots.txt](#robotstxt)
- [MCP Server 集成](#mcp-server-集成)
  - [Fetcher MCP（推荐）](#fetcher-mcp推荐)
  - [手动构建 Lightpanda MCP Server](#手动构建-lightpanda-mcp-server)
- [命令行参数参考](#命令行参数参考)
- [已知限制](#已知限制)
- [性能对比](#性能对比)
- [常见问题](#常见问题)
- [参考链接](#参考链接)

---

## 项目介绍

Lightpanda 是专为无头浏览器场景设计的新一代浏览器：

| 特性                | 说明                            |
| ----------------- | ----------------------------- |
| **语言**            | Zig（底层系统编程语言）                 |
| **JavaScript 引擎** | v8                            |
| **HTML 解析器**      | html5ever                     |
| **HTTP 客户端**      | libcurl                       |
| **通信协议**          | CDP（Chrome DevTools Protocol） |
| **兼容性**           | Puppeteer、Playwright、chromedp |

---

## 安装方式

### 方式一：下载预编译二进制（推荐）

```bash
cd /usr/local/bin
curl -L -o lightpanda https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-aarch64-macos
chmod a+x ./lightpanda
```

### 方式三：Docker

如果你有 Docker 环境，这是最简单的隔离部署方式。

```bash
docker run -d --name lightpanda -p 9222:9222 lightpanda/browser:nightly
```

这会自动启动一个 CDP 服务器，监听在 `9222` 端口。

---

## 基础使用

### 快速抓取网页

使用 `fetch` 命令快速获取网页内容（包含 JavaScript 执行结果）：

```bash
lightpanda fetch --log-format pretty --log-level info https://www.baidu.com/
```

参数说明：
- `--obey-robots`：遵守 robots.txt 规则
- `--log-format pretty`：美化日志输出
- `--log-level info`：日志级别

---

### 启动 CDP 服务器

CDP 服务器允许你使用 Puppeteer、Playwright 等客户端连接：

```bash
lightpanda serve --log-format pretty --log-level info --host 127.0.0.1 --port 9222
```

---

### 与 Puppeteer 集成

#### 安装 Puppeteer

```bash
npm install puppeteer-core
```

> [!NOTE]
> 使用 `puppeteer-core` 而不是 `puppeteer`，因为你不需要下载 Chromium（Lightpanda 会替代它）。

#### JavaScript 示例

```javascript
import puppeteer from 'puppeteer-core';

// 连接 Lightpanda CDP 服务器
const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://127.0.0.1:9222',
});

// 创建新页面
const context = await browser.createBrowserContext();
const page = await context.newPage();

// 访问页面
await page.goto('https://example.com/', { waitUntil: 'networkidle0' });

// 执行 JavaScript 获取内容
const title = await page.title();
const links = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('a')).map(a => ({
    href: a.href,
    text: a.textContent.trim()
  }));
});

console.log('Title:', title);
console.log('Links:', links);

// 关闭
await page.close();
await context.close();
await browser.disconnect();
```

---

### 与 Playwright 集成

#### 安装 Playwright

```bash
npm install playwright
```

#### TypeScript 示例

```typescript
import { chromium } from 'playwright';

async function main() {
  // 连接 Lightpanda
  const browser = await chromium.connect({
    wsEndpoint: 'ws://127.0.0.1:9222',
  });

  const page = await browser.newPage();

  // 访问页面
  await page.goto('https://example.com/');

  // 获取内容
  const content = await page.content();
  console.log('Page content length:', content.length);

  await browser.close();
}

main();
```

#### 命令行使用

Playwright 也可以直接从命令行使用：

```bash
# 确保 Lightpanda CDP 服务器在 127.0.0.1:9222 运行

npx playwright chromium --headless --remote-debugging-port=9222
```

---

### 与 chromedp 集成

chromedp 是 Go 语言的 CDP 客户端库。

#### 安装

```bash
go get github.com/chromedp/chromedp
```

#### Go 示例

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/chromedp/chromedp"
)

func main() {
    // 创建 Lightpanda CDP 客户端
    cdpURL := "ws://127.0.0.1:9222"
    allocOpts := []chromedp.ExecAllocatorOption{
        chromedp.NoFirstRun,
        chromedp.NoDefaultBrowserCheck,
        chromedp.DisableGPU,
        chromedp.Server(cdpURL), // 指定 Lightpanda 服务器
    }

    ctx, cancel := chromedp.NewExecAllocator(context.Background(), allocOpts...)
    defer cancel()

    // 创建上下文
    ctx, cancel = chromedp.NewContext(ctx)
    defer cancel()

    // 执行任务
    var title string
    err := chromedp.Run(ctx,
        chromedp.Navigate("https://example.com/"),
        chromedp.Title(&title),
    )
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("Page title: %s\n", title)
}
```

---

## 进阶用法

### 环境变量配置

#### 禁用遥测

Lightpanda 默认会收集使用数据。如需禁用：

```bash
export LIGHTPANDA_DISABLE_TELEMETRY=true
./lightpanda fetch https://example.com/
```

#### 显示内存统计（Mimalloc）

在开发模式下构建时，可以显示内存统计：

```bash
export MIMALLOC_SHOW_STATS=1
./lightpanda serve --host 127.0.0.1 --port 9222
```

---

### 代理支持

Lightpanda 支持通过命令行参数或环境变量配置代理：

```bash
# 命令行参数
./lightpanda fetch --proxy http://proxy.example.com:8080 https://example.com/

# 环境变量
export HTTPS_PROXY=http://proxy.example.com:8080
./lightpanda fetch https://example.com/
```

---

### robots.txt

Lightpanda 支持遵守 robots.txt 规则：

```bash
# 遵守 robots.txt（默认行为）
./lightpanda fetch --obey-robots https://example.com/

# 忽略 robots.txt
./lightpanda fetch https://example.com/
```

---

## MCP Server 集成

### Fetcher MCP（推荐）

Fetcher MCP 是一个通用的网页抓取 MCP 服务器，支持 Lightpanda 作为底层引擎。

#### 安装

```bash
# 安装浏览器依赖
npx playwright install chromium
```

#### 启动服务

```bash
npx -y fetcher-mcp --transport=http --host=0.0.0.0 --port=3000
```

#### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "fetcher": {
      "command": "npx",
      "args": ["-y", "fetcher-mcp"]
    }
  }
}
```

#### 使用示例

在 Claude Code 中，你可以：

1. **抓取网页内容**
   ```
   请帮我抓取 https://example.com/ 的内容
   ```

2. **批量抓取**
   ```
   请同时抓取这三个网页的内容：
   - https://site1.com/
   - https://site2.com/
   - https://site3.com/
   ```

3. **设置超时**
   ```
   请抓取 https://example.com/，设置超时为 60 秒
   ```

4. **调试模式**（显示浏览器窗口）
   ```
   请用调试模式抓取 https://example.com/，我需要手动登录
   ```

#### Fetcher MCP 功能

| 功能 | 说明 |
|------|------|
| `fetch_url` | 获取单个 URL 的内容 |
| `fetch_urls` | 批量并行获取多个 URL |
| JavaScript 执行 | 支持动态网页 |
| 内容提取 | 内置 Readability 算法，自动提取主要内容 |
| 输出格式 | 支持 HTML 和 Markdown |

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | 必填 | 要抓取的网址 |
| `timeout` | number | 30000 | 超时时间（毫秒） |
| `waitUntil` | string | 'load' | 导航完成条件 |
| `extractContent` | boolean | true | 是否提取主要内容 |
| `returnHtml` | boolean | false | 是否返回 HTML |
| `disableMedia` | boolean | true | 是否禁用媒体资源 |

---

### 手动构建 Lightpanda MCP Server

如果你想基于 Lightpanda 自行开发 MCP Server，可以参考以下架构：

```python
# 示例：简单的 Lightpanda MCP 工具（Python）
import asyncio
import websockets
import json
import subprocess

async def lightpanda_fetch(url: str) -> str:
    """使用 Lightpanda 抓取网页内容"""
    result = subprocess.run(
        ['./lightpanda', 'fetch', '--log-format', 'pretty', url],
        capture_output=True,
        text=True
    )
    return result.stdout

class LightpandaMCPServer:
    def __init__(self):
        self.tools = {
            'fetch_url': {
                'description': 'Fetch web page content using Lightpanda browser',
                'parameters': {
                    'url': {'type': 'string', 'description': 'URL to fetch'}
                },
                'handler': lightpanda_fetch
            }
        }

    async def handle_request(self, method: str, params: dict):
        if method == 'tools/call':
            tool_name = params.get('name')
            args = params.get('arguments', {})
            return await self.tools[tool_name]['handler'](**args)
```

---

## 命令行参数参考

### 全局参数

| 参数 | 说明 |
|------|------|
| `--log-format pretty` | 美化日志输出 |
| `--log-format json` | JSON 格式日志 |
| `--log-level debug` | Debug 日志级别 |
| `--log-level info` | Info 日志级别 |
| `--log-level warn` | Warn 日志级别 |
| `--log-level error` | Error 日志级别 |

### fetch 子命令

```bash
./lightpanda fetch [options] <url>
```

| 参数 | 说明 |
|------|------|
| `--obey-robots` | 遵守 robots.txt |
| `--dump` | 输出 DOM 树 |
| `--proxy <url>` | 使用代理 |

### serve 子命令

```bash
./lightpanda serve [options]
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--host <address>` | 127.0.0.1 | 监听地址 |
| `--port <port>` | 9222 | 监听端口 |
| `--obey-robots` | false | 是否遵守 robots.txt |
| `--insecure-disable-tls-host-verification` | false | 禁用 TLS 验证 |

---

## 已知限制

> [!WARNING]
> Lightpanda 目前处于 Beta 阶段，仍在积极开发中。以下功能可能尚未完全支持：

### 已实现功能

- ✅ HTTP 加载（libcurl）
- ✅ HTML 解析（html5ever）
- ✅ DOM 树
- ✅ JavaScript 支持（v8）
- ✅ DOM APIs
- ✅ Ajax（XHR + Fetch）
- ✅ DOM dump
- ✅ CDP/WebSocket 服务器
- ✅ 点击交互
- ✅ 表单输入
- ✅ Cookies
- ✅ 自定义 HTTP 头
- ✅ 代理支持
- ✅ 网络拦截
- ✅ robots.txt 支持

### Web API 覆盖

Lightpanda 正在逐步实现 Web API。完整的 Web API 有数百个，完整覆盖需要时间。查看当前状态请参考 [MDN Web API 文档](https://developer.mozilla.org/en-US/docs/Web/API)。

### Playwright 兼容性注意事项

由于 Playwright 使用中间 JavaScript 层选择执行策略，如果 Lightpanda 添加了新 Web API，Playwright 可能会选择不同的代码路径。如果遇到兼容性问题，请：

1. 检查是否在已知工作的版本
2. 提交包含详细信息的 [GitHub Issue](https://github.com/lightpanda-io/browser/issues)

---

## 性能对比

根据官方 benchmarks（AWS EC2 m5.large 实例，抓取 933 个真实网页）：

| 指标 | Chrome | Lightpanda | 提升 |
|------|--------|------------|------|
| 内存占用 | 100% | 11% | **9x 降低** |
| 执行时间 | 100% | 9% | **11x 加速** |
| 启动时间 | 较慢 | 即时 | **即时启动** |

> [!TIP]
> 详细 benchmark 数据请查看 [官方 demo 仓库](https://github.com/lightpanda-io/demo/blob/main/BENCHMARKS.md)。

---

## 常见问题

### Q: 为什么选择 Lightpanda 而不是 Chrome？

Chrome 是一个桌面应用程序，被设计用来渲染 UI。将它用于无头服务器场景会有以下问题：
- 内存和 CPU 占用高
- 难以打包、部署和扩展
- 包含大量无头场景不需要的功能

### Q: Lightpanda 和 Playwright 是什么关系？

Lightpanda 实现了 CDP（Chrome DevTools Protocol），可以被 Playwright 使用作为底层浏览器引擎。你可以把 Lightpanda理解为 Playwright 的一个可选引擎，就像 Playwright 支持 Chromium、Firefox、WebKit 一样。

### Q: 我的脚本在 Lightpanda 上不工作怎么办？

1. 确认你的 Puppeteer/Playwright 脚本在标准 Chrome 上正常工作
2. 查看 [GitHub Issues](https://github.com/lightpanda-io/browser/issues) 是否有类似问题
3. 提交新 Issue，包含：
   - 你的脚本
   - 预期行为
   - 实际行为
   - 错误信息

### Q: macOS Intel 能用吗？

目前官方只提供 Apple Silicon (aarch64) 的预编译版本。Intel Mac 用户需要从源码编译。

---

## 参考链接

- 🌐 官网：https://lightpanda.io
- 📦 GitHub：https://github.com/lightpanda-io/browser
- 📖 官方文档：https://github.com/lightpanda-io/browser/blob/main/README.md
- 🐛 问题反馈：https://github.com/lightpanda-io/browser/issues
- 💬 Discord：https://discord.gg/K63XeymfB5
- 🐦 Twitter：https://twitter.com/lightpanda_io
- 📊 Benchmark：https://github.com/lightpanda-io/demo
- 🤖 Fetcher MCP：https://github.com/phil-02/fetcher-mcp
