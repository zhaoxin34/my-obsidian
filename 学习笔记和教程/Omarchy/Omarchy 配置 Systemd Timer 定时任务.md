# Omarchy 配置 Systemd Timer 定时任务

> 场景：需要每天 8 点自动执行 `pi update --all`（更新 pi 自身 + 所有扩展）。Omarchy（Arch 系）默认没有 `crontab` 命令，且 `crontab` 在 PATH 很精简的环境下连 `mise` 安装的 `pi` 都找不到。改用 **systemd timer**（user 级）实现，效果一样但更现代。
>
> 通用结论：任何"mac 思维"的 cron 定时任务，在 Omarchy（以及绝大多数现代 Linux 发行版）上**都优先用 systemd timer**，不折腾 cron。

## 0. 前置确认

```bash
# 0.1 当前是否真的没 crontab（Omarchy 默认没有）
command -v crontab || echo "无 crontab，确认要用 systemd timer"

# 0.2 systemd --user 守护进程在跑（图形登录后会自动起）
systemctl --user status | head -3
# 期望：State: running

# 0.3 要执行的命令本机能直接跑通（避免定时跑起来才发现 PATH 错）
pi update --all --help    # 至少能打印 help
```

**关键**：systemd user service 启动时**不会 source 你的 shell rc**（不会读 `.bashrc` / `.config/fish/config.fish` / `.zshrc`），PATH 只有 `/usr/bin:/bin`。所以 `ExecStart` 必须用**绝对路径**，或者用包装命令（本文用 `mise exec`）。

## 1. 思路

| 维度 | crontab | systemd timer（本文方案） |
|------|---------|---------------------------|
| Omarchy 默认安装 | ❌ | ✅ |
| PATH/环境变量隔离 | 经常踩坑 | 可显式声明 |
| 错过时间补跑 | ❌ | ✅ `Persistent=true` |
| 日志 | 自管 | journalctl + 文件双写 |
| 随机延迟 | 自己写 | ✅ `RandomizedDelaySec` |
| 依赖网络 | 自己写 | ✅ `After=network-online.target` |

## 2. 准备日志目录

```bash
mkdir -p ~/logs && touch ~/logs/pi-update.log
# 权限 700，只有当前用户能看
```

## 3. 写 service 文件：`~/.config/systemd/user/pi-update.service`

```ini
[Unit]
Description=Daily update of pi and all extensions (pi update --all)
Documentation=https://github.com/badlogic/pi
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot

# 用 mise exec 包装，让 pi 内部用的 npm/git/node 都有正确 PATH
ExecStart=/usr/bin/mise exec -- pi update --all

# 输出同时写文件 + journalctl
StandardOutput=append:/home/zhaoxin/logs/pi-update.log
StandardError=append:/home/zhaoxin/logs/pi-update.log

# pi update 会跑 npm install，限个内存避免失控
MemoryMax=2G

PrivateTmp=true
NoNewPrivileges=true
```

**关键**：`ExecStart` 用 `/usr/bin/mise exec -- pi update --all`，**不要**直接写 `pi update --all`，否则会报 `pi: command not found`。如果你的工具不是 mise 装的，改为绝对路径，例如 `/home/zhaoxin/.local/bin/pi update --all`。

## 4. 写 timer 文件：`~/.config/systemd/user/pi-update.timer`

```ini
[Unit]
Description=Daily pi update timer (08:00)
Requires=pi-update.service

[Timer]
# 每天 08:00
OnCalendar=*-*-* 08:00:00

# 电脑在 8 点关机/休眠了，开机后自动补跑
Persistent=true

# 随机延迟 0~5 分钟：避免整点任务扎堆 + 减少 npm registry 限流
RandomizedDelaySec=5min

[Install]
WantedBy=timers.target
```

## 5. 启用 + 验证

```bash
# 5.1 重新加载配置
systemctl --user daemon-reload

# 5.2 启用 timer（创建 symlink 到 timers.target.wants/）
systemctl --user enable pi-update.timer

# 5.3 启动 timer
systemctl --user start pi-update.timer

# 5.4 看下次执行时间
systemctl --user list-timers pi-update.timer
# 期望：NEXT 列显示明天 08:0X（X 是 0~5 的随机数）

# 5.5 手动跑一次验证（不等明天）
systemctl --user start pi-update.service
sleep 2
systemctl --user status pi-update.service
# 期望：Active: inactive (dead)，Main PID ... status=0/SUCCESS

# 5.6 看日志
tail -20 ~/logs/pi-update.log
journalctl --user -u pi-update.service -n 15
```

实测结果（2026-09-17 在 omachy 机器上）：

- 耗时：7.4 秒
- 内存峰值：230 MB
- 下次执行：`Fri 2026-09-18 08:01:45 CST`
- `is-enabled`：`enabled`

## 6. 日常运维命令速查

```bash
# 查看下次执行时间
systemctl --user list-timers pi-update.timer

# 立刻手动触发一次
systemctl --user start pi-update.service

# 跟踪日志（实时）
tail -f ~/logs/pi-update.log

# 通过 journalctl 跟踪
journalctl --user -u pi-update.service -f

# 暂停定时（不删配置）
systemctl --user disable --now pi-update.timer

# 重新启用
systemctl --user enable --now pi-update.timer

# 完全卸载
systemctl --user disable --now pi-update.timer
mv ~/.config/systemd/user/pi-update.{service,timer} ~/.local/share/.delete.pi-update/
systemctl --user daemon-reload
```

## 7. 关键坑位汇总

1. **PATH 问题（最常见）**：`ExecStart` 必须用绝对路径，或者用 `mise exec` / `npx` / `source` 环境的包装。systemd 默认 PATH 只有 `/usr/bin:/bin`。
2. **网络未就绪**：`pi update --all` 要连 npm registry 和 git remote。如果不写 `After=network-online.target`，系统刚启动还没拨号时 timer 触发会失败。
3. **不会 source shell rc**：cron 会 `SHELL=/bin/sh` 然后执行命令，但 systemd 是**完全干净的环境**。`~/.bashrc`、`~/.config/fish/config.fish`、`mise activate` 都不生效。
4. **user service 没 ambient caps**：如果你的任务需要 `cap_net_admin` / `cap_net_bind_service` 等特殊能力（如 mihomo TUN 模式），**user systemd 不够**，必须写 `/etc/systemd/system/` 下的 system service，并用 `AmbientCapabilities` 授权。详见 [[Omarchy 安装 Mihomo (Clash Meta) 操作记录]] §6.2。
5. **电脑休眠时 timer 不一定触发**：用 `Persistent=true` 保证唤醒后补跑；否则 8 点在休眠，醒来不补，任务就丢了。
6. **修改 service/timer 后必须 `daemon-reload`**：否则 systemd 还在用内存里旧的定义。
7. **输出被 systemd 截断**：超长 stdout（比如 npm install 的进度条）可能不在 journalctl 显示，但 `StandardOutput=append:...` 的文件一定完整。

## 8. 复用：别的任务也想要每天定时执行？

复制 3 步走：

```bash
# 1. 复制两个文件，改名 + 改 ExecStart
cp ~/.config/systemd/user/pi-update.{service,timer} \
   ~/.config/systemd/user/my-task.{service,timer}
sed -i 's/pi update --all/my-command/' ~/.config/systemd/user/my-task.service

# 2. 启用
systemctl --user daemon-reload
systemctl --user enable --now my-task.timer

# 3. 验证
systemctl --user list-timers my-task.timer
```

OnCalendar 语法速查：

| 表达式 | 含义 |
|--------|------|
| `*-*-* 08:00:00` | 每天 8 点 |
| `Mon..Fri 09:00:00` | 工作日 9 点 |
| `*-*-1 00:00:00` | 每月 1 号 0 点 |
| `*:0/15` | 每 15 分钟一次 |
| `Sat *-*-1..7 00:00:00` | 每月第一个周六 0 点 |

## 9. 参考资料

- systemd.timer 官方文档：`man systemd.timer`
- systemd.service 官方文档：`man systemd.service`
- pi 更新命令：`pi update --help`
- 相关：[[Omarchy 安装 Mihomo (Clash Meta) 操作记录]]（system 级 systemd service 案例，对比参考）
