## 简介和前言

[ Store And Recall Code Memory, Fast](https://www.youtube.com/watch?v=iRyRkfzhLQI)
上面这个视频介绍了如何高质量的存储和使用Memory，将 Memory存储到[byterover](https://docs.byterover.dev/cipher/quickstart)


## 安装配置（未实践）

### 安装

```bash
npm install -g @byterover/cipher
```

### 配置

```yaml
# MCP Servers (optional)
mcpServers: 
  filesystem:
    type: stdio
    command: npx
    args:
      - -y
      - '@modelcontextprotocol/server-filesystem'
      - .
# If you don't wanna add any mcp server, leave this like this:
# mcpServers: {}

# Choose ONLY ONE of the following LLM providers
llm:
  provider: openai
  model: gpt-4o-mini
  apiKey: $OPENAI_API_KEY
  maxIterations: 50

# System Prompt - User customizable
systemPrompt:
  enabled: true
  content: |
    You are an AI programming assistant focused on coding and reasoning tasks.
```

llm exampe
```yaml
llm:
  provider: gemini
  model: gemini-2.5-flash
  apiKey: $GEMINI_API_KEY
  maxIterations: 50
```

### Vector Store Configuration

Qdrant
Milvus
ChromaDB
In-Memory (Dev/Test)


存储Memory提示词[[Store Memory]]

召回Memory提示词[[Retrieve Memory]]