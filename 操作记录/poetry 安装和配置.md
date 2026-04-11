## poetry 初始化

初始化python环境，安装pip，参考 [[python 环境初始化]]

```bash
pip install poetry
```

整合zsh补全，整合oh my zsh

```bash
mkdir $ZSH_CUSTOM/plugins/poetry
poetry completions zsh > $ZSH_CUSTOM/plugins/poetry/_poetry
```

最后在.zshrc中的plugins=加入poetry

## poetry 重要方法 https://python-poetry.org/docs/cli/

### add 添加依赖

```bash
poetry add requests pendulum
# Allow >=2.0.5, <3.0.0 versions
poetry add pendulum@^2.0.5
# Allow >=2.0.5, <2.1.0 versions
poetry add pendulum@~2.0.5
# Allow >=2.0.5 versions, without upper bound
poetry add "pendulum>=2.0.5"
# Allow only 2.0.5 version
poetry add pendulum==2.0.5
poetry add pendulum@latest
```

### add 添加工程依赖

```bash
poetry add --editable ./my-package/
poetry add --editable git+ssh://github.com/sdispater/pendulum.git#develop
```

### install 安装命令

```bash
# If you want to exclude one or more dependency groups for the installation, you can use the `--without` option.
poetry install --without test,docs
```

### env 可以用于创建和activate环境

我暂时用 venv管理环境
### config 配置管理

```bash
# 列举配置
poetry config --list
```
### publish 工程发布