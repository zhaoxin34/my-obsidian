# Fedora 开发环境与常用软件

> 按你常用栈：Python、Node、Java、Chrome、git、SQL 客户端、输入法。

## 0. 代理持久化（推荐 ~/.zshrc）

```bash
# 写 ~/.zshrc
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
export all_proxy=socks5://127.0.0.1:7890
# 国内用阿里云 dnf 仓库可解除 docker proxy
```

## 1. Python

### 系统自带 + uv

```bash
sudo dnf install -y python3 python3-pip python3-devel

# uv（强烈推荐，比 pip 快 10x）
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
exec zsh

# 新项目
uv init myproj && cd myproj
uv add fastapi uvicorn
uv run python main.py
```

### pyenv（可选，多版本）

```bash
sudo dnf install -y gcc make zlib-devel bzip2 bzip2-libs xz-libs \
  sqlite sqlite-libs readline-devel openssl-devel tk-devel libffi-devel
curl https://pyenv.run | bash

# ~/.zshrc
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pyenv install 3.12
pyenv global 3.12
```

## 2. Node.js

见 [[07-Fedora-pi-agent安装与配置#1. 前置：Node.js]]，推荐 **fnm** 管理多版本。

```bash
# 验证
node -v
npm -v
```

## 3. Java

```bash
# OpenJDK 21（默认 LTS）
sudo dnf install -y java-21-openjdk java-21-openjdk-devel

# jenv 多版本（参考已有笔记 [[安装Jenv管理jdk环境]]）
sudo dnf install -y jenv
echo 'export PATH="$HOME/.jenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(jenv init -)"' >> ~/.zshrc
exec zsh

jenv add /usr/lib/jvm/java-21-openjdk
jenv versions
jenv global 21
```

构建工具：

```bash
sudo dnf install -y maven gradle
```

## 4. Chrome

```bash
# 添加 Google 源
sudo dnf config-manager --add-repo \
  https://dl.google.com/linux/chrome/rpm/stable/x86_64/google-chrome.repo
sudo dnf install -y google-chrome-stable

# 启动一个支持远程调试的实例（给 pi / Chrome Devtools MCP 用）
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-fedora
```

## 5. git 配置

```bash
git config --global user.name "Zhao Xin"
git config --global user.email "your@email.com"
git config --global init.defaultBranch main
git config --global http.postBuffer 524288000

# 用代理（如果需要）
# git config --global http.proxy  http://127.0.0.1:7890
# git config --global https.proxy http://127.0.0.1:7890

# 默认编辑器
git config --global core.editor nvim

# 漂亮 log
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative"

# diff 工具
git config --global diff.tool nvimdiff
```

## 6. SQL 客户端

```bash
# 命令行
sudo dnf install -y postgresql mysql
# mysql-client 已在大多数 dnf 仓库有
sudo dnf install -y mysql-community-client   # 或 mariadb

# GUI：dbeaver（推荐，跨平台）
sudo dnf install -y dbeaver
# 或者 AppImage
curl -L -o /tmp/dbeaver.appimage \
  https://dbeaver.io/files/dbeaver-ce-latest-linux.gtk.x86_64-nojdk.tar.gz
```

## 7. 输入法（中文）

Fedora 自带 ibus，但默认未装中文。Wayland 下推荐 **Fcitx5**：

```bash
sudo dnf install -y fcitx5 fcitx5-chinese-addons fcitx5-gtk fcitx5-qt fcitx5-configtool

# 环境变量（Wayland）
echo 'export GTK_IM_MODULE=fcitx' >> ~/.zshrc
echo 'export QT_IM_MODULE=fcitx' >> ~/.zshrc
echo 'export XMODIFIERS=@im=fcitx' >> ~/.zshrc
echo 'export INPUT_METHOD=fcitx' >> ~/.zshrc
echo 'export SDL_IM_MODULE=fcitx' >> ~/.zshrc

# 启动
fcitx5 &
# 配置工具
fcitx5-configtool
```

> Wayland 下还要确保 portal 选了 fcitx：
> `sudo dnf install -y xdg-desktop-portal-gtk`

## 8. 其他常用

```bash
# 截图（Flameshot）
sudo dnf install -y flameshot
# 绑定到 Print 键：设置 → 键盘 → 自定义快捷键 → `flameshot gui`

# 视频播放
sudo dnf install -y vlc

# 解压全套
sudo dnf install -y unzip p7zip p7zip-plugins unrar

# PDF
sudo dnf install -y okular

# ImageMagick
sudo dnf install -y ImageMagick

# 远程拷贝
sudo dnf install -y rsync
```

## 9. dotfiles 同步（强烈推荐）

把配置文件集中到 `~/code/dotfiles`，与 Mac 共享：

```bash
mkdir -p ~/code/dotfiles
cd ~/code/dotfiles
git init

# 拷配置（**用 cp 而不是 mv，保留原文件兜底**）
cp -r ~/.config/nvim ./nvim
cp -r ~/.config/wezterm ./wezterm
cp -r ~/.config/zellij ./zellij
cp -r ~/.config/starship.toml . 2>/dev/null
cp -r ~/.oh-my-zsh/custom ./oh-my-zsh-custom   # 自定义主题和插件
cp ~/.zshrc ./.zshrc
cp ~/.gitconfig ./.gitconfig
cp -r ~/.pi/agent ./pi

# 创建 install 脚本（按需软链）
cat > install.sh <<'EOF'
#!/usr/bin/env bash
set -e
[ -d ~/.config ] || mkdir -p ~/.config
ln -sfn $(pwd)/nvim ~/.config/nvim
ln -sfn $(pwd)/wezterm ~/.config/wezterm
ln -sfn $(pwd)/zellij ~/.config/zellij
[ -f $(pwd)/starship.toml ] && ln -sfn $(pwd)/starship.toml ~/.config/starship.toml
[ -f $(pwd)/.zshrc ] && ln -sfn $(pwd)/.zshrc ~/.zshrc
echo "Dotfiles installed."
EOF
chmod +x install.sh

git add -A && git commit -m "init dotfiles"
```

Mac / Fedora 切换时 `bash install.sh` 即可同步。

## 后续

- 回到 [[00-Fedora上手教程]] 检查清单
