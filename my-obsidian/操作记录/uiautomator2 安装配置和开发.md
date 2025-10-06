
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

### 安装Andriod Studio
启动模拟器, 使用下命令查看device
```bash
adb devices

# 设置检测wifi的网站
adb shell settings put global captive_portal_https_url https://www.baidu.com
```

以下命令可以运行输出device的信息
```python
import uiautomator2 as u2

d = u2.connect('emulator-5554') # 连接多台设备需要指定设备序列号
print(d.info)
```

### 安装 APK 的命令
#### 安装
`adb -s emulator-5554 install your_app.apk`
*常见参数*
- `-r` ：允许覆盖安装（更新已有应用）
- `-d` ：允许降级安装（版本号比现有低时也能装）
- `-g` ：自动授予所有运行时权限
*比如：*
`adb -s emulator-5554 install -r -g your_app.apk`
#### 📌 验证安装是否成功
*安装完可以查看：*
`adb -s emulator-5554 shell pm list packages | grep your.app.package`
*或者直接启动：*
`adb -s emulator-5554 shell monkey -p your.app.package -c android.intent.category.LAUNCHER 1`