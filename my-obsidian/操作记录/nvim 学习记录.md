### 一些必须初始化的命令

```bash
# markdown preview 需要用
npm install markdownlint-cli2 --global
# js 格式化需要用
npm install prettier --global 
```
### 快捷键帮助地址
https://www.lazyvim.org/keymaps

比较有意义的命令

| Key          | Description                | Mode         |
| ------------ | -------------------------- | ------------ |
| `<leader>ft` | Terminal (Root Dir)        | **n**        |
| `]]`         | Next Reference             | **n**        |
| `[[`         | Prev Reference             | **n**        |
| `<a-n>`      | Next Reference             | **n**        |
| `<a-p>`      | Prev Reference             | **n**        |
| `<leader>sr` | Search and Replace         | **n**, **v** |
| `<leader>,`  | Buffers                    | **n**        |
| `<leader>.`  | Toggle Scratch Buffer      | **n**        |
| `<leader>/`  | Grep (Root Dir)            | **n**        |
| `<leader>:`  | Command History            | **n**        |
| `<leader>fe` | Explorer Snacks (root dir) | **n**        |
| `<leader>fE` | Explorer Snacks (cwd)      | **n**        |
| `<leader>ff` | Find Files (Root Dir)      | **n**        |
| `<leader>n`  | Notification History       | **n**        |
| `<leader>sp` | Search for Plugin Spec     | **n**        |
| `gd`         | Goto Definition            | **n**        |
| `gr`         | References                 | **n**        |
| `gcc`        | 注释当前行                      | **n**        |
| `gbc`        | 注释代码块                      | **n**        |
| `<leader>ss` | Goto Symbol (Aerial)       | **n**        |
| `>>`         | 增加缩进                       | **n**        |
| `<<`         | 减少缩进                       | **n**        |
#### [markdown-preview.nvim](https://github.com/iamcco/markdown-preview.nvim.git)

Part of [lazyvim.plugins.extras.lang.markdown](https://www.lazyvim.org/extras/lang/markdown)
需要先安装npm命令行

| Key          | Description      | Mode  |
| ------------ | ---------------- | ----- |
| `<leader>cp` | Markdown Preview | **n** |
#### [venv-selector.nvim](https://github.com/linux-cultist/venv-selector.nvim.git)
Part of [lazyvim.plugins.extras.lang.python](https://www.lazyvim.org/extras/lang/python)

| Key          | Description       | Mode  |
| ------------ | ----------------- | ----- |
| `<leader>cv` | Select VirtualEnv | **n** |

### 一些命令

查看所有事件
:h events
产看当前文件是否支持格式化及其他lsp信息
:LspInfo
:ConformInfo
查看某个事件的命令，如下示例展示了文件保存后的回调
verbose autocmd BufWritePre

### [[Python Neovim环境创建]]

### [[NeoVim Copilot安装配置]]