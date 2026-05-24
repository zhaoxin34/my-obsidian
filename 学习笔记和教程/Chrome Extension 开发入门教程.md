---
title: "Build your first Chrome Extension"
description: "Learn the basics of Chrome Extension development by building a page inspector extension"
---

# Build Your First Chrome Extension

在本教程中，你将构建一个 **页面检查器扩展**。它可以在弹出窗口中显示当前网页的标题、URL 和页面内容摘要。完成后，你将拥有一个真实可用的 Chrome 扩展。

<Note>
本教程大约需要 20 分钟。你不需要任何 Chrome Extension 开发经验。
</Note>

## 你将构建什么

一个可以在浏览器工具栏显示的扩展，点击后弹出一个小窗口，展示当前网页的信息：

- 网页标题
- 网页 URL
- 页面内容摘要（提取前 500 个字符）

<Frame caption="完成后的扩展效果">
  ```mermaid
  flowchart LR
      A["🔗 当前页面"] --> B["点击扩展图标"]
      B --> C["弹出窗口显示页面信息"]
      
      C --> D["标题: xxx"]
      C --> E["URL: https://..."]
      C --> F["摘要: ..."]
  ```
</Frame>

## 前置要求

在开始之前，确保你已安装：

- **Google Chrome** 浏览器（任何版本都可以）
- **任意文本编辑器**（推荐 VS Code）

<Tip>
你不需要任何 JavaScript 或 Web 开发经验。本教程会逐步解释每一行代码。
</Tip>

## Step 1: 创建项目文件夹

首先，创建一个空文件夹来存放扩展的所有文件。

在终端中运行：

```bash
mkdir my-page-inspector
cd my-page-inspector
```

你应该看到终端提示符变为类似 `~/my-page-inspector $`，表示你现在在这个文件夹中。

<Note>
记住这个文件夹的位置，稍后我们需要用它来加载扩展。
</Note>

## Step 2: 创建扩展清单文件

Chrome Extension 的核心是一个名为 `manifest.json` 的清单文件，它告诉 Chrome 这个扩展是什么以及如何运行。

在项目文件夹中创建 `manifest.json` 文件，内容如下：

```json
{
  "manifest_version": 3,
  "name": "Page Inspector",
  "version": "1.0",
  "description": "显示当前页面的基本信息",
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png"
    }
  }
}
```

保存文件后，你的项目结构应该是：

```
my-page-inspector/
└── manifest.json
```

## Step 3: 创建弹出窗口 HTML

现在创建扩展点击后显示的弹出窗口界面。

在同一文件夹中创建 `popup.html` 文件：

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      width: 350px;
      padding: 15px;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h2 {
      font-size: 16px;
      margin: 0 0 10px 0;
    }
    .info-item {
      margin-bottom: 12px;
    }
    .label {
      font-weight: bold;
      font-size: 12px;
      color: #666;
      margin-bottom: 4px;
    }
    .value {
      font-size: 14px;
      word-break: break-all;
    }
    .url {
      color: #1a73e8;
    }
  </style>
</head>
<body>
  <h2>📋 页面信息</h2>
  
  <div class="info-item">
    <div class="label">标题</div>
    <div class="value" id="page-title">加载中...</div>
  </div>
  
  <div class="info-item">
    <div class="label">网址</div>
    <div class="value url" id="page-url">-</div>
  </div>
  
  <div class="info-item">
    <div class="label">内容摘要</div>
    <div class="value" id="page-summary">-</div>
  </div>
  
  <script src="popup.js"></script>
</body>
</html>
```

保存文件后，你的项目结构变为：

```
my-page-inspector/
├── manifest.json
└── popup.html
```

## Step 4: 创建弹出窗口脚本

现在创建实际的逻辑脚本，它将获取当前页面的信息并显示在弹出窗口中。

在同一文件夹中创建 `popup.js` 文件：

```javascript
// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
  // 获取当前活动标签页的信息
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    const tab = tabs[0];
    
    // 显示标题
    document.getElementById('page-title').textContent = tab.title || '无标题';
    
    // 显示 URL
    document.getElementById('page-url').textContent = tab.url || '无URL';
    
    // 通过消息获取页面内容摘要
    chrome.tabs.sendMessage(tab.id, { action: 'getContent' }, function(response) {
      if (response && response.content) {
        const summary = response.content.substring(0, 500);
        document.getElementById('page-summary').textContent = 
          summary + (response.content.length > 500 ? '...' : '');
      } else {
        document.getElementById('page-summary').textContent = '无法获取页面内容';
      }
    });
  });
});
```

保存后项目结构：

```
my-page-inspector/
├── manifest.json
├── popup.html
└── popup.js
```

## Step 5: 创建内容脚本

内容脚本是运行在网页中的代码，它可以访问网页内容。我们用它来提取页面文本。

在同一文件夹中创建 `content.js` 文件：

```javascript
// 监听来自 popup 的消息
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'getContent') {
    // 获取 body 标签的文本内容
    const body = document.body;
    if (body) {
      // 移除所有脚本和样式标签
      const clone = body.cloneNode(true);
      const scripts = clone.querySelectorAll('script, style');
      scripts.forEach(el => el.remove());
      
      sendResponse({ content: clone.innerText.trim() });
    } else {
      sendResponse({ content: '' });
    }
  }
  return true; // 保持消息通道开放
});
```

## Step 6: 更新清单文件添加内容脚本

现在需要更新 `manifest.json`，添加内容脚本的权限和配置：

```json
{
  "manifest_version": 3,
  "name": "Page Inspector",
  "version": "1.0",
  "description": "显示当前页面的基本信息",
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png"
    }
  },
  "permissions": [
    "activeTab",
    "scripting"
  ],
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"]
    }
  ]
}
```

<Warning>
请确保 JSON 格式正确，每行末尾用逗号分隔（最后一行不要逗号）。
</Warning>

## Step 7: 创建扩展图标

Chrome 需要至少一个图标文件。我们可以创建一个简单的 PNG 图片，但为了快速完成，我们先跳过这一步，稍后一起处理。

先创建一个 `icons` 文件夹占位：

```bash
mkdir icons
```

对于正式的扩展，你需要创建 16x16、32x32、48x48 等尺寸的图标。但现在我们可以使用浏览器默认图标，或者稍后添加。

先在 `icons` 文件夹中创建一个占位的 README 文件：

```bash
echo "在此文件夹中添加扩展图标文件：
- icon16.png (16x16 像素)
- icon32.png (32x32 像素)
- icon48.png (48x48 像素)
- icon128.png (128x128 像素)" > icons/README.md
```

当前项目结构：

```
my-page-inspector/
├── manifest.json
├── popup.html
├── popup.js
├── content.js
└── icons/
    └── README.md
```

## Step 8: 加载扩展到 Chrome

现在将扩展加载到 Chrome 中进行测试。

打开 Chrome 浏览器，按照以下步骤操作：

1. 在地址栏输入 `chrome://extensions/` 并回车
2. 在页面右上角，开启 **开发者模式** 开关
3. 点击 **加载已解压的扩展程序** 按钮
4. 选择 `my-page-inspector` 文件夹

你应该看到：

<Frame caption="扩展加载成功后的界面">
  ```
  ┌─────────────────────────────────────────┐
  │  开发者模式 已开启 ✓                     │
  │                                          │
  │  ┌─────────────────────────────────┐    │
  │  │ 📋 Page Inspector          v1.0 │    │
  │  │ 显示当前页面的基本信息           │    │
  │  │                                   │    │
  │  │ [重新加载] [删除]                 │    │
  │  └─────────────────────────────────┘    │
  │                                          │
  │  [+ 加载已解压的扩展程序]                 │
  └─────────────────────────────────────────┘
  ```
</Frame>

你应该在 Chrome 工具栏中看到一个扩展图标（可能是拼图块形状）。

## Step 9: 测试扩展

现在测试扩展是否正常工作。

1. 打开任意一个网页（如 https://www.example.com）
2. 点击工具栏中的扩展图标

你应该看到弹出窗口显示：

- **标题**: 页面的标题
- **网址**: 当前页面的 URL
- **内容摘要**: 页面的文本内容前 500 个字符

<Frame caption="扩展运行效果示例">
  ```
  ┌──────────────────────────┐
  │ 📋 页面信息              │
  │                          │
  │ 标题                     │
  │ Example Domain           │
  │                          │
  │ 网址                     │
  │ https://www.example.com  │
  │                          │
  │ 内容摘要                 │
  │ This domain is for use...│
  └──────────────────────────┘
  ```
</Frame>

如果扩展没有正常显示内容，可能是图标区域被折叠了。请点击工具栏右侧的拼图图标 🧩，然后固定扩展。

## Step 10: 修改和热重载

现在你已经成功加载了扩展，让我们修改它来添加更多功能。

打开 `popup.html`，在样式中添加一个刷新按钮：

```html
  <style>
    body {
      width: 350px;
      padding: 15px;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      background: #fafafa;
    }
    h2 {
      font-size: 16px;
      margin: 0 0 10px 0;
    }
    .info-item {
      margin-bottom: 12px;
    }
    .label {
      font-weight: bold;
      font-size: 12px;
      color: #666;
      margin-bottom: 4px;
    }
    .value {
      font-size: 14px;
      word-break: break-all;
      background: white;
      padding: 8px;
      border-radius: 4px;
      border: 1px solid #eee;
    }
    .url {
      color: #1a73e8;
    }
    button {
      width: 100%;
      padding: 10px;
      background: #1a73e8;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
    }
    button:hover {
      background: #1557b0;
    }
  </style>
```

同时在 HTML 末尾添加按钮：

```html
  <button id="refresh-btn">🔄 刷新</button>
  <script src="popup.js"></script>
```

更新 `popup.js` 添加刷新功能：

```javascript
// 等待 DOM 加载完成
document.addEventListener('DOMContentLoaded', function() {
  loadPageInfo();
  
  // 添加刷新按钮功能
  document.getElementById('refresh-btn').addEventListener('click', function() {
    loadPageInfo();
  });
});

function loadPageInfo() {
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    const tab = tabs[0];
    
    document.getElementById('page-title').textContent = '加载中...';
    document.getElementById('page-url').textContent = '-';
    document.getElementById('page-summary').textContent = '-';
    
    document.getElementById('page-title').textContent = tab.title || '无标题';
    document.getElementById('page-url').textContent = tab.url || '无URL';
    
    chrome.tabs.sendMessage(tab.id, { action: 'getContent' }, function(response) {
      if (response && response.content) {
        const summary = response.content.substring(0, 500);
        document.getElementById('page-summary').textContent = 
          summary + (response.content.length > 500 ? '...' : '');
      } else {
        document.getElementById('page-summary').textContent = '无法获取页面内容';
      }
    });
  });
}
```

返回 Chrome 扩展页面，点击扩展卡片上的 **重新加载** 按钮，然后刷新测试页面。

你应该能看到更新后的界面和刷新按钮。

## 你学到了什么

在本教程中，你：

- ✅ 理解了 Chrome Extension 的基本结构
- ✅ 创建了 `manifest.json` 清单文件
- ✅ 编写了弹出窗口界面（`popup.html`）
- ✅ 实现了弹出窗口逻辑（`popup.js`）
- ✅ 编写了内容脚本（`content.js`）来访问网页内容
- ✅ 成功加载并测试了扩展
- ✅ 学会了热重载修改

## 后续步骤

现在你已经有了一个可用的扩展，可以继续学习：

- **[Chrome Extension 进阶教程]** - 学习添加右键菜单、快捷键、后台脚本等功能
- **[Chrome API 参考]** - 了解所有可用的 Chrome API
- **[添加浏览器图标]** - 学习如何为扩展添加自定义图标
- **[发布扩展到 Chrome Web Store]** - 学习如何发布你的扩展让其他人使用

## 完整项目代码

最终的项目结构：

```
my-page-inspector/
├── manifest.json
├── popup.html
├── popup.js
├── content.js
└── icons/
    └── README.md
```

### manifest.json

```json
{
  "manifest_version": 3,
  "name": "Page Inspector",
  "version": "1.0",
  "description": "显示当前页面的基本信息",
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png"
    }
  },
  "permissions": [
    "activeTab",
    "scripting"
  ],
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"]
    }
  ]
}
```

### popup.html

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      width: 350px;
      padding: 15px;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      background: #fafafa;
    }
    h2 {
      font-size: 16px;
      margin: 0 0 10px 0;
    }
    .info-item {
      margin-bottom: 12px;
    }
    .label {
      font-weight: bold;
      font-size: 12px;
      color: #666;
      margin-bottom: 4px;
    }
    .value {
      font-size: 14px;
      word-break: break-all;
      background: white;
      padding: 8px;
      border-radius: 4px;
      border: 1px solid #eee;
    }
    .url {
      color: #1a73e8;
    }
    button {
      width: 100%;
      padding: 10px;
      background: #1a73e8;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
    }
    button:hover {
      background: #1557b0;
    }
  </style>
</head>
<body>
  <h2>📋 页面信息</h2>
  
  <div class="info-item">
    <div class="label">标题</div>
    <div class="value" id="page-title">加载中...</div>
  </div>
  
  <div class="info-item">
    <div class="label">网址</div>
    <div class="value url" id="page-url">-</div>
  </div>
  
  <div class="info-item">
    <div class="label">内容摘要</div>
    <div class="value" id="page-summary">-</div>
  </div>
  
  <button id="refresh-btn">🔄 刷新</button>
  <script src="popup.js"></script>
</body>
</html>
```

### popup.js

```javascript
document.addEventListener('DOMContentLoaded', function() {
  loadPageInfo();
  
  document.getElementById('refresh-btn').addEventListener('click', function() {
    loadPageInfo();
  });
});

function loadPageInfo() {
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    const tab = tabs[0];
    
    document.getElementById('page-title').textContent = '加载中...';
    document.getElementById('page-url').textContent = '-';
    document.getElementById('page-summary').textContent = '-';
    
    document.getElementById('page-title').textContent = tab.title || '无标题';
    document.getElementById('page-url').textContent = tab.url || '无URL';
    
    chrome.tabs.sendMessage(tab.id, { action: 'getContent' }, function(response) {
      if (response && response.content) {
        const summary = response.content.substring(0, 500);
        document.getElementById('page-summary').textContent = 
          summary + (response.content.length > 500 ? '...' : '');
      } else {
        document.getElementById('page-summary').textContent = '无法获取页面内容';
      }
    });
  });
}
```

### content.js

```javascript
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === 'getContent') {
    const body = document.body;
    if (body) {
      const clone = body.cloneNode(true);
      const scripts = clone.querySelectorAll('script, style');
      scripts.forEach(el => el.remove());
      
      sendResponse({ content: clone.innerText.trim() });
    } else {
      sendResponse({ content: '' });
    }
  }
  return true;
});
```