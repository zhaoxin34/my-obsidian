---
title: "Git Hooks 配置指南"
description: "快速掌握 Git 自定义 hooks 目录的配置方法"
---

## Git Hooks 配置指南

本教程面向熟悉 Git 的开发者，介绍如何配置自定义 hooks 目录。

### 快速开始

#### 1. 创建 hooks 目录

```bash
mkdir hooks
```

#### 2. 添加 hook 脚本

```bash
# post-push 示例
cat > hooks/post-push << 'EOF'
#!/bin/bash
echo "Running post-push..."
make install-tool
EOF

# post-merge 示例
cat > hooks/post-merge << 'EOF'
#!/bin/bash
echo "Running post-merge..."
make install-tool
EOF

chmod +x hooks/post-push hooks/post-merge
```

#### 3. 配置 Git 使用 hooks 目录

```bash
git config core.hooksPath hooks
```

#### 验证

```bash
git config core.hooksPath
# 输出: hooks
```

### 可用 Hooks

| Hook        | 触发时机               |
| ----------- | ------------------ |
| pre-commit  | `git commit` 前     |
| post-commit | `git commit` 后     |
| post-push   | `git push` 后       |
| post-merge  | `git merge/pull` 后 |
| pre-push    | `git push` 前       |