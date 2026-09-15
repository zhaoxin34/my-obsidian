# Omarchy 安装 Mihomo (Clash Meta) 操作记录

> 在另一台机器（mac）已有 Clash Verge + 订阅的前提下，把同一份订阅 / 节点搬到 Omarchy 主机，复用 mac 作为上游代理。
> 重点：GFW / 订阅 403 / omarchy 网络受限 / TUN 模式 / GUI 替代（TUI）的全流程坑。

## 0. 环境与前提

| 角色 | 机器 | IP | 用途 |
|---|---|---|---|
| 已有 mac | macOS | `192.168.31.67` | 跑 Clash Verge，`allow-lan: true`，端口 `7890`（mixed HTTP+SOCKS5） |
| 目标机 | Omarchy（Arch 内核，Hyprland 桌面） | `192.168.31.36` | 跑 mihomo + TUN 接管所有流量 |
| 订阅 | 貝雪雲 (besnow) | — | URL 含 token + name，**Cloudflare 403 屏蔽所有非常规 IP**（详见故障 1） |
| 用户 | — | — | mac `~/.bashrc` / `~/.zshrc` 已被你**注释掉**所有代理 export，**本 playbook 不再触碰**这两个文件 |

> 关键事实：omarchy 主机**无法直连** GitHub / AUR / besnow.uk / 任何国际站点（GFW）。所有出网必须经 `mac:7890` 代理。

---

## 1. 准备：让 omarchy 通过 mac 出网

omarchy 装好以后默认断网（GFW）。先 SSH 登录，再设 mac 代理。

```bash
# 1.1 从 mac 登录 omarchy
ssh omc                    # ~/.ssh/config 里配了 Host omc -> 192.168.31.36

# 1.2 验证代理可达（mac 端 Clash 须先开 allow-lan: true）
curl -sS --max-time 5 -x http://192.168.31.67:7890 -I https://www.google.com
# 期望：HTTP/1.1 200 Connection established
curl --max-time 5 -I https://www.google.com
# 期望：connection timed out（直连被 GFW 挡）

# 1.3 当前 shell 设环境变量（仅本 session 生效；不写 .zshrc/.bashrc）
export http_proxy=http://192.168.31.67:7890
export https_proxy=http://192.168.31.67:7890
export all_proxy=socks5://192.168.31.67:7890
export no_proxy=127.0.0.1,localhost,192.168.31.0/24
```

> **重要约定**：本 playbook 后续所有操作（`yay` / `scp` / `curl`），都**默认你已 export 这 4 个变量**。你已声明 `.zshrc`/`.bashrc` 不让我碰。

---

## 2. 安装 mihomo（AUR）

mihomo 不在官方仓库，只有 AUR。`yay` 已预装。

```bash
# 2.1 搜索
yay -Ss mihomo
# 期望看到：
#   aur/mihomo-bin     (二进制版，推荐)
#   aur/mihomo         (源码版，慢)
#   aur/mihomo-git     (git 版)

# 2.2 安装（必须带 --noconfirm + 跳 PKGBUILD 编辑，否则 yay 卡交互）
yes | yay -S --noconfirm --answeredit None --answerdiff None --removemake mihomo-bin
```

**踩坑**：
- `yay` 不认 `--nodiff` / `--noedit`（旧文档里常见），正确的是 `--answeredit None --answerdiff None`。
- `--removemake` 让装完删 makedepends（mihomo 是预编译二进制，其实不需要编译，但留着无害）。
- 安装时 pacman 后置 hook 会 reload systemd（`Reloading system manager configuration`），属正常。

---

## 3. 赋予 TUN 能力（必须 sudo）

```bash
sudo setcap cap_net_admin,cap_net_bind_service=+ep /usr/bin/mihomo
getcap /usr/bin/mihomo
# 期望：/usr/bin/mihomo cap_net_bind_service,cap_net_admin=ep
```

> 不 setcap 的话，mihomo 启动时会报 `operation not permitted` 起不来 TUN。
> **每次 mihomo-bin 升级后要重跑**（新二进制覆盖会丢 cap）。

---

## 4. 准备配置目录 + secret

```bash
mkdir -p ~/.config/mihomo ~/.config/systemd/user

# 4.1 生成 controller secret（32 hex）
SECRET=$(openssl rand -hex 16)
echo "$SECRET" > ~/.config/mihomo/.secret
chmod 600 ~/.config/mihomo/.secret

# 4.2 验证 mihomo 装好
/usr/bin/mihomo -v
# 期望：Mihomo Meta v1.19.x linux amd64 with go1.x ... with_gvisor
```

---

## 5. 拿到订阅（mac 上 cache 复制过来）

订阅 URL 在 omarchy 上**完全无法直连**（besnow 走 Cloudflare，omarchy IP 被 403；走 mac 代理也 403，因为 Cloudflare 还认 TLS 指纹，curl 的指纹不像 clash 客户端）。所以**直接从 mac 的 clash-verge 缓存拉订阅 YAML**最稳。

```bash
# 5.1 找 mac 上的订阅文件
ls ~/Library/Application\ Support/io.github.clash-verge-rev.clash-verge-rev/profiles/
# 期望看到 RrB3nwVaJ7Rz.yaml（mac 当前订阅的 cache）

# 5.2 同时也把 MMDB / GeoSite 拉过来（omarchy 自己下 GitHub 必失败）
scp "~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/profiles/RrB3nwVaJ7Rz.yaml" \
    omc:/home/zhaoxin/.config/mihomo/config.yaml

scp ~/Library/Application\ Support/io.github.clash-verge-rev.clash-verge-rev/Country.mmdb \
    omc:/home/zhaoxin/.config/mihomo/Country.mmdb

scp ~/Library/Application\ Support/io.github.clash-verge-rev.clash-verge-rev/geosite.dat \
    omc:/home/zhaoxin/.config/mihomo/geosite.dat
```

> ⚠️ 文件名含空格，scp 路径要加引号（mac 这边）或用 `\` 转义。`~` 在 mac 终端和远程 scp 都会被展开，注意歧义。

---

## 6. 改 config.yaml（3 处修改）

mac 的订阅配置是 clash-verge 风格，omarchy 上 mihomo 要做 3 处小改：

```bash
SECRET=$(cat ~/.config/mihomo/.secret)

# 6.1 allow-lan: true → false（mac 是 LAN 共享，omarchy 只本机用）
sed -i 's|allow-lan: true|allow-lan: false|' ~/.config/mihomo/config.yaml

# 6.2 secret 写进 external-controller 后（独立顶层 key，不能是子 key）
#    原 mac 行：external-controller: '127.0.0.1:9090'
#    用 awk 在 proxies: 段之前插入我们自己的：tun + geodata-mode + geox-url + secret
awk -v SECRET="$SECRET" '
/^proxies:$/ && !done_tun {
  print ""
  print "# --- omarchy TUN additions (placed before proxies) ---"
  print "geodata-mode: false"
  print "geox-url:"
  print "  geoip: \"file:///home/zhaoxin/.config/mihomo/Country.mmdb\""
  print "  geosite: \"file:///home/zhaoxin/.config/mihomo/geosite.dat\""
  print ""
  print "tun:"
  print "  enable: true"
  print "  stack: system"
  print "  auto-route: true"
  print "  auto-detect-interface: true"
  print "  dns-hijack:"
  print "    - any:53"
  print ""
  done_tun=1
}
/^external-controller:/ && !done_secret {
  print
  print "secret: \"" SECRET "\""
  done_secret=1
  next
}
{ print }
' ~/.config/mihomo/config.yaml > /tmp/new-config.yaml
mv /tmp/new-config.yaml ~/.config/mihomo/config.yaml

# 6.3 验证配置
mihomo -t -f ~/.config/mihomo/config.yaml
# 期望结尾：configuration file ... is successful
```

**关键排版坑**（已踩过）：
- `secret` **不能**写在 `external-controller:` 下面做子 key（它是 string，不是 map）。YAML 解析会报 `did not find expected key`。
- `tun.dns-hijack` 的正确格式是 `[{addr}:{port}]`（如 `- any:53`），**不要**写 `- tcp:53`（mihomo 会 `unable to parse IP`）。
- `tun` 块必须放在**顶层**——不能插到 `dns:` 段内部（会破坏缩进）。
- `geodata-mode: false` + `geox-url.geoip: file://...` 才会**用本地 MMDB**，否则会去 GitHub 拉（omarchy 拉不到）。

---

## 7. systemd user service

```bash
# 7.1 写 service 文件
cat > ~/.config/systemd/user/mihomo.service <<'UNIT_EOF'
[Unit]
Description=mihomo (Clash Meta) daemon
Documentation=https://wiki.metacubex.one/
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
Environment=http_proxy=http://192.168.31.67:7890
Environment=https_proxy=http://192.168.31.67:7890
Environment=all_proxy=socks5://192.168.31.67:7890
Environment=no_proxy=127.0.0.1,localhost,192.168.31.0/24
ExecStart=/usr/bin/mihomo -d /home/zhaoxin/.config/mihomo
Restart=on-failure
RestartSec=5
LimitNOFILE=1048576

[Install]
WantedBy=default.target
UNIT_EOF

# 7.2 启用
systemctl --user daemon-reload
systemctl --user enable --now mihomo.service
systemctl --user status mihomo.service --no-pager
# 期望：Active: active (running)
#       LISTEN 7890 / LISTEN 9090（用 ss -tlnp 验）
#       ip tuntap list → Meta: tun
```

**坑**：
- 第一次启动可能 `Start TUN listening error: parse dns-hijack url error`，**这不代表失败**——mihomo 仍然会起 mixed proxy，TUN 用默认空配置。重修 dns-hijack 后 `systemctl --user restart`。
- 想 SSH 断电后 mihomo 仍跑，需要 `sudo loginctl enable-linger zhaoxin`（**要 sudo**）。

---

## 8. 验收（必跑）

```bash
# 8.1 HTTP 代理
curl -sS --max-time 10 -x http://127.0.0.1:7890 -I https://www.google.com
# 期望：HTTP/2 200

# 8.2 SOCKS5
curl -sS --max-time 10 --socks5-hostname 127.0.0.1:7890 -I https://www.youtube.com

# 8.3 TUN 设备
ip tuntap list
# 期望：Meta: tun
ip route | grep 198.18
# 期望：198.18.0.0/30 dev Meta ...

# 8.4 Dashboard API
curl -sS -H "Authorization: Bearer $(cat ~/.config/mihomo/.secret)" \
    http://127.0.0.1:9090/version
# 期望：{"meta":true,"version":"v1.19.x"}
```

---

## 9. TUI 客户端（替代 mac 的 Clash Verge GUI）

```bash
# 9.1 装（用代理，否则 AUR 下不到）
yay -S --noconfirm --answeredit None --answerdiff None --removemake mihomo-tui-bin

# 9.2 写配置（mihomo-tui 走 mihomo controller API）
mkdir -p ~/.config/mihomo-tui
SECRET=$(cat ~/.config/mihomo/.secret)
cat > ~/.config/mihomo-tui/config.yaml <<EOF
mihomo-api: http://127.0.0.1:9090
mihomo-secret: "$SECRET"
log-file: /tmp/mihomo-tui.log
log-level: error
proxy-setting:
  test-url: https://www.gstatic.com/generate_204
  test-timeout: 5000
EOF

# 9.3 启动（mihomo-tui 也走代理环境变量）
mihomo-tui
```

TUI 键位（potoo0/mihomo-tui）：
- `Tab` / `Shift+Tab`：切换面板
- `↑/↓` 或 `j/k`：上下选
- `Enter`：确认
- `Space`：延迟测试
- `u` / `d`：上一/下一节点
- `?`：帮助
- `q` / `Esc`：退出
- `r`：reload 配置
- `:`：命令模式

---

## 10. 控制脚本 mihomo-ctl

```bash
cat > ~/.local/bin/mihomo-ctl <<'BASH_EOF'
#!/bin/bash
SECRET=$(cat ~/.config/mihomo/.secret 2>/dev/null)
API="http://127.0.0.1:9090"
AUTH=(-H "Authorization: Bearer $SECRET")

case "${1:-status}" in
  status)   systemctl --user status mihomo --no-pager | head -10
            echo '--- listening ---'
            ss -tlnp 2>/dev/null | grep -E ':(7890|9090)\s'
            echo '--- TUN ---'
            ip tuntap list 2>/dev/null ;;
  restart)  systemctl --user restart mihomo && sleep 2 && echo 'restarted' ;;
  stop)     systemctl --user stop mihomo ;;
  start)    systemctl --user start mihomo ;;
  logs)     journalctl --user -u mihomo -f ;;
  log)      journalctl --user -u mihomo -n 50 --no-pager ;;
  proxies)  curl -sS "${AUTH[@]}" $API/proxies | python3 -m json.tool 2>/dev/null | head -40 ;;
  groups)   curl -sS "${AUTH[@]}" $API/proxies | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(k, "->", v.get("type")) for k,v in d.get("proxies",{}).items() if v.get("type") in ("select","url-test","fallback","load-balance")]' 2>/dev/null ;;
  refresh)  sudo systemctl restart mihomo 2>/dev/null || systemctl --user restart mihomo ;;
  test)     echo 'HTTP proxy:'; curl -sS --max-time 5 -x http://127.0.0.1:7890 -I https://www.google.com 2>&1 | head -1
            echo 'SOCKS5:';     curl -sS --max-time 5 --socks5-hostname 127.0.0.1:7890 -I https://www.youtube.com 2>&1 | head -1 ;;
  tui)      command -v mihomo-tui >/dev/null 2>&1 || { echo 'mihomo-tui not installed (yay -S mihomo-tui-bin)'; exit 1; }
            exec mihomo-tui ;;
  *)        echo "Usage: mihomo-ctl {status|start|stop|restart|logs|log|proxies|groups|refresh|test|tui}" ;;
esac
BASH_EOF
chmod +x ~/.local/bin/mihomo-ctl
```

常用：
```bash
mihomo-ctl            # 等价 status
mihomo-ctl tui        # 启动 TUI（最常用）
mihomo-ctl test       # HTTP/SOCKS 快速验证
mihomo-ctl log        # 最近 50 行日志
mihomo-ctl groups     # 列所有代理组
```

---

## 11. 故障排查（按出现顺序）

### 故障 1：omarchy 所有出网都失败

**症状**：`curl https://www.google.com` 连接超时；`yay -S` 下载失败。

**根因**：omarchy 在 GFW 后面。**唯一出路**是走 mac 的 LAN 代理（`192.168.31.67:7890`），前提是 mac 的 Clash Verge 已开 `allow-lan: true`。

**诊断**：
```bash
curl --max-time 5 -I https://www.google.com           # 必超时
curl --max-time 5 -x http://192.168.31.67:7890 -I https://www.google.com  # 必 200
```

**修**：export 4 个 proxy 变量（见 §1.3）。`yay` / `curl` / `scp` 全认这些 env。

---

### 故障 2：besnow.uk 订阅返回 403

**症状**：`curl https://durian.besnow.uk/api/v1/client/subscribe?token=...&name=...` 返回 403 Cloudflare HTML（无论直连还是走 mac 代理都一样）。

**根因**：Cloudflare 走 Bot Management，对 curl 的 TLS 指纹（JA3）识别为非 clash 客户端，拒绝服务。**mac 自己的 Clash Verge 客户端能拿到是因为 TLS 指纹正确。**

**修**：**不要试图在线拉**。直接从 mac 把订阅文件 scp 过来（§5.2）。订阅文件本身是完整 Clash YAML（混合端口 + 节点 + 代理组 + 规则），mihomo 直接吃。

> 以后想自动刷新：写脚本在 mac 上跑 Clash Verge 的"刷新订阅"功能，再 scp 到 omarchy + `systemctl --user restart mihomo`。

---

### 故障 3：`mihomo -t` 报 "can't download MMDB / GeoSite"

**症状**：测试 config 时日志：
```
ERRO can't initial GeoIP: can't download MMDB: ...
    https://github.com/MetaCubeX/meta-rules-dat/...
ERRO DNS FallbackGeosite[0] format error
```

**根因**：omarchy 不通 GitHub；mihomo 启动时默认从 GitHub 拉 MMDB / GeoSite。

**修**：
1. 从 mac 复制 MMDB/GeoSite（§5.2）。
2. config.yaml 加：
   ```yaml
   geodata-mode: false
   geox-url:
     geoip: "file:///home/zhaoxin/.config/mihomo/Country.mmdb"
     geosite: "file:///home/zhaoxin/.config/mihomo/geosite.dat"
   ```
3. 重测 `mihomo -t`。

---

### 故障 4：TUN 启动报错

**症状 A**：`Start TUN listening error: parse dns-hijack url error: ParseAddr("tcp")` —— `dns-hijack` 写了 `- tcp:53`。
**修**：改成 `- any:53`（`any` 是关键字，匹配所有 53 端口请求）。

**症状 B**：TUN 不起来但 mixed proxy 正常 —— 通常是 setcap 没成功。
**修**：`sudo setcap cap_net_admin,cap_net_bind_service=+ep /usr/bin/mihomo`，重跑 `systemctl --user restart mihomo`。

---

### 故障 5：YAML 验证报 "did not find expected key"

**症状**：`yaml: line N: did not find expected key`。

**最常见原因**：用 sed 把 `secret: "..."` 错误地缩进到 `external-controller:` 下面。`external-controller` 是 string，不是 map，secret 必须是**顶层独立 key**。

**修**：用 awk 插入（§6.2），别用 sed `a\`（会破坏缩进）。

---

### 故障 6：`mihomo-tui` 启动后乱码 / 黑屏

**症状**：TUI 看起来错位 / 显示 ▒ 等乱码。
**根因**：终端类型不对。Omarchy 默认 `foot` / `kitty` 是 OK 的；`linux` 不行。
**修**：`echo $TERM` 应该是 `foot`、`xterm-256color` 或类似。SSH 进去用 `alacritty` / `wezterm` 也行。

---

### 故障 7：mihomo 升级后 TUN 又挂了

**症状**：`yay -Syu` 升级 mihomo-bin 后，service 起不来 / TUN 没权限。
**根因**：`setcap` 是在旧二进制上设置的，新二进制覆盖会丢。
**修**：
```bash
sudo setcap cap_net_admin,cap_net_bind_service=+ep /usr/bin/mihomo
sudo systemctl restart mihomo    # 如果 mihomo 是 system service
# 或：systemctl --user restart mihomo
```
**建议**：升级前 `mihomo-ctl stop`，升级后重设 cap 再 `mihomo-ctl start`。

---

## 12. 一次性密码 / 凭据

- mac Clash Verge `secret`：**无**（mac 用默认配置，没设 secret）
- omarchy mihomo controller secret：见 `~/.config/mihomo/.secret`（32 hex）
- besnow 订阅 token：在订阅 URL 里（不存本地；想换得去 besnow 网站）

---

## 13. 完整文件清单（最终态）

```
~/.config/mihomo/
├── config.yaml          # 主配置（mac 订阅基础 + 我们的 TUN/MMDB 块）
├── Country.mmdb         # 从 mac 复制
├── geosite.dat          # 从 mac 复制
└── .secret              # controller secret（chmod 600）

~/.config/systemd/user/
└── mihomo.service       # systemd user unit

~/.config/mihomo-tui/
└── config.yaml          # TUI 客户端配置

~/.local/bin/
└── mihomo-ctl           # 控制脚本
```

- `/usr/bin/mihomo` （AUR `mihomo-bin`）
- `/usr/bin/mihomo-tui` （AUR `mihomo-tui-bin`）

---

## 14. 速查：升级 mihomo-bin 后的 3 步

```bash
yay -S --noconfirm mihomo-bin
sudo setcap cap_net_admin,cap_net_bind_service=+ep /usr/bin/mihomo
mihomo-ctl restart
```

---

## 15. 速查：mihomo 不通时的 5 条诊断

```bash
mihomo-ctl status    # 服务在跑？端口在听？TUN 设备在？
mihomo-ctl log | tail -30   # 最近日志
journalctl --user -u mihomo -n 50 --no-pager
ip tuntap list       # TUN 设备名（应该 Meta: tun）
curl -x http://127.0.0.1:7890 -I https://www.google.com   # mixed proxy
```

如果 mixed proxy 通但全局流量不通 → TUN 挂了（`sudo setcap` 后 `mihomo-ctl restart`）。
如果 mixed proxy 也不通 → 检查 `mac:7890` 是否仍可达（`curl -x http://192.168.31.67:7890 ...`）。
