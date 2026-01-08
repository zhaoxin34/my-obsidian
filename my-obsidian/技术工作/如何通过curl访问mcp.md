# 通过 Curl 访问 MCP (Model Context Protocol) 服务指南

本文档记录了如何使用 curl 命令行工具访问 MCP 服务，以 StarRocks MCP 服务为例。

## 环境信息

- **服务地址**: `http://localhost:9040`
- **服务类型**: StarRocks MCP Server
- **协议版本**: 2024-11-05
- **默认数据库**: `wolf`

## 访问步骤

### 1. 初始化会话

首先需要初始化一个 MCP 会话：

```bash
curl -v -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "curl",
        "version": "1.0"
      }
    }
  }'
```

**响应示例**:
```
event: message
data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":true},"resources":{"subscribe":false,"listChanged":true},"tools":{"listChanged":true}},"serverInfo":{"name":"mcp-server-starrocks","version":"1.16.0"}}}
```

从响应头中获取 `mcp-session-id`，例如：`b1d253075f544616bb78518721eba2c5`

### 2. 发送初始化完成通知

```bash
curl -v -X POST http://localhost:9040/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```

将 `YOUR_SESSION_ID` 替换为第一步中获取的会话 ID。

### 3. 获取工具列表

```bash
curl -v -X POST http://localhost:9040/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/list"
  }'
```

### 4. 调用具体工具

#### 执行查询 (read_query)

```bash
curl -v -X POST http://localhost:9040/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "read_query",
      "arguments": {
        "query": "SELECT * FROM your_table LIMIT 10"
      }
    }
  }'
```

#### 获取数据库摘要 (db_summary)

```bash
curl -v -X POST http://localhost:9040/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "db_summary",
      "arguments": {}
    }
  }'
```

## 重要说明

### 请求头要求

1. **Content-Type**: `application/json`
2. **Accept**: `application/json, text/event-stream` (必须同时包含两者)
3. **mcp-session-id**: 从初始化响应中获取的会话 ID

### 响应格式

- MCP 服务使用 **Server-Sent Events (SSE)** 格式返回响应
- 响应以 `event: message` 开头，数据在 `data:` 字段中
- JSON 数据经过 URL 编码，可能需要解码

### 错误处理

常见错误及解决方案：

1. **406 Not Acceptable**: 缺少正确的 Accept 头
   ```
   "error":{"code":-32600,"message":"Not Acceptable: Client must accept both application/json and text/event-stream"}
   ```

2. **400 Bad Request**: 缺少会话 ID
   ```
   "error":{"code":-32600,"message":"Bad Request: Missing session ID"}
   ```

3. **404 Not Found**: 端点路径错误
   - 正确路径: `/mcp`
   - 错误路径: `/`, `/tools`, `/mcp/tools`

## StarRocks MCP 工具列表

| 工具名称 | 功能描述 | 主要参数 |
|---------|---------|---------|
| `read_query` | 执行 SELECT 查询 | `query`(必需), `db`(可选) |
| `write_query` | 执行 DDL/DML 操作 | `query`(必需), `db`(可选) |
| `analyze_query` | 查询性能分析 | `uuid`, `sql`, `db`(都可选) |
| `collect_query_dump_and_profile` | 收集查询转储和配置文件 | `query`(必需), `db`(可选) |
| `query_and_plotly_chart` | 查询并生成图表 | `query`, `plotly_expr`(必需), `format`(可选) |
| `table_overview` | 获取表概览 | `table`(必需), `refresh`(可选) |
| `db_summary` | 数据库摘要 | `db`, `limit`, `refresh`(都可选) |

## 调试技巧

1. **使用 `-v` 参数** 查看完整的 HTTP 请求和响应
2. **检查会话 ID** 确保每次请求都使用正确的会话 ID
3. **监听响应头** 注意 `mcp-session-id` 的变化
4. **解析 SSE 响应** 正确处理 `event: message` 格式

## 会话管理

- 每次初始化都会生成新的会话 ID
- 会话 ID 在请求头中传递：`mcp-session-id: SESSION_ID`
- 如果会话过期，需要重新初始化

## 示例脚本

```bash
#!/bin/bash

# MCP 服务地址
MCP_URL="http://localhost:9040/mcp"

# 初始化会话
echo "初始化 MCP 会话..."
INIT_RESPONSE=$(curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "curl", "version": "1.0"}
    }
  }')

# 提取会话 ID (需要根据实际响应格式调整)
SESSION_ID=$(echo "$INIT_RESPONSE" | grep -o 'mcp-session-id: [^*]*' | cut -d' ' -f2)

echo "会话 ID: $SESSION_ID"

# 发送初始化完成通知
curl -s -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "method": "notifications/initialized"}'

# 获取工具列表
echo "获取工具列表..."
curl -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}'
```

---

*文档创建时间: 2025-10-30*
*适用 MCP 协议版本: 2024-11-05*
