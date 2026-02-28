Google Search MCP 是一个 Model Context Protocol 服务器，提供基于 Google 自定义搜索 API 的网页搜索和内容提取功能。
## 功能特性

- **搜索工具**：使用 Google Custom Search API 执行网页搜索
  - 搜索整个网络或特定网站
  - 控制结果数量（1-10）
  - 返回结构化的标题、链接和摘要

- **网页阅读器**：提取任意网页内容
  - 获取并解析网页内容
  - 提取页面标题和正文
  - 清理脚本和样式

## 前置准备

### 1. 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. **启用计费**（必须）

### 2. 启用 Custom Search API

1. 访问 [API Library](https://console.cloud.google.com/apis/library)
2. 搜索 "Custom Search API"
3. 点击 "Enable"

### 3. 获取 API Key

1. 访问 [Credentials](https://console.cloud.google.com/apis/credentials)
2. 点击 "Create Credentials" > "API Key"
3. 复制 API Key
4. （可选）将 API Key 限制为仅限 Custom Search API

### 4. 创建自定义搜索引擎

1. 访问 [Programmable Search Engine](https://programmablesearchengine.google.com/create/new)
2. 输入要搜索的网站（通用搜索使用 `www.google.com`）
3. 点击 "Create"
4. 在下一页点击 "Customize"
5. 在设置中启用 "Search the entire web"
6. 复制搜索引擎 ID（cx）

## 安装配置

### 安装 Smithery 版本（推荐）

```bash
npx -y @smithery/cli install @adenot/mcp-google-search --client claude
```

### 手动配置

#### 安装依赖

```bash
# 克隆仓库
git clone https://github.com/adenot/mcp-google-search.git
cd mcp-google-search

# 安装依赖
npm install

# 构建
npm run build
```

#### 配置 Claude Desktop

在以下位置找到配置文件：

- **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "google-search": {
      "command": "npx",
      "args": [
        "-y",
        "@adenot/mcp-google-search"
      ],
      "env": {
        "GOOGLE_API_KEY": "你的API密钥",
        "GOOGLE_SEARCH_ENGINE_ID": "你的搜索引擎ID"
      }
    }
  }
}
```

## 使用方法

### 搜索工具

```json
{
  "name": "search",
  "arguments": {
    "query": "搜索关键词",
    "num": 5
  }
}
```

### 网页阅读器

```json
{
  "name": "read_webpage",
  "arguments": {
    "url": "https://example.com"
  }
}
```

## 调试

如果遇到问题，可以使用 MCP Inspector 进行调试：

```bash
npm run inspector
```

这会提供一个可在浏览器中访问的调试工具 URL。

## 相关链接

- GitHub: https://github.com/adenot/mcp-google-search
- Smithery: https://smithery.ai/server/@adenot/mcp-google-search
