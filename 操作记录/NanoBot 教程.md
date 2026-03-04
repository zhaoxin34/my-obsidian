Ultra-Lightweight Personal AI Assistant

## 安装
```bash
uv tool install nanobot-ai
```

## 升级

```bash
uv tool update nanobot-ai
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

到这步可以对话了
```bash
nanobot agent
🐈 Interactive mode (type exit or Ctrl+C to quit)

You: hello

🐈 nanobot
你好！有什么我可以帮你的吗？ 😊
```

## 配置ollama作为model

这里需要注意，ollama一次支持配置一个model，所以，如果配置ollama，必须去掉别的模型配置

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.nanobot/workspace",
      "model": "qwen3:1.7b",
      "maxTokens": 8192,
      "temperature": 0.1,
      "maxToolIterations": 40,
      "memoryWindow": 100
    }
  }
}
{
  "providers": {
    "vllm": {
      "apiKey": "ollama-local",
      "apiBase": "http://localhost:11434/v1",
      "extraHeaders": null
    }
}
```
---