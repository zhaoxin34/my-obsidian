---
title: "Next.js 全栈开发入门教程：从零做一个用户登录系统"
description: "通过构建一个完整的用户登录系统，掌握 Next.js 15 App Router + Server Actions 的全栈开发流程"
tags: [Next.js, React, 全栈, 教程, TypeScript]
---

# Next.js 全栈开发入门教程：从零做一个用户登录系统

> 适用版本：**Next.js 15.x** + **React 19** + **TypeScript**
> 预计耗时：**45 分钟**

## 你好，我是你的老师

你说你会 JS、TS、HTML、CSS，但不会 Next.js —— 那正好，Next.js 对你来说会是一个**非常自然**的进阶：它本质上就是把这些技术打包在一起，再加上两个新概念（**App Router** 和 **Server Action**），让你一个项目同时做前端和后端。

我们不学概念，**我们直接做一个能跑的登录系统**。等你做完，概念自然就懂了。

## 你将做出什么

一个最小可用的"用户登录系统"，包含：

- ✅ 一个登录页面（输入用户名 + 密码）
- ✅ 后端验证逻辑（在同一个项目里，不开第二个服务）
- ✅ 登录成功后自动跳转到一个**只有登录用户能看**的 Dashboard
- ✅ Dashboard 上能看到"欢迎，xxx"，右上角有**退出登录**按钮
- ✅ 没登录的人访问 Dashboard 会被踢回登录页
- ✅ 密码用 bcrypt 哈希存储，永远不存明文

做完之后，你对 Next.js 的"全栈"会有非常具体的体感。

## 前置要求

在开始之前，请确认你电脑上已经有：

- **Node.js 20 或更高版本**（打开终端输入 `node -v` 检查；如果是 18，请先升级）
- 一个你顺手的代码编辑器（VS Code / Cursor / WebStorm 都行）
- 一个浏览器（Chrome / Safari / Edge 都行）
- 终端的基本使用能力（`cd`、`ls`、`mkdir`）

> ⚠️ **不要安装额外的数据库。** 本教程故意用**内存数组**当"数据库"，让你专注学 Next.js 的核心概念，而不是被环境配置劝退。

---

## Step 1：创建 Next.js 项目

我们用官方脚手架一键创建项目。打开终端，进入你想放项目的目录，然后执行：

```bash
npx create-next-app@latest login-demo
```

接下来脚手架会问一堆问题。请**严格按照下面的回答选择**，不要改：

```
✔ Would you like to use TypeScript?        → Yes
✔ Would you like to use ESLint?             → Yes
✔ Would you like to use Tailwind CSS?       → No  ← 我们用普通 CSS，你有 CSS 基础
✔ Would you like to use `src/` directory?   → Yes
✔ Would you like to use App Router?         → Yes  ← Next.js 15 的核心
✔ Would you like to use Turbopack?          → Yes
✔ Would you like to customize the import alias? → No
```

> 💡 **为什么不用 Tailwind？** Tailwind 很流行，但你已经有 CSS 基础了。用普通 CSS 你反而能看清 Next.js 在做什么，不会被工具链淹没。等你熟悉了再切 Tailwind 不迟。

等脚手架跑完，进入项目目录：

```bash
cd login-demo
```

**你应该看到**：终端最后几行打印类似

```
Success! Created login-demo at /你的路径/login-demo
```

说明项目建好了。

---

## Step 2：启动开发服务器，先看一眼

我们先把它跑起来，确认环境没问题：

```bash
npm run dev
```

**你应该看到**：

```
  ▲ Next.js 15.1.0 (turbo)
   - Local:        http://localhost:3000
   - Network:      http://192.168.x.x:3000

 ✓ Starting...
 ✓ Ready in 1.2s
```

打开浏览器访问 [http://localhost:3000](http://localhost:3000)。

**你应该看到**：一个 Next.js 的默认欢迎页，旋转的 Next logo，标题写着 "Get started by editing app/page.tsx"。

> ✅ **恭喜，第一个里程碑达成**：你的 Next.js 项目跑起来了，前后端是在同一个进程里的（这就是 Next.js 的"全栈"含义 —— 不像传统前端要再开一个 Node/Express 服务）。

> 🛑 如果浏览器没反应、端口被占用，编辑 `package.json` 里的 `"dev": "next dev"` 改成 `"dev": "next dev -p 3001"` 然后重新 `npm run dev`。先别深究为什么。

按 `Ctrl + C` 停掉服务器，进入下一步。

---

## Step 3：清理掉示例代码，看清项目结构

脚手架生成了一堆示例。我们要把它删到最干净。**先看一眼结构**：

```bash
ls -la
```

你应该看到一堆文件和文件夹。重点关注这几个：

```
login-demo/
├── src/
│   └── app/        ← 【重点】所有的"页面"都放在这里
│       ├── layout.tsx
│       ├── page.tsx
│       └── globals.css
├── public/
├── package.json
└── next.config.ts
```

> 💡 **核心概念 1：App Router**
> 你只要在 `src/app/` 下放一个 `xxx/page.tsx`，访问 `/xxx` 就能看到这个页面。文件即路由。这就是 **App Router**。
> 比如 `src/app/about/page.tsx` 对应的就是 `http://localhost:3000/about`。

我们先把示例页改成最简单的。打开 `src/app/page.tsx`，**把里面所有内容删掉**，换成：

```tsx
export default function Home() {
  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>登录系统 Demo</h1>
      <p>
        <a href="/login">前往登录</a>
      </p>
    </main>
  );
}
```

保存。再 `npm run dev`，刷新浏览器。

**你应该看到**：一个简单的页面，标题是"登录系统 Demo"，下面有一行"前往登录"的链接（点现在还是 404，没关系，下一步建）。

> 🎯 **到这里你应该感受到 Next.js 的爽**：你改完一个文件，浏览器自动刷新。不用配 webpack，不用配 vite，**Next.js 自带热更新**。

---

## Step 4：建一个"假的用户数据库"

在写登录之前，我们要先有个地方放用户。真实项目会用 MySQL/PostgreSQL，但本教程**故意用内存数组**，省掉一切数据库配置。

新建文件 `src/lib/users.ts`：

```ts
import bcrypt from "bcryptjs";

export type User = {
  id: string;
  username: string;
  passwordHash: string;
};

// 这就是我们的"数据库"，重启服务就清空。
// 生产环境绝对不要这样做 —— 本教程只是为了让你专注学 Next.js。
const users: User[] = [];

// 启动时塞一个测试用户，方便你立刻能登录
// 用户名: demo / 密码: 123456
const demoPasswordHash = bcrypt.hashSync("123456", 10);
users.push({
  id: "u_1",
  username: "demo",
  passwordHash: demoPasswordHash,
});

export function findUserByUsername(username: string): User | undefined {
  return users.find((u) => u.username === username);
}

export function verifyPassword(user: User, password: string): boolean {
  return bcrypt.compareSync(password, user.passwordHash);
}
```

**你应该看到**：文件保存后终端没报错（如果有错，99% 是 `bcryptjs` 没装 —— 我们现在装一下）：

```bash
npm install bcryptjs
npm install -D @types/bcryptjs
```

> 💡 **为什么 `npm install` 而不是 `npm install -D`？** `bcryptjs` 运行时要用，所以装到 dependencies。类型定义只在写代码时用，所以 `-D` 装到 devDependencies。

---

## Step 5：写"后端"—— Next.js 的 Server Action

传统做法：前端 fetch 一个 `/api/login` 接口，那个接口写在 `app/api/login/route.ts` 里。

**Next.js 15 的现代做法：直接写一个 Server Action**。它的本质是**一段在服务器上跑的 TypeScript 函数**，前端像调用普通函数一样调用它。

新建文件 `src/app/actions/login.ts`：

```ts
"use server"; // ← 这一行让它变成"后端代码"

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { findUserByUsername, verifyPassword } from "@/lib/users";
import { createSession } from "@/lib/session";

export async function loginAction(formData: FormData) {
  const username = formData.get("username") as string;
  const password = formData.get("password") as string;

  // 1. 校验输入
  if (!username || !password) {
    return { error: "用户名和密码不能为空" };
  }

  // 2. 找用户
  const user = findUserByUsername(username);
  if (!user) {
    return { error: "用户名或密码错误" };
  }

  // 3. 验证密码
  const ok = verifyPassword(user, password);
  if (!ok) {
    return { error: "用户名或密码错误" };
  }

  // 4. 创建 session（下一步会写这个函数）
  await createSession(user.id);

  // 5. 跳转到 dashboard
  redirect("/dashboard");
}
```

> 💡 **核心概念 2：Server Action**
> 你看，文件顶部一行 `"use server"` 就把它变成了"后端代码"。它的代码永远**只在服务器上跑**，前端拿不到它的逻辑，密码校验逻辑不会被打包到浏览器。这比传统 API 更安全、更简洁。

**但你会发现现在还跑不起来** —— 因为我们引用了 `@/lib/session`，这个文件还没建。先建它：

新建文件 `src/lib/session.ts`：

```ts
import "server-only";
import { cookies } from "next/headers";
import { SignJWT, jwtVerify } from "jose";

const SECRET = new TextEncoder().encode(
  process.env.SESSION_SECRET ?? "dev-secret-change-me-in-production"
);

// 内存里的 session 存储（重启就清空）
// key 是 token，value 是 userId
const sessions = new Map<string, string>();

export async function createSession(userId: string) {
  // 生成一个 JWT
  const token = await new SignJWT({ userId })
    .setProtectedHeader({ alg: "HS256" })
    .setExpirationTime("7d")
    .sign(SECRET);

  // 存到内存"数据库"
  sessions.set(token, userId);

  // 设置 cookie 给浏览器
  const cookieStore = await cookies();
  cookieStore.set("session_token", token, {
    httpOnly: true,    // JS 读不到，防 XSS
    secure: false,     // 开发环境用 false；上线后必须 true（要求 HTTPS）
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7, // 7 天
  });
}

export async function getSessionUserId(): Promise<string | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("session_token")?.value;
  if (!token) return null;

  // 先验 JWT 签名
  try {
    await jwtVerify(token, SECRET);
  } catch {
    return null;
  }

  // 再查 session 是否还有效
  return sessions.get(token) ?? null;
}

export async function destroySession() {
  const cookieStore = await cookies();
  const token = cookieStore.get("session_token")?.value;
  if (token) sessions.delete(token);
  cookieStore.delete("session_token");
}
```

装一下 `jose` 和 `server-only`：

```bash
npm install jose server-only
```

> 💡 **核心概念 3：cookies() 是 async 的**
> Next.js 15 里 `cookies()` 必须 `await`。如果你看到教程写 `cookies().get(...)`（没有 await），那一定是过时的 Next.js 14 写法。

---

## Step 6：写"前端" —— 登录页面

现在写登录页面。**它同时干两件事**：渲染 UI（前端），并且把表单**直接连到** Server Action（后端）。

新建文件 `src/app/login/page.tsx`：

```tsx
import { loginAction } from "../actions/login";

export default function LoginPage() {
  return (
    <main style={{ maxWidth: 360, margin: "4rem auto", fontFamily: "sans-serif" }}>
      <h1>登录</h1>

      {/* 把表单直接绑到 Server Action，零 fetch 代码 */}
      <form action={loginAction} style={{ display: "grid", gap: "0.75rem" }}>
        <label>
          用户名
          <input
            name="username"
            type="text"
            required
            style={{ display: "block", width: "100%", padding: 8 }}
          />
        </label>

        <label>
          密码
          <input
            name="password"
            type="password"
            required
            style={{ display: "block", width: "100%", padding: 8 }}
          />
        </label>

        <button type="submit" style={{ padding: 10 }}>
          登录
        </button>
      </form>
    </main>
  );
}
```

**你应该看到**：

- 文件保存后，`src/app/login/page.tsx` 自动就对应了 `/login` 路由
- 访问 [http://localhost:3000/login](http://localhost:3000/login) 看到一个登录表单

> 💡 **这就是 Next.js 全栈的核心套路**：
> - `page.tsx` 是**前端**（渲染 UI）
> - `actions/xxx.ts` 里带 `"use server"` 的是**后端**
> - 用 `<form action={...}>` 直接把它们连起来，**不需要写 fetch、不需要写 API 路由、不需要写 useState**

---

## Step 7：写受保护的 Dashboard

现在写一个只有登录用户能看的页面。**关键点**：在 Next.js 里，你可以在 `page.tsx` 这种"前端"文件里**直接调用后端函数**（比如我们刚写的 `getSessionUserId`），不需要写 API。

新建文件 `src/app/dashboard/page.tsx`：

```tsx
import { redirect } from "next/navigation";
import { getSessionUserId } from "@/lib/session";
import { findUserByUsername } from "@/lib/users"; // 我们再加一个函数
import { logoutAction } from "../actions/logout";

// 在服务端渲染前就检查登录状态
export default async function DashboardPage() {
  const userId = await getSessionUserId();
  if (!userId) {
    redirect("/login");
  }

  // 找到用户名展示出来
  // （本教程简化：直接根据 userId 反查 username）
  const username = userId === "u_1" ? "demo" : "未知用户";

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Dashboard</h1>
        {/* 退出登录也走 Server Action */}
        <form action={logoutAction}>
          <button type="submit">退出登录</button>
        </form>
      </div>
      <p>欢迎，{username}！</p>
      <p>这是只有登录用户能看到的页面 🎉</p>
    </main>
  );
}
```

我们再补两个小文件，让上面的代码能跑起来。

**1)** 在 `src/lib/users.ts` 末尾追加一个函数（编辑现有文件）：

```ts
export function findUserById(id: string): User | undefined {
  return users.find((u) => u.id === id);
}
```

**2)** 在 `src/app/page.tsx` 顶部加个跳转，已登录就跳 dashboard（编辑现有文件）：

```tsx
import { redirect } from "next/navigation";
import { getSessionUserId } from "@/lib/session";

export default async function Home() {
  const userId = await getSessionUserId();
  if (userId) redirect("/dashboard");

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>登录系统 Demo</h1>
      <p>
        <a href="/login">前往登录</a>
      </p>
    </main>
  );
}
```

**3)** 新建 `src/app/actions/logout.ts`：

```ts
"use server";

import { destroySession } from "@/lib/session";
import { redirect } from "next/navigation";

export async function logoutAction() {
  await destroySession();
  redirect("/login");
}
```

---

## Step 8：跑起来！第一次完整测试

保存所有文件，重启开发服务器（`Ctrl + C` 然后 `npm run dev`），按顺序做这几件事：

1. 打开 [http://localhost:3000](http://localhost:3000)
   - **你应该看到** "登录系统 Demo" 页面（因为没登录）
2. 点击 "前往登录"
   - **你应该看到** 登录表单
3. 用户名填 `demo`，密码填 `123456`，点"登录"
   - **你应该看到**：浏览器跳到 `/dashboard`，页面上写着"欢迎，demo！"
4. 复制 URL，刷新页面
   - **你应该看到**：依然在 dashboard（**session 没失效**）
5. 手动在地址栏改成 `http://localhost:3000/login`，回车
   - **你应该看到**：能看到登录页（受保护的是 dashboard，不是 login 页本身）
6. 点"退出登录"
   - **你应该看到**：回到登录页
7. 再访问 `/dashboard`
   - **你应该看到**：被踢回登录页

> ✅ **如果以上 7 步都对，你的全栈登录系统就完成了。**

---

## Step 9：故意输错，看错误处理

测试一下错误处理：

1. 用户名填 `demo`，密码填 `wrong`，点"登录"
   - **你会发现**：跳到了 dashboard，没有报错 ❌
   
这不对！我们返回了 `{ error: "..." }`，但页面没显示。修一下登录页，让它能展示错误。

**但是有个问题**：Server Action 返回值，前端默认拿不到。Next.js 15 + React 19 用 `useActionState` 这个 hook 来接。

把 `src/app/login/page.tsx` 改成下面这样（注意 `'use client'` 加在顶部）：

```tsx
"use client";

import { useActionState } from "react";
import { loginAction } from "../actions/login";

export default function LoginPage() {
  const [state, formAction, pending] = useActionState(loginAction, null);

  return (
    <main style={{ maxWidth: 360, margin: "4rem auto", fontFamily: "sans-serif" }}>
      <h1>登录</h1>

      {state?.error && (
        <p style={{ color: "red" }}>{state.error}</p>
      )}

      <form action={formAction} style={{ display: "grid", gap: "0.75rem" }}>
        <label>
          用户名
          <input
            name="username"
            type="text"
            required
            disabled={pending}
            style={{ display: "block", width: "100%", padding: 8 }}
          />
        </label>

        <label>
          密码
          <input
            name="password"
            type="password"
            required
            disabled={pending}
            style={{ display: "block", width: "100%", padding: 8 }}
          />
        </label>

        <button type="submit" disabled={pending} style={{ padding: 10 }}>
          {pending ? "登录中..." : "登录"}
        </button>
      </form>
    </main>
  );
}
```

> 💡 **核心概念 4：'use client'**
> 加了 `'use client'` 的文件就是"前端组件"，能用 `useState`、`useActionState` 这些 hook。
> **不是所有文件都要 `'use client'`** —— Next.js 默认全是"服务器组件"，只在需要交互的地方用客户端组件。

**注意：现在我们要改一下 `loginAction` 的签名来配合 `useActionState`**。编辑 `src/app/actions/login.ts`，把函数签名改成：

```ts
export async function loginAction(
  prevState: { error?: string } | null,
  formData: FormData
) {
  // ... 函数体不变 ...
}
```

保存。再试一次输错密码：

- **你应该看到**：页面上显示红色错误 "用户名或密码错误"，不再跳走 ✅

---

## 你已经学会的

做完这个教程，你已经掌握了 Next.js 全栈开发的核心套路：

- ✅ **App Router**：在 `src/app/` 下建文件夹 + `page.tsx` 就是一个路由
- ✅ **Server Component vs Client Component**：默认是服务器组件，需要交互的地方加 `'use client'`
- ✅ **Server Action**：用 `"use server"` 写的函数就是"后端"，前端用 `<form action={...}>` 直接调
- ✅ **cookies()**：Next.js 15 里它是 `async` 的，用 `await cookies()`
- ✅ **useActionState**：拿 Server Action 返回值的 hook
- ✅ **HTTP-only Cookie + JWT**：登录状态的安全保存方式
- ✅ **bcrypt**：密码哈希，永远不存明文
- ✅ **redirect()**：在服务器端/Server Action 里直接跳转

## 下一步建议

你的登录系统已经能用了。下面是几个**自然的下一步**，按推荐顺序：

1. **加个注册页面**：在 `src/lib/users.ts` 加一个 `createUser(username, password)`，写个 `registerAction`。让用户能自己注册，不再用写死的 `demo / 123456`。
2. **换成真实数据库**：用 [Prisma + SQLite](https://www.prisma.io/docs/getting-started/setup-prisma/start-from-scratch/relational-databases-typescript-sqlite) 替换 `users: User[]`。SQLite 不需要额外装服务，单文件数据库。
3. **加 Middleware 保护**：在项目根目录建 `middleware.ts`，对 `/dashboard/*` 路径做统一拦截，不用每个页面都写 `if (!userId) redirect(...)`。
4. **接入 OAuth**：研究 [Auth.js (NextAuth) v5](https://authjs.dev/getting-started)，用它加 GitHub 登录。
5. **美化 UI**：把内联样式换成 Tailwind CSS（你现在应该能看清 Next.js 在做什么了，加 Tailwind 不会让你迷路）。

## 常见踩坑

| 现象 | 原因 | 解法 |
|---|---|---|
| `cookies()` 报 `undefined is not a function` | 漏了 `await` | Next.js 15 里 `cookies()` 是 async 的，必须 `await` |
| 改了文件浏览器没刷新 | Turbopack 偶尔抽风 | `Ctrl+C` 重启 `npm run dev` |
| Server Action 里读不到 `formData` | 表单没 `name` 属性 | 每个 `<input>` 必须有 `name="xxx"` |
| `useActionState` 报类型错误 | `loginAction` 签名没加 `prevState` 参数 | 按本教程 Step 9 的方式改签名 |
| 部署后登录不上 | `secure: false` 上线后 cookie 不生效 | 生产环境改成 `secure: true`（必须 HTTPS） |

---

🎉 **教程完成。** 你现在有一个能跑、能演示、能扩展的 Next.js 全栈登录系统。去做你自己的项目吧。
