## 如何查看日志

使用`ps axu|grep zellij` 会返回启动的进程信息

> /opt/homebrew/bin/zellij --server /var/folders/c5/lx_yfpg90b5gvp18ccw1jydw0000gn/T/zellij-501/0.43.1/polished-clarinet

一般日志就在
/var/folders/c5/lx_yfpg90b5gvp18ccw1jydw0000gn/T/zellij-501/zellij-log 目录下

## Layout 配置技巧

*下面配置展示了，如果2个pane横向分割，当增加第3个pane时，会变成纵向3个*
```kdl
layout {
    swap_tiled_layout name="h2v" {
        tab max_panes=2 {
            pane
            pane
        }
        tab {
            pane split_direction="vertical" {
                pane
                pane
                pane
            }
        }
    }
}
```