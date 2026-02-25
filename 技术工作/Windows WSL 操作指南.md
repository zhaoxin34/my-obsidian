WSL (Windows Subsystem for Linux) 是Windows 10/11上运行Linux二进制可执行文件的兼容层，让你可以在Windows上原生运行Linux环境。

## 目录

- [前置要求](#前置要求)
- [安装 WSL](#安装-wsl)
- [基本使用](#基本使用)
- [发行版管理](#发行版管理)
- [文件系统互操作](#文件系统互操作)
- [网络配置](#网络配置)
- [GUI 应用支持](#gui-应用支持)
- [Docker 与 WSL](#docker-与-wsl)
- [性能优化](#性能优化)
- [常见问题](#常见问题)

---

## 前置要求

- **Windows 10 版本 2004 及以上** (Build 19041+)
- **Windows 11** (推荐)
- 需要启用虚拟化功能 (BIOS/UEFI中)

检查系统版本：
```powershell
winver
```

检查虚拟化是否启用：
```powershell
systeminfo | findstr /C:"Hyper-V"
```

---

## 安装 WSL

```powershell
# 安装
wsl --install

# 升级
wsl --update
```

#### 2. 安装发行版

打开 Microsoft Store，搜索并安装你喜欢的 Linux 发行版：

| 发行版 | 命令行安装 |
|--------|-----------|
| Ubuntu | `wsl --install -d Ubuntu` |
| Ubuntu 22.04 LTS | `wsl --install -d Ubuntu-22.04` |
| Ubuntu 24.04 LTS | `wsl --install -d Ubuntu-24.04` |
| Debian | `wsl --install -d Debian` |
| Kali Linux | `wsl --install -d kali-linux` |
| Arch Linux | `wsl --install -d Arch` |

---

## 基本使用

### 启动 WSL

```bash
# 启动默认发行版
wsl

# 启动指定发行版
wsl -d Ubuntu

# 在当前目录启动指定发行版
wsl -d Debian
```

### 退出 WSL

```bash
exit
# 或按 Ctrl+D
```

### 常用命令

```bash
# 列出所有已安装的发行版
wsl --list --verbose
wsl -l -v

# 查看运行中的发行版
wsl --list --running
wsl -l --running

# 关闭指定发行版
wsl --terminate Ubuntu
wsl -t Ubuntu

# 关闭所有运行中的 WSL
wsl --shutdown

# 设置默认发行版
wsl --set-default Ubuntu
```

---

## 发行版管理

### 导入/导出发行版

```bash
# 导出发行版为 tar 文件
wsl --export Ubuntu ubuntu-backup.tar

# 从 tar 文件导入创建新发行版
wsl --import Ubuntu-2 /path/to/store ubuntu-backup.tar

# 删除发行版
wsl --unregister Ubuntu
```

### 版本切换

```bash
# 将发行版从 WSL1 转换为 WSL2
wsl --set-version Ubuntu 2

# 查看当前版本
wsl --list --verbose
```

### 用户管理

```bash
# 创建新用户
sudo adduser username

# 设置默认用户
ubuntu config --default-user username

# 切换到 root 用户
sudo -i
```

---

## 文件系统互操作

### Windows 访问 WSL 文件

```bash
# 在 WSL 中打开 Windows 文件管理器
explorer.exe .

# 在 Windows 文件管理器中访问 WSL
\\wsl$\Ubuntu\home\username

# 挂载 Windows 驱动器到 WSL
ls /mnt/c  # C: 驱动器
ls /mnt/d  # D: 驱动器
```

### WSL 访问 Windows 文件

Windows 文件在 WSL 中的位置：
- C: 驱动器 → `/mnt/c`
- D: 驱动器 → `/mnt/d`

**注意**：建议将项目文件放在 WSL 文件系统中，以获得更好的性能。

### 跨系统复制文件

```bash
# Windows → WSL
cp /mnt/c/path/to/file.txt ~/

# WSL → Windows
cp ~/file.txt /mnt/c/path/to/
```

---

## 网络配置

### 访问 Windows 本地服务

从 WSL 访问 Windows 上的服务：

```bash
# 访问 Windows 上的 localhost 服务
curl http://localhost:8080
```

### 访问 WSL 服务 from Windows

WSL2 有独立的虚拟 IP：

```bash
# 获取 WSL 的 IP 地址
hostname -I

# 在 WSL 中启动服务后，Windows 通过 localhost 访问
# 或通过 WSL 的 IP 地址访问
```

### 端口转发

```powershell
# 将 Windows 端口转发到 WSL（如果需要）
netsh interface portproxy add v4tov4 listenport=8080 connectport=8080 connectaddress=172.x.x.x
```

---

## GUI 应用支持

### 方法一：WSLg (Windows 11 / Windows 10 21H2+)

Windows 11 原生支持 WSLg，可以直接运行 GUI 应用：

```bash
# 安装 Gedit 作为测试
sudo apt install gedit

# 运行 GUI 应用
gedit
```

### 方法二：X Server (旧版 Windows 10)

1. 安装 X Server (如 [VcXsrv](https://sourceforge.net/projects/vcxsrv/) 或 [Xming](https://sourceforge.net/projects/xming/))

2. 在 WSL 中配置：

```bash
# 安装 X11 工具
sudo apt install x11-apps

# 配置 DISPLAY 环境变量
echo 'export DISPLAY=:0' >> ~/.bashrc
source ~/.bashrc

# 测试
xeyes
```

---

## Docker 与 WSL

### Docker Desktop with WSL2 (推荐)

1. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)

2. 在 Docker Desktop 设置中启用 WSL2 集成

3. 在 WSL 中使用 Docker：

```bash
# 验证 Docker 是否可用
docker --version
docker ps

# 使用 Docker Compose
docker-compose --version
```

### Docker 深入集成

```bash
# 将 Docker socket 链接到 WSL
mkdir -p ~/.docker/cli-plugins
ln -sf ~/.docker/cli-plugins/docker-compose ~/.docker/cli-plugins/docker-compose

# 启动 Docker 服务
sudo service docker start
```

---

## 性能优化

### WSL2 内存限制

WSL2 默认会占用约 50% 的可用内存，可以通过 `.wslconfig` 限制：

创建文件 `C:\Users\<用户名>\.wslconfig`：

```ini
[wsl2]
# 限制内存使用
memory=4GB

# 限制处理器数量
processors=2

# 分配更多交换空间
swap=2GB

# 禁用 GUI（可选，提升性能）
guiApplications=false
```

使配置生效：

```powershell
wsl --shutdown
```

### 性能最佳实践

1. **将文件存储在 WSL 文件系统中** - 避免在 `/mnt` 中操作大文件
2. **使用 SSD** - WSL2 对磁盘 I/O 敏感
3. **关闭不使用的发行版** - 减少资源占用
4. **定期清理** - 删除不需要的包和缓存：

```bash
sudo apt autoremove
sudo apt clean
```

---

## 常见问题

### WSL2 比 WSL1 慢？

对于跨文件系统操作（Windows ↔ WSL），WSL1 反而更快。纯 WSL2 操作建议将文件放在 WSL 文件系统中。

### 启动报错 "The virtual machine could not be started"

确保：
1. CPU 虚拟化已在 BIOS/UEFI 中启用
2. Hyper-V 已正确安装

修复：
```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V-All /all /norestart
```

### WSL 中中文显示乱码

```bash
# 设置 locales
sudo locale-gen zh_CN.UTF-8
export LANG=zh_CN.UTF-8

# 在 .bashrc 中添加
echo 'export LANG=zh_CN.UTF-8' >> ~/.bashrc
```

### 网络连接问题

如果 WSL2 无法联网：

```powershell
# 重置 WSL 网络
netsh winsock reset
wsl --shutdown
```

### 发行版无法启动

```bash
# 重新注册发行版
wsl --unregister Ubuntu
wsl --install -d Ubuntu
```

---

## 快捷操作

```powershell
# 一行命令启动 WSL 并执行命令
wsl -e ls -la

# 从 PowerShell 运行 WSL 命令
wsl ls -la

# 混合使用
wsl ls /mnt/c/Users | grep Documents
```

---

## 参考链接

- [WSL 官方文档](https://docs.microsoft.com/zh-cn/windows/wsl/)
- [WSL 安装指南](https://docs.microsoft.com/zh-cn/windows/wsl/install)
- [WSL 配置](https://docs.microsoft.com/zh-cn/windows/wsl/wsl-config)
