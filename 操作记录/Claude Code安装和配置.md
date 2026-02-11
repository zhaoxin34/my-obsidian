# 文档

https://docs.claude.com/en/docs/claude-code/quickstart
## 安装

[![](https://camo.githubusercontent.com/42dd0d4d66d954a88749cfbcf0b9ddcb7675d2f7bd8072675e99e6da8abde5c0/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4e6f64652e6a732d31382532422d627269676874677265656e3f7374796c653d666c61742d737175617265)](https://camo.githubusercontent.com/42dd0d4d66d954a88749cfbcf0b9ddcb7675d2f7bd8072675e99e6da8abde5c0/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4e6f64652e6a732d31382532422d627269676874677265656e3f7374796c653d666c61742d737175617265) [![npm](https://camo.githubusercontent.com/961ca37273ecd043d77954d3cf7d9fb9a2da2d5cf043ba6dca3609debae0ff6e/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f762f40616e7468726f7069632d61692f636c617564652d636f64652e7376673f7374796c653d666c61742d737175617265)](https://www.npmjs.com/package/@anthropic-ai/claude-code)

```bash
npm install -g @anthropic-ai/claude-code
```

## 配置claude code使用glm

运行claude，这时会报错，说禁止中国访问，ctrlc结束它，这时~/.claude目录有了，创建文件
~/.claude/settings.json
```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "5e58910a65cd43869e73adc42869772d.V2T1Gn7ccArKGiM8",
    "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.6",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.6"
  },
  "alwaysThinkingEnabled": true
}
```

再次进入就好了

## 配置mcp

*值得一看* [[如何通过curl访问mcp]]

### 配置文件的位置

`~/.claude.json`

### 重要的命令

claude mcp add
claude mcp add-json -s user '{json}'
claude mcp remove xxxx
  
### 添加context7 mcp

注册context7 mcp api key https://context7.com/dashboard

```bash
claude mcp add --transport http context7 https://mcp.context7.com/mcp --header "CONTEXT7_API_KEY: ctx7sk-557ec667-d615-488c-891d-0c6fb25d6c31"
```

### 添加starrocks mcp


```bash
# 首先用nv启动这个mcp的server
  STARROCKS_HOST=${STARROCKS_HOST:-localhost} \
    STARROCKS_PORT=${STARROCKS_PORT:-9030} \
    STARROCKS_USER=${STARROCKS_USER:-root} \
    STARROCKS_PASSWORD=$1 \
    STARROCKS_DB=${STARROCKS_DB:-wolf} \
    uv run --with mcp-server-starrocks mcp-server-starrocks \
    --mode streamable-http \
    --host 0.0.0.0 \
    --port $port \

# 添加
claude mcp add -s user --transport http mcp-server-starrocks http://localhost:9040/mcp
```

###  playwright

claude mcp add playwright npx @playwright/mcp@latest

### mysql

```bash
claude mcp add mcp_server_mysql \
  -e MYSQL_HOST="127.0.0.1" \
  -e MYSQL_PORT="3306" \
  -e MYSQL_USER="root" \
  -e MYSQL_PASS="your_password" \
  -e MYSQL_DB="your_database" \
  -e MYSQL_POOL_SIZE="10" \
  -e MYSQL_QUERY_TIMEOUT="30000" \
  -e MYSQL_CACHE_TTL="60000" \
  -e MYSQL_RATE_LIMIT="100" \
  -e MYSQL_SSL="true" \
  -e ALLOW_INSERT_OPERATION="false" \
  -e ALLOW_UPDATE_OPERATION="false" \
  -e ALLOW_DELETE_OPERATION="false" \
  -e MYSQL_ENABLE_LOGGING="true" \
  -- npx @benborla29/mcp-server-mysql
```
## chrome dev tool

```bash
claude mcp add -s user chrome-devtools npx chrome-devtools-mcp@latest
```

*如果想使用当前浏览器，需要如下命令启动一个浏览器*

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-profile-stable
```

> 注意9222是调试端口，user-data-dir是一个新的用户目录，防止冲突



## 安装百炼搜索mcp

```js
    "WebSearch": {
      "type": "sse",
      "url": "https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/sse",
      "headers": {
        "Authorization": "Bearer ${BAILIAN_API_KEY}"
      }
    }
```


## Tip

* Run claude --debug to see logs inline, or view log files i  /Users/zhaoxin/Library/Caches/claude-cli-nodejs/-Volumes-data-working-docker 

## 使用skills

### 安装市场和示例skills

`claude: /plugin marketplace add anthropics/skills`

 **这个命令可能会由于墙的问题clone不下来，那样的话就手动下载就行，方法如下所示**
 
```bash
cd ~/.claude/plugins/marketplaces
git clone https://github.com/anthropics/skills anthropics-skills
```

`claude: /plugin  marketplace add ~/.claude/plugins/marketplaces/anthropics-skills`

*然后再用/plugin按提示安装skills*

## 自定义statusline

使用第三方插件

```bash
npm install -g @cometix/ccline

# 以下是相关命令，并不需要运行
# Initialize configuration file
ccline --init

# Check configuration validity  
ccline --check

# Print current configuration
ccline --print

# Enter TUI configuration mode
ccline --config
```

修改~/.claude/settings.json 加入下面这段

```json
{
  "statusLine": {
    "type": "command", 
    "command": "~/.claude/ccline/ccline",
    "padding": 0
  }
}
```

## 工具介绍

### 列举当前tools

```bash
当前claude code有多少种tools，列举一下

⏺ 根据我的配置，Claude Code目前有以下几类工具：

  内置工具 (Built-in Tools)

  1. Task - 启动专门的代理来处理复杂的多步骤任务
  2. Bash - 执行shell命令
  3. Glob - 文件模式匹配搜索
  4. Grep - 基于ripgrep的强大搜索工具
  5. Read - 读取文件内容
  6. Edit - 精确的字符串替换编辑
  7. Write - 写入新文件
  8. NotebookEdit - 编辑Jupyter笔记本单元格
  9. WebFetch - 获取网页内容
  10. WebSearch - 网络搜索
  11. TodoWrite - 任务列表管理
  12. ExitPlanMode - 退出计划模式
  13. AskUserQuestion - 向用户提问
  14. Skill - 执行专业技能
  15. SlashCommand - 执行斜杠命令
  16. BashOutput - 获取后台shell输出
  17. KillShell - 终止后台shell

  技能工具 (Skills)

  专业技能包括：
  - document-skills:xlsx - Excel电子表格处理
  - document-skills:docx - Word文档处理
  - document-skills:pptx - PowerPoint演示文稿处理
  - document-skills:pdf - PDF文档处理
  - example-skills:skill-creator - 创建新技能的指南
  - example-skills:mcp-builder - MCP服务器构建指南
  - example-skills:canvas-design - 视觉艺术设计
  - example-skills:algorithmic-art - 算法艺术生成
  - example-skills:internal-comms - 内部沟通文档
  - example-skills:webapp-testing - Web应用测试
  - example-skills:artifacts-builder - 复杂HTML构建
  - example-skills:slack-gif-creator - Slack GIF创作
  - example-skills:theme-factory - 主题样式工具
  - example-skills:brand-guidelines - 品牌规范工具

  MCP服务器工具 (MCP Server Tools)

  当前没有配置MCP服务器，但可以通过MCP协议扩展更多外部工具。

⏺ 总计约18种内置工具 + 13种专业技能工具 = 31种主要工具类型。
```

```bash
我想你给我展示当前claude code加载了哪些skills

⏺ 根据当前配置，Claude Code 加载了以下技能：

  网页获取

  - web-fetcher - 获取 URL 对应的内容

  文档处理

  - document-skills:xlsx - 电子表格创建、编辑和分析
  - document-skills:docx - Word 文档创建、编辑和分析
  - document-skills:pptx - 演示文稿创建、编辑和分析
  - document-skills:pdf - PDF 文档处理工具包

  开发指南

  - example-skills:skill-creator - 创建有效技能的指南
  - example-skills:mcp-builder - 构建高质量 MCP 服务器的指南

  设计创作

  - example-skills:canvas-design - 创建 .png 和 .pdf 格式的视觉艺术设计
  - example-skills:algorithmic-art - 使用 p5.js 创建算法艺术
  - example-skills:artifacts-builder - 创建复杂的多组件 HTML artifacts
  - example-skills:slack-gif-creator - 为 Slack 创建动画 GIF
  - example-skills:theme-factory - 为 artifacts 设置主题
  - example-skills:brand-guidelines - 应用 Anthropic 官方品牌风格

  实用工具

  - example-skills:internal-comms - 编写内部交流资料
  - example-skills:webapp-testing - 使用 Playwright 测试本地 Web 应用
```

* [web-fetch-tool](https://docs.claude.com/en/docs/agents-and-tools/tool-use/web-fetch-tool)


## 值得一看
