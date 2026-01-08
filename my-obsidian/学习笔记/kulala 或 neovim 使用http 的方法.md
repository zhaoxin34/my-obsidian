https://neovim.getkulala.net/docs/usage/using-environment-variables

## 示例1 使用kulala生成sessionid 并访问mcp
`注意一下用 mcp-session-id 方法` 详细介绍如何使用response的方法见[# Request Variables](https://neovim.getkulala.net/docs/usage/request-variables)
```
### Test MCP Server HTTP API

### This file tests the DataAnalytics MCP server endpoints


### Base URL

@base_url = http://localhost:8000/mcp


### INIT

POST {{base_url}} HTTP/1.1
Content-Type: application/json
Accept: application/json, text/event-stream

{
  "id": 1,
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "capabilities": {
      "tools": {}
    },
    "clientInfo": {
      "name": "HTTP Client",
      "version": "1.0.0"
    },
    "protocolVersion": "2024-11-05"
  }
}


### GET_SYSTEM_STATUS

POST {{base_url}} HTTP/1.1
Content-Type: application/json
Accept: application/json, text/event-stream
Mcp-Session-Id: {{INIT.response.headers['mcp-session-id']}}

{
  "id": 2,
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "arguments": {},
    "name": "get_system_status"
  }
}
```
