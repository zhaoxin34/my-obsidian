# Omarchy 下修复 pi `fetch_content` 工具（mihomo fake-IP 冲突）

> 在 Omarchy + mihomo TUN + fake-IP 环境下，让 pi 的 `fetch_content` 工具正常工作。
> 2026-09-17 在 `omc-15` 上踩坑后总结，重点记录 **配置文件路径** 这个最容易错的点。

---

## 1. 问题现象

在 pi 里调用 `fetch_content("https://www.baidu.com")` 报 SSRF 拦截：

```
Error: Blocked internal address for www.baidu.com: 198.18.0.29.
This address is in 198.18.0.0/15, commonly used by TUN/fake-IP proxies.
If that matches your setup, configure ssrf.allowRanges with ["198.18.0.0/15"]
in web-search.json.
```

- 浏览器、curl 都能正常访问 baidu
- pi 的 `web_search` 工具正常（说明网络和代理都通）
- 只有 `fetch_content`（以及依赖它的工具）失败

---

## 2. 根本原因

**mihomo TUN 模式 + fake-IP** 与 **pi 内置的 SSRF 防护**互相冲突：

```
baidu.com  ──DNS──►  198.18.0.29   (mihomo fake-IP 段)
                              │
                              ▼
                pi SSRF 防护: "这是内网地址，拒绝"
                              ✗ 拦截
```

具体机制：

| 组件 | 行为 |
|---|---|
| **mihomo** (`/etc/mihomo/config.yaml`) | `enhanced-mode: fake-ip` + `tun.enable: true`，所有域名解析到 `198.18.0.0/16` |
| **pi (pi-web-access)** | 默认拒绝 `198.18.0.0/15` 段（因为这是 RFC 保留段，正常情况下是"假内网"） |
| **结果** | fetch 工具被错误拦截 |

确认 mihomo 是 fake-IP 模式：

```bash
grep -A 2 -E "enhanced-mode|fake-ip|tun:" /etc/mihomo/config.yaml
# 期望看到：
#     enhanced-mode: fake-ip
#     fake-ip-range: 198.18.0.1/16
# tun:
#     enable: true
```

---

## 3. 修复方案

### 3.1 创建配置文件

**路径必须是 `$XDG_CONFIG_HOME/pi/web-search.json`**，不是 `~/.pi/agent/web-search.json`（见 §5 坑 1）：

```bash
# 1. 先看 XDG_CONFIG_HOME 是啥
echo "XDG_CONFIG_HOME=$XDG_CONFIG_HOME"
# 期望：XDG_CONFIG_HOME=/home/zhaoxin/.config

# 2. 创建配置目录
mkdir -p "$XDG_CONFIG_HOME/pi"

# 3. 写入白名单
cat > "$XDG_CONFIG_HOME/pi/web-search.json" <<'JSON'
{
	"ssrf": {
		"allowRanges": ["198.18.0.0/15"]
	}
}
JSON
```

### 3.2 重启 pi 让其加载新配置

```bash
# 退出当前 pi 会话（Ctrl+D 或 /exit），然后重新启动 pi
pi
```

> ⚠️ **pi 会缓存这个配置，启动时读取一次**，mtime 变化在已运行的进程里不会重新加载。**必须重启。**

### 3.3 验证

```bash
# raw 模式直接看原始 HTML，能拿到就说明网络层通了
fetch_content("https://example.com", mode="raw")
# 期望：<!doctype html><html lang="en">...

fetch_content("https://www.baidu.com", mode="raw")
# 期望：<html>...location.replace... (百度的老 JS 跳转)
```

如果 raw 模式能拿到 HTML、readable 模式报 "Extracted content appears incomplete"，那**不是 bug**，是 pi 的 readability 提取器对极简页面的保守判断（example.com 太短，baidu 是 JS 重定向）。

---

## 4. 原理补充（可选）

相关源码：`~/.pi/agent/npm/node_modules/pi-web-access/ssrf-protection.ts`

```typescript
// 关键函数 loadSsrfConfig() —— 启动时只读一次配置
export function loadSsrfConfig(): SsrfConfig {
    const parsed = loadConfigRoot();  // 读 $XDG_CONFIG_HOME/pi/web-search.json
    if (!parsed) return { allowRanges: [], trustEnvProxy: false };
    const ssrf = parsed.ssrf;
    return {
        allowRanges: Array.isArray(ssrf?.allowRanges) ? ssrf.allowRanges : [],
        trustEnvProxy: ssrf?.trustEnvProxy === true,
    };
}

// 关键校验 —— allowRanges 会绕过 isBlockedIPv4 的内网检查
if (isInAllowedRange(normalized, ipVersion, allowRanges)) return;
```

`getWebSearchConfigDir()` 优先级（高→低）：

1. `$PI_CODING_AGENT_DIR`（环境变量，强制）
2. `$XDG_CONFIG_HOME/pi/web-search.json`（存在就用这个目录）
3. `~/.pi/web-search.json`（legacy，存在就用）
4. `~/.pi/agent`（fallback）

---

## 5. 坑提示

### 坑 1：配置文件路径看 XDG_CONFIG_HOME

**最容易踩的坑**。如果环境变量 `XDG_CONFIG_HOME=/home/zhaoxin/.config`，pi 会去找 `/home/zhaoxin/.config/pi/web-search.json`，**而不是**直觉上的 `~/.pi/agent/web-search.json`。

```bash
# 错误示范（我第一次就是这样，折腾半天才发现）
mv /home/zhaoxin/.pi/agent/web-search.json /home/zhaoxin/.config/pi/web-search.json

# 验证当前 pi 到底看哪个文件（运行时根据 XDG_CONFIG_HOME 推算）
echo "$XDG_CONFIG_HOME/pi/web-search.json"
```

### 坑 2：必须重启 pi 才能生效

pi 启动时把配置缓存到内存里（`cachedConfigRoot`），运行中改文件不会重新加载。**重启是必须的，不是可选。**

### 坑 3：readable 模式可能误报"内容不完整"

`mode: "readable"`（默认）对极简 HTML 会判定为 incomplete：

- example.com 只有一段话 → 报 incomplete
- baidu.com 是 JS 跳转 → 报 incomplete

**用 `mode: "raw"` 验证网络通不通**，别误以为没修复成功。

### 坑 4：mihomo 的 fake-IP 段不一定是 /15

我的 mihomo 配置里写的是 `198.18.0.1/16`，但 pi 默认拦截 `/15`（更宽，覆盖整个保留段）。`/15` 是更安全的白名单，**不需要改成 /16**，/15 已经覆盖了。

---

## 6. web_search 工具：跳过 curator 弹窗

### 6.1 现象

`web_search` 工具默认会**自动弹出网页**让你审核搜索结果（curator 流程），体验很差：

- 会开浏览器/TUI 一个 curator 页面
- 等久了不点还会报 `Search curation cancelled (stale)`
- 弹窗 ≠ AI 帮你总结，纯人肉看链接

### 6.2 三种 workflow 模式

`web_search` 工具的 `workflow` 参数控制 curator 行为：

| workflow | 行为 | 适用场景 |
|---|---|---|
| `summary-review`（默认） | 弹网页让你审核 + 自动生成 AI 摘要草稿 | 需要人工把关的高风险搜索 |
| **`auto-summary`（推荐）** | 直接 AI 生成摘要，**不开网页** | 日常大部分搜索 |
| `none` | 完全不 curator，直接返回原始结果 | 想自己看链接的情况 |

### 6.3 一次性用法（每次手动加参数）

```python
web_search(
    query="...",
    workflow="auto-summary",  # 跳过 curator
)
```

### 6.4 一劳永逸：全局设置默认 workflow

pi 提供 `/curator` 命令，配置会持久化到 `web-search.json` 的 `workflow` 字段：

```
/curator auto-summary   # 设成默认（推荐）
/curator off            # 等价于 /curator none
/curator on             # 恢复默认 summary-review
/curator                # 切换 on/off（默认 <-> none）
```

设置后，下次启动 pi 也生效。当前 `web-search.json` 配置：

```bash
cat ~/.config/pi/web-search.json
{
    "ssrf": { "allowRanges": ["198.18.0.0/15"] },
    "workflow": "auto-summary"
}
```

### 6.5 验证

```bash
# 当前会话里直接 web_search 一次，看还会不会弹网页
web_search(query="test", workflow="auto-summary")
# 期望：直接返回 AI 总结 + Sources 列表，不开 curator
```

---

## 7. 相关文档

- [Omarchy 安装 Mihomo (Clash Meta) 操作记录.md](./Omarchy%20安装%20Mihomo%20(Clash%20Meta)%20操作记录.md) —— 怎么装 mihomo + TUN
- pi 官方文档：`~/.local/share/mise/installs/pi/0.85.1/pi/docs/`