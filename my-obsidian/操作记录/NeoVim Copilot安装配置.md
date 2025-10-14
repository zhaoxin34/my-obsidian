https://github.com/zbirenbaum/copilot.lua

<<<<<<< HEAD
`:LazyExtras` 选择ai.copilot进行安装
=======
## 安装配置
:LazyExtras 选择ai.copilot进行安装
>>>>>>> 85d49b4165d0eed06fa63b112f56cf46a4939b10

配置放到plugins/copilot.lua

授权:Copilot auth

*注意这里可能要升级到22以后的nodejs*
```bash
nvm install 24
nvm use 24
nvm alias default 24
```

<<<<<<< HEAD
<<<<<<< HEAD
### 常见问题

`:LspInfo` 如果发现copilot-language-server没有运行, 可以尝试手动安装

```bash
npm i -g @github/copilot-language-server
```
=======
**切换账户的方法**
=======
## **切换账户的方法**
>>>>>>> 85d49b4165d0eed06fa63b112f56cf46a4939b10

删除掉以下的目录
```bash
rm -rf ~/.config/github-copilot
```
<<<<<<< HEAD

>>>>>>> cbdc4a004ed2564eceba0bd40712251761dd3541
=======
重启neovim，重新登录
`:Copilot auth`
>>>>>>> 85d49b4165d0eed06fa63b112f56cf46a4939b10
