# UI/UX Pro Max Skill 项目调研报告

> 来源: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
> 版本: v2.5.0
> 许可证: MIT
> 网站: [uupm.cc](https://uupm.cc)

## 概述

UI/UX Pro Max (UI/UX Pro Max Skill) 是一个 AI 驱动的设计智能工具包，为构建专业 UI/UX 提供跨平台、跨框架的设计情报。它作为 AI 编程助手（Claude Code、Cursor、Windsurf 等）的 Skill 工作。

核心能力：通过可搜索的数据库提供 UI 风格、配色方案、字体搭配、图表类型和 UX 最佳实践。

## 核心数据规模

| 资源类型 | 数量 | 说明 |
|---------|------|------|
| UI 风格 | 67 种 | 从极简主义到 Cyberpunk |
| 行业类别 | 161 个 | Tech/SaaS、金融、医疗、电商等 |
| 配色方案 | 161 套 | 按行业类型分类 |
| 字体搭配 | 57 种 | 含 Google Fonts 链接 |
| Landing Page 模式 | 24 种 | 含 CTA 策略 |
| 图表类型 | 25+ 种 | 含库推荐 |
| UX 指南 | 99+ 条 | 最佳实践和反模式 |

## 核心功能

### 1. Design System Generator（v2.0 旗舰功能）

AI 驱动的推理引擎，根据项目需求在几秒钟内生成完整的定制设计系统。

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. 用户请求                                                       │
│ "Build a landing page for my beauty spa"                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. 多域并行搜索 (5个搜索)                                          │
│ • 产品类型匹配 (161 类别)                                         │
│ • 风格推荐 (67 风格)                                             │
│ • 配色选择 (161 配色)                                            │
│ • Landing Page 模式 (24 模式)                                    │
│ • 字体搭配 (57 搭配)                                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. 推理引擎                                                       │
│ • 产品 → UI 类别规则匹配                                         │
│ • 风格优先级应用 (BM25 排名)                                     │
│ • 行业反模式过滤                                                 │
│ • 决策规则处理 (JSON 条件)                                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. 完整设计系统输出                                               │
│ 模式 + 风格 + 颜色 + 字体 + 效果                                  │
│ + 避免的反模式 + 预交付检查清单                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2. 行业特定推理规则（161 条）

| 类别 | 示例 |
|------|------|
| Tech & SaaS | SaaS、Micro SaaS、B2B 服务、开发者工具、AI/Chatbot 平台 |
| Finance | Fintech/Crypto、银行、保险、个人财务追踪、发票工具 |
| Healthcare | 医疗诊所、药房、牙科、兽医、心理健康、药物提醒 |
| E-commerce | 综合、奢侈品、市场、P2P、订阅盒、食品外卖 |
| Services | 美容/Spa、餐厅、酒店、法律、家庭服务、预约 |
| Creative | 作品集、代理、摄影、游戏、音乐流媒体、照片/视频编辑 |
| Lifestyle | 习惯追踪、食谱烹饪、冥想、天气、日记、心情追踪 |
| Emerging Tech | Web3/NFT、空间计算、量子计算、 autonomous 无人机编队 |

### 3. 67 种 UI 风格（部分列表）

| # | 风格 | 最佳适用 |
|---|------|---------|
| 1 | Minimalism & Swiss Style | 企业应用、仪表盘、文档 |
| 2 | Neumorphism | 健康/健康应用、冥想平台 |
| 3 | Glassmorphism | 现代 SaaS、财务仪表盘 |
| 4 | Brutalism | 设计作品集、艺术项目 |
| 5 | 3D & Hyperrealism | 游戏、产品展示、沉浸式 |
| 6 | Vibrant & Block-based | 创业公司、创意机构、游戏 |
| 7 | Dark Mode (OLED) | 夜间模式应用、编码平台 |
| 8 | Accessible & Ethical | 政府、医疗、教育 |
| 9 | Claymorphism | 教育应用、儿童应用、SaaS |
| 10 | Aurora UI | 现代 SaaS、创意机构 |
| 11 | Retro-Futurism | 游戏、娱乐、音乐平台 |
| 12 | Flat Design | Web 应用、移动应用、Startup MVP |
| 19 | Soft UI Evolution | 现代企业应用、SaaS |
| 20 | Neubrutalism | Gen Z 品牌、创业公司 |
| 25 | AI-Native UI | AI 产品、聊天机器人、copilots |
| 36 | Spatial UI (VisionOS) | 空间计算应用、VR/AR |
| 38 | Gen Z Chaos / Maximalism | Gen Z 生活方式、音乐人 |
| 49 | Vintage Analog / Retro Film | 摄影、音乐/黑胶品牌 |

### 4. 支持的技术栈

| 类别 | 技术栈 |
|------|-------|
| Web (HTML) | HTML + Tailwind (默认) |
| React 生态 | React, Next.js, shadcn/ui |
| Vue 生态 | Vue, Nuxt.js, Nuxt UI |
| Angular | Angular |
| PHP | Laravel (Blade, Livewire, Inertia.js) |
| 其他 Web | Svelte, Astro |
| iOS | SwiftUI |
| Android | Jetpack Compose |
| 跨平台 | React Native, Flutter |

## 使用方法

### 安装方式

**Claude Marketplace (Claude Code):**
```
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

**CLI 安装（推荐，可全局使用）:**
```bash
npx uipro-cli init --ai <platform>
```

### 使用模式

#### Skill Mode（自动激活）

支持：Claude Code、Cursor、Windsurf、Antigravity、Codex CLI、Continue、Gemini CLI、OpenCode、Qoder、CodeBuddy、Droid (Factory)、KiloCode、Warp、Augment

只需自然语言聊天即可：
```
Build a landing page for my SaaS product
Create a dashboard for healthcare analytics
Design a portfolio website with dark mode
```

#### Workflow Mode（斜杠命令）

支持：Kiro、GitHub Copilot、Roo Code、KiloCode
```
/ui-ux-pro-max Build a landing page for my SaaS product
```

### 设计系统命令（高级）

直接访问设计系统生成器：
```bash
python3 src/ui-ux-pro-max/scripts/design_system.py "Serenity Spa"
```

### 持久化设计系统（Master + Overrides 模式）

创建 `design-system/` 文件夹结构用于跨会话的分层检索：
```
design-system/
├── MASTER.md        # 全局真理来源（颜色、字体、间距、组件）
└── pages/
    └── dashboard.md  # 页面特定覆盖（仅与 Master 的偏差）
```

## 架构

```
src/ui-ux-pro-max/           # 真理来源
├── data/                    # 规范 CSV 数据库
│   ├── products.csv
│   ├── styles.csv
│   ├── colors.csv
│   ├── typography.csv
│   └── stacks/              # 技术栈特定指南
├── scripts/
│   ├── search.py            # CLI 入口
│   ├── core.py              # BM25 + regex 混合搜索引擎
│   └── design_system.py     # 设计系统生成
└── templates/
    ├── base/                # 基础模板
    └── platforms/          # 平台配置

cli/                         # CLI 安装器 (npm: uipro-cli)
├── src/
│   ├── commands/init.ts     # 安装命令+模板生成
│   └── utils/template.ts    # 模板渲染引擎
└── assets/                  # 捆绑资源 (~564KB)
    ├── data/
    ├── scripts/
    └── templates/

.claude/skills/ui-ux-pro-max/  # Claude Code skill (符号链接)
```

### 搜索命令

```bash
# 域搜索
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain>

# 可用域:
# product   - 产品类型推荐
# style     - UI 风格 + AI 提示和 CSS 关键词
# typography - 字体搭配 + Google Fonts 导入
# color     - 按产品类型分类的配色
# landing   - 页面结构和 CTA 策略
# chart     - 图表类型和库推荐
# ux        - 最佳实践和反模式

# 技术栈搜索
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --stack <stack>

# 可用栈: html-tailwind (默认), react, nextjs, astro, vue, nuxtjs,
# nuxt-ui, svelte, swiftui, react-native, flutter, shadcn, jetpack-compose
```

## 项目特色

### 与 Product Manager Skills 的对比

| 对比项 | Product Manager Skills | UI/UX Pro Max |
|--------|----------------------|---------------|
| 定位 | 产品管理技能框架 | UI/UX 设计智能工具 |
| 核心功能 | PM 流程、发现、PRD、优先级 | 风格推荐、配色、字体、布局 |
| 数据规模 | 47 个 PM Skills | 67 风格 + 161 行业 + 161 配色 |
| 输出形式 | 框架指导、模板、流程 | 设计系统生成、代码提示 |
| 目标用户 | 产品经理 | 前端/全栈开发者、设计师 |

两者可互补：PM 定义「做什么」→ UI/UX Pro Max 定义「怎么做视觉」

### 优点
- 覆盖极其全面的设计风格和行业类别
- 多平台支持（18+ AI 编程助手）
- 内置 BM25 搜索引擎，检索精准
- 设计系统生成器可快速产出完整设计方案
- 预交付检查清单确保质量
- MIT 许可证，商用友好

### 缺点
- 主要是 Web/移动端 UI，对桌面应用支持有限
- 需要 Python 3.x 环境（搜索脚本）
- 偏向生成实现，对设计理论讲解较少

## 总结

UI/UX Pro Max 是一个**专注于 UI/UX 实现**的设计智能工具。它的核心价值在于：

1. **广度**：67 种 UI 风格、161 个行业类别、57 种字体搭配的海量数据库
2. **智能推荐**：基于 BM25 的搜索引擎 + 行业推理规则，自动匹配最佳设计方案
3. **设计系统生成**：输入产品描述，输出完整的颜色、字体、布局、动效建议
4. **多平台兼容**：支持 18+ 主流 AI 编程助手

配合 Product Manager Skills 使用，可以形成「产品规划 → 设计实现」的完整闭环。
