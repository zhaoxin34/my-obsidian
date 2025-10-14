https://github.com/zbirenbaum/copilot.lua

## 安装配置
:LazyExtras 选择ai.copilot进行安装

配置放到plugins/copilot.lua

授权:Copilot auth

*注意这里可能要升级到22以后的nodejs*
```bash
nvm install 24
nvm use 24
nvm alias default 24
```

## **切换账户的方法**

删除掉以下的目录
```bash
rm -rf ~/.config/github-copilot
```
重启neovim，重新登录
`:Copilot auth`
