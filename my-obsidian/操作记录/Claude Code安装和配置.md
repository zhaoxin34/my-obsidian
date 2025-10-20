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

## 添加context7 mcp

注册context7 mcp api key https://context7.com/dashboard
