# Omarchy 安装 Mihomo (Clash Meta) 操作记录

> 在另一台机器（mac）已有 Clash Verge + 订阅的前提下，把同一份订阅 / 节点搬到 Omarchy 主机，复用 mac 作为上游代理。
> 重点：GFW / 订阅 403 / omarchy 网络受限 / TUN 模式 / **必须用 system service（root）才能 TUN 接管全流量** / GUI 替代（TUI）的全流程坑。

## 0. 环境与前提

| 角色     | 机器                           | IP  | 用途                                                                          |
| ------ | ---------------------------- | --- | --------------------------------------------------------------------------- |
| 已有 mac | macOS                        |     | 跑 Clash Verge，`allow-lan: true`，端口 `7890`（mixed HTTP+SOCKS5）                |
| 目标机    | Omarchy（Arch 内核，Hyprland 桌面） |     | 跑 mihomo + TUN 接管所有流量                                                       |
| 订阅     | 貝雪雲 (besnow)                 | —   | URL 含 token + name，**Cloudflare 403 屏蔽所有非常规 IP**（详见故障 2）                    |
| 用户     | —                            | —   | mac `~/.bashrc` / `~/.zshrc` 已被你**注释掉**所有代理 export，**本 playbook 不再触碰**这两个文件 |

> 关键事实：omarchy 主机**无法直连** GitHub / AUR / besnow.uk / 任何国际站点（GFW）。所有出网必须经 `mac:7890` 代理。

> **大坑预警**：mihomo TUN 模式**必须以 root 跑**（system service）。user systemd 受 Linux capability 限制，加 iptables/nftables 规则和 default route 都会失败。详见故障 8。

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

## 3. 赋予 TUN 能力（即使 system service 是 root，也建议设）

```bash
sudo setcap cap_net_admin,cap_net_bind_service,cap_net_raw=+ep /usr/bin/mihomo
getcap /usr/bin/mihomo
# 期望：/usr/bin/mihomo cap_net_bind_service,cap_net_admin,cap_net_raw=ep
```

> 不 setcap 的话，mihomo 启动时会报 `operation not permitted` 起不来 TUN。
> **每次 mihomo-bin 升级后要重跑**（新二进制覆盖会丢 cap）。
> 增加了 `cap_net_raw` 是因为某些场景下 mihomo 需要原始 socket（健康检查等）。

---

## 4. 准备配置目录 + secret（system service 用 `/etc/mihomo/`）

mihomo 标准位置是 `/etc/mihomo/`（macOS 习惯放 `~/Library/Application Support/...`，Linux 标准是 `/etc/`）。

```bash
# 4.1 建临时目录 + secret（先在 user home 搞，后面再 sudo mv）
mkdir -p ~/.config/mihomo

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

## 6. 改 config.yaml（Linux 必须加 3 个关键项）

mac 的订阅配置是 clash-verge 风格，**直接用不行**——Linux 上 mihomo 必须额外配置：

| 字段                             | 为什么必须加（mac 上不需要）                                          |
| ------------------------------ | --------------------------------------------------------- |
| `tun.auto-redirect: true`      | Linux only，让 mihomo 调 nftables/iptables 把 DNS 重定向到 mihomo |
| `tun.dns-hijack: any:53`       | 让 TUN 抓 DNS 包自己回 fake-IP                                  |
| `tun.dns-hijack: tcp://any:53` | TCP DNS 也接管（DoH 客户端可能用 TCP）                               |

```bash
SECRET=$(cat ~/.config/mihomo/.secret)

# 6.1 allow-lan: true → false（mac 是 LAN 共享，omarchy 只本机用）
sed -i 's|allow-lan: true|allow-lan: false|' ~/.config/mihomo/config.yaml

# 6.2 在 proxies: 段之前插入 tun + auto-redirect + dns-hijack + geodata-mode + secret
awk -v SECRET="$SECRET" '
/^proxies:$/ && !done_tun {
  print ""
  print "# --- omarchy TUN additions (Linux only) ---"
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
  print "  auto-redirect: true"
  print "  dns-hijack:"
  print "    - any:53"
  print "    - tcp://any:53"
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
- `tun.dns-hijack` 的正确格式是 `[{addr}:{port}]`（如 `- any:53`），**不要**写 `- tcp:53`（mihomo 会 `unable to parse IP`）。**TCP 端口要写完整** `tcp://any:53`。
- `tun` 块必须放在**顶层**——不能插到 `dns:` 段内部（会破坏缩进）。
- `geodata-mode: false` + `geox-url.geoip: file://...` 才会**用本地 MMDB**，否则会去 GitHub 拉（omarchy 拉不到）。
- 移动到 system service 后（§7）config.yaml 的路径要改成 `/etc/mihomo/config.yaml`，下面所有路径同步替换。

---

## 7. systemd system service（root 跑，必须 sudo）

**这是关键**：mihomo TUN 必须以 root 跑。user systemd 受 Linux capability 限制，加不上 iptables/nftables 规则 + default route。详见故障 8。

```bash
# 7.1 移 config 到 /etc/mihomo/（system service 标准位置）
sudo mkdir -p /etc/mihomo
# 注意 bash 通配符 * 不匹配隐藏文件，要单独 cp .secret
sudo cp -r ~/.config/mihomo/* /etc/mihomo/
sudo cp ~/.config/mihomo/.secret /etc/mihomo/.secret
sudo chown -R root:root /etc/mihomo
sudo chmod 700 /etc/mihomo
sudo chmod 600 /etc/mihomo/.secret
sudo chmod 755 /etc/mihomo/config.yaml
sudo chmod 644 /etc/mihomo/{Country.mmdb,geosite.dat}

# 7.2 写 system service（不是 user service！）
sudo tee /etc/systemd/system/mihomo.service > /dev/null <<'EOF'
[Unit]
Description=mihomo (Clash Meta) daemon
Documentation=https://wiki.metacubex.one/
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/mihomo -d /etc/mihomo
Restart=on-failure
RestartSec=5
LimitNOFILE=1048576
# system service 可以用 AmbientCapabilities 拿到 caps（user service 不行）
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE CAP_NET_RAW
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE CAP_NET_RAW

[Install]
WantedBy=multi-user.target
EOF

# 7.3 启用 + 启动
sudo systemctl daemon-reload
sudo systemctl enable --now mihomo.service
sleep 3
sudo systemctl status mihomo.service --no-pager
# 期望：Active: active (running)
#       Main PID 下显示 /usr/bin/mihomo -d /etc/mihomo
#       CGroup: /system.slice/mihomo.service

ss -tlnp | grep -E ':(7890|9090)'
# 期望 LISTEN 127.0.0.1:7890 / 127.0.0.1:9090

ip tuntap list
# 期望：Meta: tun
```

**关键注意**：
- 第一次启动时如果**旧的 user systemd mihomo 还活着**，新的 system mihomo 启动会因端口冲突失败（log 里会看到 `bind: address already in use` 和 `configure tun interface: device or resource busy`）。必须先杀掉旧的：
  ```bash
  sudo pkill -9 -u zhaoxin mihomo
  sudo systemctl restart mihomo.service
  ```
- `WantedBy=multi-user.target`（**不是** `default.target`）。user service 用 `default.target`，system service 用 `multi-user.target`。

---

## 8. 验收（必跑）

```bash
# 8.1 service 状态
sudo systemctl status mihomo.service --no-pager
# 期望：Active: active (running)

# 8.2 mixed proxy 端口
ss -tlnp | grep -E ':(7890|9090)'

# 8.3 TUN 设备
ip tuntap list
# 期望：Meta: tun
ip route | grep 198.18
# 期望：198.18.0.0/30 dev Meta（fake-IP 段路由）

# 8.4 mixed proxy（直连）
curl -sS --max-time 10 -x http://127.0.0.1:7890 -I https://www.google.com
# 期望：HTTP/2 200

# 8.5 SOCKS5
curl -sS --max-time 10 --socks5-hostname 127.0.0.1:7890 -I https://www.youtube.com

# 8.6 TUN 真接管（不配代理直连）
curl -sS --max-time 8 -I https://github.com
# 期望：HTTP/2 200（直连被 GFW 挡，200 = TUN 接管成功）
# 这是验证 TUN 是否真工作的**决定性**测试

# 8.7 Dashboard API
curl -sS -H "Authorization: Bearer $(cat /etc/mihomo/.secret)" \
    http://127.0.0.1:9090/version
# 期望：{"meta":true,"version":"v1.19.x"}

# 8.8 终极测试：git clone 一个公共 repo（验证 DNS + TCP + TUN 全链路）
cd /tmp && rm -rf Hello-World 2>/dev/null
git clone --depth=1 https://github.com/octocat/Hello-World
ls Hello-World
# 期望：README 文件落盘
```

如果 8.6 / 8.8 失败，看故障 8。

---

## 9. TUI 客户端（替代 mac 的 Clash Verge GUI）

```bash
# 9.1 装（用代理，否则 AUR 下不到）
yay -S --noconfirm --answeredit None --answerdiff None --removemake mihomo-tui-bin

# 9.2 写配置（mihomo-tui 走 mihomo controller API）
mkdir -p ~/.config/mihomo-tui
SECRET=$(cat /etc/mihomo/.secret)
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

## 10. 控制脚本 mihomo-ctl（system service 版）

注意：所有 systemctl 命令都加 `sudo`（system service 在 system bus，不在 user bus）。

```bash
sudo tee /usr/local/bin/mihomo-ctl > /dev/null <<'BASH_EOF'
#!/bin/bash
# mihomo 控制脚本（system service 版）
SECRET=$(cat /etc/mihomo/.secret 2>/dev/null)
API="http://127.0.0.1:9090"
AUTH=(-H "Authorization: Bearer $SECRET")

sudo_needed() {
  if ! sudo -n true 2>/dev/null; then
    echo "(needs sudo: $1)"
    sudo -n "$@" 2>&1 || sudo "$@"
  fi
}

case "${1:-status}" in
  status)   sudo systemctl status mihomo --no-pager | head -10
            echo '--- listening ---'
            ss -tlnp 2>/dev/null | grep -E ':(7890|9090)\s'
            echo '--- TUN ---'
            ip tuntap list 2>/dev/null ;;
  restart)  sudo systemctl restart mihomo && sleep 2 && echo 'restarted' ;;
  stop)     sudo systemctl stop mihomo ;;
  start)    sudo systemctl start mihomo ;;
  logs)     sudo journalctl -u mihomo -f ;;
  log)      sudo journalctl -u mihomo -n 50 --no-pager ;;
  proxies)  curl -sS "${AUTH[@]}" $API/proxies | python3 -m json.tool 2>/dev/null | head -40 ;;
  groups)   curl -sS "${AUTH[@]}" $API/proxies | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(k, "->", v.get("type")) for k,v in d.get("proxies",{}).items() if v.get("type") in ("select","url-test","fallback","load-balance")]' 2>/dev/null ;;
  refresh)  echo 're-download from mac: scp omc mac:Library/.../RrB3nwVaJ7Rz.yaml /etc/mihomo/config.yaml.bak'
            sudo systemctl restart mihomo ;;
  test)     echo 'HTTP proxy:'; curl -sS --max-time 5 -x http://127.0.0.1:7890 -I https://www.google.com 2>&1 | head -1
            echo 'SOCKS5:';     curl -sS --max-time 5 --socks5-hostname 127.0.0.1:7890 -I https://www.youtube.com 2>&1 | head -1
            echo 'TUN (no proxy):'; curl -sS --max-time 5 -I https://github.com 2>&1 | head -1 ;;
  tui)      command -v mihomo-tui >/dev/null 2>&1 || { echo 'mihomo-tui not installed (yay -S mihomo-tui-bin)'; exit 1; }
            exec mihomo-tui ;;
  *)        echo "Usage: mihomo-ctl {status|start|stop|restart|logs|log|proxies|groups|refresh|test|tui}" ;;
esac
BASH_EOF
sudo chmod +x /usr/local/bin/mihomo-ctl
```

常用：
```bash
sudo mihomo-ctl            # 等价 status
sudo mihomo-ctl tui        # 启动 TUI
sudo mihomo-ctl test       # HTTP/SOCKS/TUN 三合一验证
sudo mihomo-ctl log        # 最近 50 行日志
sudo mihomo-ctl groups     # 列所有代理组
```

> 为什么放 `/usr/local/bin` 而不是 `~/.local/bin`？因为 system service 路径是 `/etc/mihomo/`，脚本要 sudo 才能读 .secret。放 `/usr/local/bin` 全局可见，需要 `sudo mihomo-ctl`。

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

> 以后想自动刷新：写脚本在 mac 上跑 Clash Verge 的"刷新订阅"功能，再 scp 到 omarchy + `sudo systemctl restart mihomo`。

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

### 故障 4：TUN 启动报错（dns-hijack 格式）

**症状 A**：`Start TUN listening error: parse dns-hijack url error: ParseAddr("tcp")` —— `dns-hijack` 写了 `- tcp:53`。
**修**：改成 `- tcp://any:53`（带协议前缀，`any` 是关键字）。

**症状 B**：TUN 不起来但 mixed proxy 正常 —— 通常是 setcap 没成功。
**修**：`sudo setcap cap_net_admin,cap_net_bind_service,cap_net_raw=+ep /usr/bin/mihomo`，重跑 `sudo systemctl restart mihomo`。

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
yay -S --noconfirm mihomo-bin
sudo setcap cap_net_admin,cap_net_bind_service,cap_net_raw=+ep /usr/bin/mihomo
sudo systemctl restart mihomo
```
**建议**：升级前 `sudo mihomo-ctl stop`。

---

### 故障 8：TUN 启动但流量不接管（user systemd 限制）— **本 playbook 的最大坑**

**症状**：
- `mihomo -t` validate 通过
- `ip tuntap list` 看到 `Meta: tun`
- 端口 7890/9090 在监听
- `curl -x http://127.0.0.1:7890 https://github.com` **通**
- **`curl https://github.com`（不配代理）超时或 LAN 直连**
- mihomo log 里**完全没有** `TCP ... github.com` 这类条目
- iptables NAT / mangle 表是空的（或只有 ufw/docker 链）
- `ip route show table all | grep 198.18` 只看到 `198.18.0.0/30`（fake-IP 段），**没** default route via Meta
- `getent hosts github.com` 返回真实 IP（`20.205.243.166`），不是 fake-IP

**根因**：mihomo 之前用 user systemd 跑（`~/.config/systemd/user/mihomo.service`）。user systemd 服务即使 setcap 加了 cap_net_admin，**子进程拿不到这些 caps**（user systemd 拒绝 AmbientCapabilities / CapabilityBoundingSet，会报 `Failed at step CAPABILITIES spawning /bin/sh: Operation not permitted`）。后果：
- mihomo 自己的 auto-route 只加 fake-IP 范围（/30）的 ip rule + table 2022，不会加 default route 覆盖真实外网 IP
- mihomo 加不上 iptables / nftables 的 DNS 重定向规则（写 /run/user/<uid>/ 或 nft 句柄都需要 cap_net_admin）
- systemd-resolved 没改成指向 198.18.0.2（user 服务无法改 /etc/systemd/resolved.conf.d/）

**修**：mihomo 必须以 **root 跑**（system service）。详见 §7。步骤：

```bash
# 1. 停掉 user service（从 user shell 跑，或者忽略这步直接 pkill）
systemctl --user stop mihomo 2>/dev/null
sudo pkill -9 -u zhaoxin mihomo  # 确保旧进程死透

# 2. 移 config 到 /etc/mihomo/
sudo mkdir -p /etc/mihomo
sudo cp -r ~/.config/mihomo/* /etc/mihomo/   # * 不匹配隐藏文件
sudo cp ~/.config/mihomo/.secret /etc/mihomo/.secret
sudo chown -R root:root /etc/mihomo
sudo chmod 700 /etc/mihomo
sudo chmod 600 /etc/mihomo/.secret

# 3. 写 /etc/systemd/system/mihomo.service（带 AmbientCapabilities）
sudo tee /etc/systemd/system/mihomo.service > /dev/null <<'EOF'
[Unit]
Description=mihomo (Clash Meta) daemon
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/mihomo -d /etc/mihomo
Restart=on-failure
RestartSec=5
LimitNOFILE=1048576
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE CAP_NET_RAW
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE CAP_NET_RAW

[Install]
WantedBy=multi-user.target
EOF

# 4. 启动 + 验证
sudo systemctl daemon-reload
sudo systemctl enable --now mihomo.service
sleep 3
sudo systemctl status mihomo.service --no-pager

# 5. 终极测试
curl https://github.com   # 应该 200（直连被 GFW 挡，200 = TUN 接管成功）
git clone https://github.com/octocat/Hello-World /tmp/test-tun  # 应该成功
```

**判断是否成功**：
- `curl https://github.com` → 200（TUN 真的接管）
- `sudo nft list ruleset | grep -iE '198.18|Meta'` → 看到 mihomo 加的 nftables 规则
- `sudo journalctl -u mihomo -n 50 --no-pager | grep -E 'TCP|UDP'` → 看到 mihomo 处理的 TCP/UDP 流量

---

### 故障 9：system service 启动后端口冲突 / TUN device busy

**症状**：system service 启动时 log 里出现：
```
External controller listen error: listen tcp 127.0.0.1:9090: bind: address already in use
Start Mixed(http+socks) server error: listen tcp 127.0.0.1:7890: bind: address already in use
[TUN] default interface changed by monitor, => wlp3s0
Start TUN listening error: configure tun interface: device or resource busy
```

**根因**：**旧的 user systemd mihomo 进程没被杀死**，占了 7890/9090 和 TUN 设备。

**修**：
```bash
sudo pkill -9 mihomo  # 或者 sudo pkill -9 -u zhaoxin mihomo（更精确）
sleep 2
sudo systemctl restart mihomo.service
sleep 3
ss -tlnp | grep -E ':(7890|9090)'  # 应该只剩新进程在 listen
ip tuntap list                      # 应该只剩一个 Meta: tun
sudo systemctl status mihomo.service --no-pager  # Active: active (running)
```

---

### 故障 10：arch 用 nftables 而不是 iptables，所以 iptables 检查是空的

**症状**：`sudo iptables -t nat -L` 看不到 mihomo 的 DNS redirect 规则，但 TUN 实际工作。
**根因**：Arch Linux 默认是 nftables 后端，`iptables` 命令其实是 nft 的兼容层（或者 iptables-nft 包）。
**修**：用 `sudo nft list ruleset` 查 mihomo 的规则，能看到就说明生效了。**或者直接信 TUN 工作的事实**（curl 直连 github.com 返回 200 = 工作）。

---

## 12. 一次性密码 / 凭据

- mac Clash Verge `secret`：**无**（mac 用默认配置，没设 secret）
- omarchy mihomo controller secret：见 `/etc/mihomo/.secret`（32 hex，root only，chmod 600）
- besnow 订阅 token：在订阅 URL 里（不存本地；想换得去 besnow 网站）

---

## 13. 完整文件清单（最终态）

```
/etc/mihomo/
├── config.yaml          # 主配置（mac 订阅基础 + Linux TUN/auto-redirect/dns-hijack）
├── Country.mmdb         # 从 mac 复制
├── geosite.dat          # 从 mac 复制
└── .secret              # controller secret（root only, chmod 600）

/etc/systemd/system/
└── mihomo.service       # system service（root 跑）

~/.config/mihomo-tui/
└── config.yaml          # TUI 客户端配置

/usr/local/bin/
└── mihomo-ctl           # 控制脚本（system service 版）
```

- `/usr/bin/mihomo` （AUR `mihomo-bin`）
- `/usr/bin/mihomo-tui` （AUR `mihomo-tui-bin`）

> 旧位置 `~/.config/mihomo/` 和 `~/.config/systemd/user/mihomo.service` 可以删了（system service 不再用）：
> ```bash
> sudo rm -rf ~/.config/mihomo
> rm ~/.config/systemd/user/mihomo.service
> ```

---

## 14. 速查：升级 mihomo-bin 后的 4 步

```bash
yay -S --noconfirm mihomo-bin
sudo setcap cap_net_admin,cap_net_bind_service,cap_net_raw=+ep /usr/bin/mihomo
sudo systemctl restart mihomo.service
sudo mihomo-ctl test    # 验证 TUN 还在工作
```

---

## 15. 速查：mihomo 不通时的 6 条诊断

```bash
sudo systemctl status mihomo    # service 在跑？
ss -tlnp | grep -E ':(7890|9090)'  # 端口在听？
ip tuntap list                    # TUN 设备（应该 Meta: tun）
sudo journalctl -u mihomo -n 50 --no-pager  # 最近日志
curl -x http://127.0.0.1:7890 -I https://www.google.com   # mixed proxy 通不通
curl https://github.com                                 # TUN 真工作了吗（直连应该被 GFW 挡，能 200 = TUN 接管成功）
```

如果 mixed proxy 通但 TUN 不接管 → **大概率是故障 8**（user systemd 限制）→ 迁移到 system service。
如果 mixed proxy 也不通 → 检查 `mac:7890` 是否仍可达（`curl -x http://192.168.31.67:7890 ...`），以及 mac 的 Clash Verge 是否开了 `allow-lan: true`。

---

## 16. mac 和 omarchy 的角色对照（重要）

| | mac | omarchy |
|---|---|---|
| 跑的 client | Clash Verge（GUI） | mihomo（TUI/CLI） |
| 跑的 core | 同一个 mihomo 内核 | 同一个 mihomo 内核 |
| 订阅源 | 貝雪雲（同一份 URL） | 貝雪雲（同 mac 缓存复制过来） |
| 配置文件 | clash-verge 自带 | `~/.config/mihomo/config.yaml`（mac 缓存 → 改 3 处） |
| 进程身份 | 用户（GUI app） | **root**（system service） |
| mixed port | 7890（`allow-lan: true`，供 omarchy 用） | 7890（本机用） |
| TUN | mac utun | Linux tun（Meta） |
| DNS 接管 | clash-verge 自动改系统 DNS | mihomo 自己改（`auto-redirect: true` + `dns-hijack`） |

两台机器**互不直接通信**，各走各的代理。如果以后要 omarchy 拉更新：
- 在 mac 上让 Clash Verge 刷新订阅
- scp 新 YAML 到 omarchy `/etc/mihomo/config.yaml.bak`
- （可选）覆盖 `/etc/mihomo/config.yaml` + `sudo systemctl restart mihomo`
