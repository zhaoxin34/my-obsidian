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

### 添加starrocksmcp


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
claude mcp add
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