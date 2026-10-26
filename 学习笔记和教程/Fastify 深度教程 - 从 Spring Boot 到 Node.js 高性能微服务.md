---
title: "Fastify 深度教程：从 Spring Boot 到 Node.js 高性能微服务"
description: "面向 Spring Cloud 开发者的 Fastify 5 深度教程：请求生命周期管线、插件封装模型、Schema 驱动契约、TypeScript 类型安全、测试与生产实践"
tags:
  - Fastify
  - Node.js
  - TypeScript
  - 微服务
  - 性能
created: 2026-10-26
revised: 2026-10-26
environment: "fastify 5.12.x / Node 20+ / TypeScript 5.x"
---

# Fastify 深度教程：从 Spring Boot 到 Node.js 高性能微服务

> **本文读者**：有 Spring Boot / Spring Cloud 工程经验的程序员，熟悉 MVC 分层、IoC 容器、Filter/Interceptor 链、声明式校验、事务边界这些概念。
>
> **本文不做的事**：不解释"什么是 HTTP"、不手把手教 `npm install`、不写 Hello World。
>
> **本文要做的事**：把 Fastify 的每个机制**锚定到你已经掌握的 Spring 概念上**，让你在 1~2 小时内建立完整心智模型，并能在真实项目里做出正确决策。
>
> **版本基线**：`fastify@5.12.x`（2026-10 实测），要求 Node.js ≥ 20。v6 处于 alpha 阶段，本文不涉及。

---

## 目录

- [第 1 章：Fastify 在生态中的位置](#第-1-章fastify-在生态中的位置)
  - [1.1 一句话定位](#11-一句话定位)
  - [1.2 Node 框架横向对比](#12-node-框架横向对比)
  - [1.3 它为什么快：三个关键设计](#13-它为什么快三个关键设计)
  - [1.4 Spring 开发者最该先想清楚的 5 个问题](#14-spring-开发者最该先想清楚的-5-个问题)
- [第 2 章：请求生命周期 —— Fastify 的管线模型](#第-2-章请求生命周期--fastify-的管线模型)
  - [2.1 完整管线](#21-完整管线)
  - [2.2 十个请求级 Hook 与 Spring 的对应关系](#22-十个请求级-hook-与-spring-的对应关系)
  - [2.3 应用级 Hook](#23-应用级-hook)
  - [2.4 在 Hook 中提前响应](#24-在-hook-中提前响应)
  - [2.5 Hook 的作用域规则](#25-hook-的作用域规则)
- [第 3 章：Encapsulation —— Fastify 最独特也最易踩坑的设计](#第-3-章encapsulation--fastify-最独特也最易踩坑的设计)
  - [3.1 作用域树](#31-作用域树)
  - [3.2 Encapsulation 在 Spring 中没有对应物](#32-encapsulation-在-spring-中没有对应物)
  - [3.3 fastify-plugin：打破封装的标准手段](#33-fastify-plugin打破封装的标准手段)
  - [3.4 插件加载顺序与依赖声明](#34-插件加载顺序与依赖声明)
  - [3.5 常见踩坑清单](#35-常见踩坑清单)
- [第 4 章：Schema 驱动的契约 —— 校验、序列化、文档三合一](#第-4-章schema-驱动的契约--校验序列化文档三合一)
  - [4.1 v5 的重要变化：强制完整 JSON Schema](#41-v5-的重要变化强制完整-json-schema)
  - [4.2 请求校验：Ajv 的行为细节](#42-请求校验ajv-的行为细节)
  - [4.3 响应序列化：性能收益与"字段消失"陷阱](#43-响应序列化性能收益与字段消失陷阱)
  - [4.4 共享 Schema 与 $ref](#44-共享-schema-与-ref)
  - [4.5 TypeScript 类型安全：TypeBox + Type Provider](#45-typescript-类型安全typebox--type-provider)
  - [4.6 OpenAPI 文档自动生成](#46-openapi-文档自动生成)
  - [4.7 与 Spring 校验链的对照](#47-与-spring-校验链的对照)
- [第 5 章：错误处理与可观测性](#第-5-章错误处理与可观测性)
  - [5.1 错误处理器的层级语义（实测）](#51-错误处理器的层级语义实测)
  - [5.2 业务异常的统一建模](#52-业务异常的统一建模)
  - [5.3 404 处理](#53-404-处理)
  - [5.4 Pino 日志与请求级 child logger](#54-pino-日志与请求级-child-logger)
  - [5.5 指标、追踪与过载保护](#55-指标追踪与过载保护)
- [第 6 章：依赖注入 —— Fastify 没有 DI 容器](#第-6-章依赖注入--fastify-没有-di-容器)
  - [6.1 三种主流注入模式](#61-三种主流注入模式)
  - [6.2 能力差距对照表](#62-能力差距对照表)
  - [6.3 事务边界放哪里](#63-事务边界放哪里)
  - [6.4 什么时候你该换回 Spring](#64-什么时候你该换回-spring)
- [第 7 章：工程化 —— 项目结构、配置、测试](#第-7-章工程化--项目结构配置测试)
  - [7.1 目录结构](#71-目录结构)
  - [7.2 build 工厂模式](#72-build-工厂模式)
  - [7.3 配置管理](#73-配置管理)
  - [7.4 测试](#74-测试)
  - [7.5 autoload：按目录自动注册路由](#75-autoload按目录自动注册路由)
- [第 8 章：生产实践](#第-8-章生产实践)
  - [8.1 优雅关闭](#81-优雅关闭)
  - [8.2 健康检查与就绪探针](#82-健康检查与就绪探针)
  - [8.3 反向代理下的真实 IP](#83-反向代理下的真实-ip)
  - [8.4 超时、体积限制与连接复用](#84-超时体积限制与连接复用)
  - [8.5 多进程与水平扩展](#85-多进程与水平扩展)
  - [8.6 生产配置检查表](#86-生产配置检查表)
- [第 9 章：与 Spring Cloud 生态集成](#第-9-章与-spring-cloud-生态集成)
  - [9.1 服务注册与发现](#91-服务注册与发现)
  - [9.2 配置中心](#92-配置中心)
  - [9.3 服务间调用](#93-服务间调用)
  - [9.4 熔断限流降级](#94-熔断限流降级)
  - [9.5 用 Fastify 做 BFF / 网关](#95-用-fastify-做-bff--网关)
  - [9.6 链路追踪](#96-链路追踪)
- [第 10 章：选型决策与常见误区](#第-10-章选型决策与常见误区)
  - [10.1 决策树](#101-决策树)
  - [10.2 什么场景不该用 Fastify](#102-什么场景不该用-fastify)
  - [10.3 新人最容易犯的 12 个错](#103-新人最容易犯的-12-个错)
- [附录 A：Fastify v4 与 v5 迁移要点](#附录-afastify-v4-与-v5-迁移要点)
- [附录 B：核心 API 速查表](#附录-b核心-api-速查表)
- [附录 C：常用插件清单](#附录-c常用插件清单)
- [附录 D：参考资源](#附录-d参考资源)

---

## 第 1 章：Fastify 在生态中的位置

### 1.1 一句话定位

**Fastify 是"Servlet 容器 + Spring MVC 基础设施，但把编译期工作做到极致"的 Node 框架。**

它不是 Spring Boot 的等价物（没有 DI、没有 AOP、没有事务、没有自动装配），而是**一个刻意做减法的框架**：只提供路由 + 生命周期 + 契约 + 插件，其余全部交给生态。

这个"减法"是有代价的，下文会反复出现：**你从 Spring 那里免费获得的东西（依赖注入、AOP、声明式事务、统一异常抽象、配置绑定），在 Fastify 里都要自己搭或者换一种思路。**

另一个必须先说清楚的定位差异：

> **Fastify 的编程模型 ≈ Spring MVC（Servlet），不是 Spring WebFlux（Reactor）。**
>
> Fastify 的 handler 是 `async/await` 函数，运行在 Node 的单线程事件循环上，**没有 reactive streams、没有 backpressure、没有背压驱动的流式处理**（除响应体可以是 Stream 外）。
>
> Spring 开发者最容易犯的错，是看到 `async/await` 就以为像 WebFlux 的 `Mono`。实际上：
>
> - Spring MVC：一个请求一个线程，可阻塞 IO（JDBC）。
> - Spring WebFlux：一个请求一个（虚拟）线程处理事件流，IO 异步不阻塞。
> - Fastify：**一个进程一个 JS 线程**，所有请求共享一个事件循环。IO 异步不阻塞，但**任何同步阻塞（`fs.readFileSync`、大 JSON 解析、CPU 密集计算）都会阻塞全部请求**。
>
> 这意味着 Fastify 的"水平扩容"单位是**进程**，不是线程。一个 Node 进程 ≈ 一个 Tomcat 实例，而不是一个 Tomcat 线程。

### 1.2 Node 框架横向对比

| 维度 | Express | Koa | Fastify | NestJS | Hono |
| --- | --- | --- | --- | --- | --- |
| 心智模型 | 中间件链 | 洋葱模型（async/await 中间件） | 生命周期 Hook + 插件 | 装饰器 + DI 容器 | Fetch API 标准 |
| 性能 | 基准 | 中 | **高** | 中高（底层可用 Fastify） | 极高（尤其边缘运行时） |
| 校验 | 手工 / 第三方 | 手工 | **Schema 驱动（Ajv + fast-json-stringify）** | DTO + class-validator | Schema / Hono Validator |
| DI | 无 | 无 | 无（装饰器模式） | **完整容器** | 无 |
| OpenAPI | 手工 | 手工 | 自动生成 | 自动生成（Swagger 模块） | 手工 |
| 运行时要求 | Node 18+ | Node 18+ | Node 20+ | Node 20+ | 边缘运行时 |
| 适合 | 历史包袱 | 极简中间件 | **高性能服务、BFF、网关** | 大团队、强规范、Java 背景迁移 | 边缘 / Serverless |

**选择逻辑（给 Spring 开发者的翻译）**：

- 想要 "Spring Boot 体验" → NestJS（底层可选 Fastify 适配器）。
- 想要 "Spring Boot Web 但更轻、更快、约束更明确" → **Fastify**。
- 想要 "Netty + Reactor 的极致" → Hono（但生态与 Java 习惯差距更大）。
- 已经在用 Express 且无性能诉求 → 别动。

### 1.3 它为什么快：三个关键设计

理解这三个设计，后面所有的 API 设计都会变得自然。

**① 路由树是 radix tree（`find-my-way`）**

Spring 的 `DispatcherServlet` 靠 `HandlerMapping` + `AntPathMatcher` 做路径匹配，是**逐段字符串比较**。`find-my-way` 预先把路由编译成 radix tree，匹配是**指针跳转**，且**不为每个请求重新解析 URL**（静态路由命中时直接跳过解析）。

参数路由、约束（`/user/:id(\\d+)`）、通配符都在**注册期**编译好，运行期零字符串解析。

**② 序列化和校验都在启动时编译成 JS 函数**

这是 Fastify 最容易被低估的性能来源：

```text
JSON Schema  --ajv 编译-->  校验函数（JS 闭包）
JSON Schema  --fast-json-stringify 编译-->  序列化函数（JS 闭包）
```

请求到来时执行的是**普通 JS 函数调用**，不是"遍历 schema 树做解释"。对比 Spring：

| 环节 | Spring 默认 | Fastify |
| --- | --- | --- |
| 请求校验 | Jakarta Validation，**运行时反射 + 代理** | Ajv 编译后的闭包，**零反射** |
| 响应序列化 | Jackson，**运行时反射 introspect** | fast-json-stringify 编译后的闭包，**生成直写代码** |
| 反射成本 | 首次有缓存，但仍是运行时元数据 | 编译期确定，**GC 压力更小** |

fast-json-stringify 的本质是：**根据 schema 生成一段"手写"的序列化 JS 代码**，直接 `output.push(...)`，而不是通用遍历。所以它能比 `JSON.stringify` 快 2~3 倍，并且**天然丢弃 schema 里没声明的字段**（这既是性能特性，也是安全特性，后面 4.3 节详述）。

**③ 插件加载是拓扑排序的（`avvio`）**

Spring 的 Bean 容器有依赖图解析能力，Fastify 也有 —— `avvio` 会在 `ready()` 前按 `dependencies` 元数据拓扑排序插件加载顺序。这保证了你"装饰器在谁之后可用"是确定的。

### 1.4 Spring 开发者最该先想清楚的 5 个问题

在读 API 之前，先对这 5 个问题给出我的判断：

**Q1：没有 DI 容器，Service 怎么拿到 Repository？**
→ 用**闭包工厂 + 显式传参**，这是 Fastify 社区的主流做法。Fastify 的 `decorate` 是给"实例级基础设施"（db、redis、config）用的，不是通用 DI。详见第 6 章。

**Q2：没有 AOP，事务、日志、鉴权怎么办？**
→ 用 **Hook**（Fastify 的 AOP 等价物，且切点比 Spring 更细）。`preHandler` 钩子做鉴权/权限，`preSerialization` 做统一包装。真正需要"织入方法"的能力（@Transactional）应该下沉到 Repository 层显式管理。详见 6.3。

**Q3：没有 `@RestControllerAdvice`，全局异常怎么办？**
→ `app.setErrorHandler()`，而且它**遵循封装作用域**：子作用域可以覆盖父作用域的错误处理器（实测见 5.1），这比 Spring 的 `@Order` + `if` 判断更干净。

**Q4：Spring Cloud 那套（注册中心、配置中心、Gateway）能接上吗？**
→ 能。Node 侧有 Nacos/Consul/Eureka 客户端、有配置中心 SDK、有 OpenTelemetry。详见第 9 章。

**Q5：数据校验怎么做？DRO 和 `@Valid` 那一套没了？**
→ 换成 **JSON Schema 声明式契约**。这是 Fastify 的核心设计哲学：**契约写在路由上，一次声明同时产出校验、序列化、TypeScript 类型、OpenAPI 文档**。详见第 4 章。

---

## 第 2 章：请求生命周期 —— Fastify 的管线模型

### 2.1 完整管线

Fastify 没有 `DispatcherServlet`，但它有一条**比 Spring MVC 更细粒度**的管线。理解这张图，后面的 API 都是自然结果：

```mermaid
flowchart TD
    A["HTTP 请求到达 Node http.Server"] --> B["路由匹配 find-my-way"]
    B --> C["onRequest"]
    C --> D["preParsing"]
    D --> E["Content-Type Parser<br/>解析 body 为 JS 对象"]
    E --> F["preValidation"]
    F --> G["Ajv 校验 body/query/params/headers"]
    G --> H["preHandler"]
    H --> I["Handler 业务逻辑"]
    I --> J["preSerialization"]
    J --> K["fast-json-stringify 序列化"]
    K --> L["onSend"]
    L --> M["响应写回 socket"]
    M --> N["onResponse"]

    C -. 抛错 .-> X["onError"]
    H -. 抛错 .-> X
    I -. 抛错 .-> X
    X --> Y["setErrorHandler<br/>→ 响应"]
```

注意这条管线**不是 Servlet Filter 那种"套娃"结构**，而是**扁平的顺序阶段**。这是 Fastify 与 Spring 最大的 API 差异：

- Spring：`Filter → DispatcherServlet → Interceptor.preHandle → Handler → Interceptor.postHandle → afterCompletion → Filter`
- Fastify：一条线，10 个命名阶段，每个阶段可以选择"安装一个全局函数"或"每个路由一个函数"。

### 2.2 十个请求级 Hook 与 Spring 的对应关系

| Fastify Hook | 执行时机 | Spring 中的近似对应物 | 典型用途 |
| --- | --- | --- | --- |
| `onRequest` | 收到请求，**body 还未解析** | `Filter#doFilter` 前半段 / `OncePerRequestFilter` | 认证、限流、traceId 注入、early return |
| `preParsing` | body 解析**之前**，拿到原始流 | `Filter` 中处理 body 流 | 解压、加密报文解包、协议转换 |
| `preValidation` | 解析完成、**校验之前** | `HandlerInterceptor#preHandle`（部分） | 参数归一化、补默认值 |
| `preHandler` | 校验通过、**handler 之前** | `HandlerInterceptor#preHandle` | 鉴权、权限、资源加载 |
| `preSerialization` | handler 返回后、**序列化之前** | `ResponseBodyAdvice#beforeBodyWrite` | 统一响应包装、字段脱敏 |
| `onError` | 出错时，**在 errorHandler 之前** | `HandlerExceptionResolver` | 统一错误日志、补充 header |
| `onSend` | payload 序列化后、**写 socket 前** | `Filter` 中包装 `HttpServletResponse` | 压缩、注入 header、审计 |
| `onResponse` | 响应**已发出** | `Filter#doFilter` 的 finally / `afterCompletion` | 耗时统计、埋点上报 |
| `onTimeout` | socket 级超时 | — | 连接超时监控 |
| `onRequestAbort` | 客户端提前断开 | — | 取消正在进行的昂贵查询 |

**三个 Spring 开发者会立刻发现的增强点**：

1. **切点比 `HandlerInterceptor` 细得多**。Spring 的 `HandlerInterceptor` 只有 preHandle/postHandle/afterCompletion 三个点，且拿不到"body 还没解析"和"序列化前"的时机。Fastify 有 10 个点，能实现"响应序列化前统一脱敏""body 解析前解压"这类需求，而不需要 `Filter` + `ResponseBodyAdvice` 两套机制。

2. **Hook 可以按路由安装**。Spring 的 `@Interceptor` 是全局的 + `HandlerMapping` 过滤；Fastify 可以：

```ts
// 全局
app.addHook('preHandler', authHook)

// 单路由
app.get('/public', { preHandler: [] }, handler)          // 显式清空
app.get('/admin', { preHandler: [authHook, adminHook] }, handler)  // 局部追加
```

路由级 hook 是**追加**到作用域 hook 之后的（不是替换）。

3. **`onError` 不能改错误**。它是纯观测点。想改错误内容请在 `setErrorHandler` 里做。

### 2.3 应用级 Hook

| Hook | 时机 | 用途 |
| --- | --- | --- |
| `onReady` | 所有插件加载完、开始 listen 前 | 预热缓存、连接数据库、加载配置 |
| `onListen` | 端口绑定成功后 | 注册到注册中心、上报存活 |
| `onClose` | `app.close()` 时 | 关闭连接池、注销注册中心 |
| `preClose` | `onClose` 之前 | 停止接收新流量 |
| `onRoute` | 每条路由注册时 | 路由级审计、自动加鉴权、生成文档 |
| `onRegister` | 每个插件注册时 | 插件级审计、依赖检查 |

`onRoute` 是 Fastify 的一个特色钩子，Spring 里没有直接对应物：

```ts
app.addHook('onRoute', (routeOptions) => {
  // 统一给所有路由打标签、挂 metrics、强制 schema
  console.log(`注册路由: ${routeOptions.method} ${routeOptions.url}`)
})
```

### 2.4 在 Hook 中提前响应

和 Spring Filter 里的"短路返回"一样，Fastify 允许在 hook 中直接 `reply.send()`，此时**后续所有 hook 和 handler 都被跳过**：

```ts
app.addHook('onRequest', async (req, reply) => {
  const token = req.headers.authorization
  if (!token) {
    reply.code(401).send({ error: 'unauthorized' })
    return reply   // ⚠️ 必须 return，否则请求会继续执行
  }
})
```

> ⚠️ **最高频的坑**：在 `async` hook 里调用 `reply.send()` 后**必须 `return reply`**。
>
> 原因：`reply.send()` 是**同步**发起响应（写入 socket 是异步的），但 `async` 函数返回 `undefined` 会让 Fastify 认为"hook 正常结束，继续走"，导致 handler 被再次执行，最终抛出 `FST_ERR_REP_ALREADY_SENT`。
>
> 官方文档特别强调：**不要混用 callback 风格（`done`）和 async/Promise 风格**，否则 hook 链会被执行两次。

另外注意 `done` 回调在 async 函数里不可用：`done` 回调与 `async/await` **不要混用**。

### 2.5 Hook 的作用域规则

Hook 遵循封装作用域规则（下一章详述）：

- 在 root 注册的 hook → **对所有子作用域的路由生效**。
- 在子作用域注册的 hook → **只对该作用域内的路由生效**，且与父级 hook **按注册顺序串联执行**（父先子后）。
- 子作用域**不能移除**父级的 hook，只能在自己的路由上用 `preHandler: []` 之类做路由级覆盖。

---

## 第 3 章：Encapsulation —— Fastify 最独特也最易踩坑的设计

### 3.1 作用域树

`app.register(plugin)` **总是创建一个新的作用域**。新作用域里：

- `decorate` 添加的属性 → **只在该作用域及其子作用域可见**
- `addHook` 添加的 hook → **只对该作用域内的路由生效**
- `addSchema` 添加的 schema → 同上
- 路由 → 属于该作用域

```mermaid
flowchart TD
    Root["root scope<br/>app = Fastify()"]
    Root -->|"register(dbPlugin)"| Db["scope: db<br/>decorate('db') ✅ 内部可见<br/>父级 ❌ 不可见"]
    Root -->|"register(userRoutes)"| Users["scope: user-routes"]
    Users --> UsersGet["scope: GET /users"]
    Users --> UsersId["scope: GET /users/:id"]
    Root -->|"register(orderRoutes)"| Orders["scope: order-routes"]
    Root -->|"register(authPlugin)"| Auth["scope: auth<br/>addHook('preHandler')"]
```

实测验证（Fastify 5.12.x）：

```ts
const app = Fastify()
app.register(async (inst) => {
  inst.decorate('secret', 'child-only')
})
// await app.ready()
console.log(app.hasDecorator('secret'))  // false ← 父级看不到
```

### 3.2 Encapsulation 在 Spring 中没有对应物

这是最难迁移的心智障碍。Spring 的世界是**扁平的**：所有 Bean 在同一个容器里，`@Autowired` 全局可见，没有"私有作用域"的概念。

Fastify 的作用域树带来的是**真正的模块隔离**，最接近的类比是：

| 场景 | Spring 中的对应物 |
| --- | --- |
| 插件私有依赖（不希望泄漏） | Spring 里只能靠包名约定 + `@ConditionalOnMissingBean`；Fastify 是**语言级强制** |
| 模块化单体（Modular Monolith） | Fastify 天然支持；Spring 要靠 `spring.modulith` 或 Maven 多模块 |
| 多租户 | 靠作用域给每个租户注入不同的 db 实例 |

**但代价也很明显**：Spring 里 `@Autowired` 一定能拿到；Fastify 里"父级拿不到子级的 decorator"是**默认行为而非异常**，很多人在这里浪费半天。

### 3.3 fastify-plugin：打破封装的标准手段

当你希望一个插件的能力**扩散到父作用域**（比如注入 db、redis、config），用 `fastify-plugin` 包裹：

```ts
import fp from 'fastify-plugin'

export default fp(async (app, opts) => {
  app.decorate('db', createPool(opts.connectionString))
  app.addHook('onClose', async () => { await app.db.end() })
}, {
  name: 'db-plugin',
  fastify: '5.x',
})
```

`fastify-plugin` 的本质是设置 `Symbol.for('skip-override')`，让 avvio **不创建新作用域**，插件在父作用域上执行。

> ⚠️ **不要用** `plugin[Symbol.for('skip-override')] = true` 手写这个标记（虽然官方文档提过，但明确不推荐）：`fastify-plugin` 还能做 Fastify 版本兼容性校验，未来 API 变更由它兜底。

**判断标准**：

| 场景 | 是否 `fp` 包裹 |
| --- | --- |
| 提供基础设施（db / redis / config / logger 增强） | ✅ 包裹 |
| 提供一组路由 + 路由私有 hook | ❌ 不包裹（保持隔离） |
| 提供一组路由，但希望 hook 覆盖全应用 | ✅ 包裹（此时要注意 hook 泄漏影响面） |
| 纯工具函数 | ❌ 直接导出函数即可，不用做成插件 |

> ⚠️ **注意**：`fp` 包裹的插件如果同时注册了路由，`prefix` 选项会**失效**（因为没有新作用域来挂前缀）。需要前缀就用不包裹的版本。

### 3.4 插件加载顺序与依赖声明

`avvio` 会按依赖元数据做拓扑排序：

```ts
app.register(async (inst) => {
  inst.decorate('config', loadConfig())
}, { dependencies: ['env'] })

app.register(async (inst) => {
  // 能安全使用 inst.config，因为 env 先加载
  const cfg = inst.config
}, { dependencies: ['env'] })
```

命名插件才能被依赖：

```ts
export default fp(async (app) => { /* ... */ }, { name: 'env' })
```

**顺序也是依赖的一种表达**：`register` 是顺序执行的，前一个插件的装饰器对后一个可见（因为后者的 `opts` 函数参数拿到的实例已包含前面的装饰器）。但**不要依赖隐式顺序**，用 `dependencies` 显式声明。

### 3.5 常见踩坑清单

| 现象 | 原因 | 解法 |
| --- | --- | --- |
| `app.db` is undefined | 插件未用 `fp` 包裹，装饰器没上浮 | 用 `fp` 包裹，或在插件内把 db 通过 `opts` 传给子插件 |
| `instance.xyz is not a function` | 父级在子作用域外访问子作用域装饰器 | 同上 |
| `fastify.register` 后立刻 `app.get` 找不到路由 | 插件是异步加载的，`register` 返回时插件还没执行 | 用 `await app.ready()`；或 `app.after()` |
| `prefix` 没生效 | 插件被 `fp` 包裹 | 去掉 `fp`，或手动在插件内拼路径 |
| hook 影响了不该影响的路由 | hook 注册在了 root 作用域 | 移到具体子作用域注册 |

---

## 第 4 章：Schema 驱动的契约 —— 校验、序列化、文档三合一

### 4.1 v5 的重要变化：强制完整 JSON Schema

Fastify v5 移除了 `jsonShortHand` 选项，`querystring` / `params` / `body` / `response` **必须写完整 JSON Schema**（必须含 `type: 'object'` 和 `properties`）：

```ts
// ❌ v4 写法，v5 会报错
schema: { querystring: { name: { type: 'string' } } }

// ✅ v5 写法
schema: {
  querystring: {
    type: 'object',
    properties: { name: { type: 'string' } },
    required: ['name'],
  },
}
```

> **为什么改？** 因为要兼容 Zod 等其他校验库、让 `@fastify/swagger` 能正确推断参数类型、消除歧义。对使用者是好事，但你从网上抄的 v4 教程会直接报错。

### 4.2 请求校验：Ajv 的行为细节

Fastify 内置 Ajv v8，基线配置如下（**这几个默认值会直接影响你的业务语义，必须知道**）：

```js
{
  coerceTypes: 'array',   // 类型强制
  useDefaults: true,      // 用 schema 里的 default 填充缺失字段
  removeAdditional: true, // 删除 schema 未声明的字段（当 additionalProperties 为 false 时）
  allErrors: false,       // 只报第一个错误（安全考虑，避免 DoS）
}
```

**`coerceTypes: 'array'` 的含义**：query string 里所有值都是字符串，所以

```text
?ids=1&ids=2   →  { ids: ['1', '2'] }
?ids=1        →  { ids: ['1'] }      // 注意：不是标量
?active=true  →  { active: true }    // boolean 被强制转换
?page=2       →  { page: 2 }         // number 被强制转换
```

这跟 Spring 的 `WebDataBinder` + `ConversionService` 行为一致（`List<Long> ids` 也能从 `ids=1&ids=2` 绑定），心智上可以无缝迁移。

**⚠️ 副作用 1：`removeAdditional: true`**

当 schema 声明了 `additionalProperties: false` 时，**未声明的请求字段会被静默删除**。这意味着：

```ts
schema: {
  body: {
    type: 'object',
    additionalProperties: false,
    properties: { name: { type: 'string' } },
  }
}
```

客户端传 `{ name: 'x', isAdmin: true }` → `req.body.isAdmin` **不存在**（不是报错，是被删了）。安全上没问题，但如果你的业务期望"拒绝未知字段"，需要自己在 `preValidation` 里检查或改用 `allErrors` + 自定义错误处理。

**⚠️ 副作用 2：`allErrors: false`**

校验失败只返回**第一个**错误，不是全部。这是为了防 DoS（大量错误信息本身是攻击面）。Spring 的 `@Valid` 默认也是 fail-fast（收集第一个错误就抛），行为一致；但如果你用 `jakarta.validation` 的 `Errors` 对象收集全部错误，语义就不同了。

**⚠️ 副作用 3：Ajv 的 `anyOf` + `coerceTypes` 有坑**

```ts
// ❌ 危险：0 和 false 会被强制转成 null
{ anyOf: [{ type: 'null' }, { type: 'number' }] }

// ✅ 用 nullable
{ type: 'number', nullable: true }
```

### 4.3 响应序列化：性能收益与"字段消失"陷阱

声明 `response` schema 后，Fastify 用 `fast-json-stringify` 序列化。**这个 schema 是白名单**：

```ts
const Order = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    total: { type: 'number' },
  },
}

app.get('/orders/:id', {
  schema: { response: { 200: Order } },
}, async () => {
  return {
    id: 'o-1',
    total: 99,
    internalCost: 42,     // ← 这个字段不会出现在响应里
    password: 'secret',   // ← 同上，永远不会泄漏
  }
})
```

响应体只有 `{"id":"o-1","total":99}`。

**这是特性不是 bug**，而且是**安全收益**：即使你在 Repository 里 `SELECT *`，实体上带着 `password_hash`、`deleted_at` 等敏感字段，Fastify 的响应 schema 会在序列化层把它们全部拦掉。这比"记得在 DTO 上打 `@JsonIgnore`"可靠得多。

**但要警惕**：如果你的响应 schema 写漏了字段，**前端拿不到，且没有任何报错**。类型系统能帮你发现（见 4.5），但纯 JS 项目里这是个常见事故源。

**另一个细节**：响应 schema 按**状态码**组织：

```ts
schema: {
  response: {
    200: SuccessSchema,
    404: ErrorSchema,
    '2xx': AnySuccessSchema,   // 匹配所有 2xx
    default: ErrorSchema,      // 兜底
  }
}
```

序列化函数是**按状态码缓存编译**的（用 `WeakMap`），所以不同状态码用不同 schema 不会互相干扰。

**Content-Type 级别的响应 schema**（多格式响应）：

```ts
response: {
  200: {
    content: {
      'application/json': { schema: JsonSchema },
      'application/vnd.v1+json': { schema: V1Schema },
    }
  }
}
```

### 4.4 共享 Schema 与 $ref

```ts
// 定义一次
app.addSchema({
  $id: 'Order',
  type: 'object',
  properties: {
    id: { type: 'string' },
    items: { type: 'array', items: { $ref: 'OrderItem#' } },
  },
})

app.addSchema({
  $id: 'OrderItem',
  type: 'object',
  properties: { sku: { type: 'string' }, qty: { type: 'integer' } },
})

// 引用
app.get('/orders', {
  schema: { response: { 200: { $ref: 'Order#' } } },
}, handler)
```

`$ref` 解析规则：

| 写法 | 含义 |
| --- | --- |
| `{ $ref: 'Order#' }` | 引用 `$id: 'Order'` 的 schema 根 |
| `{ $ref: 'Order#/properties/id' }` | 引用其某个子字段 |
| `{ $ref: '#Order' }` | 当前作用域内 `$id: '#Order'` 的 schema |
| `{ $ref: '#/$defs/foo' }` | 当前 schema 内 `$defs.foo` |

`addSchema` 也是**作用域隔离**的：子作用域可以引用父作用域的 schema，反之不行。

### 4.5 TypeScript 类型安全：TypeBox + Type Provider

这是 Fastify v5 最实用的改进之一：**Schema 即类型源**。

```ts
import { Type, type Static } from '@sinclair/typebox'
import { TypeBoxTypeProvider } from '@fastify/type-provider-typebox'

const app = Fastify({ logger: true }).withTypeProvider<TypeBoxTypeProvider>()

const OrderItem = Type.Object({
  sku: Type.String(),
  qty: Type.Integer(),
})

const CreateOrder = Type.Object({
  userId: Type.Integer(),
  items: Type.Array(OrderItem),
  coupon: Type.Optional(Type.String()),
})

// 类型导出，供业务层复用
export type CreateOrderDto = Static<typeof CreateOrder>

app.post('/orders', {
  schema: {
    body: CreateOrder,
    response: {
      201: Type.Object({
        id: Type.String(),
        total: Type.Number(),
      }),
    },
  },
}, async (req, reply) => {
  req.body.userId     // ✅ number
  req.body.items[0].sku  // ✅ string
  req.body.coupon     // ✅ string | undefined

  reply.code(201)
  return { id: 'o-1', total: 100 }
})
```

**收益**：

- `req.body` / `req.query` / `req.params` **自动推导类型**，零手写 DTO、零 `as` 断言。
- 校验、序列化、类型、OpenAPI 文档**四处同源**，不会漂移。
- v5 起 type provider 把类型拆成了 `validator` 与 `serializer` 两套（因为 v5 允许二者用不同 schema），用 TypeBox 时两者一致。

> **注意**：v5 中如果你的自定义 type provider 还是 v4 的写法（只有 `input`/`output`），需要改成 `validator` / `serializer`。`@fastify/type-provider-typebox` 和 `@fastify/type-provider-json-schema-to-ts` 的最新版本已经适配。

**不想引入 TypeBox？** 也有纯 JSON Schema + `json-schema-to-ts` 的方案：

```ts
import { FromSchema } from 'json-schema-to-ts'
import { JsonSchemaToTsProvider } from '@fastify/type-provider-json-schema-to-ts'

const app = Fastify().withTypeProvider<JsonSchemaToTsProvider>()
type Body = FromSchema<typeof bodySchema>
```

### 4.6 OpenAPI 文档自动生成

```ts
import swagger from '@fastify/swagger'
import swaggerUi from '@fastify/swagger-ui'

await app.register(swagger, {
  openapi: {
    openapi: '3.1.0',
    info: { title: 'Order Service', version: '1.0.0' },
    components: {
      securitySchemes: {
        bearerAuth: { type: 'http', scheme: 'bearer', bearerFormat: 'JWT' },
      },
    },
  },
})

await app.register(swaggerUi, { routePrefix: '/docs' })
```

**关键点**：

- `@fastify/swagger` **必须先于所有路由注册**（否则发现不到路由）。
- 版本兼容：`@fastify/swagger` ≥ 9.x 对应 Fastify 5.x；≥7 <9 对应 Fastify 4.x。
- schema 里的 `description` / `summary` / `tags` 会被写入 OpenAPI。
- 需要前端展示可另加 `@fastify/swagger-ui` 或 `@scalar/fastify-api-reference`。

**版本对照（容易踩坑）**：

| Fastify | @fastify/swagger | @fastify/type-provider-typebox |
| --- | --- | --- |
| 5.x | ≥ 9.x | ≥ 5.x（适配 v5 类型拆分） |
| 4.x | ≥ 7.x < 9.x | 4.x |

### 4.7 与 Spring 校验链的对照

| Spring | Fastify | 备注 |
| --- | --- | --- |
| `@Valid @RequestBody` + `jakarta.validation` | `schema.body` + Ajv | Fastify 内置，无需 starter |
| `@NotBlank @Size @Min` 等注解 | JSON Schema 关键字（`minLength` / `minimum` / `pattern`） | 声明式程度更高 |
| `@Valid` on `@RequestParam` | `schema.querystring` | |
| `@PathVariable` 校验 | `schema.params` | |
| `@InitBinder` + `ConversionService` | Ajv `coerceTypes` | 行为相近 |
| `springdoc-openapi` | `@fastify/swagger` | |
| Jackson `@JsonInclude` / `@JsonIgnore` | `response` schema 白名单 | Fastify 方式更可靠 |
| `@RestControllerAdvice` + `MethodArgumentNotValidException` | `setErrorHandler` + `error.validation` | |

**迁移的心智调整**：

- 注解 → JSON Schema：字段约束从注解挪到 schema，**和路由定义在一起**（不是和 DTO 放一起）。
- DTO 类 → TypeBox schema：DTO 的"运行时校验 + 类型"职责合并为一个 schema 对象。
- Fastify 的校验发生在**路由层**，而 Spring 的校验发生在**参数解析层**。结果一样，但 Fastify 更快（无反射）。

---

## 第 5 章：错误处理与可观测性

### 5.1 错误处理器的层级语义（实测）

`setErrorHandler` **遵循封装作用域**。这是实测结果（fastify 5.12.7）：

```ts
const app = Fastify()
app.setErrorHandler((err, req, reply) => reply.code(500).send({ where: 'root' }))

app.register(async (inst) => {
  inst.setErrorHandler((err, req, reply) => reply.code(500).send({ where: 'child' }))
  inst.get('/boom', async () => { throw new Error('x') })
})
app.get('/boom-root', async () => { throw new Error('x') })

// GET /boom      → {"where":"child"}   ← 子作用域的错误处理器
// GET /boom-root  → {"where":"root"}    ← 根作用域的错误处理器
```

**这是 Spring 做不到的干净**：Spring 里全局只有一个 `@RestControllerAdvice`，要实现"某个模块特殊处理"得靠 `@Order` + `instanceof` 判断 + `handler.getBeanType()` 之类的 hack。Fastify 里就是**作用域继承 + 覆盖**，天然干净。

> ⚠️ **注意**：如果你在**根作用域**注册了 `setErrorHandler`，它对所有子作用域生效（除非子作用域覆盖）。这跟 Spring 全局 Advice 的直觉一致。

### 5.2 业务异常的统一建模

Fastify 的错误处理核心约定：**错误对象上带 `statusCode`**。

```ts
// 定义业务异常
export class BizError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly statusCode = 400,
    public readonly details?: unknown,
  ) {
    super(message)
    this.name = 'BizError'
  }
}

// 全局错误处理
app.setErrorHandler((error, request, reply) => {
  request.log.error({ err: error }, 'request failed')

  if (error instanceof BizError) {
    return reply.code(error.statusCode).send({
      code: error.code,
      message: error.message,
      details: error.details,
    })
  }

  // 校验错误（400）
  if (error.validation) {
    return reply.code(400).send({
      code: 'VALIDATION_ERROR',
      message: `invalid ${error.validationContext}`,
      details: error.validation,
    })
  }

  // 其余一律 500，不暴露内部信息
  return reply.code(500).send({ code: 'INTERNAL_ERROR', message: 'Internal Server Error' })
})
```

关键属性：

| 属性 | 说明 |
| --- | --- |
| `error.statusCode` | 校验错误固定为 400；自定义错误由你设置 |
| `error.validation` | 校验失败的详情（Ajv 错误数组） |
| `error.validationContext` | `'body' \| 'querystring' \| 'params' \| 'headers'` |
| `error.code` | Fastify 内置错误码，如 `FST_ERR_CTP_BODY_TOO_LARGE` |

**推荐用 `@fastify/sensible`**（Fastify 官方维护）替代手写异常类，它提供了 `httpErrors.notFound()`、`badRequest()` 等一整套：

```ts
import sensible from '@fastify/sensible'
app.register(sensible)
app.get('/:id', async (req) => {
  if (!await exists(req.params.id)) {
    throw app.httpErrors.notFound('order not found')
  }
})
```

### 5.3 404 处理

```ts
app.setNotFoundHandler((request, reply) => {
  reply.code(404).send({
    code: 'NOT_FOUND',
    message: `Route ${request.method} ${request.url} not found`,
  })
})
```

`setNotFoundHandler` 同样遵循作用域规则。

### 5.4 Pino 日志与请求级 child logger

Fastify 内置 Pino（不是可选的）。v5 起，**自定义 logger 实例必须用 `loggerInstance`**，`logger` 选项只接受配置对象：

```ts
// ❌ v4 写法，v5 不再支持
const logger = pino()
Fastify({ logger })

// ✅ v5
Fastify({ loggerInstance: pino({ level: 'info' }) })
```

**每个请求自带一个带绑定字段的 child logger**，这是 Fastify 的杀手锏之一：

```ts
app.addHook('onRequest', async (req, reply) => {
  req.log.info('incoming request')   // 自动带上 reqId
})

app.get('/:id', async (req) => {
  req.log.info({ orderId: req.params.id }, 'loading order')
  // 输出：{"reqId":"req-3","orderId":"o-1","msg":"loading order", ...}
})
```

`reqId` 默认自动生成（`req-1`、`req-2`…），也可以自定义：

```ts
Fastify({ genReqId: (req) => req.headers['x-request-id'] as string })
```

**对比 Spring 的 SLF4J MDC**：Fastify 的 child logger 是**对象级别的**，不需要手动 put/remove；MDC 方案在异步/协程场景下容易串味，Fastify 没这个问题。

**开发环境美化输出**：

```ts
Fastify({
  logger: {
    transport: { target: 'pino-pretty' },
  },
})
```

### 5.5 指标、追踪与过载保护

| 能力 | Fastify 方案 | Spring 对应 |
| --- | --- | --- |
| 指标 | `prom-client` + 自写 hook | Micrometer + Actuator |
| 追踪 | `@opentelemetry/instrumentation-fastify` | Micrometer Tracing |
| 过载保护 | `@fastify/under-pressure`（事件循环延迟超阈值返回 503） | 无直接对应（Tomcat 自带线程池排队） |
| 请求 ID | 内置 `reqId` | Micrometer Tracing / Sleuth |
| 优雅关闭 | `app.close()` + `onClose` hook | `server.shutdown()` + `@PreDestroy` |

**`@fastify/under-pressure` 值得单独说**：Node 单线程的致命问题是一次 CPU 密集操作会阻塞所有请求。这个插件监控事件循环延迟，超过阈值时直接返回 503，保护自己在雪崩中存活。**生产环境强烈建议开启**。

```ts
app.register(underPressure, {
  maxEventLoopDelay: 1000,  // ms
  maxHeapUsedBytes: 400 * 1024 * 1024,
  retryAfter: 50,
})
```

---

## 第 6 章：依赖注入 —— Fastify 没有 DI 容器

### 6.1 三种主流注入模式

**模式 A：闭包工厂（最常用，推荐）**

```ts
// src/routes/orders.ts
export function orderRoutes(service: OrderService) {
  return async function (app: FastifyInstance) {
    app.get('/', async (req) => service.list(req.query))
    app.get('/:id', async (req) => service.get(req.params.id))
  }
}

// src/app.ts
app.register(orderRoutes(orderService))
```

优点：依赖显式、可测（直接传 mock）、无魔法。对应 Spring 里的"构造器注入"，只是把 Spring 容器承担的"组装"工作交给了**代码本身**。

**模式 B：装饰器（用于基础设施）**

```ts
import fp from 'fastify-plugin'

export interface Db {
  query<T>(sql: string, params?: unknown[]): Promise<T[]>
}

// TypeScript 类型增强，让 app.db 有类型
declare module 'fastify' {
  interface FastifyInstance {
    db: Db
  }
}

export default fp(async (app, opts: { url: string }) => {
  const pool = new Pool({ connectionString: opts.url })
  app.decorate('db', {
    query: async (sql, params) => (await pool.query(sql, params)).rows,
  })
  app.addHook('onClose', async () => { await pool.end() })
}, { name: 'db' })
```

用的时候：

```ts
app.db.query('select * from orders where id = $1', [id])
```

**模式 C：插件 + `opts` 传参（推荐的可测试方式）**

```ts
// plugins/repositories.ts
export default fp(async (app, opts: { db: Db }) => {
  app.decorate('orders', new OrderRepository(opts.db))
}, { name: 'repositories', dependencies: ['db'] })
```

### 6.2 能力差距对照表

| Spring 能力 | Fastify 是否有替代 | 现实答案 |
| --- | --- | --- |
| 构造器注入 | ❌ | 用闭包工厂，手动传参 |
| `@Autowired` / `@Qualifier` | ❌ | 用 `decorate` + `opts`，语义更简单但更显式 |
| Bean 生命周期（`@PostConstruct`） | ⚠️ | 手动在插件里 `await` 初始化；`onReady` hook 是全局版本 |
| `@Profile` | ⚠️ | 用环境变量判断 |
| AOP（`@Aspect`） | ⚠️ | 用 hook（但只能切请求边界，切不到方法内部） |
| `@Transactional` | ❌ | Repository 层显式管理（见 6.3） |
| `@ConfigurationProperties` | ⚠️ | `@fastify/env`（基于 TypeBox 的环境变量校验） |
| `@RestControllerAdvice` | ✅ | `setErrorHandler`（且支持作用域覆盖） |
| `@PreAuthorize` | ⚠️ | `preHandler` hook 或自建装饰器 |
| 自动装配 Starter | ⚠️ | 插件 + `fp`，但需要自己写装配逻辑 |
| 循环依赖检测 | ❌ | 自己避免；Fastify 没有容器也就没有这个问题 |
| AOP 事务传播（`REQUIRES_NEW`） | ❌ | 显式 API 调用 |

### 6.3 事务边界放哪里

Spring 开发者最容易在 Fastify 里踩的坑，是**试图用 hook 实现事务**。

**错误做法**：

```ts
// ❌ 不要这样做
app.addHook('preHandler', async (req, reply) => {
  await db.begin()
  reply.addHook('onResponse', async () => { await db.commit() })
})
```

原因：
1. `onResponse` 在响应**已经发给客户端之后**才执行，事务提交失败时你已经返回 200 了。
2. 响应是流式/长连接时，事务边界完全失控。

**正确做法：事务在 Repository / Service 的显式方法里**。

```ts
export class OrderService {
  constructor(private readonly db: Db) {}

  async create(dto: CreateOrderDto): Promise<Order> {
    return this.db.transaction(async (tx) => {
      const [order] = await tx.query('insert into orders(...) values(...)', [...])
      await tx.query('insert into order_items(...) values(...)', [...])
      return order
    })
  }
}
```

**原则**：**事务边界 = 业务用例边界 = Service 方法边界**。这和 Spring 的 `@Transactional` 加在 Service 上其实是同一个理念，只是 Fastify 里没有 AOP，所以要显式调用。

如果确实想要注解式体验，可以引入 `tsyringe` / `typedi` 做 DI，但**不要同时用装饰器和 AOP 织入**——Fastify 的 hook 体系已经能覆盖大部分横切需求，引入 AOP 反而增加心智负担。

### 6.4 什么时候你该换回 Spring

**如果你的项目具备以下特征，Java/Spring 可能仍是更好的选择**：

- 团队没有 Node 经验，但有深厚 Java 经验（学习成本 > 性能收益）。
- 业务复杂度高、大量领域建模和事务编排（Spring 的事务抽象更成熟）。
- 需要连接大量只提供 Java SDK 的中间件/厂商产品。
- 已有大量 Java 业务代码需要复用。

**Fastify 的优势场景**：

- 需要高吞吐/低延迟的**网关、BFF、聚合层**。
- 轻量微服务（Go 那种"小而美"），需要**启动快、内存小**的镜像。
- Serverless / 边缘部署。
- 与前端同构（TypeScript 全栈，共享类型定义）。

---

## 第 7 章：工程化 —— 项目结构、配置、测试

### 7.1 目录结构

推荐结构（对应 Spring Boot 的分层，但按 Fastify 的插件/作用域组织）：

```text
my-service/
├── src/
│   ├── app.ts                 # buildApp 工厂：装配一切
│   ├── server.ts              # 启动入口：读配置、listen、优雅关闭
│   ├── config/
│   │   ├── env.ts             # @fastify/env 配置校验
│   │   └── index.ts
│   ├── plugins/
│   │   ├── db.ts              # fp 包裹，decorate('db')
│   │   ├── auth.ts            # fp 包裹，addHook('preHandler')
│   │   └── observability.ts   # OTel / metrics
│   ├── modules/               # ★ 业务模块 = 一个作用域
│   │   ├── orders/
│   │   │   ├── routes.ts      # 插件：注册该模块的路由
│   │   │   ├── service.ts     # 业务逻辑
│   │   │   ├── repository.ts  # 数据访问
│   │   │   └── schemas.ts     # TypeBox schemas
│   │   └── users/
│   │       └── ...
│   ├── common/
│   │   ├── errors.ts          # BizError
│   │   └── types.ts
│   └── types/
│       └── fastify.d.ts       # 类型增强（decorate 的类型声明）
├── tests/
│   ├── orders.test.ts
│   └── helpers.ts
├── package.json
├── tsconfig.json
└── Makefile
```

**关键设计**：`modules/` 下的每个目录是一个**独立的作用域**。模块内部的 hook、装饰器不会泄漏到其他模块。这天然实现了**模块化单体（Modular Monolith）**。

### 7.2 build 工厂模式

这是 Fastify 工程化**最重要的一个约定**：把应用构建和进程启动分开。

```ts
// src/app.ts
import Fastify, { type FastifyInstance } from 'fastify'
import dbPlugin from './plugins/db'
import { orderRoutes } from './modules/orders/routes'

export interface BuildOptions {
  logger?: boolean
  dbUrl?: string
}

export async function buildApp(opts: BuildOptions = {}): Promise<FastifyInstance> {
  const app = Fastify({
    logger: opts.logger ?? true,
    trustProxy: true,
  })

  // 错误处理放最前
  app.setErrorHandler(errorHandler)

  // 基础设施
  await app.register(dbPlugin, { url: opts.dbUrl })

  // 业务模块
  await app.register(orderRoutes({ db: app.db }))

  return app
}
```

```ts
// src/server.ts
import { buildApp } from './app'

const app = await buildApp({ logger: true })

await app.listen({ port: Number(process.env.PORT ?? 3000), host: '0.0.0.0' })
```

**为什么这么写**：

- 测试可以 `buildApp({ logger: false })` 拿到一个干净的实例，用 `inject()` 直接打请求，**不需要真的监听端口**（对应 Spring 的 `@SpringBootTest` + `MockMvc`）。
- 启动逻辑只有一份，不会出现"测试环境和生产环境启动方式不同"的经典问题。

### 7.3 配置管理

用 `@fastify/env` 做**带校验的配置**（对应 `@ConfigurationProperties` + `@Validated`）：

```ts
import env from '@fastify/env'
import { Type } from '@sinclair/typebox'

await app.register(env, {
  schema: {
    type: 'object',
    properties: {
      NODE_ENV: { type: 'string', default: 'development' },
      PORT: { type: 'integer', default: 3000 },
      DB_URL: { type: 'string' },
      LOG_LEVEL: { type: 'string', default: 'info' },
      JWT_SECRET: { type: 'string' },
    },
    required: ['DB_URL', 'JWT_SECRET'],
  },
})

app.config.DB_URL  // 类型安全，缺失直接启动失败
```

**这比 Spring 的 `@Value` 更好**：配置缺失在**启动时**就报错，而不是在第一次访问数据库时。

**12-Factor 建议**：配置全部来自环境变量；不同环境用不同环境变量注入（K8s ConfigMap / Secret）；不要在代码里 `if (env === 'prod')` 分支。

### 7.4 测试

**`app.inject()` 是 Fastify 的杀手锏**：它用 `light-my-request` 在进程内模拟一次 HTTP 请求，**不经过真实 socket**，速度快（微秒级）且可以断言完整响应。

```ts
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { buildApp } from '../src/app'

test('GET /orders/:id 返回订单', async (t) => {
  const app = await buildApp({ logger: false, dbUrl: 'postgres://test' })

  t.after(async () => { await app.close() })

  const res = await app.inject({
    method: 'GET',
    url: '/orders/o-1',
  })

  assert.equal(res.statusCode, 200)
  assert.deepEqual(res.json(), { id: 'o-1', total: 100 })
})
```

**与 Spring 测试的对照**：

| Spring | Fastify |
| --- | --- |
| `MockMvc.perform()` | `app.inject()` |
| `@WebMvcTest` | `buildApp()` + mock 掉基础设施插件 |
| `@SpringBootTest` | `buildApp()` + 真实依赖（用 testcontainers） |
| `TestRestTemplate` | `inject` 或全局 `fetch` |
| `WebTestClient` | `inject` |
| `@MockBean` | 手写 mock 对象注入（模式 A/B） |

**依赖 mock 的实用做法**：把基础设施做成可注入的，测试时传入假实现。

```ts
export async function buildApp(opts: BuildOptions = {}) {
  const app = Fastify({ logger: opts.logger ?? true })

  const db = opts.db ?? createRealDb(opts.dbUrl)
  await app.register(dbPlugin, { db })   // 插件接收 db 实例，不自己建
  ...
}
```

> 社区也常用 [`@fastify/mock` 系列之外的方案](https://github.com/fastify/fastify-mock)：`fastify-mock`（装饰器 mock）、`fastify-mock-send`（mock `reply.send`）。但更推荐**在架构上留出注入点**，而不是在测试里打补丁。

**测试运行器**：`node:test`（内置，零依赖，v5 推荐）或 `vitest`（更好的 DX 和生态）。我推荐 **vitest**（watch 模式、覆盖率、mock 一站式），但团队想零依赖就用 `node --test`。

### 7.5 autoload：按目录自动注册路由

`@fastify/autoload` 可以按目录结构自动注册路由插件，省去手动 `register`：

```ts
import autoload from '@fastify/autoload'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const dirname = path.dirname(fileURLToPath(import.meta.url))

await app.register(autoload, {
  dir: path.join(dirname, 'modules'),
  dirNameRoutePrefix: true,       // modules/orders/routes.ts → 前缀 /orders
  matchFilter: (path) => path.endsWith('routes.ts'),
  ignoreFilter: (path) => path.includes('__tests__'),
  encapsulate: true,               // 每个目录一个独立作用域 ★
  autoHooks: true,                 // 自动加载 .autohooks.ts
  cascadeHooks: true,
})
```

**`encapsulate: true` 是重点**：每个模块目录成为一个独立作用域，天然实现模块隔离 —— 这正是 Spring 用 `spring.modulith` 或多模块 Maven 才能做到的事，在这里是一个配置项。

---

## 第 8 章：生产实践

### 8.1 优雅关闭

Node 进程收到 `SIGTERM`（K8s 滚动更新）时，必须先停止接收新请求、等存量请求处理完、再关闭资源。Fastify 提供了完整支持：

```ts
// src/server.ts
const app = await buildApp()

// onClose hook 里关闭资源（DB 连接池、Redis 等）
// app.close() 会触发所有 onClose hook

let closing = false
const shutdown = async (signal: string) => {
  if (closing) return
  closing = true
  app.log.info(`${signal} received, shutting down`)
  try {
    await app.close()      // 停止监听 + 执行 onClose hooks
    process.exit(0)
  } catch (err) {
    app.log.error(err)
    process.exit(1)
  }
}

process.on('SIGTERM', () => shutdown('SIGTERM'))
process.on('SIGINT', () => shutdown('SIGINT'))
```

配合 K8s：

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sh", "-c", "sleep 5"]   # 先等负载均衡摘掉这个 Pod
terminationGracePeriodSeconds: 30
```

### 8.2 健康检查与就绪探针

```ts
app.get('/health/live', async () => ({ status: 'ok' }))   // liveness：进程活着吗

app.get('/health/ready', async (req, reply) => {
  try {
    await app.db.query('select 1')
    return { status: 'ready' }
  } catch (err) {
    reply.code(503)
    return { status: 'not-ready', reason: 'db unavailable' }
  }
})
```

**注意**：Spring Boot Actuator 的 `/actuator/health/liveness` 和 `/readiness` 语义完全一致，直接映射即可。

### 8.3 反向代理下的真实 IP

在 Nginx / Ingress / ELB 后面，`req.ip` 默认是**代理的 IP**，不是客户端 IP。这会导致：

- 日志里所有请求来源都一样
- IP 限流失效
- 审计日志错误

```ts
Fastify({
  trustProxy: true,        // 信任所有上游代理（简单但有伪造风险）
  // 或者指定可信代理：
  // trustProxy: ['127.0.0.1', '10.0.0.0/8'],
})
```

**安全提醒**：`trustProxy: true` 时客户端可以伪造 `X-Forwarded-For`。生产环境尽量用**具体 IP 列表或 CIDR**，或只信任一跳。

Spring Boot 对应 `server.forward-headers-strategy`。

### 8.4 超时、体积限制与连接复用

**实测默认值（Fastify 5.12.7）**：

| 配置 | 默认值 | 说明 |
| --- | --- | --- |
| `bodyLimit` | **1048576（1 MiB）** | 超限返回 413 `FST_ERR_CTP_BODY_TOO_LARGE` |
| `requestTimeout` | 0（不超时） | 从收到请求到请求体接收完毕 |
| `connectionTimeout` | 0（不超时） | socket 空闲超时 |
| `handlerTimeout` | 0（不超时） | handler 执行超时（基于 `request.signal` 协作式取消） |

> **⚠️ 全部是"不超时"，这在生产环境是危险的。** 一个卡死的下游依赖可以让请求永远挂着，堆积内存直到 OOM。

**推荐生产配置**：

```ts
Fastify({
  bodyLimit: 2 * 1024 * 1024,   // 按业务调整
  requestTimeout: 10_000,        // 10s 内必须收完 body
  connectionTimeout: 72_000,     // 72s 对齐 ALB/Nginx 默认
  handlerTimeout: 30_000,        // handler 超时 → 触发 request.signal abort
  keepAliveTimeout: 72_000,      // 与上游代理一致
  keepAliveMaxTimeout: 10 * 60_000,
  maxRequestsPerSocket: 0,       // 0 = 不限
})
```

**`handlerTimeout` 的协作式取消**：超时时 Fastify 会 abort `request.signal`，你可以把 signal 传给数据库驱动，让查询真正取消而不是白跑。这比 Spring 的 `@Transactional(timeout=)` 更彻底（Spring 只是抛异常，底层 IO 未必停）。

### 8.5 多进程与水平扩展

Node 单进程只能吃满一个 CPU 核。水平扩展方式：

**方式 A：Node 内置 `cluster`**

```ts
import cluster from 'node:cluster'

if (cluster.isPrimary) {
  for (let i = 0; i < 4; i++) cluster.fork()
  cluster.on('exit', () => cluster.fork())
} else {
  const app = await buildApp()
  app.listen({ port: 3000 })
}
```

**方式 B：容器编排（推荐）**

每个容器跑一个进程，用 K8s HPA 按 CPU 扩缩容。**这是云原生时代的默认答案** —— 把进程管理交给编排器。

**方式 C：`@fastify/cluster` / `fastify-cluster`**（社区插件，需谨慎评估维护状态）。

**Fastify 在多核上的建议**：用 `cluster` 或容器 + PM2/K8s，**不要用 `worker_threads` 跑 HTTP 处理**（HTTP server 在 worker_threads 里支持有限，且 `SharedArrayBuffer` 序列化开销会吃掉收益）。

### 8.6 生产配置检查表

- [ ] `bodyLimit` 按业务设置，不要用 1MB 默认值硬扛大文件上传
- [ ] `requestTimeout` / `handlerTimeout` / `connectionTimeout` 都显式设置
- [ ] `trustProxy` 设为具体 IP 列表，而不是 `true`
- [ ] 开启 `@fastify/under-pressure` 过载保护
- [ ] `SIGTERM` 优雅关闭 + `preClose` 停止接流量
- [ ] 健康检查区分 liveness / readiness
- [ ] `logger` 级别生产用 `info`，不要用 `debug`（结构化日志的 IO 成本不低）
- [ ] 日志中**不要打印**完整 body（`req.body` 里可能有密码、身份证）
- [ ] 开启 `@fastify/helmet`（安全响应头）
- [ ] 开启 `@fastify/cors`（如果前后端分离）
- [ ] 跨域来源用**白名单**，不要 `origin: '*'` + `credentials: true`（浏览器会拒绝）
- [ ] 优雅关闭时间 < K8s `terminationGracePeriodSeconds`
- [ ] 接入 OpenTelemetry，traceId 贯穿日志

---

## 第 9 章：与 Spring Cloud 生态集成

### 9.1 服务注册与发现

| 注册中心 | Node 客户端 |
| --- | --- |
| Nacos | `nacos` npm 包（阿里官方） |
| Consul | `consul` npm 包（HashiCorp 官方） |
| Eureka | 社区实现较少，通常用 HTTP 直接调 |
| Kubernetes | **不需要客户端**，用 `K8S_SERVICE_HOST` 环境变量 + DNS 直连（推荐） |

**Kubernetes 场景（推荐）**：不要在应用里做服务发现，直接用 DNS：

```ts
const baseUrl = `http://order-service.${namespace}.svc.cluster.local`
```

或者用 `undici` 的 Pool + K8s Service 做负载均衡。

### 9.2 配置中心

| 配置中心 | Node 客户端 |
| --- | --- |
| Nacos | `nacos` npm 包（支持 config listener 动态刷新） |
| Apollo | `apollo-client-nodejs` |
| Consul | `consul` 的 KV API |
| Spring Cloud Config | 直接 HTTP 调 `/actuator/env` 或自定义端点 |

配置热更新在 Node 生态里比 Java 弱（Java 有 `@RefreshScope`），常见做法是：**收到变更事件 → 重建受影响的对象**（而不是原地改），因为 Node 的模块是常驻内存的闭包。

### 9.3 服务间调用

**首选 Node 内置的 `fetch` / `undici`**：

```ts
// 用 undici 的 Pool 复用连接
import { Pool, request } from 'undici'

const pool = new Pool('http://user-service:3000', {
  connections: 32,
  pipelining: 1,
})

const res = await request('http://user-service:3000/users/1', {
  dispatcher: pool,
  headers: { 'x-request-id': traceId },
})
```

`undici` 的 `Pool` 是 Fastify 官方推荐的 HTTP 客户端（Fastify 团队维护），性能优于 `axios`。

**超时与重试**：Node 18+ 的 `fetch` 用 `AbortSignal.timeout(3000)`。

### 9.4 熔断限流降级

| Spring Cloud 组件 | Node 对应 |
| --- | --- |
| Spring Cloud CircuitBreaker + Resilience4j | `opossum`（Netflix 出品，事实标准） |
| `spring-cloud-starter-alibaba-sentinel` | `sentinel-nodejs`（阿里官方） |
| Bucket4j / Redis 限流 | `@fastify/rate-limit`（支持 Redis store） |
| Resilience4j Bulkhead | `@fastify/under-pressure` + 自定义信号量 |

**`@fastify/rate-limit` 用法**：

```ts
app.register(rateLimit, {
  max: 100,
  timeWindow: '1 minute',
  // 分布式限流需要 Redis store
  // redis: new Redis(...)
  keyGenerator: (req) => req.headers['x-user-id'] as string ?? req.ip,
})
```

**熔断器（opossum）**：

```ts
import CircuitBreaker from 'opossum'

const breaker = new CircuitBreaker(async (userId: string) => {
  const res = await fetch(`http://user-service/users/${userId}`)
  if (!res.ok) throw new Error(`upstream ${res.status}`)
  return res.json()
}, {
  timeout: 2000,
  errorThresholdPercentage: 50,
  resetTimeout: 10000,
})
```

### 9.5 用 Fastify 做 BFF / 网关

Fastify 做 BFF（Backend for Frontend）或轻量 API 网关是**最推荐的落地场景**：

- **启动快、内存小** → 冷启动友好，适合 FaaS 和 K8s 自动扩缩
- **Schema 契约强** → 聚合多个下游服务时，能保证响应结构稳定
- **性能** → 作为网关层，QPS 直接决定用户体验

**Spring Cloud Gateway 是 WebFlux（响应式）**，Fastify 不是。如果你要做**流式聚合**（多个下游结果边到边返回，如 `Promise.allSettled` + SSE），Fastify 也能做，但编程模型是"Promise 编排"而不是"响应式流"：

```ts
// SSE 扇出：多个下游并行，任意一个就绪即推送
app.get('/dashboard', async (req, reply) => {
  reply.raw.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  })

  const sources = await Promise.allSettled([
    fetchJson(`${ORDER_URL}/summary`),
    fetchJson(`${USER_URL}/summary`),
  ])

  for (const s of sources) {
    reply.raw.write(`data: ${JSON.stringify(s.status === 'fulfilled' ? s.value : null)}\n\n`)
  }
  reply.raw.end()
})
```

用 `@fastify/sse` 可以更规范。

### 9.6 链路追踪

```ts
import { NodeSDK } from '@opentelemetry/sdk-node'
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node'
import { FastifyInstrumentation } from '@opentelemetry/instrumentation-fastify'

const sdk = new NodeSDK({
  instrumentations: [
    getNodeAutoInstrumentations(),
    new FastifyInstrumentation(),
  ],
})
sdk.start()
```

OpenTelemetry 的 Fastify instrumentation 会自动创建 span，并把 traceId 注入到 Fastify 的日志上下文。

**对应 Spring Cloud Sleuth / Micrometer Tracing**。差别：Java 生态用 Micrometer 统一抽象，Node 生态基本只有 OTel 一条路。

---

## 第 10 章：选型决策与常见误区

### 10.1 决策树

```mermaid
flowchart TD
    Start["要做一个 Node 后端服务"] --> Q1{"已有大量 Java 业务代码<br/>需要复用或强事务编排？"}
    Q1 -->|是| Spring["用 Spring Boot<br/>（或混合架构）"]
    Q1 -->|否| Q2{"主要痛点是性能/启动速度/内存？"}
    Q2 -->|否| Q3{"团队有 NestJS 经验<br/>或需要强 DI + 装饰器规范？"}
    Q2 -->|是| Fastify["用 Fastify ✅"]
    Q3 -->|是| Nest["用 NestJS"]
    Q3 -->|否| Q4{"部署在边缘/Serverless？"}
    Q4 -->|是| Hono["用 Hono"]
    Q4 -->|否| Express["用 Express/Koa<br/>（生态优先）"]
```

### 10.2 什么场景不该用 Fastify

- **CPU 密集型服务**：图像处理、复杂算法、加解密 —— Node 单线程会阻塞一切，用 Go/Rust 更合适。
- **大量既有 Java SDK 依赖**：没有 Node 版本的中间件/厂商 SDK。
- **团队完全没有 Node 经验**：学习成本远超性能收益，Spring Boot 是更理性的选择。
- **需要复杂事务传播 / 分布式事务编排**：Spring 的事务抽象更成熟。
- **超大型团队 + 强规范治理**：NestJS 的装饰器 + 模块 + DI 更适合"框架管规范"。

### 10.3 新人最容易犯的 12 个错

| # | 错误 | 后果 | 正确做法 |
| --- | --- | --- | --- |
| 1 | 用了 `fastify-plugin` 导致 `prefix` 失效 | 路由前缀丢失 | 需要前缀就别包 `fp` |
| 2 | 父作用域访问子作用域的 decorator | `undefined` | 用 `fp` 上浮，或通过 `opts` 传递 |
| 3 | async hook 里 `reply.send()` 后没 `return reply` | `FST_ERR_REP_ALREADY_SENT` | 永远 `return reply` |
| 4 | 混用 `done` 回调和 `async/await` | hook 链执行两次 | 全项目统一一种风格 |
| 5 | 没写 `response` schema | 响应慢，且敏感字段泄漏 | 每个路由都声明响应 schema |
| 6 | 写了 `response` schema 但漏字段 | 前端拿不到数据且无报错 | 用 TypeBox 让类型系统兜底 |
| 7 | 依赖 v4 的 `jsonShortHand` 写法 | 启动即报错 | v5 必须写完整 schema |
| 8 | 用 `logger` 传自定义 logger 实例 | v5 报错 | 用 `loggerInstance` |
| 9 | 生产环境不设超时 | 内存耗尽 / OOM | 显式设置三个 timeout |
| 10 | `trustProxy: true` | IP 可伪造 | 用具体 IP/CIDR 列表 |
| 11 | 在 hook 里做事务 | 响应已发出才提交 | 事务放 Service 方法里 |
| 12 | 用 `reply.sent = true` 阻止发送 | v5 已禁止 | 用 `reply.hijack()` |

---

## 附录 A：Fastify v4 与 v5 迁移要点

| 变更 | v4 | v5 |
| --- | --- | --- |
| Node 版本 | 14+ | **20+** |
| Schema 写法 | 支持简写（`jsonShortHand`） | **必须完整 JSON Schema** |
| 自定义 logger | `logger: pinoInstance` | **`loggerInstance: pinoInstance`** |
| `reply.redirect()` | `redirect(301, url)` | **`redirect(url, 301)`** |
| `reply.getResponseTime()` | 有 | **改为 `reply.elapsedTime`** |
| `request.connection` | 有 | **改为 `request.socket`** |
| `reply.sent = true` | 可用于阻止发送 | **改用 `reply.hijack()`** |
| 路由版本控制 | `version` / `versioning` | **改用 `constraints: { version }`** |
| 路由定义访问 | `req.routeSchema` / `req.routeConfig` / `req.routerPath` | **统一用 `req.routeOptions.{schema,config,url,method}`** |
| `decorateRequest` 传对象 | `decorateRequest('x', { a: 1 })` | **禁止引用类型**，改用函数或 getter |
| `req.hostname` | 含端口（`localhost:3000`） | **不含端口**，另有 `req.host` / `req.port` |
| query 分隔符 | 支持 `;` | **默认不支持**（可 `useSemicolonDelimiter: true` 开启） |
| `req.params` 原型 | 有原型（`hasOwnProperty` 可用） | **无原型**（用 `Object.hasOwn`） |
| 插件 API | 可混用 callback/promise | **不可混用** |
| `listen()` 签名 | `listen(8000)` | **`listen({ port: 8000 })`** |
| type provider 类型 | `input` / `output` | **`validator` / `serializer`** |
| HTTP 方法 | 含 PROPFIND / TRACE 等 | **移除**（可用 `addHttpMethod` 加回） |
| `DELETE` + JSON body | 允许空 body | **不允许** |
| `time`/`date-time` 格式 | 不强制时区 | **强制时区**（可用 `iso-date-time` 兼容） |
| 诊断通道 | 无 | **支持 Node Diagnostics Channel** |

---

## 附录 B：核心 API 速查表

**创建与启动**

```ts
const app = Fastify({ logger: true, bodyLimit: 1024 * 1024 })
await app.register(plugin, opts)
await app.listen({ port: 3000, host: '0.0.0.0' })
await app.ready()      // 等待所有插件加载完（测试用）
await app.close()      // 优雅关闭，触发 onClose
```

**路由**

```ts
app.get(url, options?, handler)
app.route({ method, url, handler, schema, preHandler })
app.register(routes, { prefix: '/api/v1' })
```

**Request 常用属性**

| 属性 | 说明 |
| --- | --- |
| `req.body` | 解析后的 body（JSON 对象） |
| `req.query` | 查询参数（对象，已 coerce） |
| `req.params` | 路径参数 |
| `req.headers` | 请求头（小写键） |
| `req.ip` | 客户端 IP（受 `trustProxy` 影响） |
| `req.hostname` / `req.host` / `req.port` | 主机信息 |
| `req.id` / `req.reqId` | 请求 ID |
| `req.log` | 带绑定字段的 Pino child logger |
| `req.routeOptions` | 路由定义（schema / config / url / method） |
| `req.raw` | 原始 `IncomingMessage` |
| `req.signal` | AbortSignal（`handlerTimeout` 触发） |

**Reply 常用方法**

```ts
reply.code(201).send(data)
reply.header('x-key', 'value')
reply.type('application/json')
reply.redirect('/new-url', 301)
reply.hijack()          // 接管底层响应，跳过后续 hook
reply.serializer(fn)    // 自定义序列化
reply.elapsedTime       // 耗时（ms）
```

**应用级 API**

```ts
app.decorate(name, value)
app.decorateRequest(name, value | getter)
app.addHook(name, fn)
app.setErrorHandler(fn)
app.setNotFoundHandler(fn)
app.addSchema(schema)
app.setValidatorCompiler(fn)
app.setSerializerCompiler(fn)
app.register(async (instance) => { /* ... */ })
```

---

## 附录 C：常用插件清单

| 插件 | 用途 | Fastify 5 版本 |
| --- | --- | --- |
| `@fastify/swagger` | OpenAPI 文档生成 | ≥ 9.x |
| `@fastify/swagger-ui` | Swagger UI | ≥ 5.x |
| `@fastify/type-provider-typebox` | TypeBox 类型推导 | ≥ 5.x |
| `@fastify/type-provider-json-schema-to-ts` | JSON Schema → TS 类型 | 最新 |
| `@fastify/autoload` | 按目录自动加载路由 | 最新 |
| `@fastify/cors` | 跨域 | ≥ 10.x |
| `@fastify/helmet` | 安全响应头 | ≥ 12.x |
| `@fastify/rate-limit` | 限流 | ≥ 10.x |
| `@fastify/under-pressure` | 过载保护 | ≥ 8.x |
| `@fastify/sensible` | HTTP 错误工具集 | ≥ 6.x |
| `@fastify/jwt` | JWT 认证 | ≥ 9.x |
| `@fastify/session` | 会话 | ≥ 11.x |
| `@fastify/cookie` | Cookie 解析/序列化 | ≥ 11.x |
| `@fastify/static` | 静态文件 | ≥ 8.x |
| `@fastify/multipart` | 文件上传 | ≥ 9.x |
| `@fastify/websocket` | WebSocket | ≥ 11.x |
| `@fastify/sse` | Server-Sent Events | 最新 |
| `@fastify/formbody` | 表单解析 | ≥ 8.x |
| `@fastify/env` | 环境变量校验 | 最新 |
| `@fastify/accept-negotiator` | 内容协商 | 最新 |
| `fastify-plugin` | 打破封装 | v5 兼容 |
| `undici` | HTTP 客户端（官方推荐） | — |
| `opossum` | 熔断器 | — |

> ⚠️ **版本务必核对**：Fastify 官方插件通常与框架主版本严格绑定，装之前先看插件 README 的兼容性表格。

---

## 附录 D：参考资源

**官方文档**

- Fastify 官网与文档：<https://fastify.dev/>
- 生命周期：<https://fastify.dev/docs/latest/Reference/Lifecycle/>
- 钩子：<https://fastify.dev/docs/latest/Reference/Hooks/>
- 插件：<https://fastify.dev/docs/latest/Reference/Plugins/>
- 封装：<https://fastify.dev/docs/latest/Reference/Encapsulation/>
- 校验与序列化：<https://fastify.dev/docs/latest/Reference/Validation-and-Serialization/>
- 测试：<https://fastify.dev/docs/latest/Guides/Testing/>
- v5 迁移指南：<https://fastify.dev/docs/latest/Reference/Guides/Migration-Guide-V5/>

**源码与社区**

- 核心仓库：<https://github.com/fastify/fastify>
- 插件列表：<https://github.com/fastify/fastify-plugins>
- 生态总览：<https://fastify.dev/docs/latest/Guides/Ecosystem/>

**相关阅读**

- 性能基准：<https://fastify.dev/benchmarks/>
- `find-my-way`（路由树）：<https://github.com/delvedor/find-my-way>
- `avvio`（插件加载器）：<https://github.com/fastify/avvio>
- `fast-json-stringify`：<https://github.com/fastify/fast-json-stringify>
- `light-my-request`（inject 实现）：<https://github.com/fastify/light-my-request>

---

## 写在最后

如果你从 Spring 迁移过来，最需要转变的**不是 API，而是三个观念**：

1. **没有隐式魔法**。Spring 的 DI、AOP、事务、配置绑定都是"容器在背后帮你完成的"。Fastify 里每一次依赖获取都是显式的。这看起来更啰嗦，但换来的是**可预测性**：你知道对象什么时候创建、什么时候销毁、谁持有它。

2. **契约优先于实现**。Fastify 把"这个接口长什么样"写在路由的 schema 里，一次声明产出校验、序列化、类型、文档四样东西。这个约束一开始会觉得麻烦，但会倒逼你把 API 设计想清楚。

3. **单线程是最大的约束**。所有架构决策（不要阻塞 IO、CPU 任务放 worker、水平扩展靠进程）都源于这一点。Spring 里你可以随手 `Thread.sleep()`，Node 里这是**所有请求的死刑判决**。

把这三点吃透，Fastify 剩下的部分就只是查文档了。
