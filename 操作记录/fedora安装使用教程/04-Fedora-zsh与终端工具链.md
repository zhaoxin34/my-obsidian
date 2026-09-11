# Fedora zsh 与终端工具链

> 目标：装 zsh + oh-my-zsh + starship（推荐）or p10k，配套 eza / btop / yazi / ripgrep / fzf / ast-grep / lazygit / zoxide。

## 1. zsh 与 oh-my-zsh

```bash
sudo dnf install -y zsh

# 把 zsh 设为默认
chsh -s $(which zsh)
# 重新登录生效

# oh-my-zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

## 2. 插件

```bash
# oh-my-zsh 自带 git 插件（在 ~/.zshrc 的 plugins=(...) 里启用）

# 第三方插件（推荐 clone 到 $ZSH_CUSTOM/plugins/）
git clone https://github.com/zsh-users/zsh-autosuggestions \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

git clone https://github.com/zsh-users/zsh-syntax-highlighting \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

git clone https://github.com/jeffreytse/zsh-vi-mode \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-vi-mode

git clone https://github.com/agkozak/zsh-z \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-z

# ~/.zshrc 的 plugins=(...) 改为：
# plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-vi-mode zsh-z sudo)
```

## 3. 主题：starship（推荐）or p10k

### starship（更轻、跨 shell、速度更快）

```bash
curl -sS https://starship.rs/install.sh | sh

# 在 ~/.zshrc 末尾添加
echo 'eval "$(starship init zsh)"' >> ~/.zshrc

# 主题配置
mkdir -p ~/.config && starship preset catppuccin-powerline -o ~/.config/starship.toml
# 或用 nerd font symbol preset
starship preset nerd-font-symbols -o ~/.config/starship.toml
```

### p10k（OH-MY-ZSH 经典）

参考 [[安装配置p10k]]（已有笔记），简要步骤：

```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/themes/powerlevel10k

# ~/.zshrc 改 ZSH_THEME="powerlevel10k/powerlevel10k"
exec zsh  # 重启 shell，进入配置向导
```

## 4. 命令工具链（强烈建议一次性装齐）

```bash
# 用 dnf + Fedora COPR 加速
sudo dnf install -y \
  eza \
  ripgrep \
  fd-find \
  bat \
  fzf \
  btop \
  htop \
  tmux \
  zellij \
  zoxide \
  jq \
  yq \
  lazygit \
  neofetch \
  fastfetch \
  tldr

# ast-grep（结构化搜索）
sudo dnf install -y ast-grep

# yazi（TUI 文件管理器）
sudo dnf install -y yazi ffmpeg 7zip

# atuin（历史记录增强 + 跨机器同步）
# Fedora 41+ 没有，直接装官方脚本
curl --proto '=https' --tlsv1.2 -sSf https://setup.atuin.sh | sh
echo 'eval "$(atuin init zsh)"' >> ~/.zshrc
atuin import zsh  # 导入现有历史
```

## 5. ~/.zshrc 关键配置

```bash
# ── oh-my-zsh ──
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"   # 或在 starship 方案下删除这一行

plugins=(
  git
  zsh-autosuggestions
  zsh-syntax-highlighting
  zsh-vi-mode
  zsh-z
  sudo
  copypath
  web-search
)

source $ZSH/oh-my-zsh.sh

# ── starship（如果用 starship 而不是 p10k） ──
# eval "$(starship init zsh)"

# ── zsh-vi-mode 优化 ──
export ZVM_CURSOR_STYLE_ENABLED=false

# ── 终端工具 ──
alias ls="eza --icons=always"
alias ll="eza --icons=always -l"
alias la="eza --icons=always -la"
alias cat="bat"
alias grep="rg"
alias cd="z"
alias lg="lazygit"
alias ld="lazydocker"
alias top="btop"

# ── atuin ──
eval "$(atuin init zsh)"

# ── 代理 ──
# export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890

# ── 命令横幅（自选） ──
function fedora-on-pre-prompt() {
  figlet "Fedora Dev"
  fedora-on-pre-prompt() {}
}
# 注：figlet 需要 sudo dnf install -y figlet
```

## 6. 让 fzf / zoxide 真正用起来

```bash
# fzf：默认已经装好，按 Ctrl+R 历史 / Ctrl+T 文件 / Alt+C 目录
# 配置快捷搜索
# 在 ~/.zshrc 加：
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_DEFAULT_OPTS="--height 60% --layout=reverse --preview 'bat --style=numbers --color=always --line-range=:500 {}'"

# zoxide：别名 cd=z，前面已加
```

## 7. 我的判断

- **starship 比 p10k 现代化**：跨 shell、启动快、配置用 toml 更易版本管理。p10k 在 zsh 下依然最强，但 starship 已够用。
- 不要把 oh-my-zsh 装得太臃肿，加 5-7 个插件即可，否则启动慢。
- 如果你只用 zsh，可以考虑直接**用 starship + 纯 zsh 配置**，跳过 oh-my-zsh。但 oh-my-zsh 的 `git` 插件太香，还是推荐留着。

## 后续

- [[05-Fedora-Neovim配置]]
- [[06-Fedora-Wezterm与Zellij]]
