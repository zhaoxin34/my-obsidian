实施配置
```bash
yabai -m config --space 1 layout float
yabai -m config --space 5 layout stack
```

修改window呈现的样子
```shell
# modify window shadows (default: on, options: on, off, float)
# example: show shadows only for floating windows
yabai -m config window_shadow float

# window opacity (default: off)
# example: render all unfocused windows with 90% opacity
yabai -m config window_opacity on
yabai -m config active_window_opacity 1.0
yabai -m config normal_window_opacity 0.9
```
### Tricks

绑定重启快捷键
ctrl + alt + cmd - r : yabai --restart-service

闪烁 focus的window
```bash
yabai -m signal --add label="flash_focus" event="window_focused" action="yabai -m window \$YABAI_WINDOW_ID --opacity 0.1 && sleep $(yabai -m config window_opacity_duration) && yabai -m window \$YABAI_WINDOW_ID --opacity 0.0"
```

yabai -m rule --list