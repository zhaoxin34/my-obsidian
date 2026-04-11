本文档整理了 Claude Code 从版本 2.1.52 到 2.1.71 的主要新功能和变更，按功能类别进行组织。

---

## 新增功能

### CLI 命令与子命令
- **`/loop` 命令**: 新增 `/loop` 命令，支持按 recurring interval (如 `/loop 5m check the deploy`) 运行提示或斜杠命令
- **Cron 调度工具**: 添加了会话内 recurring prompts 的 cron 调度工具
- **`/copy` 命令**: 新增 `/copy` 命令，在存在代码块时显示交互式选择器，允许选择单个代码块或完整响应
- **`/simplify` 和 `/batch`**: 新增捆绑的斜杠命令
- **`/reload-plugins` 命令**: 新增 `/reload-plugins` 命令，无需重启即可激活待处理的插件更改
- **`/claude-api` skill**: 新增 `/claude-api` skill，用于使用 Claude API 和 Anthropic SDK 构建应用

### 认证与远程控制
- **Remote Control 扩展**: 扩展 Remote Control 功能给更多用户使用
- **`/remote-control` 名称参数**: `/remote-control` 和 `claude remote-control` 支持可选的名称参数 (`/remote-control My Project` 或 `--name "My Project"`) 设置自定义会话标题

### 模型支持
- **Opus 4.6 默认 Effort**: Opus 4.6 现在为 Max 和 Team 订阅者默认使用 medium effort
- **"ultrathink" 关键词**: 重新引入 "ultrathink" 关键词来启用下一轮的高 effort
- **Opus 4/4.1 移除**: 从第一方 API 的 Claude Code 中移除了 Opus 4 和 4.1，使用这些模型的用户自动迁移到 Opus 4.6
- **Sonnet 4.6 迁移**: 将 Pro/Max/Team Premium 的 Sonnet 4.5 用户自动迁移到 Sonnet 4.6
- **Effort 级别显示**: 在 logo 和 spinner 中显示 effort 级别 (如 "with low effort")

### Voice 功能
- **新语言支持**: Voice STT 支持 10 种新语言 (共 20 种) — 俄语、波兰语、土耳其语、荷兰语、乌克兰语、希腊语、捷克语、丹麦语、瑞典语、挪威语
- **数字键盘支持**: 在 Claude 的面试问题中添加数字键盘支持选择选项
- **Push-to-Talk 按键绑定**: 添加 `voice.pushToTalk` keybinding，可在 `keybindings.json` 中重新绑定 voice 激活键 (默认: 空格)

### 插件与 MCP
- **HTTP Hooks**: 新增 HTTP hooks，可以 POST JSON 到 URL 并接收 JSON，而不是运行 shell 命令
- **`/plugin` 改进**: 改进插件提供的 MCP server 去重 — 重复的手动配置的 server 现在会被跳过
- **`oauth.authServerMetadataUrl` 配置**: 添加 `oauth.authServerMetadataUrl` 配置选项，供 MCP servers 在标准发现失败时指定自定义 OAuth 元数据发现 URL
- **手动 URL 粘贴**: 在 MCP OAuth 认证期间添加手动 URL 粘贴后备
- **`ENABLE_CLAUDEAI_MCP_SERVERS=false`**: 添加 `ENABLE_CLAUDEAI_MCP_SERVERS=false` 环境变量以选择退出 claude.ai MCP servers
- **`pathPattern` 严格市场**: 在 `strictKnownMarketplaces` 添加 `pathPattern` 用于 regex 匹配文件/目录市场源
- **插件源类型 `git-subdir`**: 添加 `git-subdir` 插件源类型，指向 git repo 内的子目录
- **`pluginTrustMessage`**: 在托管设置中添加 `pluginTrustMessage`，用于在插件信任警告前附加组织特定上下文
- **`includeGitInstructions` 设置**: 添加 `includeGitInstructions` 设置 (和 `CLAUDE_CODE_DISABLE_GIT_INSTRUCTIONS` 环境变量) 以从 Claude 系统提示中移除内置的提交和 PR 工作流指令
- **`sandbox.enableWeakerNetworkIsolation`**: 添加 `sandbox.enableWeakerNetworkIsolation` 设置 (仅 macOS)，允许 Go 程序如 `gh`、`gcloud`、`terraform` 在使用自定义 MITM 代理时验证 TLS 证书

### Hook 事件
- **`InstructionsLoaded` Hook**: 新增 `InstructionsLoaded` hook 事件，在 CLAUDE.md 或 `.claude/rules/*.md` 文件加载到上下文时触发
- **Hook 字段增强**: 在 hook 事件中添加 `agent_id` (subagents) 和 `agent_type` (subagents 和 `--agent`)
- **Worktree Hook 字段**: 在 status line hook 命令中添加 `worktree` 字段，包含 name、path、branch 和原始 repo 目录
- **`TeammateIdle` 和 `TaskCompleted` 改进**: 支持 `{"continue": false, "stopReason": "..."}` 来停止 teammate

### 配置与会话
- **项目配置与 auto memory 共享**: 项目配置和 auto memory 现在在同一 repository 的 git worktrees 间共享
- **`/resume` 改进**: `/resume` 选择器现在显示最近的提示而非第一个
- **`/rename` 改进**: `/rename` 现在在 Claude 处理时也能工作
- **`/model` 改进**: 改进 `/model` 命令在斜杠命令菜单中显示当前活动的模型
- **会话上传改进**: 改进会话上传和 memory sync，避免在大小/二进制检查前将大文件读入内存

### Bash 自动化
- **Bash 自动批准列表扩展**: 在 bash 自动批准列表中添加 `fmt`、`comm`、`cmp`、`numfmt`、`expr`、`test`、`printf`、`getconf`、`seq`、`tsort` 和 `pr`

### 其他
- **Always copy full response**: 在 `/copy` 选择器中添加 "Always copy full response" 选项
- **`${CLAUDE_SKILL_DIR}` 变量**: 添加 `${CLAUDE_SKILL_DIR}` 变量供 skills 在 SKILL.md 内容中引用自己的目录
- **启动提示**: 添加一次性的启动提示，建议 macOS 和 Windows 用户使用 Claude Code Desktop (最多显示 3 次，可关闭)
- **策略限制获取**: 为 Team plan OAuth 用户获取策略限制 (如远程控制限制)，而不仅仅是 Enterprise

---

## 性能优化

### 启动性能
- 改进 `--worktree` 启动，消除了启动路径上的 git 子进程
- 改进 macOS 启动，消除了托管设置解析时多余的 settings-file reloads
- 改进 macOS 启动，为 claude.ai enterprise/team 用户跳过不必要的 keychain 查找
- 改进 MCP `-p` 启动，通过管道化 claude.ai 配置获取与本地连接
- 改进 voice 启动，移除了 imperceptible warmup pulse 动画
- 改进启动时间，推迟原生 image processor 加载到首次使用时
- 延迟 Yoga WASM 预加载，减少约 16MB 基线内存

### 内存优化
- 修复多个内存泄漏问题：
  - 桥接轮询循环中的 listener 泄漏
  - MCP OAuth flow 清理中的 listener 泄漏
  - hooks 配置菜单中的内存泄漏
  - 交互式权限处理程序中的 listener 泄漏
  - 文件计数缓存忽略 glob ignore patterns
  - bash 命令前缀缓存中的内存泄漏
  - MCP tool/resource 缓存泄漏
  - IDE host IP 检测缓存错误跨端口共享结果
  - WebSocket listener 泄漏
  - git root 检测缓存中的内存泄漏
  - JSON 解析缓存中的内存泄漏
  - VSCode: 远程会话不显示在对话历史中
  - REPL bridge 中的竞争条件
  - AppState 中长运行的 teammates 保留所有消息
  - MCP server fetch 缓存在断开时未清除
  - 子代理上下文压缩期间剥离重型进度消息负载
  - 长会话中 in-process teammates 的内存保留
  - 交互模式下 hook 事件无界累积
  - React Compiler `memoCache` 中旧消息数组版本累积
  - REPL render scopes 累积 (~35MB over 1000 turns)
  - API 400 errors in forked agents (autocompact, summarization)
- 改进长时间会话内存使用 (处理后清除大型工具结果)
- 改进长时间会话内存使用 (压缩后清除内部缓存)
- 改进长时间会话内存使用 (压缩后清除内部缓存)
- 改进 LSP tool 渲染和内存上下文构建，不再读取整个文件
- 减少会话恢复 (包括压缩历史) 的内存使用

### 渲染与终端
- 改进 spinner 性能，通过将 50ms 动画循环与周围 shell 隔离
- 改进原生二进制中的 UI 渲染性能 (React Compiler)
- 减少 token 使用量，更简洁的子代理最终报告
- 减少约 74% 的 prompt input re-renders

### 网络
- 减少 Remote Control `/poll` 频率到每 10 分钟一次 (连接时)，减少约 300 倍服务器负载

### 其他
- 改进 MCP 二进制内容处理：返回 PDF、Office 文档或音频的工具现在将解码字节保存到磁盘，并带有正确的文件扩展名
- 改进文件操作性能，避免在存在性检查时读取文件内容 (6 处)

---

## Bug 修复

### Windows 特定
- 修复 Windows 上 VS Code 扩展崩溃 ("command 'claude-vscode.editor.openLast' not found")
- 修复 Windows 上导致 UI 闪烁的问题
- 修复 Windows 上 BashTool 失败 (EINVAL 错误)
- 修复 Windows 上的 panic ("switch on corrupted value")
- 修复 Windows 上生成多个进程时可能崩溃的问题
- 修复 Linux x64 和 Windows x64 上 WebAssembly 解释器中的崩溃
- 修复 Windows ARM64 上 2 分钟后有时崩溃的问题
- 修复并发写入损坏 Windows 上配置文件的问题
- 修复 Windows 上的 worktree 文件复制
- 修复 Windows 上全局 `.claude` 文件夹检测
- 修复 Windows/WSL 上剪贴板损坏非 ASCII 文本 (CJK, emoji)
- 修复 Windows 上启动时打开额外 VS Code 窗口的问题

### Shell
- 修复 shell 命令在的工作目录被删除后不显示清晰错误消息的问题
- 修复 compound bash 命令的权限提示显示链式命令而非仅显示 "Yes, allow reading from <dir>/"
- 修复 heredoc 提交消息的 false-positive 权限提示
- 修复 Windows 上模型使用 mingw 风格路径时提示 `cd <cwd> && git ...`
- 修复 Bash tool 错误消息中的重复输出

### 会话管理
- 修复 `/resume` 预览显示原始 XML 标签
- 修复大型第一提示 (>16KB) 的会话在列表中消失
- 修复 SSH 断开时会话数据丢失
- 修复 `/resume` 在第一消息超过 16KB 或使用数组格式内容时静默丢弃会话
- 修复会话关闭后进程挂起
- 修复 `/resume` 会话列表显示中断消息为标题
- 修复会话名称在 compaction 后丢失
- 修复自定义会话标题在恢复后丢失
- 修复 forked conversations (`/fork`) 共享相同的 plan 文件

### 文件操作
- 修复 ENAMETOOLONG 错误 (深层嵌套目录路径)
- 文件未找到错误现在建议纠正路径

### Agent 与 Subagent
- 修复 Agent Teams 在 Bedrock/Vertex/Foundry 上的失败问题
- 修复 Agent Teams 使用错误的模型标识符
- 修复后台任务工具崩溃 (Task tool ReferenceError)
- 修复后台任务结果返回原始转录数据而非最终答案
- 修复 teemmates 意外通过 Agent tool 的 `name` 参数生成嵌套 teemmates

### Hook
- 修复 hook 阻塞错误不向用户显示 stderr
- 修复 hook 阻塞错误显示 stderr 内容在 UI 中
- 修复 hooks (PreToolUse、PostToolUse) 在 Windows 上静默失败

### 插件与 MCP
- 修复 MCP 服务器在延迟加载后不出现在 MCP 管理对话框
- 修复斜杠命令自动完成在插件描述为非字符串类型时崩溃
- 修复技能名称/描述为裸数字时崩溃
- 修复参数提示使用 YAML 序列语法时崩溃
- 修复插件代理技能使用裸名称加载失败
- 修复 MCP OAuth token refresh 竞争条件
- 修复 `--mcp-config` 指向损坏文件时挂起
- 修复插件安装在使用多个 Claude Code 实例时丢失

### 模型相关
- 修复使用 `ANTHROPIC_BASE_URL` 与第三方网关时的 API 400 错误
- 修复使用自定义 Bedrock inference profiles 或其他不符合标准 Claude 命名模式的模型标识符时的 "API Error: 400 This model does not support the effort parameter"
- 修复 `ToolSearch` 后立即出现空模型响应
- 修复 MCP server 带 `instructions` 在第一轮后连接时的 prompt-cache bust
- 修复 `--model claude-opus-4-0` 和 `--model claude-opus-4-1` 解析到已弃用的 Opus 版本而非当前版本

### Voice
- 修复 voice 模式在 Windows 原生二进制上失败 ("native audio module could not be loaded")
- 修复 push-to-talk 在会话启动时未激活
- 修复 voice 波形光标在中间输入时覆盖第一个后缀字母
- 修复 voice 输入在 warmup 期间显示所有 5 个空格

### 权限
- 修复 "始终允许" 多行 bash 命令创建无效权限模式
- 修复设置更改时清除陈旧权限规则

### 其他
- 修复 `/resume` 在第一消息超过 16KB 或使用数组格式内容时静默丢弃会话
- 修复 `/mcp reconnect` 在给定不存在的服务器名时冻结 CLI
- 修复 `/rename` 后状态栏中的会话名称持续存在
- 修复用户定义的代理仅在 NFS/FUSE 文件系统上加载一个文件
- 修复自定义代理的 `model` 字段在生成团队队友时被忽略
- 修复计划模式在上下文压缩后丢失
- 修复 `alwaysThinkingEnabled: true` 在 Bedrock 和 Vertex 提供商上未启用思考模式
- 修复后台任务通知在流式传输 Agent SDK 模式下未送达
- 修复 `/stats` 在转录文件包含缺失或格式错误的时间戳条目时崩溃
- 修复 ctrl+o (转录切换) 在有很多文件编辑的长会话中冻结几秒钟
- 修复 `--setting-sources user` 不阻止动态发现的项目技能
- 修复从嵌套在主 repo 内的工作树运行时重复加载 CLAUDE.md、斜杠命令、代理和规则
- 修复任何 `/plugin` 操作后插件 Stop/SessionEnd 等 hooks 不触发
- 修复两个插件使用相同 `${CLAUDE_PLUGIN_ROOT}/...` 命令模板时插件 hooks 被静默丢弃
- 修复 stdin 冻结，长会话中击键停止处理但进程保持存活
- 修复 Read tool 在图像处理失败时将过大的图像放入上下文
- 修复 Chrome 扩展自动检测在本地没有 Chrome 的机器上运行后永久卡在 "not installed"
- 修复 `/plugin marketplace update` 在市场固定到 branch/tag ref 时失败并出现合并冲突
- 修复 `/permissions` 工作区 tab 中的重复条目
- 修复 `--print` 在配置了 team agents 时永远挂起
- 修复 "/color" 命令无法重置回默认颜色

---

## 安全修复

- **嵌套技能发现**: 修复嵌套技能发现可能从 gitignored 目录如 `node_modules` 加载技能的安全问题
- **信任对话框**: 修复信任对话框在首次运行时静默启用所有 `.mcp.json` 服务器的问题
- **Hook 安全漏洞**: 修复 `statusLine` 和 `fileSuggestion` hook 命令可能在交互模式下绕过工作区信任执行的问题
- **防止嵌套启动**: 防止在 Claude Code 会话中启动 Claude Code
- **权限设置**: 修复 `disableAllHooks` 设置尊重托管设置层次结构
- **符号链接绕过**: 修复通过符号链接父目录写入新文件可能在 `acceptEdits` 模式下逃逸工作目录的问题

---

## 用户体验改进

### 消息反馈
- 修复自动压缩失败错误通知显示给用户
- 修复压缩失败时显示错误通知

### 权限提示
- 权限提示现在显示限制原因而非空提示
- 改进了路径安全和工作目录阻止的权限提示

### VSCode 集成
- **计划预览**: 改进计划预览，自动更新、仅在计划准备好时启用评论、拒绝时保持预览打开以便修改
- **会话列表**: 在 VS Code 活动栏添加火花图标，列出所有 Claude Code 会话
- **计划文档视图**: 在 VS Code 中添加完整的 markdown 文档视图查看计划
- **原生 MCP 管理**: 添加原生 MCP server 管理对话框

### 后台代理
- 使用 `ctrl+f` 杀死所有后台代理而非按两次 ESC
- 后台代理现在在您按 ESC 取消主线程时继续运行

### 其他
- 改进了窄终端布局 (提示页脚)
- 改进了折叠的读取/搜索组以显示当前正在处理的文件或搜索模式
- 修复旋转器显示 "0 tokens" 计数器 (实际未收到 token 前)
- 修复旋转器不尊重自定义 spinnerVerbs
- 修复 CJK 宽字符导致时间戳和布局元素错位
- 修复折叠的读取/搜索组以显示当前正在处理的文件或搜索模式
- 修复 plan mode feedback input 不支持多行文本输入
- 修复光标不向下移动到输入框顶部的空行
- 修复转录切换在长会话中冻结

---

## 版本遗漏说明

- **2.1.54**: 该版本在 CHANGELOG 中未列出，可能是一个内部版本或跳过了
- **2.1.57**: 该版本在 CHANGELOG 中未列出
- **2.1.60**: 该版本在 CHANGELOG 中未列出
- **2.1.64**: 该版本在 CHANGELOG 中未列出
- **2.1.65**: 该版本在 CHANGELOG 中未列出
- **2.1.66**: 该版本在 CHANGELOG 中未列出
- **2.1.67**: 该版本在 CHANGELOG 中未列出

---

*文档生成时间: 2026-03-08*
