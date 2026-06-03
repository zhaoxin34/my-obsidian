---
title: "使用 OrbStack 运行你的第一个 Ubuntu 虚拟机"
description: "在 macOS 上快速创建和管理轻量级 Linux 开发环境"
---

# 使用 OrbStack 运行你的第一个 Ubuntu 虚拟机

OrbStack 是一款运行在 macOS 上的轻量级工具，可以同时运行 Docker 容器和完整的 Linux 虚拟机。它比 Docker Desktop 更快、更省资源，是 Linux 开发环境的绝佳选择。

本教程将帮助你使用 OrbStack 创建并运行一个 Ubuntu 虚拟机，即使你从未使用过虚拟机也不用担心。

<Note>
完成本教程大约需要 10-15 分钟。
</Note>

## 你将学到什么

- 在 macOS 上安装 OrbStack
- 创建你的第一个 Ubuntu 虚拟机
- 连接到虚拟机并运行命令
- 在 macOS 和 Linux 之间传输文件

## 前置要求

开始之前，请确保你有一台 Mac 电脑，并确认系统版本：

```bash
sw_vers -productVersion
```

你应该看到 macOS 版本号（如 `14.5`）。确保版本为 **13.0 或更高**。

<Tip>
不确定你的 macOS 版本？直接运行上面的命令查看。
</Tip>

## Step 1: 安装 OrbStack

打开终端，安装 OrbStack。最简单的方式是使用 Homebrew：

```bash
brew install orbstack
```

安装完成后，启动 OrbStack：

```bash
open -a OrbStack
```

你应该看到 OrbStack 的菜单栏图标出现在屏幕顶部。

## Step 2: 创建你的第一个 Ubuntu 虚拟机

在终端中，使用 `orb create` 命令创建 Ubuntu 虚拟机：

```bash
orb create ubuntu
```

OrbStack 会自动下载 Ubuntu 镜像并创建虚拟机。整个过程通常在 1 分钟内完成（取决于你的网络速度）。

你应该看到类似这样的输出：

```
Creating ubuntu... Done
Starting ubuntu... Done
```

验证虚拟机已创建并运行：

```bash
orb list
```

你应该看到类似这样的输出：

```
NAME         STATUS    IP          CPUS    MEMORY   PORTS
ubuntu      Running   127.0.0.1   2       2 GB     22 -> 2222
```

<Note>
我们推荐 Ubuntu 作为你的第一个 Linux 发行版，因为它的社区资源最丰富，遇到问题时更容易找到帮助。
</Note>

## Step 3: 连接到虚拟机

现在让我们连接到虚拟机并运行第一个命令：

```bash
orb sh ubuntu
```

你应该看到终端提示符变成了类似这样的格式：

```
username@ubuntu:~$
```

<Note>
如果你有多个虚拟机，可以使用 `orb sh` 命令并指定机器名称，如 `orb sh ubuntu22`。
</Note>

恭喜！你现在已经在 Ubuntu 虚拟机里面了。

## Step 4: 在虚拟机中运行命令

运行第一个命令，看看 Ubuntu 的版本信息：

```bash
cat /etc/os-release
```

你应该看到类似这样的输出：

```
NAME="Ubuntu"
VERSION="24.04 LTS (Noble Numbat)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 24.04 LTS"
VERSION_ID="24.04"
```

查看系统资源：

```bash
df -h
```

你应该看到磁盘使用情况和挂载信息。

## Step 5: 安装第一个软件包

让我们在 Ubuntu 中安装一些有用的工具。

首先，更新软件包列表：

```bash
sudo apt update
```

<Warning>
系统可能会提示输入密码。由于 OrbStack 默认配置了无密码 sudo，直接按回车键即可。
</Warning>

更新完成后，你应该看到类似这样的输出：

```
Reading package lists... Done
Building dependency tree... Done
X packages can be upgraded.
```

现在安装一个实用的工具——htop（系统监控工具）：

```bash
sudo apt install htop -y
```

安装完成后运行 htop：

```bash
htop
```

你应该看到一个实时显示系统资源的界面，显示 CPU 使用率、内存使用情况等信息。

按 `q` 键退出 htop。

## Step 6: 在 macOS 和 Ubuntu 之间传输文件

OrbStack 自动在 macOS 和 Ubuntu 之间共享文件。

**从 Ubuntu 访问 macOS 文件：**

在终端中，你的 macOS 主目录挂载在 Ubuntu 的 `/mnt/mac` 路径：

```bash
ls /mnt/mac
```

你应该看到你的 macOS 主目录内容，包括 Downloads、Documents、Desktop 等文件夹。

**从 macOS 访问 Ubuntu 文件：**

你的 Ubuntu 文件可以从 macOS 的 `~/OrbStack` 目录访问：

```bash
ls ~/OrbStack
```

你应该看到你的虚拟机列表。

**在虚拟机和 macOS 之间复制文件：**

从 macOS 复制到 Ubuntu：

```bash
orb cp /path/on/mac/file.txt ubuntu:/home/user/
```

从 Ubuntu 复制到 macOS：

```bash
orb cp ubuntu:/home/user/file.txt /path/on/mac/
```

## Step 7: 停止和启动虚拟机

当你不需要使用虚拟机时，可以停止它以节省资源：

```bash
orb stop ubuntu
```

你应该看到：

```
Stopping ubuntu... Done
```

重新启动虚拟机：

```bash
orb start ubuntu
```

启动后再次连接：

```bash
orb sh ubuntu
```

<Tip>
你也可以不停止虚拟机，而是让它保持运行状态。OrbStack 使用极少的资源，空闲时几乎不耗电，非常方便。
</Tip>

## 你学到了什么

恭喜你完成了本教程！现在你已经：

- ✓ 在 macOS 上安装了 OrbStack
- ✓ 创建了你的第一个 Ubuntu 虚拟机
- ✓ 连接到虚拟机并运行命令
- ✓ 安装了第一个软件包
- ✓ 在 macOS 和 Ubuntu 之间传输文件
- ✓ 学会了停止和启动虚拟机

## 后续步骤

既然你已经有一个可用的 Ubuntu 环境，可以继续探索：

- **使用 OrbStack 运行 Docker 容器** - OrbStack 原生支持 Docker，学习如何在 Ubuntu 中运行容器
- **配置你的开发环境** - 安装 Node.js、Python、Go 等你需要的开发工具
- **运行服务** - 在 Ubuntu 中启动 nginx、PostgreSQL、Redis 等服务，端口会自动转发到 localhost
- **探索更多发行版** - 试试 Debian、Fedora 或 Arch Linux，看看哪个更适合你

## 命令速查表

| 操作 | 命令 |
|------|------|
| 安装 OrbStack | `brew install orbstack` |
| 启动 OrbStack | `open -a OrbStack` |
| 列出所有虚拟机 | `orb list` |
| 创建新虚拟机 | `orb create ubuntu` |
| 连接到虚拟机 | `orb sh <名称>` |
| 启动虚拟机 | `orb start <名称>` |
| 停止虚拟机 | `orb stop <名称>` |
| 复制文件 | `orb cp <源> <目标>` |
| 查看虚拟机日志 | `orb logs <名称>` |

## 参考资源

- [OrbStack 官方文档](https://docs.orbstack.dev/)
- [OrbStack GitHub](https://github.com/orbstack/orbstack)
- [Ubuntu 官方文档](https://docs.ubuntu.com/)