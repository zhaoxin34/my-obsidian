## 目录

1. [Hook 配置详解](#hook-配置详解)
2. [环境变量](#环境变量)
3. [实战示例](#实战示例)
4. [使用 /hooks 命令配置](#使用-hooks-命令配置)

## Hooks生命周期

![img](https://mintcdn.com/claude-code/rsuu-ovdPNos9Dnn/images/hooks-lifecycle.svg?w=1100&fit=max&auto=format&n=rsuu-ovdPNos9Dnn&q=85&s=614def559f34f9b0c1dec93739d96b64)

---
## Hook 配置详解

### 1. matcher（匹配器）

`matcher` 用于匹配工具名称，仅适用于 **PreToolUse**、**PermissionRequest** 和 **PostToolUse** 事件。

```json
{
  "matcher": "Bash"
}
```

常用匹配模式：
- `Bash` - 仅匹配 Bash 工具
- `Read|Edit|Write` - 匹配多个工具
- `*` - 匹配所有工具
- `tool_input.command matches "正则表达式"` - 匹配命令内容

### 2. type（钩子类型）

Hook 有两种执行类型：

#### type: "command"
执行指定的 bash 命令：

```json
{
  "type": "command",
  "command": "echo 'Hello World'",
  "timeout": 30
}
```

#### type: "prompt"
使用 AI 生成响应：

```json
{
  "type": "prompt",
  "prompt": "请审查以下代码的安全性问题: $CLAUDE_TOOL_INPUT"
}
```

### 3. timeout（超时时间）

命令执行的超时时间，默认 30 秒。

---

## 环境变量

Hooks 可以使用以下环境变量：

| 变量                    | 说明              |
| --------------------- | --------------- |
| `$CLAUDE_PROJECT_DIR` | 项目目录路径          |
| `$CLAUDE_TOOL_NAME`   | 当前工具名称          |
| `$CLAUDE_TOOL_INPUT`  | 工具输入参数（JSON 格式） |
| `$CLAUDE_TOOL_RESULT` | 工具执行结果          |
| `$CLAUDE_SESSION_ID`  | 会话 ID           |

---

## 实战示例

### 示例 1：记录所有 Bash 命令 *亲测有效*

在执行 Bash 命令前自动记录命令到文件：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r'\"\\(.tool_input.command) - \\(.tool_input.description // \"No description\")\"' >> ~/.claude/bash-command-log.txt"
          }
        ]
      }
    ]
  }
}
```

### 示例 2：长时间运行命令前提醒使用 tmux

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "tool == \"Bash\" && tool_input.command matches \"(npm|pnpm|yarn|cargo|pytest)\"",
        "hooks": [
          {
            "type": "command",
            "command": "if [ -z \"$TMUX\" ]; then echo '[Hook] Consider tmux for session persistence' >&2; fi"
          }
        ]
      }
    ]
  }
}
```

### 示例 3：验证用户输入

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/validate-prompt.sh"
          }
        ]
      }
    ]
  }
}
```

### 示例 4：Bash 命令验证脚本

```bash
#!/bin/bash
# validate-bash-command.py - 验证 Bash 命令安全性

import sys
import json

# 从环境变量获取命令
command = "$CLAUDE_TOOL_INPUT"

# 黑名单命令
blacklist = ["rm -rf /", "dd if=/dev/zero", ":(){:|:&};:"]

for cmd in blacklist:
    if cmd in command:
        print(f"警告: 检测到危险命令 {cmd}")
        sys.exit(1)

print("命令验证通过")
```

---

## 使用 /hooks 命令配置

Claude Code 提供了交互式命令来配置 Hooks：

1. 运行 `/hooks` 命令
2. 选择要配置的 Hook 事件（如 PreToolUse）
3. 选择 **+ Add new matcher** 添加匹配器
4. 输入匹配模式（如 `Bash`）
5. 选择 **+ Add new hook** 添加钩子
6. 输入要执行的命令
7. 选择保存位置（项目级或用户级）

---

## 最佳实践

1. **从小处开始**: 先尝试简单的日志记录钩子，再逐步增加复杂逻辑
2. **注意超时**: 如果钩子需要较长时间执行，记得设置合适的 timeout
3. **错误处理**: 确保钩子脚本有适当的错误处理，避免影响主流程
4. **测试验证**: 在正式使用前先用 test 命令测试钩子行为

---

## 相关资源

- [Claude Code 官方文档](https://code.claude.com/docs/en/hooks)
- [Hookify 插件](https://github.com/anthropics/claude-code) - 交互式创建 Hooks

---

> **提示**: 你可以使用 `hookify` 插件来对话式创建 Hooks，省去手写 JSON 的麻烦。
