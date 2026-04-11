> MkDocs Material：基于 MkDocs 的 Material Design 文档主题，让文档既好看又好用。
>
> 官网：https://squidfunk.github.io/mkdocs-material/
> GitHub：https://github.com/squidfunk/mkdocs-material

## 简介

MkDocs Material 是 MkDocs 最流行的主题之一，提供：

| 特性 | 说明 |
|------|------|
| **Material Design 风格** | 现代化界面，支持明暗主题 |
| **响应式布局** | 桌面、平板、手机完美适配 |
| **强大搜索** | 内置全文搜索，支持中文 |
| **丰富插件生态** | 博客、版本管理、社交卡片等 |
| **高度可定制** | 颜色、字体、图标、Logo 均可自定义 |
| **Insiders 版本** | 赞助可获得 exclusive 功能 |

## 安装

### 前置依赖

- Python 3.9+
- pip

### 安装 MkDocs 和 Material 主题

```bash
pip install mkdocs-material
```

安装完成后验证：

```bash
mkdocs --version     # MkDocs 版本
mkdocs material --version  # Material 主题版本
```

## 快速开始

### 1. 创建新项目

```bash
mkdocs new my-docs
cd my-docs
```

生成的项目结构：

```
my-docs/
├── mkdocs.yml      # 配置文件
└── docs/
    └── index.md    # 首页文档
```

### 2. 配置 mkdocs.yml

最基本的配置：

```yaml
site_name: 我的文档站点
site_url: https://example.com

theme:
  name: material
```

### 3. 本地预览

```bash
mkdocs serve
```

然后访问 http://localhost:8000，修改文件后浏览器自动刷新。

### 4. 构建静态网站

```bash
mkdocs build
```

生成的静态文件在 `site/` 目录，可直接部署到 GitHub Pages、Netlify、Vercel 等平台。

## 常用配置

### 站点信息

```yaml
site_name: Material for MkDocs
site_url: https://example.com
site_author: 你的名字
site_description: 站点描述（SEO 用）
```

### 仓库链接

在文档右上角显示 GitHub/GitLab 链接：

```yaml
repo_name: username/repo
repo_url: https://github.com/username/repo
```

### 导航结构

```yaml
nav:
  - 首页: index.md
  - 安装: setup/index.md
  - 使用指南:
      - 快速开始: guide/quickstart.md
      - 高级配置: guide/advanced.md
  - 插件: plugins.md
```

## 主题定制

### 颜色方案

```yaml
theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: 切换到暗色模式

    - scheme: slate
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-4
        name: 切换到亮色模式
```

可选 primary/accent 颜色：`red`, `pink`, `purple`, `deep-purple`, `indigo`, `blue`, `light-blue`, `cyan`, `teal`, `green`, `light-green`, `lime`, `yellow`, `amber`, `orange`, `deep-orange`, `brown`, `grey`

### Logo 和图标

```yaml
theme:
  icon:
    logo: material/library
    repo_font: font/fa/brands/github
  logo: assets/logo.png
  favicon: assets/favicon.png
```

### 字体

```yaml
theme:
  font:
    text: Roboto
    code: Roboto Mono
```

### 语言

```yaml
theme:
  language: zh
```

支持中文界面。

### 导航增强

```yaml
theme:
  features:
    - navigation.tabs        # 顶部标签页导航
    - navigation.sections    # 侧边栏分组
    - navigation.expand      # 侧边栏默认展开
    - navigation.instant     # 导航无刷新跳转
    - navigation.tracking    # URL 跟随导航
    - toc.integrate          # 目录集成到侧边栏
    - search.suggest         # 搜索补全
    - search.highlight        # 搜索高亮
    - content.code.copy       # 代码复制按钮
    - content.code.annotate   # 代码注释
```

## 扩展功能

### 内置扩展

在 Markdown 内容中直接使用：

```markdown
!!! note "提示"
    这是一个提示框

??? warning "可折叠的警告"
    点击可展开的警告内容

!!! info inline end "行内信息"
    信息内容

=== "Tab 1"
    Tab 1 的内容

=== "Tab 2"
    Tab 2 的内容
```

提示框类型：`note`、`abstract`、`info`、`tip`、`success`、`question`、`warning`、`failure`、`danger`、`bug`、`example`、`quote`

### 代码高亮

```yaml
markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
```

### 数学公式

```yaml
markdown_extensions:
  - pymdownx.arithmatex:
      generic: true
```

然后在 `mkdocs.yml` 中加入：

```yaml
extra_javascript:
  - https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js
```

### Mermaid 图表

```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

## 常用插件

### 安装插件

```bash
pip install mkdocs-jupyter        # Jupyter Notebook 支持
pip install mkdocs-static-i18n     # 多语言支持
pip install mkdocs-table-reader-plugin  # 读取 CSV/TSV 表格
pip install mkdocs-glightbox       # 图片灯箱
pip install mkdocs-print-site-plugin  # 打印/导出
```

### 配置插件

```yaml
plugins:
  - search                  # 内置搜索
  - mkdocs-jupyter:         # Jupyter 支持
      ignore_h1_titles: true
  - glightbox:              # 图片灯箱
      auto-capture: true
  - print-site:             # 打印支持
```

> ⚠️ 如果使用 Insiders 版本，需从 GitHub 安装：
> ```bash
> pip install git+https://github.com/squidfunk/mkdocs-material-insiders
> ```

## Insiders 版本

MkDocs Material 采用 **Sponsorware** 策略：新功能优先发布给赞助者。

### 特色功能

- 社交卡片（社交媒体分享预览图）
- 博客插件
- 版本管理
- 更多导航增强

### 获取方式

在 GitHub 赞助作者后，获得 Insiders 仓库访问权限，然后：

```bash
pip install git+ssh://git@github.com:squidfunk/mkdocs-material-insiders
```

## 部署

### GitHub Pages

```bash
mkdocs gh-deploy
```

### Vercel / Netlify

在项目根目录创建 `vercel.json`（Vercel）或 `netlify.toml`（Netlify），构建命令：

```bash
mkdocs build
```

输出目录：`site/`

## 完整示例 mkdocs.yml

```yaml
site_name: 我的文档
site_url: https://example.com
site_author: 你的名字
site_description: 文档描述

repo_name: username/repo
repo_url: https://github.com/username/repo

theme:
  name: material
  language: zh
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: 切换到暗色模式
    - scheme: slate
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-4
        name: 切换到亮色模式
  font:
    text: Roboto
    code: Roboto Mono
  icon:
    logo: material/library
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.instant
    - search.suggest
    - search.highlight
    - content.code.copy

nav:
  - 首页: index.md
  - 快速开始: getting-started.md
  - 配置: configuration.md
  - 插件: plugins.md

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - pymdownx.arithmatex
  - admonition
  - pymdownx.details
  - pymdownx.mark

plugins:
  - search
```

## 相关资源

- 官方文档：https://squidfunk.github.io/mkdocs-material/
- GitHub：https://github.com/squidfunk/mkdocs-material
- MkDocs 官网：https://www.mkdocs.org/
- 社区插件：https://github.com/topics/mkdocs-plugin
