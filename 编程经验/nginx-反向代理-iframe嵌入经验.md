# nginx 反向代理 iframe 嵌入经验

## 使用场景

通过 nginx 反向代理到后端服务（Grafana / Prometheus / cAdvisor / Kibana / 自建 web 等），希望在父页面用 `<iframe>` 嵌入显示。本经验适用：

1. iframe 嵌入后**显示空白页**，但 `curl http://反代域名/` 直接访问是 200 OK
2. 浏览器 DevTools Console 报错含 `X-Frame-Options` 或 `Content-Security-Policy`
3. 服务**直连**时（如 `http://localhost:3000`）iframe 嵌入正常，但通过 nginx 反代后**不能**嵌入
4. 不同服务有的能嵌入有的不能（说明问题在上游 header 而不是 nginx 本身）

典型错误关键字：
- `Refused to display in a frame because an ancestor violates the following Content Security Policy directive`
- `Refused to display 'http://xxx' in a frame because it set 'X-Frame-Options' to 'deny'`
- `This page cannot be displayed in a frame`
- `X-Frame-Options: deny`
- `frame-ancestors 'self'`

---

## 核心经验

### 1. 上游服务默认会带 `X-Frame-Options: deny`，nginx 反代不会自动去掉

**很多 web 服务默认就在响应里加 `X-Frame-Options: deny` 防止 clickjacking**：

| 服务 | 默认 X-Frame-Options |
|---|---|
| Grafana | `deny` |
| Kibana | `deny` |
| Prometheus | 不发（默认能嵌入） |
| cAdvisor | 不发（默认能嵌入） |
| Spring Boot (with default security) | `DENY` |
| Django (with XFrameOptionsMiddleware) | `DENY` |

**nginx 反代默认透传上游的所有响应头**。所以即使反代配置正确，浏览器看到 `X-Frame-Options: deny` 就会拒绝 iframe 嵌入。

### 2. 解法：在反代 location 里加 `proxy_hide_header X-Frame-Options;`

```nginx
server {
    listen       80;
    server_name  grafana.local;

    location / {
        proxy_pass http://grafana:3000;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_hide_header X-Frame-Options;   # ← 关键这一行
    }
}
```

加完后 `curl -I http://反代域名/login` 的响应头里**不再有** `X-Frame-Options`，浏览器就不会阻止嵌入。

**注意**：如果是 HTTPS 站点，可能还需要同时去掉 `Content-Security-Policy` 里的 `frame-ancestors` 限制（`proxy_hide_header Content-Security-Policy;`）。

### 3. 用 include 文件统一管理，避免每个 server block 重复

**所有反代都需要同样的通用设置**（`proxy_set_header` 三件套 + `proxy_hide_header X-Frame-Options`）。重复写在每个 server block 里既冗余又容易漏。

**推荐结构**：

```
nginx/
├── conf/
│   └── nginx.conf          # 主配置
└── conf.d/                 # 通用配置目录
    └── proxy-common.conf   # 通用反代设置
```

`conf.d/proxy-common.conf`：

```nginx
# 通用反向代理设置 - 所有反代 location / { } 里都 include 这个文件

proxy_set_header Host              $host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;

# 允许被 iframe 嵌入 (Grafana/Kibana 等默认 X-Frame-Options: deny)
proxy_hide_header X-Frame-Options;
```

每个反代 server block 简化为：

```nginx
server {
    listen       80;
    server_name  myservice.local;

    location / {
        proxy_pass http://myservice:8080;
        include /etc/nginx/conf.d/proxy-common.conf;
    }
}
```

**未来加新反代只写 4 行 server block + 1 行 include 就自动有所有通用设置**。

docker-compose.yml 挂载：

```yaml
volumes:
  - ./nginx/conf/nginx.conf:/etc/nginx/nginx.conf:ro
  - ./nginx/conf.d:/etc/nginx/conf.d:ro   # ← 别忘了挂这个目录
  - ./nginx/www:/usr/share/nginx/www:ro
```

---

## 几个容易踩的坑

### 坑 1：nginx 配置改了但没生效

bind mount 的文件改了，nginx 进程不会自动 reload，必须手动：

```bash
# 推荐：热重载（不需要重启容器）
docker exec nginx nginx -s reload

# 推荐：改完后验证语法
docker exec nginx nginx -t
```

但**新加 volume mount** 必须 recreate 容器（热重载不会挂载新目录）：

```bash
docker compose up -d --force-recreate --no-deps nginx
```

### 坑 2：`docker compose restart nginx` 不一定真的 recreate 容器

如果只是 `restart`，容器实例不变，nginx 进程可能继续用旧的 worker 配置。需要 `--force-recreate` 才能彻底重建。

### 坑 3：调试时 curl 被代理劫持（local dev 环境常见）

Mac 上很多人设了 `http_proxy=http://127.0.0.1:7890` 之类的全局代理，curl 会走代理而不是直接连 nginx。诊断反代问题时：

```bash
unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
curl -I http://反代域名/
```

或者用 `--noproxy '*'` 临时绕开。

### 坑 4：父页面是 HTTPS 时 iframe src 不能是 HTTP

主页面是 HTTPS，iframe src 是 HTTP 会被浏览器当作 mixed content 阻止加载（即使 nginx 301 跳转到 HTTPS 也可能被卡）。解决方案：

- iframe src 直接写 HTTPS URL（如果 nginx 支持 HTTPS）
- 或者主页面也用 HTTP（dev 环境常见）

---

## 决策总结

| 决策 | 原因 |
|---|---|
| `proxy_hide_header X-Frame-Options` 而非改上游配置 | 上游是别人家的服务（Grafana），改不动；反代是自家东西，可控 |
| include 文件统一管理 | 通用设置未来只改一处；避免漏写；server block 简洁 |
| `--force-recreate --no-deps` 而非 `restart` | 新加 volume 时必须重建容器才能挂载 |
| 顺手去掉 `Content-Security-Policy` | HTTPS 站点有 `frame-ancestors` 也会拦截，同源治理 |

## 验证清单

改完后用这个流程验证：

```bash
# 1. 语法
docker exec nginx nginx -t

# 2. 热重载
docker exec nginx nginx -s reload

# 3. header 检查（应该不再有 X-Frame-Options）
unset http_proxy https_proxy all_proxy
curl -I http://反代域名/login | grep -i frameoptions || echo "OK: header hidden"

# 4. 浏览器测试
# 打开父页面（index.html），点 iframe 按钮，应该能正常显示
```
