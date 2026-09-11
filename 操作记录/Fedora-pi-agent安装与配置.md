# Fedora pi-agent 安装与配置

> pi coding agent 是你常用的 AI 编程助手。这里把它装到 Fedora，并配置 provider / skills / 代理。
> 假设你已经在 macOS 上用熟，**这里只写 Fedora 这边的差异点**。

## 1. 前置：Node.js

pi 需要 Node ≥ 18。建议用 NodeSource 或 fnm 装 LTS：

```bash
# 方法 A：Fedora 模块（Fedora 41+ 默认 Node 22，足够）
sudo dnf install -y nodejs npm

node -v    # 期望 >= 18，建议 20 / 22

# 方法 B：用 fnm（更灵活，多版本共存）
sudo dnf install -y curl unzip
curl -fsSL https://fnm.vercel.app/install | bash
# 把下面加到 ~/.zshrc
echo 'eval "$(fnm env --use-on-cd --shell zsh)"' >> ~/.zshrc
exec zsh
fnm install 22
fnm default 22
```

## 2. 装 pi

```bash
# 走代理（pi 在 GitHub release 拉二进制）
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890

# 全局装（推荐）
npm install -g @earendil-works/pi-coding-agent

# 或装到用户目录（更安全，避免 npm 全局 root 写入冲突）
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc
exec zsh
npm install -g @earendil-works/pi-coding-agent

# 验证
which pi
pi --version
```

## 3. 首次启动 + provider 配置

```bash
# 第一次启动会让你登录 / 选 provider
pi
# /login 选择 provider（OpenAI / Anthropic / Gemini / 自定义）
# 如果选自定义（推荐国内用智谱、月之暗面、deepseek 等），按提示填 base_url + api_key
```

配置文件位置：

```text
~/.pi/agent/settings.json
```

示例（智谱）：

```json
{
  "provider": "custom",
  "custom": {
    "baseUrl": "https://open.bigmodel.cn/api/anthropic",
    "apiKey": "你的智谱 key",
    "models": {
      "haiku": "glm-4.5-air",
      "sonnet": "glm-4.6",
      "opus": "glm-4.6"
    }
  }
}
```

示例（deepseek）：

```json
{
  "provider": "custom",
  "custom": {
    "baseUrl": "https://api.deepseek.com/v1",
    "apiKey": "sk-xxx",
    "models": {
      "haiku": "deepseek-chat",
      "sonnet": "deepseek-chat",
      "opus": "deepseek-reasoner"
    }
  }
}
```

## 4. 代理

如果 pi 通过 npm 装 OK，但运行后访问 model API 受限：

```bash
# ~/.zshrc
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
```

或者在 settings.json 里加：

```json
{
  "env": {
    "https_proxy": "http://127.0.0.1:7890"
  }
}
```

## 5. skills（扩展）

`pi` 用 skills 扩展能力。skills 装在 `~/.pi/agent/skills/`：

```bash
# 直接 clone
git clone https://github.com/earendil-works/awesome-skills ~/.pi/agent/skills/awesome-skills

# 在 pi 中：
/skill install <name>
/skill list
```

也可以让 pi 自己装（推荐）：

```text
pi> /plugin marketplace add anthropics/skills
pi> /skill install frontend-design
```

## 6. subagent / skills 联网

很多 skill 会在运行时 npm install / pip install，记得带代理。

## 7. 与 pi-agent 协作的典型场景

```text
pi> 帮我看一下 ~/code/myproject 的 docker-compose，把 postgres 的端口改成 5433，重启容器
pi> 在 ~/.config/nvim/init.lua 里启用 nvim-treesitter-context
pi> /simplify 当前文件
```

## 8. 我的判断

- pi 在 Fedora 上和 macOS 上几乎无差，**配置文件是同一份**，强烈建议把 `~/.pi/agent/` 链到 dotfiles：

```bash
ln -s ~/code/dotfiles/pi ~/.pi/agent
```

- 国内首选 provider：**智谱 glm-4.6**（中文最强）/ **Deepseek**（便宜、快）/ **月之暗面**。配 GLM 的好处是不用翻墙，pi 启动秒进。
- pi 在 Linux 下的终端兼容问题比 macOS 少（无 shell 权限怪问题），体感更顺。

## 后续

- [[Fedora-远程控制方案]]（你可以 Mac 上 ssh 进 Fedora 后用 wezterm + pi agent）
