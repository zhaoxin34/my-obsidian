# Fedora Neovim 配置

> 装 neovim（建议 0.10+），用 lazy.nvim 管理插件，基础配置覆盖 LSP / treesitter / telescope。
> 字体请先装 [[03-Fedora-终端美化与字体#JetBrains Mono Nerd Font]]。

## 1. 安装 neovim

Fedora 41+ 仓库版本通常 ≥ 0.10：

```bash
sudo dnf install -y neovim python3-neovim
nvim --version | head -1
```

如果版本老（比如某些 LTS），用 AppImage：

```bash
curl -LO https://github.com/neovim/neovim/releases/download/stable/nvim.appimage
chmod +x nvim.appimage
sudo mv nvim.appimage /usr/local/bin/nvim
# AppImage 需要 fuse，装一下：
sudo dnf install -y fuse fuse3
```

或者源码编译：

```bash
sudo dnf install -y cmake gcc gcc-c++ make \
  ninja-build lua-devel luajit-devel \
  libtermkey-devel libvterm-devel

git clone https://github.com/neovim/neovim.git ~/tmp/.delete/nvim
make CMAKE_BUILD_TYPE=Release
sudo make install

mv ~/tmp/.delete/nvim /tmp/claude/.delete-nvim
```

## 2. 创建配置目录

```bash
mkdir -p ~/.config/nvim
# 备份如果你有旧配置
[ -f ~/.config/nvim/init.lua ] && mv ~/.config/nvim/init.lua{,.bak}
```

## 3. lazy.nvim

```lua
-- ~/.config/nvim/init.lua
-- bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)
```

## 4. 最小可用配置

```lua
-- ~/.config/nvim/lua/config/options.lua
vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.cursorline = true
vim.opt.signcolumn = "yes"
vim.opt.updatetime = 250
vim.opt.termguicolors = true
vim.opt.mouse = "a"

-- 不要备份文件（可选）
vim.opt.backup = false
vim.opt.swapfile = false
vim.opt.undofile = true
```

```lua
-- ~/.config/nvim/lua/config/keymaps.lua
local map = vim.keymap.set
map("n", "<leader>e", "<cmd>NvimTreeToggle<cr>", { desc = "文件树" })

map("n", "<leader>ff", "<cmd>Telescope find_files<cr>", { desc = "查找文件" })
map("n", "<leader>fg", "<cmd>Telescope live_grep<cr>", { desc = "全文搜索" })
map("n", "<leader>fb", "<cmd>Telescope buffers<cr>", { desc = "buffer" })

map("n", "<leader>lg", "<cmd>LazyGit<cr>", { desc = "lazygit" })

-- 保存自动格式化
map("n", "<leader>w", "<cmd>write<cr>", { desc = "保存" })
```

```lua
-- ~/.config/nvim/lua/config/lazy.lua
return {
  "folke/lazy.nvim",
  event = "VeryLazy",
  opts = {
    change_detection = { enabled = false },
  },
  spec = {
    -- colorscheme
    { "catppuccin/nvim", name = "catppuccin", priority = 1000 },

    -- 文件树
    { "nvim-tree/nvim-tree.lua", dependencies = "nvim-tree/nvim-web-devicons" },

    -- telescope
    { "nvim-telescope/telescope.nvim", dependencies = { "nvim-lua/plenary.nvim" } },

    -- treesitter
    { "nvim-treesitter/nvim-treesitter", build = ":TSUpdate" },

    -- LSP
    { "neovim/nvim-lspconfig", dependencies = { "hrsh7th/cmp-nvim-lsp", "hrsh7th/nvim-cmp", "L3MON4D3/LuaSnip", "saadparwaiz1/cmp_luasnip", "hrsh7th/cmp-buffer", "hrsh7th/cmp-path", "hrsh7th/cmp-cmdline" } },

    -- 通用 UI
    { "lukas-reineke/indent-blankline.nvim" },
    { "lewis6991/gitsigns.nvim" },
    { "kevinhwang91/nvim-bqf" },

    -- lazygit
    { "kdheepak/lazygit.nvim" },
  },
  config = function(_, opts)
    require("lazy").setup(opts.spec)
    require("catppuccin").setup({ flavour = "mocha" })
    vim.cmd.colorscheme("catppuccin-mocha")
  end,
}
```

```lua
-- ~/.config/nvim/init.lua 末尾
require("config.options")
require("config.keymaps")
require("config.lazy")
```

## 5. LSP：Python / TS / Java / Rust

```bash
# Python
sudo dnf install -y python3-pip
pip install --user pyright

# Node（给 typescript LSP 用）
sudo dnf install -y nodejs npm
npm install -g typescript typescript-language-server

# Java
sudo dnf install -y java-21-openjdk-devel
# jdtls 由 eclipse.jdt.ls 提供，建议按 nvim-lspconfig 的 jdtls 指引装

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup component add rust-analyzer
```

`~/.config/nvim/lua/config/lsp.lua`：

```lua
local lspconfig = require("lspconfig")
local on_attach = function(_, bufnr)
  local map = vim.keymap.set
  map("n", "gd", vim.lsp.buf.definition, { buffer = bufnr })
  map("n", "gr", vim.lsp.buf.references, { buffer = bufnr })
  map("n", "K", vim.lsp.buf.hover, { buffer = bufnr })
  map("n", "<leader>rn", vim.lsp.buf.rename, { buffer = bufnr })
  map("n", "<leader>ca", vim.lsp.buf.code_action, { buffer = bufnr })
end

lspconfig.pyright.setup({ on_attach = on_attach })
lspconfig.ts_ls.setup({ on_attach = on_attach })
lspconfig.jdtls.setup({ on_attach = on_attach, cmd = { "jdtls" } })
lspconfig.rust_analyzer.setup({ on_attach = on_attach })
```

## 6. 进入 nvim 后跑

```vim
:Lazy install
:TSInstall all
:MasonInstall pyright typescript-language-server jdtls
:checkhealth
```

## 7. mermaid 可视化

```bash
sudo dnf install -y npm
sudo npm install -g @mermaid-js/mermaid-cli

# neovim 装 image 插件（lazy 加："3chan/image.nvim"）
```

## 8. 与 Mac 同步

把 `~/.config/nvim` 软链到 dotfiles 仓库，Mac 和 Fedora 同款配置：

```bash
# dotfiles 仓库假设 ~/code/dotfiles
ln -s ~/code/dotfiles/nvim ~/.config/nvim
```

## 常见问题

- **Chinese 字符显示乱码**：终端字体没装 Nerd Font，见 [[03-Fedora-终端美化与字体]]
- **LSP 不启动**：`:LspInfo` 看 server 是否 attach；缺 server 看 `:Mason`
- **Treesitter 解析失败**：`:TSUpdate` 重新编译

## 后续

- [[06-Fedora-Wezterm与Zellij]]（在终端里跑 neovim 体验更稳）
- [[07-Fedora-pi-agent安装与配置]]（让 pi 帮你改 nvim 配置）
