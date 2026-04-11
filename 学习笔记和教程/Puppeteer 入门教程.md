---
title: Puppeteer 入门教程
description: 通过本教程，你将学会使用 Puppeteer 进行浏览器自动化
---

# Puppeteer 入门教程

在本教程中，你将构建一个自动化脚本，实现自动打开浏览器、访问网页、截图并生成 PDF。通过这个实际可运行的脚本，你将掌握 Puppeteer 的核心用法。

<Note>
本教程需要约 15 分钟完成。你不需要有任何浏览器自动化的经验，我们会在操作过程中解释每一步。
</Note>

## 什么是 Puppeteer？

Puppeteer 是一个 JavaScript 库，它提供了高级 API 来通过 DevTools 协议控制 Chromium 或 Chrome 浏览器。默认情况下，Puppeteer 以无头模式（headless）运行浏览器，这意味着浏览器不显示用户界面，所有操作都在后台执行。

Puppeteer 可以完成你在浏览器中手动执行的绝大多数操作：
- 生成页面截图和 PDF
- 抓取 SPA（单页应用）并生成预渲染内容
- 自动提交表单、进行 UI 测试、键盘输入
- 自动化测试环境
- 捕获网站的 timeline trace 分析性能
- 测试浏览器扩展

## 你将构建什么

在本教程结束时，你将创建一个自动化脚本，能够：
- 自动启动 Chrome 浏览器
- 访问任意网页
- 对网页进行截图
- 生成 PDF 文档

## 前置要求

在开始之前，请确保你具备：

- **Node.js** - Puppeteer 是 Node.js 库，需要 Node.js 环境
- **一个文本编辑器** - 推荐 VS Code

<Tip>
如果还没有安装 Node.js，请访问 https://nodejs.org 下载并安装 LTS 版本。
</Tip>

## 步骤 1：创建项目并安装 Puppeteer

首先，创建一个新文件夹作为你的项目目录：

```bash
mkdir puppeteer-tutorial
cd puppeteer-tutorial
```

初始化一个新的 Node.js 项目：

```bash
npm init -y
```

现在，安装 Puppeteer：

```bash
npm install puppeteer
```

<Note>
安装 Puppeteer 时，它会自动下载最新版本的 Chromium（约 170MB Mac，282MB Linux，280MB Windows），以保证 API 可以正常使用。这可能需要几分钟时间。
</Note>

安装完成后，你应该在 `node_modules` 目录中看到 Puppeteer。你可以运行以下命令验证安装成功：

```bash
ls node_modules | grep puppeteer
```

你应该看到 `puppeteer` 目录。

## 步骤 2：创建你的第一个自动化脚本

在项目根目录下创建一个新文件 `screenshot.js`：

```javascript
const puppeteer = require('puppeteer');

(async () => {
  // 启动浏览器
  const browser = await puppeteer.launch();

  // 创建一个新页面
  const page = await browser.newPage();

  // 访问网页
  await page.goto('https://example.com');

  // 对网页进行截图
  await page.screenshot({ path: 'example.png' });

  // 关闭浏览器
  await browser.close();

  console.log('截图已保存到 example.png');
})();
```

保存文件。

## 步骤 3：运行脚本

在终端中运行：

```bash
node screenshot.js
```

你应该看到类似这样的输出：

```
截图已保存到 example.png
```

现在检查项目目录，你应该看到一个新生成的文件 `example.png`：

```bash
ls -la example.png
```

你应该看到：

```
-rw-r--r--  1 zhaoxin  staff   42K  example.png
```

用图片查看器打开它，你应该能看到 example.com 的页面截图。

打开 `example.png` 文件，你应该能看到 example.com 的首页，看起来类似于浏览器中打开的页面。

<Warning>
如果遇到错误，请确保：
1. 已保存 screenshot.js 文件
2. 当前在正确的项目目录中
3. 已成功运行 npm install puppeteer
</Warning>

## 步骤 4：生成 PDF 文档

现在，让我们扩展脚本，同时生成 PDF 文件。修改 `screenshot.js`：

```javascript
const puppeteer = require('puppeteer');

(async () => {
  // 启动浏览器
  const browser = await puppeteer.launch();

  // 创建一个新页面
  const page = await browser.newPage();

  // 设置视口大小
  await page.setViewport({ width: 1280, height: 720 });

  // 访问网页
  await page.goto('https://example.com');

  // 对网页进行截图
  await page.screenshot({
    path: 'example.png',
    fullPage: true
  });
  console.log('✓ 截图已保存到 example.png');

  // 生成 PDF
  await page.pdf({
    path: 'example.pdf',
    format: 'A4',
    printBackground: true
  });
  console.log('✓ PDF 已保存到 example.pdf');

  // 关闭浏览器
  await browser.close();
})();
```

再次运行脚本：

```bash
node screenshot.js
```

你应该看到类似这样的输出：

```
✓ 截图已保存到 example.png
✓ PDF 已保存到 example.pdf
```

现在检查项目目录，你应该看到生成了两个文件：

```bash
ls -la example.*
```

你应该看到：

```
-rw-r--r--  1 zhaoxin  staff   42K  example.png
-rw-r--r--  1 zhaoxin  staff   21K  example.pdf
```

## 步骤 5：与网页交互

Puppeteer 不仅可以截图，还可以与网页进行交互。让我们创建一个更高级的脚本，演示如何点击按钮、填写表单。

创建一个新文件 `interact.js`：

```javascript
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // 访问一个搜索页面
  await page.goto('https://www.baidu.com');

  // 在搜索框中输入文字
  await page.type('#kw', 'Puppeteer 教程');

  // 点击搜索按钮
  await page.click('#su');

  // 等待搜索结果加载
  await page.waitForSelector('.result');

  // 截图保存搜索结果
  await page.screenshot({ path: 'search-result.png' });

  console.log('✓ 搜索结果截图已保存');

  await browser.close();
})();
```

运行这个脚本：

```bash
node interact.js
```

你应该看到类似这样的输出：

```
✓ 搜索结果截图已保存
```

现在检查项目目录，你应该看到一个新文件 `search-result.png`，用图片查看器打开它，你应该能看到百度的搜索结果页面。

## 核心 API 简介

通过上面的例子，你已经接触了 Puppeteer 的核心 API：

### Browser 对象

Browser 对象代表浏览器实例，负责管理整个浏览器的生命周期：

| 方法 | 说明 |
|------|------|
| `puppeteer.launch()` | 启动浏览器 |
| `browser.newPage()` | 创建新页面 |
| `browser.close()` | 关闭浏览器 |

### Page 对象

Page 对象是 Puppeteer 中最常用的 API，代表单个浏览器标签页：

| 方法 | 说明 |
|------|------|
| `page.goto(url)` | 导航到指定 URL |
| `page.click(selector)` | 点击页面元素 |
| `page.type(selector, text)` | 输入文本 |
| `page.screenshot()` | 截图 |
| `page.pdf()` | 生成 PDF |
| `page.evaluate()` | 在页面上下文中执行 JavaScript |
| `page.setViewport()` | 设置视口大小 |

## 进阶技巧

### 使用 puppeteer-core 节省空间

如果不想下载 Chromium，可以使用 `puppeteer-core` 连接到已安装的浏览器：

```bash
npm install puppeteer-core
```

然后指定已安装的浏览器路径：

```javascript
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/path/to/your/chrome'
  });
  // ... 其余代码相同
})();
```

### 无头模式 vs 有头模式

默认情况下 Puppeteer 以无头模式运行。如果想看到浏览器界面：

```javascript
const browser = await puppeteer.launch({
  headless: false  // 显示浏览器窗口
});
```

## 你学到了什么

在本教程中，你：

- 安装了 Puppeteer 并创建了第一个自动化脚本
- 学会了如何启动浏览器、访问网页
- 掌握了截图和生成 PDF 的方法
- 了解了如何与网页进行交互（输入、点击）
- 认识了核心的 Browser 和 Page API

## 下一步

现在你已经掌握了 Puppeteer 的基础知识，可以继续学习：

- **网页数据抓取** - 使用 Puppeteer 抓取动态加载的网页内容
- **自动化测试** - 使用 Puppeteer 进行端到端测试
- **性能分析** - 使用 Puppeteer 捕获 timeline trace 分析网页性能

<Note>
想了解更多 Puppeteer 的高级用法，请访问官方文档：https://pptr.dev
</Note>
