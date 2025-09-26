使用pyenv管理python版本
```bash
# 安装pyenv
brew install pyenv

# 安装到zsh
echo 'if which pyenv > /dev/null; then eval "$(pyenv init --path)"; eval "$(pyenv init -)"; fi' >> ~/.zshrc
source ~/.zshrc
```

pyenv install --list 可以查看python可用的版本

2025-9-26目前安装3.12和3.13两个版本

```bash
pyenv install 3.12.11

```