# ==================== Docker 容器内安装 ====================

## 背景

在Docker容器内运行VPN的好处：
- VPN流量完全隔离在容器内
- 不影响宿主机网络速度
- `docker compose down` 即可断开VPN

## 初始化步骤

### 1. 启动容器

```bash
cd /Volumes/data/working/docker/ubuntu
docker compose up -d
docker compose exec openvpn bash
```

### 2. 配置DNS（解决apt下载慢的问题）

```bash
echo 'nameserver 8.8.8.8' > /etc/resolv.conf
```

### 3. 配置清华镜像源（国内访问快）

```bash
echo 'deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ noble main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ noble-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ noble-security main restricted universe multiverse' > /etc/apt/sources.list
```

### 4. 更新软件源并安装软件

```bash
apt-get update

# 安装的软件清单：
# - openvpn          : VPN客户端
# - iproute2         : 网络工具（ip命令）
# - curl             : HTTP客户端
# - iputils-ping     : ping命令
# - openssh-client   : SSH客户端
# - sshpass          : SSH密码自动化

apt-get install -y openvpn iproute2 curl iputils-ping openssh-client sshpass
```

### 5. 挂载VPN配置文件

在 `docker-compose.yml` 中配置：

```yaml
volumes:
  - ~/.ssh/zhaoxin.ovpn:/root/vpn.ovpn:ro
```

### 6. 启动VPN

```bash
openvpn --config /root/vpn.ovpn --daemon
```

### 7. 验证VPN连接

```bash
# 查看tun接口
ip addr show tun0

# ping测试
ping -c 2 8.8.8.8

# 查看公网IP
curl -s ifconfig.me
```

## 注意事项

- **容器重启后安装会丢失** - 如果需要持久化，需要构建自定义镜像
- **代理配置** - 如果需要代理，配置 `host.docker.internal:7890`
- **VPN服务器** - 确认VPN服务器地址可访问

## 自定义镜像（可选）

如果需要持久化软件安装，创建 Dockerfile：

```dockerfile
FROM ubuntu:noble-20260509.1

RUN echo 'nameserver 8.8.8.8' > /etc/resolv.conf && \
    echo 'deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ noble main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ noble-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ noble-security main restricted universe multiverse' > /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    openvpn iproute2 curl iputils-ping openssh-client sshpass && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root
```

然后修改 docker-compose.yml：

```yaml
services:
  openvpn:
    build: .
    image: my-vpn-ubuntu:latest
```
