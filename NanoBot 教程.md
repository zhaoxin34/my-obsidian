Ultra-Lightweight Personal AI Assistant

## 安装
```bash
uv tool install nanobot-ai
```

## 初始化
```bash
nanobot onboard
```

输出如下
>Created config at /Users/zhaoxin/.nanobot/config.json
  Created HEARTBEAT.md
  Created USER.md
  Created SOUL.md
  Created AGENTS.md
  Created TOOLS.md
  Created memory/MEMORY.md
  Created memory/HISTORY.md

## 配置model

修改config.json的providers段
```json
{
  "providers": {
    "minimax": {
      "apiKey": "xxxx",
      "apiBase": "https://api.minimaxi.com/anthropic",
      "extraHeaders": null
    },
  }
}
```