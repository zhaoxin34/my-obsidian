 ## 配置c hrome 使用remote debug的方式

*启动chrome*
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-profile-stable  > /dev/null 2>&1 &
```

*安装 MCP 使用的命令是：*

```bash
  claude mcp add -s user chrome-devtools -- npx chrome-devtools-mcp@latest -u http://127.0.0.1:9222
```

  说明：
  - -s user - 添加到用户级别的配置（所有项目可用）
  - chrome-devtools - MCP 服务器名称
  - -- - 分隔符，后面是实际要执行的命令
  - npx chrome-devtools-mcp@latest -u http://127.0.0.1:9222 - 使用 -u 参数（不是 --browser-url）
## 2026-3-18 新的方法

chrome最新版146版支持原生mcp了，打开方法如下

* chrome://flags/WebMCP-for-testing enable
* chrome://inspect/#remote-debugging 打开

这样就不用上面那种启动chrome的方法了






















