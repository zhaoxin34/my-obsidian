
## [工作原理](https://github.com/openatx/uiautomator2/blob/master/README_CN.md)
本框架主要包含两个部分:

1. 手机端: 运行一个基于UiAutomator的HTTP服务，提供Android自动化的各种接口
2. Python客户端: 通过HTTP协议与手机端通信，调用UiAutomator的各种功能

简单来说就是把Android自动化的能力通过HTTP接口的方式暴露给Python使用。这种设计使得Python端的代码编写更加简单直观。

## 初始化环境

```bash
cd working/python/uiautomator2
# 可以先用python local 3.12.11选择pyenv的版本
python -m venv .venv
source .venv/bin/activate

pip install uiautomator2
uiautomator2 version
pip install uiautodev
# 命令行启动后会自动打开浏览器
uiautodev
```

配合 [[python 环境初始化#自动切换venv的zsh插件]] 可以自动切换venv
