https://github.com/zbirenbaum/copilot.lua

`:LazyExtras` 选择ai.copilot进行安装

配置放到plugins/copilot.lua

授权:Copilot auth

*注意这里可能要升级到22以后的nodejs*
```bash
nvm install 24
nvm use 24
nvm alias default 24
```

### 常见问题

`:LspInfo` 如果发现copilot-language-server没有运行, 可以尝试手动安装

```bash
npm i -g @github/copilot-language-server
```