# Fedora 安装与初始化

> 适用版本：Fedora 41/42 Workstation，UEFI + GPT，GNOME（Wayland 默认）。

## 0. 下载镜像

- 官方：<https://getfedora.org/en/workstation/download/>
- 国内镜像：<https://mirror.tuna.tsinghua.edu.cn/fedora/releases/>
- 推荐 **Workstation** 版本（GNOME 桌面），如果是服务器请用 Server 版

## 1. 制作启动 U 盘

macOS 下用 `dd` 或 balenaEtcher：

```bash
# 查看 U 盘设备
diskutil list

# 取消挂载（不要 eject）
diskutil unmountDisk /dev/disk4

# 写入镜像（注意 if=/dev/rdisk4 加速）
sudo dd if=/path/to/Fedora-Workstation-Live-x86_64-*.iso \
       of=/dev/rdisk4 bs=4m status=progress
```

## 2. 安装

1. U 盘启动 → "Install Fedora"
2. 关键选择：
   - **Installation Destination** → 自动分区即可（NVMe 选 Ext4 或 Btrfs）
   - **Network & Host Name** → 插网线 / 连 Wi-Fi，**顺手打开网络**，避免装机时拿不到最新包
3. 设置 root 密码 + 创建用户（**勾上 Make this user administrator**）

## 3. 首次启动后的基本更新

```bash
# 系统全量更新（第一次会比较久）
sudo dnf upgrade --refresh -y

# 安装 RPM Fusion 仓库（包含大量非自由/闭源软件：ffmpeg、nvidia、steam 等）
sudo dnf install \
  https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
  https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

# 基础开发工具链
sudo dnf install -y \
  @development-tools \
  git curl wget vim nano \
  tar unzip p7zip p7zip-plugins \
  openssh-server rsync

# 启用 SSH（开机自启 + 立即启动）
sudo systemctl enable --now sshd
sudo systemctl status sshd
```

## DNF 镜像加速

默认源在境外，国内很慢。换成清华/阿里：

```bash
sudo mkdir -p /etc/dnf/protected.d
# 屏蔽默认源（如果以后想用回来可以恢复）
sudo tee /etc/dnf/protected.d/google-chrome.repo <<'EOF'
[this repo is protected]
EOF

# 添加清华镜像
sudo tee /etc/yum.repos.d/fedora.repo <<'EOF' >/dev/null
[fedora]
name=Fedora $releasever - $basearch
baseurl=https://mirrors.tuna.tsinghua.edu.cn/fedora/releases/$releasever/Everything/$basearch/os/
enabled=1
metadata_expire=7d
repo_gpgcheck=0
type=rpm
gpgcheck=1
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/fedora/releases/$releasever/Everything/$basearch/os/RPM-GPG-KEY-fedora-$releasever-$basearch

[fedora-modular]
name=Fedora $releasever - Modular
baseurl=https://mirrors.tuna.tsinghua.edu.cn/fedora/releases/$releasever/Modular/$basearch/os/
enabled=1
metadata_expire=7d
repo_gpgcheck=0
type=rpm
gpgcheck=1
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/fedora/releases/$releasever/Everything/$basearch/os/RPM-GPG-KEY-fedora-$releasever-$basearch

[fedora-updates]
name=Fedora $releasever - $basearch - Updates
baseurl=https://mirrors.tuna.tsinghua.edu.cn/fedora/updates/$releasever/Everything/$basearch/
enabled=1
metadata_expire=7d
repo_gpgcheck=0
type=rpm
gpgcheck=1
gpgkey=https://mirrors.tuna.tsinghua.edu.cn/fedora/releases/$releasever/Everything/$basearch/os/RPM-GPG-KEY-fedora-$releasever-$basearch
EOF

sudo dnf makecache
sudo dnf upgrade --refresh -y
```

## 代理配置

### 命令行代理（仅当前终端）

```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890
# 写进 ~/.bashrc / ~/.zshrc 持久化
```

### DNF 走代理

```bash
sudo tee /etc/dnf/dnf.conf <<'EOF'
[main]
gpgcheck=1
installonly_limit=3
clean_requirements_on_remove=True
fastestmirror=True
proxy=http://127.0.0.1:7890
EOF
```

### git 代理

```bash
git config --global http.proxy  http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
# 取消
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### Node / npm 走代理

```bash
npm config set proxy http://127.0.0.1:7890
npm config set https-proxy http://127.0.0.1:7890
# 取消
npm config delete proxy
npm config delete https-proxy
```

## 防火墙 firewalld

Fedora 默认开启 firewalld，Docker 起容器后会需要一些调整：

```bash
# 查看默认区域和状态
sudo firewall-cmd --list-all

# 允许 SSH（默认已开）
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload

# 容器常用：开启 IP 转发 + 允许 80/443（按需）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

> Docker 安装后会自己加 iptables 规则，但 firewalld 经常与之冲突；如果遇到容器无法联网，参考 [[Fedora-Docker安装与使用#防火墙冲突]]

## SELinux

默认 enforcing。日常开发不用改，但如果你装 nvidia 驱动 / 某些 Docker 高级用法被它挡了，可以临时排查：

```bash
# 查看是否被 SELinux 阻挡
sudo ausearch -m avc --start recent

# 临时宽容（不推荐生产长期开）
sudo setenforce 0
```

## 用户与 sudo

```bash
# 把自己加入 docker 组（等装 Docker 之后看 [[Fedora-Docker安装与使用#非 root 用户使用 docker]]）
# 把 zhaoxin 加到 wheel（其实装机时勾了 administrator 就已经是了）
sudo usermod -aG wheel zhaoxin

# 默认 wheel 免密（可选，**只用于个人开发机**）
sudo visudo
# 取消注释：%wheel  ALL=(ALL)       NOPASSWD: ALL
```

## hostname / 时区

```bash
sudo hostnamectl set-hostname fedora-dev
sudo timedatectl set-timezone Asia/Shanghai
```

## 后续步骤

- [[Fedora-终端美化与字体]] ← 先装字体，避免后面终端全是方块
- [[Fedora-Docker安装与使用]]
- [[Fedora-zsh与终端工具链]]
