# Claude Code 2.1.39 - 2.1.51 变更记录

本文档整理了 Claude Code 从版本 2.1.39 到 2.1.51 的主要新功能和变更。

---

## 2.1.51

### 新增功能
- **remote-control 子命令**: 新增 `claude remote-control` 子命令，支持外部构建，允许本地环境为所有用户服务
- **插件 Git 超时配置**: 插件市场默认 Git 超时从 30s 增加到 120s，新增 `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` 环境变量配置
- **自定义 npm 注册表**: 支持安装插件时使用自定义 npm 注册表和指定版本固定
- **环境变量**: 新增 `CLAUDE_CODE_ACCOUNT_UUID`、`CLAUDE_CODE_USER_EMAIL`、`CLAUDE_CODE_ORGANIZATION_UUID` 环境变量供 SDK 调用者同步提供账户信息
- **/model 选择器改进**: 显示人类可读的模型标签（如 "Sonnet 4.5"），而非原始模型 ID

### 性能优化
- **BashTool 优化**: 当 shell 快照可用时，默认跳过登录 shell（`-l` 标志），提升命令执行性能
- **工具结果持久化**: 超过 50K 字符的工具结果现在会持久化到磁盘（之前是 100K），减少上下文窗口使用

### 安全修复
- **Hook 安全漏洞**: 修复 `statusLine` 和 `fileSuggestion` hook 命令可能在交互模式下绕过工作区信任执行的问题

### Bug 修复
- 修复重复 `control_response` 消息导致 API 400 错误
- 修复斜杠命令自动完成在插件描述为非字符串类型时崩溃

---

## 2.1.50

### 新增功能
- **LSP 服务器超时配置**: 支持 `startupTimeout` 配置
- **Worktree Hook 事件**: 新增 `WorktreeCreate` 和 `WorktreeRemove` hook 事件，支持在代理 worktree 隔离创建/删除时进行自定义 VCS 设置
- **Agent 工作树隔离**: Agent 定义支持 `isolation: worktree`，允许在隔离的 git worktree 中运行
- **claude agents 命令**: 新增 `claude agents` CLI 命令列出所有配置的代理
- **1M 上下文控制**: 新增 `CLAUDE_CODE_DISABLE_1M_CONTEXT` 环境变量禁用 1M 上下文窗口支持
- **Opus 4.6 快速模式**: 现在包含完整的 1M 上下文窗口
- **VSCode 支持**: 添加 `/extra-usage` 命令支持

### 性能优化
- 改进无头模式（`-p` 标志）启动性能
- 改进长时间会话的内存使用
- 改进提示建议缓存命中率

### Bug 修复
- 修复 Linux 在 glibc < 2.30 系统上的本机模块加载问题
- 修复多个内存泄漏问题
- 修复 Agent Teams 在 Bedrock/Vertex/Foundry 上的失败问题
- 修复 `CLAUDE_CODE_SIMPLE` 模式未完全剥离功能的问题

---

## 2.1.49

### 新增功能
- **MCP OAuth 改进**: 改进 OAuth 认证，支持 step-up auth 和发现缓存
- **Worktree 支持**: 新增 `--worktree` (`-w`) 标志启动隔离的 git worktree
- **后台代理**: Agent 定义支持 `background: true` 始终作为后台任务运行
- **插件默认配置**: 插件可以包含 `settings.json` 提供默认配置
- **ConfigChange Hook**: 新增配置变更时触发的 hook 事件
- **Simple 模式增强**: Simple 模式现在包含文件编辑工具

### 用户体验改进
- **Ctrl+F 杀死后台代理**: 使用 Ctrl+F 杀死后台代理（3秒内按两次确认）
- 文件未找到错误现在建议纠正路径
- 权限提示现在显示限制原因

### 性能优化
- 改进非交互模式启动性能
- 改进 HTTP 和 SSE MCP 服务器的认证失败缓存

---

## 2.1.47

### 用户体验改进
- **VSCode 计划预览**: 改进计划预览，自动更新、仅在计划准备好时启用评论
- **后台代理控制**: 使用 `ctrl+f` 杀死所有后台代理而非按两次 ESC

### Bug 修复
- 文件写入工具保留尾随空行
- Windows 终端渲染修复（包括 `\r\n` 问题）
- 修复大量 bug（超过 50 个）

---

## 2.1.46

### 新增功能
- **MCP 连接器支持**: 支持在 Claude Code 中使用 claude.ai MCP 连接器
- **孤立进程修复**: 修复终端断开后的孤立 CC 进程

---

## 2.1.45

### 新增功能
- **Claude Sonnet 4.6**: 支持新的 Sonnet 4.6 模型
- **目录配置读取**: 支持从 `--add-dir` 目录读取 `enabledPlugins` 和 `extraKnownMarketplaces`
- **自定义提示**: 新增 `spinnerTipsOverride` 设置自定义旋转提示
- **速率限制事件**: 新增 `SDKRateLimitInfo` 和 `SDKRateLimitEvent` 类型

### Bug 修复
- 修复 Agent Teams 在 Bedrock/Vertex/Foundry 上的失败
- 修复沙箱写入临时文件错误
- 修复后台任务工具崩溃
- 修复插件安装后需要重启的问题

---

## 2.1.44

- 修复 ENAMETOOLONG 错误（深层嵌套目录路径）
- 修复认证刷新错误

---

## 2.1.43

- AWS 认证刷新添加 3 分钟超时
- 修复结构化输出 beta header 问题

---

## 2.1.42

### 性能优化
- 改进启动性能（延迟 Zod schema 构建）
- 改进提示缓存命中率

### 新增功能
- Opus 4.6 一次性提示

---

## 2.1.41

### 新增功能
- **认证子命令**: 新增 `claude auth login/status/logout` 子命令
- **Windows ARM64**: 新增 Windows ARM64 (win32-arm64) 原生二进制支持
- **自动命名会话**: `/rename` 无参数时自动从对话上下文生成会话名

### 安全改进
- 防止在 Claude Code 会话中启动 Claude Code

### Bug 修复
- 修复 Agent Teams 在 Bedrock/Vertex/Foundry 使用错误的模型标识符
- 修复 MCP 工具在流式传输时返回图像内容崩溃

---

## 2.1.39

- 终端渲染性能改进
- 修复致命错误被吞没的问题
- 修复会话关闭后进程挂起
- 修复终端屏幕边界字符丢失
- 修复详细转录视图中的空行

---

## 版本遗漏说明

- **2.1.48**: 该版本在 CHANGELOG 中未列出，可能是一个内部版本或跳过了
- **2.1.40**: 该版本在 CHANGELOG 中未列出

---

*文档生成时间: 2026-02-24*
