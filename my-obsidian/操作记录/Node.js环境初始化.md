使用nvm管理node.js版本
brew install nvm
在zshrc中加入下面两行
export NVM_DIR="$HOME/.nvm"
[ -s "$(brew --prefix nvm)/nvm.sh" ] && \. "$(brew --prefix nvm)/nvm.sh"
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"  # This loads nvm bash_completion

安装 node 20版本，并设置成默认的
```bash
nvm install 20
nvm use 20
nvm alias default 20   # 设置默认版本
```
验证版本
```bash
node -v   # v20.x.x
npm -v    # >= 8.x
```