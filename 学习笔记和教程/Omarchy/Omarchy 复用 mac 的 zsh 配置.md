# Omarchy 复用 mac 的 zsh 配置

> 跨设备共享 zsh 配置的完整流程。前提：mac 端 `~/.config` 本身是 git 仓库（remote `git@github.com:zhaoxin34/config.git`），里面 `zsh/` 是完整的 zsh 配置；omarchy 在 `/Volumes/data/working/ai/config` 已 clone 同一份仓库。共享后两台机器的 alias、函数、prompt、插件保持一致。

## 0. 前置确认

```bash
# mac 端
ls ~/.config/zsh            # mac 上的 zsh 配置（worktree）
git -C ~/.config remote -v  # 应该是 git@github.com:zhaoxin34/config.git

# omarchy 端
ls /Volumes/data/working/ai/config/zsh   # omarchy 的 clone（和 mac 共用同一 git remote）
git -C /Volumes/data/working/ai/config status
```

两边 `zsh/zshrc.d/` 文件应一致（hashfile 数量、文件名都应一样）。如果不一致，先 `cd ~/.config && git pull` 同步。

## 1. omarchy 上创建 3 个 symlink

mac 的 zshrc 引用路径规律：

- `~/.zshrc` → `$XDG_CONFIG_HOME/zsh/zshrc`（实际是个独立文件）
- `~/.zprofile` → `$XDG_CONFIG_HOME/zsh/zprofile`
- zshrc 里 source：`$XDG_CONFIG_HOME/zsh/zshrc.d/[0-9]*.zsh`

所以 omarchy 必须让 `~/.zshrc` / `~/.zprofile` / `~/.config/zsh` 都指向 clone 里的内容。

```bash
# 备份默认 zshrc（pacman newuser 创建的 32 字节占位）
[ -e ~/.zshrc ] && [ ! -L ~/.zshrc ] && mv ~/.zshrc ~/.zshrc.bak.default

# 建 3 个 symlink（路径用 git clone 位置，不用改 clone 本身）
ln -sf /Volumes/data/working/ai/config/zsh/zshrc ~/.zshrc
ln -sf /Volumes/data/working/ai/config/zsh/zprofile ~/.zprofile
ln -sf /Volumes/data/working/ai/config/zsh ~/.config/zsh

# 验证
ls -la ~/.zshrc ~/.zprofile ~/.config/zsh
# 期望：3 个都是 symlink，指向 /Volumes/data/working/ai/config/zsh/...
```

## 2. 安装 p10k（AUR）

mac 用 homebrew 装的 p10k 在 `/opt/homebrew/share/powerlevel10k/`。Linux 路径在 `~/.local/share/powerlevel10k/`（mac 的 zshrc 第 2 个 fallback）。AUR 有现成包。

```bash
# 设 mac 代理（omarchy 在 GFW 后）
export http_proxy=http://192.168.31.67:7890 \
       https_proxy=http://192.168.31.67:7890 \
       all_proxy=socks5://192.168.31.67:7890 \
       no_proxy=127.0.0.1,localhost,192.168.31.0/24

yes | yay -S --noconfirm --answeredit None --answerdiff None --removemake zsh-theme-powerlevel10k
```

AUR 包实际装到 `/usr/share/zsh-theme-powerlevel10k/`（不是 zshrc 期望的 `~/.local/share/...`），所以需要 symlink：

```bash
mkdir -p ~/.local/share
ln -sfn /usr/share/zsh-theme-powerlevel10k ~/.local/share/powerlevel10k

# 把 mac 上 `~/.p10k.zsh` 拷过来（个人 prompt 配置，不在 git 仓里）
scp mac:~/.p10k.zsh omc:.p10k.zsh
```

> ⚠️ yay 装完可能因 `/var/lib/pacman/db.lck` 卡住（pacman 锁残留），清掉再试：`sudo rm -f /var/lib/pacman/db.lck`

## 3. 改共享 zsh 配置：加 Linux fallback

`zsh/zshrc.d/01-path.zsh` 和 `zsh/zshrc.d/90-zinit.zsh` 有 mac-only 路径，需加 Linux fallback。**改 mac 这边，commit + push，omarchy `git pull` 同步**。

### 3.1 `zsh/zshrc.d/01-path.zsh` 第 78-88 行：brew nvm 加 mac gate

```diff
-# nvm - 延迟加载
+# nvm - 延迟加载（仅 mac homebrew；Linux 用 distro 包管理器装 node）
 export NVM_DIR="$HOME/.nvm"
-if [[ -s "$(brew --prefix nvm)/nvm.sh" ]]; then
+if [[ "$(uname)" == "Darwin" ]] && [[ -s "$(brew --prefix nvm)/nvm.sh" ]]; then
     nvm() {
         unfunction nvm
         source "$(brew --prefix nvm)/nvm.sh"
         nvm "$@"
     }
 fi
```

不 gate 的话，Linux 上启动 zsh 会报 `command not found: brew`。

### 3.2 `zsh/zshrc.d/90-zinit.zsh` 末尾：fzf key-bindings 加 Linux 路径

```diff
-# fzf - 非交互式不加载
-if [[ -o interactive ]] && [[ -f /opt/homebrew/opt/fzf/shell/key-bindings.zsh ]]; then
-    source /opt/homebrew/opt/fzf/shell/key-bindings.zsh
+# fzf - 非交互式不加载（mac homebrew 或 Linux /usr/share 都尝试）
+if [[ -o interactive ]]; then
+    if [[ -f /opt/homebrew/opt/fzf/shell/key-bindings.zsh ]]; then
+        source /opt/homebrew/opt/fzf/shell/key-bindings.zsh
+    elif [[ -f /usr/share/fzf/key-bindings.zsh ]]; then
+        source /usr/share/fzf/key-bindings.zsh
+    fi
 fi
```

不加 Linux 路径，Ctrl-R 历史搜索、Ctrl-T 文件查找都不生效。

## 4. 验证

```bash
# exec 一个全新的 zsh 看 prompt
zsh -ic 'alias | | wc -l' 2>/dev/null
# 期望：~34（不是 0）

zsh -ic 'echo "PROMPT_LEN=${#PROMPT}"' 2>/dev/null
# 期望：远大于 5（5 是默认 omarchy prompt "%m%# " 的长度）

# 直接看 prompt（视觉判断）
exec zsh
# 期望看到 ╭─ /cwd main ··· ✔ user@host HH:MM:SS ─╮ 的 p10k 风格

# 验证 fzf key-bindings 加载
zsh -xic 'source ~/.zshrc' 2>&1 | grep key-bindings.zsh
# 期望：能看到 /usr/share/fzf/key-bindings.zsh 的 source 行
```

## 5. mac 端 commit + push（让 omarchy 可以 pull）

```bash
cd ~/.config
git add zsh/zshrc.d/01-path.zsh zsh/zshrc.d/90-zinit.zsh
git commit -m "fix(zsh): brew --prefix nvm 加 mac gate，Linux 不再报错"
git commit -m "feat(zsh): fzf key-bindings 加 Linux /usr/share fallback"
git push origin main
```

omarchy 同步：

```bash
cd /Volumes/data/working/ai/config && git pull
```

## 6. 已知 mac 残留（不影响日常用）

| 项 | 文件 | 表现 |
|---|---|---|
| `pbcopy` 别名 | `10-alias.zsh` (`cpath`, `cpc`) | omarchy 上调用 `cpath` 会报 command not found |
| 几个 mac 路径函数 | `10-functions.zsh` (`toremote`, `datatist`, `mql5`) | 函数存在但路径无效，调用报错 |
| `proxy()` 函数 | `10-functions.zsh` 末尾 | 自动 export `127.0.0.1:7890` 代理。omarchy 上正好指向本地 mihomo（system service 装的），反而是个 bonus |

## 7. mac 上 `~/.zshrc` / `~/.zprofile` 是如何挂到仓里的

mac 仓根目录是 `~/.config/`（worktree）。mac 的 symlink：

- `~/.zshrc` → `~/.config/zsh/zshrc`
- `~/.zprofile` → `~/.config/zsh/zprofile`

重新装 mac 时用：

```bash
cd ~/.config/zsh && bash symlink.sh
```

会创建这两个 symlink。

## 8. 故障排查

### 故障 A：zsh 启动报错 `command not found: brew`

→ §3.1 没改（或改后没同步到 omarchy）。

### 故障 B：prompt 还是默认 `%m%#`，没看到 p10k 边框

→ §2 的 symlink 没建好，或 p10k 没装。

- `ls -la ~/.local/share/powerlevel10k` 应该是 symlink → `/usr/share/zsh-theme-powerlevel10k`
- `ls ~/.p10k.zsh` 应该在（从 mac scp 来的）
- `ls /usr/share/zsh-theme-powerlevel10k/powerlevel10k.zsh-theme` 应该在

### 故障 C：alias 数 = 0

大概率是你跑 `unalias -a` 后 `source ~/.zshrc` 没等 zinit 装完就 `alias` 了。等 5-10 秒，或者直接 `zsh -ic 'alias | wc -l' 2>/dev/null` 让 zsh 完整启动后再统计。

### 故障 D：Ctrl-R / Ctrl-T / Alt-C 都没反应

→ §3.2 没改，fzf key-bindings 没加载。

### 故障 E：omarchy 重启后 zsh 报"找不到文件"

`/Volumes/data/working/ai/config` 路径不在了？检查 mount 状态。**注意**这路径在 omarchy 上是**本地磁盘**（不是 mac 共享卷）——用户已确认。重启不影响。
