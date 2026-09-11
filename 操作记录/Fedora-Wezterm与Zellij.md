# Fedora WezTerm 与 Zellij

> wezterm 是 GPU 加速的终端模拟器（Rust 写），zellij 是终端复用器（替代 tmux）。
> 你在 macOS 上已经用过 wezterm + zellij，这里把 Linux 这边的安装 + 同步配置补齐。

## 1. wezterm 安装

```bash
# Fedora 41+ 仓库可能没有，直接 AppImage
curl -LO https://github.com/wez/wezterm/releases/download/20240203-110809-5046fc22/wezterm-20240203-110809-5046fc22-Ubuntu22.04.AppImage
chmod +x wezterm-*.AppImage
sudo mv wezterm-*.AppImage /usr/local/bin/wezterm
# 桌面集成图标
sudo mkdir -p /usr/local/share/icons/hicolor/128x128/apps
sudo cp ~/path/to/wezterm.png /usr/local/share/icons/hicolor/128x128/apps/ 2>/dev/null || true
# .desktop
sudo tee /usr/local/share/applications/wezterm.desktop <<'EOF'
[Desktop Entry]
Name=WezTerm
Comment=Wez's Terminal Emulator
Exec=/usr/local/bin/wezterm
Icon=wezterm
Type=Application
Categories=System;TerminalEmulator;
EOF
```

或者 Fedora COPR：

```bash
sudo dnf copr enable alternateved/wezterm -y
sudo dnf install -y wezterm
```

## 2. wezterm 配置

`~/.config/wezterm/wezterm.lua`：

```lua
local wezterm = require "wezterm"
local config = wezterm.config_builder()

-- 字体（与 [[Fedora-终端美化与字体]] 保持一致）
config.font = wezterm.font("JetBrainsMono Nerd Font")
config.font_size = 13.0

-- 配色（Catppuccin Mocha）
config.color_scheme = "Catppuccin Mocha"

-- 窗口透明 + 圆角
config.window_background_opacity = 0.92
config.window_decoration = "RESIZE"
config.window_padding = { left = 8, right = 8, top = 8, bottom = 8 }

-- 启动即进入 zellij
config.default_prog = { "/usr/bin/zellij", "--layout", "default", "attach", "default" }

-- 主题：tab 栏背景
config.use_fancy_tab_bar = false
config.tab_bar_at_bottom = true

-- 鼠标滚轮
config.mouse_bindings = {
  {
    event = { Down = { streak = 1, button = "WheelUp" } },
    mods = "CTRL",
    action = wezterm.action.ScrollByPage,
  },
}

-- key bindings
config.keys = {
  { key = "t", mods = "CTRL|SHIFT", action = wezterm.action.SpawnTab("DefaultDomain") },
  { key = "w", mods = "CTRL|SHIFT", action = wezterm.action.CloseCurrentTab { confirm = false } },
  { key = "LeftArrow", mods = "CTRL|SHIFT", action = wezterm.action.ActivateTabRelative(-1) },
  { key = "RightArrow", mods = "CTRL|SHIFT", action = wezterm.action.ActivateTabRelative(1) },
}

return config
```

### 与 Mac 同步

把 `~/.config/wezterm` 链到 dotfiles：

```bash
ln -s ~/code/dotfiles/wezterm ~/.config/wezterm
```

## 3. zellij 安装

```bash
# Fedora 仓库
sudo dnf install -y zellij
zellij --version

# 或者新版
curl -L https://github.com/zellij-org/zellij/releases/latest/download/zellij-x86_64-unknown-linux-musl.tar.gz \
  | sudo tar -xz -C /usr/local/bin
```

## 4. zellij 配置

`~/.config/zellij/config.yaml`：

```yaml
keybinds:
  normal:
    - action: [SwitchToMode, Pane]
      key: [Ctrl, P]
    - action: [SwitchToMode, Tab]
      key: [Ctrl, T]
    - action: [SwitchToMode, Resize]
      key: [Ctrl, R]
    - action: [SwitchToMode, Scroll]
      key: [Ctrl, S]
    - action: [NewPane, Down]
      key: Alt, h
    - action: [NewPane, Right]
      key: Alt, v
    - action: [FocusNextPane]
      key: Alt, l
    - action: [FocusPreviousPane]
      key: Alt, k
    - action: [MoveFocus, Down]
      key: Tab
    - action: [Quit]
      key: Ctrl, q
    - action: [Detach]
      key: Ctrl, d
  pane:
    - action: [SwitchToMode, Normal]
      key: Esc
  resize:
    - action: [SwitchToMode, Normal]
      key: Esc
  scroll:
    - action: [SwitchToMode, Normal]
      key: Esc

themes:
  default:
    fg: [231, 233, 237]
    bg: [30, 30, 46]
    black: [24, 24, 37]
    red: [231, 130, 132]
    green: [166, 209, 137]
    yellow: [229, 200, 144]
    blue: [180, 209, 247]
    magenta: [198, 160, 217]
    cyan: [148, 226, 213]
    white: [219, 224, 232]
    orange: [254, 169, 159]
```

`~/.config/zellij/layouts/default.kdl`：

```
layout {
  pane split_direction="vertical" {
    pane
    pane size="30%"
  }
}
```

## 5. 启动即进入 zellij

最简单：在 `~/.zshrc` 加：

```bash
# 如果 zellij 不在，wezterm 会自动起；这里保险起见用 attach
if [[ -z "$ZELLIJ" && -z "$TMUX" ]]; then
  zellij --layout default attach default || zellij --layout default
fi
```

## 6. 与 Mac 的差异

| 项 | macOS | Fedora |
| --- | --- | --- |
| wezterm 安装 | brew | AppImage / COPR |
| 字体路径 | ~/Library/Fonts | ~/.local/share/fonts |
| 默认 shell | zsh | zsh（已切换） |
| 配置文件 | 同 | 同 |

可以完全复用，关键是 wezterm 用绝对路径，zellij config 用 yaml 无差别。

## 后续

- [[Fedora-远程控制方案]]（通过 wezterm + ssh 用同一套键位远程控制 Fedora）
