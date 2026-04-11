[官网https://skills.sh/](https://skills.sh/)

Skills are reusable capabilities for AI agents. Install them with a single command to enhance your agents with access to procedural knowledge.

---

# Skills 快速入门教程

在本教程中，你将学会如何安装和使用 AI 代理的 Skills。通过跟随本教程，你将能够快速扩展你的 AI 代理能力。

<Note>
本教程大约需要 5 分钟完成。
</Note>

## 什么是 Skills？

Skills 是 AI 代理的可重用能力模块。通过安装 Skills，你的 AI 代理可以获取额外的功能，比如：
- 操作 Apple Calendar 和 Reminders
- 发送邮件
- 运维 Wolf 产品系统
- 等等...

## Step 1: 查找可用的 Skills

首先，让我们看看有哪些 Skills 可供安装。

打开终端，运行以下命令：

```bash
npx skills find
```

你应该看到类似以下的输出：

```
📦 Available skills:

  • apple-calendar      - Apple Calendar.app integration
  • apple-reminders    - Manage Apple Reminders
  • apple-mail         - Interact with Apple Mail
  • wolf-ops           - Wolf product operations
  • wezterm-cli        - Wezterm terminal integration
  ...

Total: 20+ skills available
```

<Note>
如果这是你第一次运行，可能需要等待几秒钟来下载技能列表。
</Note>

## Step 2: 查看已安装的 Skills

现在，让我们看看你的 AI 代理已经安装了哪些 Skills。

运行以下命令：

```bash
npx skills list -g
```

你应该看到类似以下的输出：

```
🔧 Global skills (used by agents):

  ✓ apple-calendar    - Calendar integration enabled
  ✓ apple-reminders   - Reminders management enabled
  ✓ obsidian          - Obsidian note management

Total: 3 global skills installed
```

<Tip>
使用 `-g` 参数可以查看全局安装的 Skills，了解哪些能力已经对你的 AI 代理可用。
</Tip>

## Step 3: 安装新的 Skill（可选）

如果你想为你的项目添加新的 Skill，可以运行：

```bash
npx skills install <skill-name>
```

例如，安装 wezterm-cli：

```bash
npx skills install wezterm-cli
```

你应该看到：

```
✓ Installing wezterm-cli...
✓ Skill installed successfully!
```

<Warning>
如果你在安装时遇到问题，确保你已经安装了 Node.js 和 npm。访问 https://nodejs.org 下载安装。
</Warning>

## 你已学会的内容

在本教程中，你：

- ✅ 了解了什么是 Skills
- ✅ 使用 `npx skills find` 查找可用的 Skills
- ✅ 使用 `npx skills list -g` 查看已安装的 Skills

## 下一步

现在你已经掌握了 Skills 的基础，可以：

- **[Skills 官网](https://skills.sh/)** - 查看完整的 Skills 列表和文档
- **探索更多 Skills** - 尝试安装你感兴趣的 Skills
- **创建自己的 Skill** - 将你的工作流程封装为可重用的 Skill

---

## 快速参考

| 操作 | 命令 |
|------|------|
| 查找可用 Skills | `npx skills find` |
| 查看全局 Skills | `npx skills list -g` |
| 安装 Skill | `npx skills install <name>` |