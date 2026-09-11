# Fedora 终端美化与字体

> 三件事：装 Nerd Font（避免方块）→ 装主题图标（GNOME 美化）→ 装扩展（提效）。
> 这一步是后面的前置：wezterm / neovim / zellij 都会引用这些字体。

## 1. 字体

### MesloLG Nerd Font（zsh/p10k 经典组合）

```bash
# Fedora 包源
sudo dnf install -y meslo-lg-nerd-font

# 或者手动下载（最新版）
mkdir -p ~/.local/share/fonts
cd ~/.tmp
curl -L -o Meslo.zip \
  https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.zip
unzip Meslo.zip -d ~/.local/share/fonts/Meslo/
fc-cache -fv
```

### JetBrains Mono Nerd Font（neovim/code 推荐）

```bash
# 直接 dnf 装（Fedora 41+ 提供）
sudo dnf install -y jetbrains-mono-fonts nerdfont-jetbrains-mono-nerd-font

# 或手动
curl -L -o JB.zip \
  https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip
unzip JB.zip -d ~/.local/share/fonts/JetBrainsMono/
fc-cache -fv
```

### 中文字体（避免中文方块）

```bash
sudo dnf install -y \
  google-noto-sans-cjk-fonts \
  google-noto-sans-mono-cjk-fonts \
  google-noto-sans-cjk-vf-fonts
```

### 配置默认字体

**GNOME 终端**：

```bash
gsettings set org.gnome.desktop.interface monospace-font-name 'JetBrainsMono Nerd Font Mono 12'
gsettings set org.gnome.desktop.interface font-name 'Noto Sans CJK SC 11'
```

**wezterm / 其它终端**：见 [[Fedora-Wezterm与Zellij]]。

## 2. GNOME Tweaks 与扩展管理器

```bash
sudo dnf install -y gnome-tweaks gnome-extensions-app

# 启用扩展需要浏览器扩展 integration（FireFox 装对应插件，或者用 chrome）
# 直接命令装一些常用扩展
```

### 推荐扩展（从 extensions.gnome.org 装）

| 扩展 | 用途 |
| ---- | ---- |
| **User Themes** | 让 tweaks 可以选 shell 主题 |
| **Dash to Dock** / **Dash to Panel** | 把 dock 变成 mac 风格 / Windows 风格任务栏 |
| **Blur My Shell** | 顶栏 + overview 模糊，媲美 macOS |
| **Transparent Top Bar** | 顶栏透明 |
| **Tiling Assistant** | macOS 风格分屏 |
| **AppIndicator** | 支持托盘图标（部分 Electron 应用需要） |
| **Burn My Windows** | 窗口打开/关闭动画 |
| **Desktop Cube** | 工作区切换 3D 效果 |
| **Gesture Improvements** | Mac 触控板体验 |

安装方法：

```bash
# 1. 浏览器打开 https://extensions.gnome.org
# 2. 安装 GNOME 浏览器 integration
# 3. 浏览器上点 ON/OFF 切换即可

# 命令行方式（不推荐，扩展依赖多）：
# sudo dnf install -y gnome-shell-extension-*
```

## 3. 主题与图标

### 主题（WhiteSur — macOS Big Sur 风格）

```bash
sudo dnf install -y gtk-murrine-engine

git clone https://github.com/vinceliuice/WhiteSur-gtk-theme.git ~/tmp/.delete/WhiteSur-gtk-theme
cd ~/tmp/.delete/WhiteSur-gtk-theme
./install.sh -l                 # light
./install.sh -d                 # dark
./install.sh -t all -N血色       # 安装所有主题变体（举例）

cd ~ && mv ~/tmp/.delete/WhiteSur-gtk-theme /tmp/claude/.delete-WhiteSur
```

### 主题（Catppuccin — 优雅紫色调）

```bash
git clone https://github.com/catppuccin/gtk.git ~/tmp/.delete/cat-gtk
cd ~/tmp/.delete/cat-gtk
./build.sh
./install.sh

mv ~/tmp/.delete/cat-gtk /tmp/claude/.delete-cat-gtk
```

### 图标（Papirus）

```bash
sudo dnf install -y papirus-icon-theme

# 补充：papirus 主题在 GitHub 有更多变体
# https://github.com/PapirusDevelopmentTeam/papirus-icon-theme
```

### 光标（McMojave / Bibata）

```bash
sudo dnf install -y bibata-cursor-theme
```

### 应用主题

```bash
gsettings set org.gnome.desktop.interface gtk-theme 'WhiteSur-Dark'
gsettings set org.gnome.desktop.interface icon-theme 'Papirus-Dark'
gsettings set org.gnome.desktop.interface cursor-theme 'Bibata-Modern-Ice'
gsettings set org.gnome.shell.extensions.user-theme name 'WhiteSur-Dark'
```

## 4. 终端配色

推荐直接配在 wezterm 里（见 [[Fedora-Wezterm与Zellij]]），GNOME 自带终端配色：

```bash
# 装 Solarized
sudo dnf install -y gnome-terminal-colors-solarized

# 或直接用 Gogh（curl 一行切换）：
bash -c "$(curl -sLo- https://git.io/vQgMr)"
```

## 5. 壁纸

```bash
# 系统自带几张；想自定义：
mkdir -p ~/Pictures/Wallpapers
# 拖图进去后：
gsettings set org.gnome.desktop.background picture-uri file:///home/$zhaoxinUSER/Pictures/Wallpapers/your.jpg
gsettings set org.gnome.desktop.background picture-uri-dark file:///home/$zhaoxinUSER/Pictures/Wallpapers/your-dark.jpg
gsettings set org.gnome.desktop.background picture-options 'zoom'
```

推荐 macOS 风壁纸源：

- <https://github.com/macOS-wallpapers>
- Wallhaven: <https://wallhaven.cc>

## 6. Wayland 屏幕共享（远程桌面需要）

Fedora 默认 Wayland，需要为屏幕共享开权限：

```bash
# 确认是 Wayland
echo $XDG_SESSION_TYPE  # 期望: wayland

# 安装 xdg-desktop-portal（远程工具依赖）
sudo dnf install -y xdg-desktop-portal xdg-desktop-portal-gtk
```

## 我的判断

- **白苏（WhiteSur）+ Papirus-Dark + Bibata** 是当下 Fedora 最接近 macOS 的组合。
- **Catppuccin** 适合程序员审美，颜色对比舒服，搭配 neovim/wezterm 同主题非常统一。
- 不要装太多扩展，GNOME 41+ 后台常驻会吃内存（每个扩展一个进程）。

## 后续

- [[Fedora-zsh与终端工具链]]
- [[Fedora-Wezterm与Zellij]]
- [[Fedora-Neovim配置]]
