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
# 查看安装的版本
pyenv versions

pyenv install 3.13.7
# 查看安装的版本
pyenv versions

```

目前先将全局版本设置为3.12.11
pyenv global 3.12.11

如果想设置某个本地目录的python版本，可以使用
pyenv local 3.13.7

### 自动切换venv的zsh插件
https://github.com/MichaelAquilina/zsh-autoswitch-virtualenv

git clone "https://github.com/MichaelAquilina/zsh-autoswitch-virtualenv.git" "$ZSH_CUSTOM/plugins/autoswitch_virtualenv"

zshrc增加
plugins=(autoswitch_virtualenv $plugins)

### [[poetry 安装和配置]]