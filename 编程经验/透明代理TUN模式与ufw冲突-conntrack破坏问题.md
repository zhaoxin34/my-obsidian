# 透明代理 TUN 模式与 ufw 防火墙的 conntrack 冲突问题

## 使用场景

Linux 服务器上同时跑了 **TUN 模式的透明代理**（mihomo / clash / sing-box / xray 等开 TUN）和 **ufw / nftables 防火墙**，**局域网入站连接（如 SSH 22 端口）不通**。具体表现：

1. **ping 通**（ICMP 不受影响）但 **TCP 不通**（SSH / RDP / 自建服务等）
2. `ufw status` 显示规则对、22 端口 allow 了来源 IP
3. `iptables -L ufw-user-input -n -v` 看到 allow 规则**但 counter 一直是 0**（包根本没匹配）
4. `sudo ufw disable` 立刻通；`sudo ufw enable` 立刻又不通
5. 代理软件的日志里**能看到**被拒的连接（如 mihomo 日志 `[TCP] 192.168.0.151:xxx --> 192.168.0.136:22 match IPCIDR(192.168.0.0/16) using DIRECT`）

典型关键字：
- `iptables ... counter packets 0`（规则写了但没命中）
- `redirect to :xxxxx`（TPROXY 重定向）
- `ct state INVALID drop`
- `ufw ... pkts bytes target ...` 全是 0
- mihomo / clash / xray 进程跑着

**适用代理软件**：所有用 Linux TUN + TPROXY 的透明代理（mihomo、Clash Meta、sing-box TUN 模式、xray tun2socks 等）。

---

## 核心经验

### 1. 透明代理 TUN 模式会破坏 conntrack 状态，触发防火墙的 INVALID drop

透明代理为了接管所有 TCP/UDP 流量，会写 nftables/iptables 规则把**所有匹配条件的包 TPROXY 重定向到代理进程**：

```nft
table inet mihomo {
    chain prerouting {
        type nat hook prerouting priority dstnat + 1;
        meta nfproto ipv4 meta l4proto tcp redirect to :42429
    }
}
```

**所有 IPv4 TCP 包**（包括从 LAN 来访问本机 22 端口的 SYN）都被重定向到代理进程。代理进程处理后再用 TUN 接口发回本机。

**关键问题**：**包头在代理 + TUN 回流的链路中被改写**，进入 `INPUT` 链时 conntrack 看到的**状态变成 INVALID**。

ufw / nftables 默认规则里有一条：

```nft
xt match "conntrack" counter packets 0 bytes 0 jump ufw-logging-deny
xt match "conntrack" counter packets 0 bytes 0 drop   # ← INVALID 状态被 drop
```

**INVALID 状态的包**走 `ufw-before-input` 链被这条规则**直接 drop**，**根本走不到你写的 allow 规则**。这就是为什么 `iptables -L ufw-user-input` 看到 22 端口 allow 规则存在但 counter 一直是 0——包在前面就被 drop 了。

### 2. `iptables -L` 显示的不一定是真的 nftables 规则

ufw 在新系统上用 **nftables 后端**（`/etc/ufw/ufw.conf` 里 `BACKEND=nftables`），但**内部走 iptables-nft 兼容层**。

**用 `iptables -L` 看到的规则**是**兼容层翻译出来的视图**，跟 `nft list ruleset` 看到的**真实 nftables 规则不完全一致**。在排查时务必用：

```bash
# 真实 nftables 规则（用这个！）
sudo nft list ruleset

# iptables 兼容层视图（参考用，可能与 nftables 不一致）
sudo iptables -L -n -v
```

如果 `iptables -L` 显示规则存在但 counter 0，**真正要看 `nft list chain ip filter ufw-user-input`**。

### 3. 解决：让代理排除 LAN 网段

**不要尝试改 ufw 规则去适应代理**——根本原因在代理。配置代理不接管 LAN 流量：

#### mihomo / Clash Meta

```yaml
tun:
  enable: true
  stack: system
  auto-route: true
  route-exclude-address:
    - 192.168.0.0/16
    - 10.0.0.0/8
    - 172.16.0.0/12
```

#### sing-box

```json
{
  "inbounds": [
    {
      "type": "tun",
      "inet4_address": "172.19.0.1/30",
      "auto_route": true,
      "strict_route": true,
      "exclude_protocol": ["dns"],
      "exclude_type": ["udp"]
    }
  ],
  "route": {
    "rules": [
      { "ip_cidr": ["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"], "action": "direct" }
    ]
  }
}
```

#### xray

不太适合 TUN 模式（通常用 tun2socks 配合），建议改用 system 模式或透明代理端口模式。

**重启代理后**，`nft list table inet mihomo`（或对应代理名）的 `prerouting` 链里会自动多一条：

```nft
ip daddr { 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 } ... return
```

目标在 LAN 网段的包**直接 return**（不被 TPROXY），conntrack 状态保持正常，ufw 的 22 端口 allow 规则就能命中了。

### 4. 加双重保险：systemd 单元 + iptables 直接插规则

**就算代理配置好了**，reboot 时序问题（代理可能比防火墙晚启动）也会让 SSH 短暂不通。**保险永远不嫌多**：

#### systemd 单元（开机自启加保险）

```bash
sudo tee /etc/systemd/system/ufw-safety-net.service > /dev/null <<'UNIT'
[Unit]
Description=SSH safety net for ufw + transparent proxy
After=ufw.service network-pre.target
Wants=ufw.service

[Service]
Type=oneshot
# 保险 1：ESTABLISHED/RELATED 接受（保老 SSH 连接）
ExecStart=/usr/sbin/iptables -I INPUT 1 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
# 保险 2：LAN 到 22 端口直接接受（深度防御）
ExecStart=/usr/sbin/iptables -I INPUT 1 -s 192.168.0.0/16 -p tcp --dport 22 -j ACCEPT
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl enable ufw-safety-net.service
```

**为什么两条都要**：
- **保险 1**：保护已建立的 SSH 连接（即使后续规则被改）
- **保险 2**：即使 mihomo 配置被改回不排除 LAN，**LAN 到 22 端口也直接通**——深度防御

**手动验证**：

```bash
sudo iptables -L INPUT -n -v --line-numbers
# 1   ACCEPT  tcp  --  192.168.0.0/16  ...  tcp dpt:22
# 2   ACCEPT  all  --  0.0.0.0/0       ...  ctstate RELATED,ESTABLISHED
# 3   ufw-before-logging-input ...
```

**注**：`ufw-safety-net` 是**自己起的名字**，不是工具名。

---

## 容易踩的坑

### 坑 1：`iptables -L` 看着对，但 `nft list ruleset` 是空

如果之前 `nft flush ruleset` 清空过 nftables，**`ufw disable` 不会自动恢复**（因为 ufw 只管理自己写过的状态）。结果：`iptables -L` 看着像有规则（兼容层会重建空结构），但 `nft list ruleset` 显示**完全空的**。

**验证**：

```bash
sudo nft list ruleset | wc -l   # 如果是 0 或个位数，可能 nftables 是空的
sudo ufw status                  # 看到 status active 但 nftables 是空 → ufw 状态混乱
```

**救回**：`sudo ufw disable && sudo ufw enable`（让 ufw 重新写规则）。

### 坑 2：`nft -f` 恢复失败，提示 `xtables compat expression`

omarchy 这种用 iptables-nft 兼容层的系统，**`nft -f` 不能直接加载 iptables-restore 格式的规则文件**。错误信息：

```
Error: unsupported xtables compat expression, use iptables-nft with this ruleset
```

**这是 iptables-nft 特有的语法**（`xt match "conntrack"`、`xt target "LOG"`），原生 `nft` 不认。

**救回**：

```bash
# 不要用 nft -f，用 iptables-restore
sudo iptables-restore < /etc/ufw/user.rules
# 或重启 ufw 让它自己重新写
sudo ufw disable && sudo ufw enable
```

### 坑 3：`ufw enable` 把 SSH 锁死，物理控制台救回

`ufw enable` 会**先警告** "may disrupt existing ssh connections"，但**默认 yes** 直接放行。如果你误操作 enable 之后 SSH 死了，**别慌**：

```bash
# 到物理控制台 / VNC / 云控制台串口
sudo ufw disable
```

SSH 老连接在 conntrack 里是 ESTABLISHED 状态，**ufw disable 不会立即 kill**（要等几秒），**够你重新连**。

### 坑 4：`mihomo stop` 后 SSH 出站包路由失败

mihomo 启用了**自定义路由表（2022）**接管出站流量。**`systemctl stop mihomo` 时如果路由表没正确清理**，本机出站包会找不到路由，**SSH 响应包发不出去**——SSH 立即断。

**救回**：

```bash
# 在 omarchy 物理终端
sudo systemctl restart mihomo       # 重启 mihomo 让它自己恢复路由
# 或
sudo ip route flush table 2022       # 清掉 mihomo 路由表
sudo ip rule del table 2022           # 删掉引用 mihomo 路由表的 rule
```

**预防**：在 `mihomo.service` 的 `[Unit]` 加 `Before=network.target`，让 mihomo 跟着网络栈走。

### 坑 5：保险 ESTABLISHED/RELATED accept 救不了新的 SYN 包

```bash
sudo iptables -I INPUT 1 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
# 这条只接受"已建立连接"的包，**新 SYN 包是 NEW 状态，不匹配**
```

**所以只有这条保险不够**，必须配合 `route-exclude-address` 或 `LAN → 22 端口 ACCEPT` 的深度防御规则。

---

## 决策总结

| 决策 | 原因 |
| --- | --- |
| 改代理配置（`route-exclude-address`）而非改 ufw | 根因在代理；改 ufw 是治标；改代理治本且不影响翻墙 |
| 双重保险（ESTABLISHED + LAN→22） | 代理配置可能被改/被重置；reboot 时序不可控；保险双保险 |
| 保险用 `iptables` 命令而非 nft 直接写 | iptables-nft 兼容层自动处理，避免 iptables / nftables 不一致 |
| 不在 `/etc/ufw/before.rules` 写保险 | nftables 后端下 before.rules 用 iptables-restore 格式，append 到 INPUT 末尾，不是最前面 |
| mihomo 路由表出站问题单独修 | 不是每次都会遇到；遇到再加 `Before=network.target` |

---

## 排查流程速查

```bash
# 1. 看真实 nftables 规则（不是 iptables -L）
sudo nft list ruleset

# 2. 看 INPUT 链的 policy + jump
sudo nft list chain ip filter INPUT

# 3. 看 ufw-user-input 链 22 端口规则 counter（正常应该有命中）
sudo nft list chain ip filter ufw-user-input | grep "dport 22"
# counter packets 0  → 包没到 ufw-user-input 链

# 4. 看 ufw-before-input 链每个规则命中数
sudo nft list chain ip filter ufw-before-input

# 5. 看代理的 mihomo 表（看 TPROXY 规则是不是排除 LAN）
sudo nft list table inet mihomo

# 6. 看代理日志，确认它是否拦截了入站包
journalctl -u mihomo --no-pager | grep "192.168"

# 7. 临时救回
sudo ufw disable                    # 恢复网络
sudo systemctl stop mihomo          # 看是不是 mihomo 的问题
sudo ufw enable                     # 重新打开防火墙
```

---

## 验证清单

```bash
# 1. 基础：22 端口 LAN 通
nc -vz <本机IP> 22 -w 5
# 期望：succeeded

# 2. ufw 自己的 allow 规则命中
sudo nft list chain ip filter ufw-user-input | grep "dport 22"
# 期望：counter packets > 0

# 3. 代理的 prerouting 链有 LAN 排除
sudo nft list table inet mihomo | grep "ip daddr"
# 期望：看到 192.168.0.0/16 等 LAN 段

# 4. 代理日志不出现 LAN → 22 端口的拦截
journalctl -u mihomo --no-pager | grep "192.168.0.*:22"
# 期望：空

# 5. 翻墙仍然工作
curl -s -o /dev/null -w "%{http_code}\n" --max-time 8 https://www.google.com
# 期望：200

# 6. reboot 后全部正常
sudo reboot
# reboot 后重跑 1-5
```
