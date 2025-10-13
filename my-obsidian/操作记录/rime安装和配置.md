## 下载安装
下载最新版 rime https://rime.im/download/
 * 鼠鬚管 Squirrel
下载后安装，要求logout然后再login系统

## 配置

首先在系統中启用input source的rime
*下载雾凇输入法源, 把相关配置都拷贝到rime的配置目录*
```bash
cd Downloads
git clone https://github.com/iDvel/rime-ice.git Rime --depth 1
cd Rime
cp -r ./* $HOME/Library/Rime/
```

*简单配置一下*
* default.yaml
```yaml
# 菜单
menu:
  page_size: 9  # 候选词个数
```

* squrrial.yaml 配置主题, vim支持
```yaml
# ascii_mode、inline、no_inline、vim_mode 等等设定
# 可参考 /Library/Input Methods/Squirrel.app/Contents/SharedSupport/squirrel.yaml
app_options:
  com.apple.Spotlight:
    ascii_mode: true    # 开启默认英文
  com.microsoft.VSCode:
    vim_mode: true   # 关闭默认英文
style:
  # 选择皮肤，亮色与暗色主题
  color_scheme: solarized_rock
  color_scheme_dark: solarized_rock

```
