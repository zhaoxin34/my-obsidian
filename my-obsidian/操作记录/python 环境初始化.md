使用pyenv管理python版本
```bash
# 安装pyenv
brew install pyenv

# 安装到zsh
echo 'if which pyenv > /dev/null; then eval "$(pyenv init --path)"; eval "$(pyenv init -)"; fi' >> ~/.zshrc
source ~/.zshrc
```