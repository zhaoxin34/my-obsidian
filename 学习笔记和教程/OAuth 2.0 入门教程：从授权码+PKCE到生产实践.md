---
title: "OAuth 2.0 入门教程：从授权码 + PKCE 到生产实践"
description: "从'为什么不能把密码给第三方'出发，讲清 OAuth 2.0 的角色、授权码 + PKCE 流程、令牌三分、令牌注入与 CSRF 防护，并给出一套可落地的 SPA + 后端架构设计"
tags: [OAuth2, PKCE, OIDC, 安全, Web, 后端, 教程]
---

# OAuth 2.0 入门教程：从授权码 + PKCE 到生产实践

> 面向：有一定 Web 开发基础（会写前端 + HTTP 接口），但对 OAuth 2.0 只有"用过登录按钮"的模糊印象。
> 预计耗时：40 分钟读完 + 20 分钟做最后的自测题。

## 你好，我是你的老师

先说结论：**OAuth 2.0 不是"登录协议"，而是"委托授权协议"**。

如果你现在脑子里只有一个模糊的印象——"点个'用 Google 登录'，然后就进去了"——那这篇教程要帮你重建的是它背后的**完整因果链**：为什么不能把密码给第三方、四个角色分别在干什么、那个看起来多余的"授权码"为什么必须绕一圈、以及在真实生产里到底该怎么存 token、怎么防攻击。

读完之后，你应该能独立回答这类问题：

> "我们 App 要读用户的 Google Drive 文件，请设计完整方案：谁发请求、token 放哪、怎么续期、怎么退出、怎么防 CSRF。"

---

## 目录

1. [OAuth 2.0 要解决什么问题](#1-oauth-20-要解决什么问题)
2. [四个角色与两种 token](#2-四个角色与两种-token)
3. [核心流程：授权码模式](#3-核心流程授权码模式)
4. [PKCE：没有 client_secret 的客户端怎么办](#4-pkce没有-client_secret-的客户端怎么办)
5. [四个防护零件](#5-四个防护零件)
6. [令牌三分：access / refresh / id](#6-令牌三分access--refresh--id)
7. [五种授权模式（grant type）](#7-五种授权模式grant-type)
8. [实战设计：SPA + 自建后端 + Google Drive](#8-实战设计spa--自建后端--google-drive)
9. [存储决策表：token 该放哪](#9-存储决策表token-该放哪)
10. [续期与撤销](#10-续期与撤销)
11. [攻击面清单与防护](#11-攻击面清单与防护)
12. [常见误解速查](#12-常见误解速查)
13. [自测题](#13-自测题)
14. [延伸学习](#14-延伸学习)

---

## 1. OAuth 2.0 要解决什么问题

### 1.1 没有 OAuth 的年代：把密码交出去

最早的"第三方登录"做法很粗暴：

```
你  →  输入密码给 记账 App
记账 App  →  拿着你的 Google 密码去登录 Google
```

问题立刻暴露：

| 问题 | 后果 |
|---|---|
| 第三方拿到了**你的密码** | 它能直接登录你的账号，能看邮件、云盘、支付 |
| 密码**无法降权** | 记账 App 只需要读一个头像，却拿到了整把万能钥匙 |
| 密码**无法撤销** | 你改完密码，第三方手里的旧密码还能继续用 |
| 密码**无法审计** | 第三方登录失败多少次你都不知道 |

### 1.2 OAuth 的思路：用受限凭证代替密码

OAuth 2.0 的核心重构是**把"身份凭证"和"授权凭证"分开**：

- 用户密码 → 只在**用户和身份提供方**之间流动，第三方**永远看不到**；
- 第三方拿到 → 一个 **access token（访问令牌）**：受限（scope）、限时、可撤销的凭证；
- 用户 → 始终**可以撤销**，且能**限定范围**。

一句话记法：

> **OAuth 2.0 用"受限的、可撤销的、临时的"令牌，替代了"永不过期的、全能的"密码。**

### 1.3 它不解决什么

| 问题 | 由谁解决 |
|---|---|
| 这个请求的发出者**是谁**（认证） | **OIDC**（OpenID Connect）——构建在 OAuth 2.0 之上的一层 |
| 这个 token **有没有权限**做这个操作（授权） | OAuth 2.0 本身 + Resource Server 的校验 |

"用 Google 登录"这个按钮，背后其实是 **OAuth 2.0（拿授权）+ OIDC（拿身份）** 两件事。OAuth 本身**不告诉你"用户是谁"**。

---

## 2. 四个角色与两种 token

### 2.1 四个角色

| 角色 | 英文 | 含义 | 例子 |
|---|---|---|---|
| 资源所有者 | Resource Owner | 数据的归属者，通常是用户 | 你 |
| 客户端 | Client | 想访问数据的第三方应用 | 某个记账 App |
| 授权服务器 | Authorization Server | **签发** token 的服务 | Google 账号中心 |
| 资源服务器 | Resource Server | 存数据、**校验** token 的 API | Google Drive API |

**关键认知：授权服务器和资源服务器可以是同一台机器，也可以完全分开。**

Google 就是同一个（accounts.google.com 同时签发并校验 token）；自建系统通常也合一；而企业内网常见"统一认证中心 + 多个独立 API 服务"的分立架构。

> 区分它们的唯一标准不是"是不是同一个域名"，而是：
> **谁签发 token（AS），谁校验并使用 token（RS）。**

### 2.2 三方与两方的边界

```
        ┌──────────────────────────┐
        │      Authorization        │
  你 ──▶│        Server            │──▶ 签发 access_token
        │  (登录 / 同意 / 签发)     │
        └──────────────────────────┘
                 │
                 │ access_token
                 ▼
        ┌──────────────────────────┐
        │      Resource Server      │◀── 你(作为客户端)带 token 来调
        │        (数据 API)          │
        └──────────────────────────┘
```

---

## 3. 核心流程：授权码模式

**Authorization Code Grant（授权码模式）+ PKCE** 是当今绝对主流的流程。你在微信、Google、GitHub、移动 App 上见到的登录，几乎都是它。

### 3.1 五步走

```
浏览器/App        你的后端            授权服务器 AS        资源服务器 RS
     │                │                    │                    │
     │ 1.跳转 /authorize│                    │                    │
     │  ?client_id=    │                    │                    │
     │  &redirect_uri= │                    │                    │
     │  &scope=        │                    │                    │
     │  &response_type=│                    │                    │
     │  &state=        │                    │                    │
     │  &code_challenge│                    │                    │
     │────────────────┼───────────────────▶│                    │
     │                │                    │ 2.用户登录+同意授权  │
     │                │                    │                    │
     │                │◀── 3.redirect_uri?code=xxx&state=yyy ───│
     │                │                    │                    │
     │ 4.POST /token {code, code_verifier, client_secret}       │
     │────────────────┼───────────────────▶│                    │
     │                │◀── 5.{access_token, refresh_token, id_token}│
     │                │                    │                    │
     │                │ 6.GET /drive/files  Authorization: Bearer xxx
     │                │────────────────────┼───────────────────▶│
```

逐步说清楚：

**第 1 步：引导授权**
客户端把浏览器重定向到授权服务器的 `/authorize` 端点，带上：
- `client_id`：应用标识
- `redirect_uri`：授权完成后回到哪里（**必须预先注册、精确匹配**）
- `response_type=code`：声明"我要走授权码模式"
- `scope`：想申请哪些权限（如 `drive.readonly`）
- `state`：随机串，防 CSRF
- `code_challenge`：PKCE 的挑战值（见第 4 节）

**第 2 步：用户登录与同意**
用户**在授权服务器自己的页面**上输入密码，AS 展示"XX 应用想访问你的以下权限"，用户点同意。
👉 **密码永远不离开 AS。** 这是 OAuth 与"密码模式"的根本区别。

**第 3 步：重定向回调**
AS 重定向到 `redirect_uri?code=xxxx&state=yyy`。
注意：**返回的是授权码，不是 token。**

**第 4 步：后端兑换 token**
客户端后端向 AS 的 `/token` 端点发起**服务器到服务器**的请求：
```
POST /token
grant_type=authorization_code
code=<授权码>
client_id=..&client_secret=..
code_verifier=<原始 verifier>   # PKCE 时需要
```
**只有持有 client_secret（或 verifier）的一方才能兑换成功。**

**第 5 步：访问资源**
```
GET /drive/files
Authorization: Bearer <access_token>
```

### 3.2 为什么要绕这一圈？三个"为什么"

这是初学者最容易卡住的地方，也是面试高频问。

**❓ 为什么第 3 步不直接返回 access_token？**

因为第 3 步要**经过用户浏览器**（重定向），这条链路上有：
- 浏览器历史记录
- URL 会被记录在服务器日志、代理日志
- `Referer` 头可能被带到下游
- 跳转链上的任何中间方

授权码模式用"**一次性 + 几十秒失效 + 只能用后端兑换**"把这个暴露窗口压到最小。code 本身泄露了也没用——没有 secret/verifier 就换不出 token。

**❓ 为什么 `redirect_uri` 必须精确匹配？**

防**授权码拦截攻击**：如果 AS 允许任意 redirect_uri，攻击者可以注册一个自己的地址，把 code 引到他那里。精确匹配（协议+主机+端口+路径全等）保证 code 只回到你登记过的地址。

**❓ 为什么要有 `state`？**

防 **CSRF / 令牌注入**。`state` 是客户端生成并在发起授权时保存在 session 里的随机串，回调时比对：
- 不一致 → 说明这个回调不是本次流程发起的，丢弃。
- 这挡住了"攻击者构造授权链接诱导你点击，从而把**攻击者的 token** 注入你的应用"。

---

## 4. PKCE：没有 client_secret 的客户端怎么办

### 4.1 问题起源

`client_secret` 的作用是**证明"这个请求来自真正的客户端后端，而不是冒充者"**。

但这些客户端**没有可信后端**，或者**藏不住 secret**：

| 客户端 | 为什么藏不住 |
|---|---|
| 浏览器 SPA / 单页应用 | JS 代码完全公开，开发者工具一打开就看见 |
| 移动 App | 二进制可被逆向提取 |
| 桌面/CLI 应用 | 本地文件可读 |

如果让它们硬塞一个 secret，那这个 secret 就是公开的，等于没有保护。

### 4.2 解法：用"原像证明"替代"共享秘密"

PKCE（Proof Key for Code Exchange, RFC 7636）让客户端用一对随机数自证身份：

**发起授权前**（客户端本地）：
```
code_verifier  = 43~128 位随机字符串（客户端自己保密保存）
code_challenge = BASE64URL(SHA256(code_verifier))   # 或 plain 模式直接用 verifier
```

**第 1 步授权请求**：只发送 `code_challenge=SHA256(verifier)`，**不发 verifier 本体**。

**AS 侧**：把 `code_challenge` 和授权码一起存起来。

**第 4 步兑换**：
```
POST /token
  code=xxxx
  code_verifier=<原始 verifier>       ← 出示原像
```

**AS 校验**：`SHA256(收到的 verifier) == 存的 code_challenge`？相等才发 token。

### 4.3 为什么这就安全？

攻击者即使截获了 code（甚至连 code_challenge 都看到了），他**只有哈希，没有原像**——**算不出**能通过校验的 verifier，所以换不出 token。

> 一句话总结：**PKCE 把"证明身份"从"共享一个秘密"改成了"证明我能出示某个只有我事先知道的随机数的原像"。**
> 因此浏览器端**不需要藏任何东西**——verifier 存在内存里即可。

### 4.4 现状

- PKCE 已是 **OAuth 2.1 的强制要求**（所有公共客户端必须使用）。
- **移动端 App 也应使用 PKCE**（不只前端）。
- 也支持 `plain` 模式（code_challenge = verifier 明文），仅在 channel 确实安全时使用。

---

## 5. 四个防护零件

生产环境必配，作用各不相同，**别混淆**：

| 零件 | 配置位置 | 防的攻击 | 缺失后果 |
|---|---|---|---|
| `redirect_uri` 精确匹配 | AS 端注册 | 授权码被发送到攻击者地址 | code 泄漏 → token 泄漏 |
| `state` 随机串 | 客户端发起时 + 回调校验 | CSRF / 令牌注入 / 会话置换 | 攻击者可把自己的 token 注入你的应用 |
| PKCE (`code_verifier`) | 客户端生成 + 兑换时出示 | 授权码截获后盗换 | 移动端/SPA 场景下无法自保 |
| `iss` / 授权服务器校验 | 客户端回调时校验 | AS mix-up 攻击（多 AS 场景） | token 被别的 AS 的 token 替换 |

### 5.1 令牌注入攻击：完整链条（重点）

这是"为什么 OAuth 要支持多个第三方 App"这个问题的落点。假设你用**隐式模式**（`response_type=token`）且没有校验 `state` / `iss`：

```
1. 攻击者用自己的账号，在自己的 App 里完成授权 → 拿到 token_A
2. 攻击者构造链接：
   /authorize?client_id=受害App&redirect_uri=受害App/callback
                &response_type=token&state=xxx
   诱导受害者点击
3. AS 把 token_A 注入受害者浏览器中受害 App 的回调页
4. 受害 App 没校验 state/iss → 以为"用户刚授权成功"，把 token_A 存下
5. 受害者之后在 App 里的所有操作，都写进了【攻击者的账号】
6. 攻击者随后用 token_A 读取这些数据
```

这叫 **token injection / session swapping（会话置换、账号预劫持）**。

**现代方案（授权码 + PKCE + state + iss 校验）逐条堵死了它**：
- 有 `state` → 第 3 步回调被拒；
- 有 PKCE → 攻击者的 code 换不出 token；
- 授权码在服务端兑换 → token 压根不下发到浏览器 URL。

---

## 6. 令牌三分：access / refresh / id

初学者最容易搞混这三个。**分清它们是面试高频点。**

| 令牌 | 代表什么 | 有效期 | 给谁用 | 关键约束 |
|---|---|---|---|---|
| **access_token** | **授权**（你能做什么） | 分钟~小时 | 客户端 → Resource Server | 每次调 API 都要带；泄露即被冒用 |
| **refresh_token** | **续期资格** | 天~月 | 客户端**后端** → AS | **不能直接调 API**；只在后端；可轮换 |
| **id_token** | **身份**（你是谁） | 与 access 类似 | 客户端 → 客户端自己 | **OIDC 专有，不能用来调 API** |

### 6.1 id_token 的常见误用

```js
// ❌ 错误：用 id_token 调 API
fetch('/api/drive/files', { headers: { Authorization: `Bearer ${id_token}` } })

// ✅ 正确：id_token 用来"确认登录了谁"，调 API 用 access_token
const claims = JSON.parse(atob(id_token.split('.')[1]))  // 看 sub / email 等
```

> 记忆法：**access_token 是"门票"（进 API），id_token 是"身份证"（证明你是谁）。**
> 拿着身份证冒充门票进 API，是初学者最典型的线上事故。

### 6.2 refresh token 的三条铁律

1. **只存在后端**（绝不放前端、绝不进 localStorage）；
2. **加密存储**（数据库/KMS），它的价值 ≈ 你的账号；
3. **轮换（rotation）**：每次使用都换新的，旧的立即作废；配合"检测到旧 token 被复用 → 撤销整个家族（token family）"，可发现 token 窃取。

---

## 7. 五种授权模式（grant type）

**先纠正一个常见混淆**：`grant_type` **不是** token 的类型，而是"**这次请求按哪种流程换 token**"的标识参数。

| grant_type | 流程 | 今天还该用吗 |
|---|---|---|
| `authorization_code` | 用授权码换 token | ✅ **默认选它**（必配 PKCE） |
| `refresh_token` | 用 refresh token 换新 access token | ✅ 续期标准做法 |
| `client_credentials` | 服务间调用，无用户在场 | ✅ 微服务 / 后端调后端 |
| `implicit` | URL fragment 直接发 token | ❌ **OAuth 2.1 已废弃** |
| `password` | 用户名密码直接换 token | ❌ 第三方禁用；仅第一方高度可信场景 |

### 7.1 为什么隐式模式被废弃

它同时缺少三样东西：

1. **没有客户端认证** —— AS 不知道对面是不是真客户端。而 OAuth 的前提就是"同一个 AS 下有成百上千个第三方 App"，所以**恶意 App 也能拿到有效 token**；
2. **token 落在浏览器里** —— URL fragment 明晃晃摆在地址栏，页面里任何脚本（第三方 SDK、广告、注入脚本）都能读到；
3. **没有 state / iss 校验的保障** —— 直接导致第 5.1 节的令牌注入攻击。

### 7.2 scope 怎么给

`scope` 描述"**要访问哪些资源/操作**"，与 grant_type 是两回事。

原则：**按最小权限申请**。

```
drive.readonly        # 读所有文件
drive.file            # 只读写"本应用创建的文件"（更窄，推荐）
drive.metadata.readonly
```

Google Docs / Sheets / Slides 还有各自的细粒度 scope（`documents.readonly` 等）。**别一次性要 `drive` 全权**——用户看到一大串权限会直接拒绝，而且一旦泄漏损失更大。

---

## 8. 实战设计：SPA + 自建后端 + Google Drive

现在把前面所有点串成一个**真实可落地的方案**。

### 8.1 需求

- React SPA（纯前端，无后端渲染）
- 自建后端 API（业务 API，需要访问用户的 Google Drive 文件）
- 用户用 Google 登录

### 8.2 完整时序

```
  SPA (浏览器)              你的后端                 Google AS          Google Drive API
     │                         │                        │                     │
     │ 1.生成 code_verifier     │                        │                     │
     │  计算 code_challenge     │                        │                     │
     │  GET /api/google/login  │                        │                     │
     │────────────────────────▶│ 生成 state,存 session │                     │
     │◀── 302 /authorize?...&  │                        │                     │
     │     state&code_challenge │                        │                     │
     │──────────────────────────────────────────────────▶│                     │
     │                         │              2.用户登录+同意                 │
     │                         │                        │                     │
     │                         │◀── 302 /callback?code&state (redirect_uri=你的后端)
     │                         │                        │                     │
     │ 3.GET /api/me            │                        │                     │
     │────────────────────────▶│ 校验 state ✓          │                     │
     │                         │ POST /token            │                     │
     │                         │  code+verifier+secret  │                     │
     │                         │───────────────────────▶│                     │
     │                         │◀─ access/refresh/id ───│                     │
     │                         │ 存 refresh(加密)       │                     │
     │                         │ 建 session,Set-Cookie  │                     │
     │◀─ 200 {user} + sid cookie│                        │                     │
     │                         │                        │                     │
     │ 4.GET /api/files         │                        │                     │
     │  (带 sid cookie)         │ access 过期?→refresh  │                     │
     │────────────────────────▶│───────────────────────▶│ (换新 token)       │
     │                         │ Authorization: Bearer ──────────────────────▶│
     │◀─ 200 文件列表           │◀────────────────────────────────────────────┘
```

### 8.3 关键设计决策

**决策 1：`redirect_uri` 指向你的后端**（不是 SPA 页面）
→ code 从浏览器出来就直接进你的服务器，**浏览器全程不接触 code**，攻击面最小。

**决策 2：SPA 持有 `code_verifier`，后端持有 `client_secret`**
→ 后端兑换时同时提交两者。SPA 不需要 secret（它也没有），但持有 verifier（PKCE 的"客户端实例"证明）。

**决策 3：Google 的 token 一律不下发前端**
→ access token、refresh token 只在你的后端。前端只有"你自己的 API 的会话凭证"。

**决策 4：一次授权，两枚 token，两个信任边界**

```
┌─ 边界一：Google ↔ 你的后端 ─────────────┐
│  Google access_token / refresh_token      │  只在后端内存 + 加密存储
└───────────────────────────────────────────┘
┌─ 边界二：浏览器 ↔ 你的后端 ─────────────┐
│  你自己的会话 cookie (httpOnly + SameSite) │  只在浏览器
└───────────────────────────────────────────┘
```

### 8.4 参考代码

**前端（SPA）**

```js
// 生成 PKCE 参数
async function pkce() {
  const verifier = base64url(crypto.getRandomValues(new Uint8Array(32)))
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier))
  return { verifier, challenge: base64url(new Uint8Array(digest)) }
}

// 发起登录：注意 verifier 存在内存（sessionStorage 也可，但内存更安全）
async function login() {
  const { verifier, challenge } = await pkce()
  sessionStorage.setItem('pkce_verifier', verifier)   // 刷新后仍在，够用

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: GOOGLE_CLIENT_ID,
    redirect_uri: `${API_BASE}/auth/google/callback`,
    scope: 'openid email https://www.googleapis.com/auth/drive.readonly',
    state: crypto.randomUUID(),
    code_challenge: challenge,
    code_challenge_method: 'S256',
    access_type: 'offline',       // 关键：要 refresh_token
    prompt: 'consent',            // 某些场景需要重新同意才发 refresh_token
  })
  window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`
}
```

**后端（Node.js / Express 风格伪码）**

```js
// 发起：生成 state 存 session，然后 302 到 Google
app.get('/auth/google/login', (req, res) => {
  const state = crypto.randomUUID()
  req.session.oauthState = state
  req.session.verifier = req.query.verifier   // 由 SPA 传来（纯前端时）
  res.redirect(`https://accounts.google.com/o/oauth2/v2/auth?...&state=${state}`)
})

// 回调：校验 state → 兑换 token → 建会话
app.get('/auth/google/callback', async (req, res) => {
  const { code, state } = req.query
  if (!state || state !== req.session.oauthState) {
    return res.status(400).send('invalid state')      // 防 CSRF / 令牌注入
  }
  delete req.session.oauthState

  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    code,
    client_id: GOOGLE_CLIENT_ID,
    client_secret: GOOGLE_CLIENT_SECRET,   // 后端才有的秘密
    code_verifier: req.session.verifier,   // SPA 生成的原像
    redirect_uri: `${API_BASE}/auth/google/callback`,
  })
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
  const tokens = await r.json()

  // refresh_token 加密后落库；access_token 只存内存/短缓存
  await saveRefreshToken(req.userId, encrypt(tokens.refresh_token))

  // 建自己的会话，发 httpOnly cookie
  req.session.sid = crypto.randomUUID()
  res.cookie('sid', req.session.sid, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 30 * 24 * 3600 * 1000,   // 持久 cookie：关浏览器也保持登录
  })
  res.redirect('https://app.example.com/')
})

// 用 token 调 Google：access 过期就静默用 refresh 换
async function googleAccessToken(userId) {
  if (cache.has(userId)) return cache.get(userId)
  const refresh = decrypt(await loadRefreshToken(userId))
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',       // ← 续期用这个，和授权码是不同流程
      refresh_token: refresh,
      client_id: GOOGLE_CLIENT_ID,
      client_secret: GOOGLE_CLIENT_SECRET,
    }),
  })
  const t = await r.json()
  cache.set(userId, t.access_token, { ttl: t.expires_in })
  return t.access_token
}
```

> ⚠️ **关于 `redirect_uri` 的一点实践提醒**：Google 对 SPA 的 redirect_uri 有要求（必须是 https、已预先登记，不能是 `localhost` 之外的随意地址）。后端回调则通常用普通 Web 应用类型客户端。**不同客户端类型（Web / SPA / Desktop）要在 Google Cloud Console 里分开注册。**

---

## 9. 存储决策表：token 该放哪

很多教程只说"别放前端"，但没说清"那放哪、怎么放"。用这张表：

| 凭证 | 存哪 | 怎么存 | 为什么 |
|---|---|---|---|
| **第三方 access_token**（如 Google） | 后端 | 内存 + 短 TTL 缓存 | 前端要调 API 就必然下发前端 → XSS 风险；且它权限大 |
| **refresh_token** | 后端 | **加密**落库 / KMS | 长期有效，泄漏 = 账号长期沦陷 |
| **你自己的会话凭证** | 浏览器 | **`httpOnly` + `secure` + `SameSite` cookie** | JS 读不到 → 抗 XSS 窃取；`SameSite` → 抗 CSRF |
| （对比）你自己的会话凭证 | 浏览器 | `localStorage` | ❌ XSS 一读一个准，不推荐 |
| **PKCE code_verifier** | 客户端内存 | `sessionStorage` 兜底 | 公开客户端唯一要守的秘密；短命即可 |

### 9.1 cookie 的两种形态

| 类型 | 写法 | 行为 |
|---|---|---|
| 会话 cookie（默认） | 不设 `Max-Age` / `Expires` | **关掉浏览器就消失** |
| 持久 cookie | `Max-Age=2592000` | 关掉浏览器仍在（30 天保持登录） |

> "关掉浏览器回来还登录着" → 需要**持久 cookie**（设置 `Max-Age`）。这是新手最常配错的一项。

### 9.2 两种会话凭证方案的取舍

| 方案 | 优点 | 代价 |
|---|---|---|
| **httpOnly cookie** | XSS 读不到；体验好（自动携带） | 需防 CSRF（SameSite + CSRF token + Origin 校验） |
| **`Authorization: Bearer` 头** | **天然免疫 CSRF**（浏览器不会自动附带头） | JS 能读到 → 需防 XSS；需自己实现 token 刷新 |

**二选一，别混用。** 混用（cookie 和头都带）通常是最危险的组合。

---

## 10. 续期与撤销

### 10.1 续期（前端完全无感）

```
前端调你的 API
   → 后端发现 Google access_token 已过期
   → 后端 POST /token  { grant_type: refresh_token, refresh_token, client_id, client_secret }
   → AS 返回新 access_token（可能连新的 refresh_token 一起给 → 触发轮换）
   → 后端更新缓存，继续调用
```

**前端不需要知道这件事发生。** 这是"refresh token 只在后端"的最大好处。

**轮换（rotation）注意**：AS 返回新的 refresh_token 时，务必把旧的立即作废并更新存储；下次如果收到**已作废的旧 refresh_token**，说明有第三方在盗用 → **撤销整个 token 家族**并让用户重新登录。

### 10.2 撤销（退出登录）

只删本地 session 是**不够的**——那只是让你本地看起来登出了，Google 侧的授权还活着，别人偷到的 refresh token 照样能用。

完整链路：

```
前端 POST /logout（带 sid cookie）
   ↓
后端 ① 删除/失效自己的 session
   ↓
后端 ② 调 RFC 7009 撤销端点：
      POST https://oauth2.googleapis.com/revoke
      body: token=<refresh_token>&client_id=..&client_secret=..
   ↓
AS：refresh_token 立即作废，且由它派生的所有 access_token 一并作废
   ↓
后端 ③ Set-Cookie: sid=; Max-Age=0  → 顺手清掉前端 cookie
```

> **撤销请求本身必须带 client 凭证**，否则任何人都能来撤销别人的 token（拒绝服务）。

**"解除授权"与"退出登录"是两件事：**
- 退出登录 → 撤销 token（上面的流程）；
- 用户在 Google 账号设置里"撤销第三方 App 授权" → AS 主动通知 RS 失效 token（依赖 **revocation endpoint** 或 **event notification / push**）。

---

## 11. 攻击面清单与防护

| 攻击 | 手法 | 防护 |
|---|---|---|
| **CSRF 登录 / 令牌注入** | 诱导用户点构造的授权链接，把攻击者的 token 注入你的应用 | `state` 随机串 + 回调校验；PKCE |
| **授权码拦截** | 从 URL / 日志 / Referer 捞到 code | 短效 + 一次性 code；PKCE；精确 `redirect_uri` |
| **XSS 窃取 token** | 同源注入脚本读 localStorage / DOM | httpOnly cookie；token 放内存；严格 CSP |
| **CSRF 写操作** | 别的网站诱导浏览器带 cookie 发 POST | `SameSite=Lax/Strict` + CSRF token + `Origin` 校验；或改用 Bearer 头 |
| **开放重定向** | 回调后按 query 参数跳转到攻击者站点 | 回调只允许跳**硬编码**白名单地址，绝不直接用 query 里的 url |
| **refresh token 长期泄漏** | 库被拖 / 前端被 XSS | 只存后端 + 加密 + 轮换 + 复用检测 |
| **令牌重放（换设备）** | token 被抄到另一台机器使用 | **Sender-constrained token**：**DPoP** 或 **mTLS**，把 token 绑定到客户端密钥对 |
| **越权 scope** | 应用申请了超出需要的权限 | 最小权限 scope；服务端二次校验 scope；Token Introspection |
| **AS mix-up** | 多授权服务器环境里 token 被别的 AS 替换 | 回调校验 `iss` 参数 / 用不同端口或不同参数命名空间隔离 |
| **重放 refresh token** | 旧的 refresh token 被盗用 | rotation + 家族撤销 |

### 11.1 DPoP：现代的"防重放"答案

bearer token 的本质弱点是：**谁拿着谁就能用**。DPoP（Demonstrating Proof of Possession）让客户端在每次请求时用自己持有的私钥签名请求，token 与该密钥对绑定：

- token 被偷走 → 攻击者没有私钥 → **签不出合法 DPoP 证明** → 请求被拒；
- 比 Bearer 安全得多，是 OAuth 2.1 生态的重要方向。

（同类方案：**mTLS**，用双向 TLS 绑定客户端证书。）

---

## 12. 常见误解速查

| ❌ 误解 | ✅ 事实 |
|---|---|
| grant_type 是 token 的类型 | 它是"换 token 的流程标识"（authorization_code / refresh_token / client_credentials…） |
| id_token 可以调 API | ❌ 它是身份证（OIDC），access_token 才是门票 |
| 有了 PKCE 就不用防 XSS | PKCE 防的是授权码截获，XSS 是另一条线 |
| 有了 httpOnly cookie 就不用防 CSRF | 恰恰相反，cookie 会自动携带，**正因如此**才必须防 CSRF |
| 退出登录就是删本地 session | 必须同时撤销 refresh token（RFC 7009） |
| token 加密了就安全 | 还要防 XSS 读取、refresh token 不下发前端、轮换 |
| 隐式模式更简单所以更好 | 已废弃：无客户端认证 + token 暴露浏览器 + 令牌注入 |
| scope 越多越方便 | 最小权限原则，用户拒绝率和使用风险都更低 |
| 第三方登录 = OAuth | 登录 = OAuth（授权）+ **OIDC**（认证） |
| refresh token 也放 localStorage | 它长期有效，等于账号的钥匙，只能在后端 |
| 用 password grant 最省事 | 第三方一律禁止；密码一旦离开 AS，OAuth 的意义就没了 |

---

## 13. 自测题

> 建议先自己答，再对照提示。想清楚再往下看答案。

**Q1.** 为什么第 3 步的重定向不能直接返回 access_token？给出至少两个具体风险。

<details><summary>答案</summary>

浏览器跳转链路上：URL 会进浏览器历史、被服务器/代理记录、通过 `Referer` 头泄露、出现在截图/剪贴板/聊天记录里；跳转链上的任何中间方都能看到。授权码方案用"一次性 + 几十秒失效 + 只有后端能兑换"把暴露窗口压到最小。

</details>

**Q2.** 纯前端 SPA 没有可信后端，怎么安全地走授权码模式？

<details><summary>答案</summary>

用 **PKCE**：SPA 本地生成 `code_verifier`，只把 `SHA256(verifier)` 作为 `code_challenge` 发出去；兑换时出示 verifier 原像。AS 校验通过才发 token。这样浏览器端无需保存任何秘密（`client_secret` 也不需要）。

</details>

**Q3.** 一次授权会产生几枚 token？分别属于哪个信任边界？

<details><summary>答案</summary>

对你的业务而言是**两枚**：第三方 AS 签发的 access/refresh token（属于"第三方 ↔ 你的后端"边界），和你自己签发的会话凭证（属于"浏览器 ↔ 你的后端"边界）。若启用 OIDC 还有第三枚 id_token（属于"第三方 AS ↔ 客户端"，只用于证明身份，不能调 API）。

</details>

**Q4.** 你的后端拿到 Google refresh_token 后，前端调你的 API 写操作时需要带 code + code_verifier 吗？

<details><summary>答案</summary>

**不需要。** code + verifier 只在首次授权时用一次。日常调用带的是**你自己的会话凭证**。后端若发现 Google access_token 过期，用 `grant_type=refresh_token` 静默换新，用户无感。

</details>

**Q5.** 完整描述"用户点退出"时系统要做的事。

<details><summary>答案</summary>

前端 POST /logout → 后端失效本地 session → 后端调 RFC 7009 撤销端点撤销 Google refresh_token（连带作废其派生的 access token）→ 清掉前端 cookie（`Max-Age=0`）。只做第一步是不完整的。

</details>

**Q6.** 你的 API 用 httpOnly cookie 做会话，怎么防 CSRF？

<details><summary>答案</summary>

三件套：`SameSite=Lax/Strict`（跨站 POST 不带 cookie）+ **CSRF token**（自定义头 `X-CSRF-Token`，跨站页面读不到）+ **校验 `Origin`/`Referer`**。（若改用 `Authorization: Bearer` 头，则天然免疫 CSRF，但需自己防 XSS。）

</details>

---

## 14. 延伸学习

| 主题 | 关键内容 |
|---|---|
| **OIDC**（RFC / OpenID Connect Core 1.0） | id_token 的 JWT 结构、`nonce`、`iss`/`aud` 校验、Discovery 文档（`/.well-known/openid-configuration`）、`jwks_uri` |
| **JWT 与令牌自校验** | 结构 `header.payload.signature`、签名 vs 加密、为什么敏感信息不能放 payload（base64 不是加密）、密钥轮换 |
| **RFC 6749 / 6750 / 7009 / 7636** | OAuth 2.0 核心框架 / Bearer Token 用法 / 撤销 / PKCE —— 规范原文最权威 |
| **OAuth 2.1 与 Security BCP (RFC 9700)** | 现状与未来：去掉隐式、PKCE 强制、精确 redirect_uri 匹配成为硬要求 |
| **DPoP (RFC 9449)** | sender-constrained token，防重放 |
| **Token Introspection (RFC 7662)** | 服务端向 AS 查询 token 状态与 scope |
| **设备授权流 (RFC 8628)** | 电视/IoT 等输入受限设备 |
| **实测练习** | 用 curl / Postman 跑通授权码 + PKCE 全流程（自己实现 `/authorize`、`/token`、`/resource` 三个端点） |

---

## 一页速查表

```
OAuth 2.0 = 委托授权协议（认证请用 OIDC）
核心替换：用受限/限时/可撤销的 token 代替第三方拿到密码

四角色：Resource Owner | Client | Authorization Server | Resource Server
        AS = 签发方，RS = 消费方（可能是同一台机器）

主流程（授权码 + PKCE）：
  /authorize?client_id&redirect_uri&response_type=code&scope&state&code_challenge
  → 用户在 AS 登录并同意（密码不离开 AS）
  → redirect_uri?code=xxx&state=yyy       ← 不是 token！
  → 后端 POST /token {code, code_verifier, client_secret}  grant_type=authorization_code
  → {access_token, refresh_token, id_token}
  → Authorization: Bearer <access_token> 调 RS

四防护：redirect_uri 精确匹配 | state | PKCE | iss 校验
令牌三分：access(授权,短期) | refresh(续期,长期,仅后端) | id(身份,OIDC专有)
一次授权 = 两枚 token = 两个信任边界
续期：grant_type=refresh_token（后端静默）
撤销：RFC 7009 撤销 refresh_token → 连带作废派生 access_token
隐式模式：已废弃 | 密码模式：第三方禁用 | client_credentials：服务间
防重放现代答案：DPoP / mTLS（sender-constrained token）
```

---

*本教程的问答部分来自一次实际的推演式学习：每一节后的"为什么"都是真实的常见误区。如果你想继续深入，最推荐的下一步是 **OIDC**——因为"登录"到底是怎么发生的，才是 OAuth 故事里剩下的那一半。*
