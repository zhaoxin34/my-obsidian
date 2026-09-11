# Fedora Docker 安装与使用

> 在 Fedora 41/42 上安装 Docker Engine + Docker Compose，并配置国内镜像加速。

## 1. 卸载旧版本（如有）

```bash
sudo dnf remove -y docker docker-client docker-client-latest \
                 docker-common docker-latest docker-latest-logrotate \
                 docker-logrotate docker-engine
```

## 2. 添加 Docker 官方仓库（推荐）

```bash
# 用清华镜像（默认 docker.io 国内访问不稳）
sudo dnf config-manager --add-repo \
  https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/fedora/docker-ce.repo

sudo dnf install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# 启用并启动
sudo systemctl enable --now docker
sudo systemctl status docker
```

> 如果清华源没有当前 Fedora 版本的 docker-ce 包，可以临时用官方源：
> `https://download.docker.com/linux/fedora/docker-ce.repo`，安装后再切回加速镜像。

## 3. 非 root 用户使用 docker

```bash
sudo usermod -aG docker $zhaoxinUSER  # 替换为你的用户名
newgrp docker
docker run hello-world
```

> ⚠️ 重新登录后 `docker` 命令免 sudo；临时可在当前 shell 用 `newgrp docker`。

## 4. 国内镜像加速

`/etc/docker/daemon.json`：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.registry.cyou",
    "https://docker-cf.registry.cyou",
    "https://dockercf.jsdelivr.fyi",
    "https://docker.jsdelivr.fyi",
    "https://dockertest.jsdelivr.fyi",
    "https://mirror.aliyuncs.com",
    "https://dockerproxy.com",
    "https://mirror.baidubce.com",
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn",
    "https://docker.mirrors.sjtug.sjtu.edu.cn",
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.iscas.ac.cn",
    "https://docker.rainbond.cc"
  ]
}
```

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "builder": {"gc": {"defaultKeepStorage": "20GB", "enabled": true}},
  "experimental": false,
  "registry-mirrors": [
    "https://docker.registry.cyou",
    "https://docker-cf.registry.cyou",
    "https://dockercf.jsdelivr.fyi",
    "https://docker.jsdelivr.fyi",
    "https://dockertest.jsdelivr.fyi",
    "https://mirror.aliyuncs.com",
    "https://dockerproxy.com",
    "https://mirror.baidubce.com",
    "https://docker.m.daocloud.io",
    "https://docker.nju.edu.cn",
    "https://docker.mirrors.sjtug.sjtu.edu.cn",
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.iscas.ac.cn",
    "https://docker.rainbond.cc"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
docker info | grep -A 20 "Registry Mirrors"
```

## 5. 防火墙冲突

Docker 默认会改 iptables，firewalld 可能阻挡容器间/容器与宿主通信。

```bash
# 把 docker0 / br-* 加入 trusted zone
sudo firewall-cmd --permanent --zone=trusted --add-interface=docker0
sudo firewall-cmd --permanent --zone=trusted --add-interface=br-+ 
sudo firewall-cmd --reload

# 或者关闭 firewalld（个人开发机可接受）
sudo systemctl disable --now firewalld
```

更稳妥的做法：在 `/etc/docker/daemon.json` 里禁用 iptables（Docker 自己管）：

```json
{
  "iptables": false,
  "ip-forward": true,
  "registry-mirrors": [ ... ]
}
```

## 6. Docker Compose

新版 Docker 自带 `docker compose`（v2，插件形式）：

```bash
docker compose version
# Docker Compose version v2.x.x
```

如果是老习惯 `docker-compose`（v1 独立二进制），Fedora 仓库已不提供，需要可手动装：

```bash
sudo curl -SL "https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 7. 存储路径（可选）

默认镜像存 `/var/lib/docker`，如果你想把数据放其他盘：

```bash
sudo systemctl stop docker
sudo mv /var/lib/docker /mnt/data/docker
sudo ln -s /mnt/data/docker /var/lib/docker
sudo systemctl start docker
```

## 8. 常用命令速查

```bash
docker ps -a                          # 所有容器
docker images                         # 所有镜像
docker logs -f <name>                 # 日志
docker exec -it <name> bash           # 进容器
docker system df                      # 磁盘占用
docker system prune -a                # 清理（**会删未用镜像和容器**）
docker volume ls                       # 卷
docker network ls                      # 网络

# compose
docker compose up -d                   # 启动
docker compose logs -f                # 日志
docker compose down -v                # 停掉并删卷（**危险**，会丢数据）
docker compose ps
```

## 9. 桌面集成（可选）

如果想在 GNOME 通知里看到容器状态：

```bash
sudo dnf install -y docker-desktop   # 注意：这是 Docker Desktop 商业版，需要注册账户
```

个人推荐直接在终端 + lazydocker 看：

```bash
# lazydocker 类似 k9s 的 docker TUI
sudo dnf install -y lazydocker
# 或者作为独立二进制
curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash
```

## 后续

- [[07-Fedora-pi-agent安装与配置]]（用 pi 操作 docker 容器）
- [[08-Fedora-远程控制方案]]（如需把 Docker 端口暴露到 Mac）
