## 目录

1. [Hook 类型详解](#hook-类型详解)
2. [配置文件的结构](#配置文件的结构)
3. [Hook 配置详解](#hook-配置详解)
4. [环境变量](#环境变量)
5. [实战示例](#实战示例)
6. [使用 /hooks 命令配置](#使用-hooks-命令配置)

---

## 什么是 Hooks

**Hooks（钩子）** 是基于触发器的自动化机制，在特定事件时触发执行自定义逻辑。与 Skills 不同，Hooks 被限制在工具调用和生命周期事件中。

### Hooks 的工作原理

```
用户输入 → SessionStart → UserPromptSubmit → PreToolUse → 工具执行 → PostToolUse → Stop → SessionEnd
                                                              ↓
                                                       PreCompact
```

Hooks 在 Claude Code 会话的关键节点触发，使你能够在 AI 助手执行操作前后插入自定义代码。

---

## Hook 类型详解

Claude Code 提供以下类型的 Hook：

| Hook 类型 | 触发时机 | 典型用途 |
|-----------|----------|----------|
| **SessionStart** | 会话开始或恢复时 | 初始化环境变量、加载项目上下文 |
| **UserPromptSubmit** | 用户提交提示时 | 验证或修改用户输入 |
| **PreToolUse** | 工具执行前 | 审批或修改工具调用、验证命令 |
| **PermissionRequest** | 需要用户权限时 | 自定义权限处理 |
| **PostToolUse** | 工具执行成功后 | 处理工具执行结果、格式化输出 |
| **SubagentStart** | 子代理启动时 | 记录子代理启动信息 |
| **SubagentStop** | 子代理完成时 | 处理子代理结果 |
| **Stop** | 主代理完成响应时 | 决定是否继续执行 |
| **PreCompact** | 上下文压缩前 | 准备压缩上下文 |
| **Notification** | 权限请求时 | 自定义通知 |
| **SessionEnd** | 会话终止时 | 清理资源、保存会话数据 |

---

## 配置文件的结构

Hooks 配置文件通常位于 `.claude/settings.json`，基本结构如下：

```json
{
  "description": "插件描述",
  "hooks": {
    "EventName": [
      {
        "matcher": "匹配模式",
        "hooks": [
          {
            "type": "command",
            "command": "要执行的命令",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### 配置位置

- **项目级配置**: `.claude/settings.json` - 仅对当前项目生效
- **用户级配置**: `~/.claude/settings.json` - 对所有项目生效

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

| 变量 | 说明 |
|------|------|
| `$CLAUDE_PROJECT_DIR` | 项目目录路径 |
| `$CLAUDE_TOOL_NAME` | 当前工具名称 |
| `$CLAUDE_TOOL_INPUT` | 工具输入参数（JSON 格式） |
| `$CLAUDE_TOOL_RESULT` | 工具执行结果 |
| `$CLAUDE_SESSION_ID` | 会话 ID |

---

## 实战示例

### 示例 1：记录所有 Bash 命令

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
