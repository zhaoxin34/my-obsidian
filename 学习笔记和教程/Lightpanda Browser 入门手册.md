# Lightpanda 入门教程：用无头浏览器抓取动态网页

> [!INFO]
> **Lightpanda** 是一个从零开始构建的无头浏览器，使用 Zig 语言编写，专门为 AI 代理和自动化场景设计。比 Chrome 快 11 倍，内存占用少 9 倍。

<Note>
本教程大约需要 **15 分钟** 完成。
</Note>

## 你将学到什么

在本教程中，你将使用 Lightpanda 构建一个简单的网页抓取工具。完成后，你将能够：

- 使用命令行快速抓取任何网页的内容（包含 JavaScript 执行结果）
- 启动 CDP 服务器，连接到 Puppeteer
- 自动化抓取动态加载的网页

## 前提条件

开始之前，确保你已安装：

- **macOS**（Apple Silicon，即 M1/M2/M3/M4 芯片）
- **Node.js**（用于运行 Puppeteer 示例）

<Note>
你的 Mac 是 Intel 还是 Apple Silicon？点击苹果菜单 → 关于本机 → 处理器可以查看。
</Note>

---

## 第一步：安装 Lightpanda

打开终端，运行以下命令：

```bash
cd /usr/local/bin
curl -L -o lightpanda https://github.com/lightpanda-io/browser/releases/download/nightly/lightpanda-aarch64-macos
chmod a+x ./lightpanda
```

<Note>
下载的是 nightly 版本，每天更新，包含最新功能。
</Note>

验证安装成功：

```bash
lightpanda --help
```

你应该看到类似输出：

```
Lightpanda Browser - The headless browser built from scratch for AI agents and automation.

USAGE:
    lightpanda [OPTIONS] <COMMAND>

COMMANDS:
    fetch    Fetch a URL and dump the content
    serve    Start a CDP server
    help     Print this message or the help of the given subcommand(s)
```

安装成功！Lightpanda 是一个命令行工具，现在你已经可以在终端中使用它了。

---

## 第二步：快速抓取一个网页

这是 Lightpanda 最基础的功能——不用写任何代码，直接在命令行抓取网页。

运行以下命令：

```bash
lightpanda fetch --log-format pretty --log-level info https://example.com/
```

你应该看到：

```
INFO  telemetry : telemetry status . . . . . . . . . . . . .  [+0ms]
      disabled = false

INFO  page : navigate . . . . . . . . . . . . . . . . . . .  [+6ms]
      url = https://example.com/
      method = GET
      ...

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Example Domain</title>
    ...
</head>
<body>
...
</body>
</html>
```

<Success>
Lightpanda 成功抓取了网页！注意它不仅获取了 HTML，还执行了页面中的 JavaScript。
</Success>

### 尝试抓取一个动态网页

Lightpanda 的强大之处在于它能执行 JavaScript。找一个需要 JS 渲染的网站试试：

```bash
lightpanda fetch https://www.baidu.com/
```

你应该能看到百度首页的完整 HTML，包括通过 JavaScript 动态生成的部分。

<Note>
Lightpanda 默认会发送使用数据。如需禁用，运行前加上：`export LIGHTPANDA_DISABLE_TELEMETRY=true`
</Note>

---

## 第三步：启动 CDP 服务器

Lightpanda 可以作为一个 CDP（Chrome DevTools Protocol）服务器运行，这样你就能用 Puppeteer、Playwright 等工具连接它。

在终端中运行：

```bash
lightpanda serve --log-format pretty --log-level info --host 127.0.0.1 --port 9222
```

你应该看到：

```
INFO  telemetry : telemetry status . . . . . . . . . . . . .  [+0ms]
      disabled = false

INFO  app : server running . . . . . . . . . . . . . . . . .  [+0ms]
      address = 127.0.0.1:9222
```

<Success>
CDP 服务器已启动，监听在 127.0.0.1:9222。
</Success>

<Note>
保持这个终端窗口打开，不要关闭。服务器正在后台运行。
</Note>

---

## 第四步：用 Puppeteer 连接 Lightpanda

现在你可以用 Puppeteer 控制 Lightpanda 了。首先安装 Puppeteer：

```bash
mkdir -p ~/lightpanda-demo
cd ~/lightpanda-demo
npm init -y
npm install puppeteer-core
```

创建文件 `scrape.js`：

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

// 获取页面标题
const title = await page.title();
console.log('Page title:', title);

// 获取所有链接
const links = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('a')).map(a => ({
    href: a.href,
    text: a.textContent.trim()
  }));
});

console.log(`Found ${links.length} links:`);
links.forEach(link => {
  console.log(`  - ${link.text} -> ${link.href}`);
});

// 关闭
await page.close();
await context.close();
await browser.disconnect();
```

运行脚本：

```bash
node scrape.js
```

你应该看到：

```
Page title: Example Domain
Found 1 links:
  - More information... -> https://www.iana.org/domains/example
```

<Success>
Puppeteer 成功通过 Lightpanda 抓取了网页内容！
</Success>

---

## 第五步：抓取动态内容

现在试试抓取一个需要 JavaScript 渲染的网页。我们来获取一个包含动态加载内容的页面。

修改 `scrape.js`，抓取一个更复杂的页面：

```javascript
import puppeteer from 'puppeteer-core';

const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://127.0.0.1:9222',
});

const context = await browser.createBrowserContext();
const page = await context.newPage();

// 设置视口大小
await page.setViewport({ width: 1280, height: 720 });

// 访问一个需要 JS 渲染的页面
console.log('Navigating to page...');
await page.goto('https://example.com/', { waitUntil: 'networkidle0' });

// 等待某个元素加载
await page.waitForSelector('body');

// 执行自定义 JavaScript 获取页面内容
const pageData = await page.evaluate(() => {
  return {
    title: document.title,
    url: window.location.href,
    bodyText: document.body.innerText.slice(0, 200) + '...',
    links: Array.from(document.querySelectorAll('a')).map(a => a.href)
  };
});

console.log('Page data:', JSON.stringify(pageData, null, 2));

await browser.disconnect();
```

运行：

```bash
node scrape.js
```

你应该能看到页面的完整数据，包括通过 JavaScript 动态生成的内容。

<Success>
现在你已经掌握了用 Lightpanda 抓取动态网页的完整流程！
</Success>

---

## 你学到了什么

本教程中，你学会了：

- ✅ 在 macOS 上安装 Lightpanda 无头浏览器
- ✅ 使用命令行快速抓取网页内容
- ✅ 启动 CDP 服务器
- ✅ 用 Puppeteer 连接 Lightpanda
- ✅ 抓取动态 JavaScript 渲染的网页

---

## 下一步

现在你已经掌握了基础，可以继续学习：

- **[使用 Playwright 连接 Lightpanda](/)** - Playwright 是另一个流行的浏览器自动化工具，API 与 Puppeteer 类似
- **[Fetcher MCP：让 AI 帮你抓网页](/)** - 配置 Claude Desktop，直接用自然语言命令抓取网页
- **[代理和 robots.txt 配置](/)** - 学习如何配置代理服务器和遵守网站规则

---

## 遇到问题？

如果遇到错误：

1. **"command not found"** — 返回第一步，确认 lightpanda 已正确安装到 `/usr/local/bin`
2. **"Connection refused"** — 确认 CDP 服务器正在运行（第三步）
3. **"Timeout"** — 有些网页加载较慢，可以增加超时时间

更多帮助请查看 [GitHub Issues](https://github.com/lightpanda-io/browser/issues)。

---

## 参考信息

| 项目 | 详情 |
|------|------|
| 官网 | https://lightpanda.io |
| GitHub | https://github.com/lightpanda-io/browser |
| Fetcher MCP | https://github.com/phil-02/fetcher-mcp |
| Benchmark | https://github.com/lightpanda-io/demo |

<Note>
Lightpanda 目前处于 Beta 阶段，仍在积极开发中。如果遇到问题，欢迎提交 [GitHub Issue](https://github.com/lightpanda-io/browser/issues)！
</Note>
