## Python 项目配置经验

### 背景

当使用 uv 管理 Python 项目时，pyproject.toml 的配置方式直接影响开发体验。uv 对 PEP 标准和非标准字段有不同处理方式，需要了解其最佳实践以避免警告和不一致。

### 目标

1. 正确配置 pyproject.toml 以避免 uv 警告
2. 统一依赖管理方式
3. 确保项目结构符合 uv 规范

### 方案

#### 1. 依赖分组

使用 `[dependency-groups]` 而非 `[project.optional-dependencies]` 或 `[tool.uv]` 来声明开发依赖：

```toml
[dependency-groups]
dev = [
  "pytest>=8.0",
  "pytest-asyncio>=0.23",
  "ruff>=0.3",
  "mypy>=1.8",
]

[project.optional-dependencies]
dev = [
  # 不要在这里添加 dev 依赖
]
```

原因：`[tool.uv]` 中的 `dev-dependencies` 已废弃，`[project.optional-dependencies]` 适合用于可发布的可选依赖，而 `[dependency-groups]` 是 uv 推荐的开发依赖管理方式。

#### 2. 安装命令

使用 `--group` 参数而非 `.[]` 语法：

```bash
# 推荐
uv pip install -e . --group dev

# 不推荐（会触发警告）
uv pip install -e ".[dev]"
```

#### 3. Makefile 中的 uv 使用

```makefile
dev:
	uv pip install -e . --group dev
```

#### 4. 完整 pyproject.toml 示例

```toml
[project]
name = "mypackage"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["requests>=2.28"]

[project.scripts]
myapp = "mypackage.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = [
  "pytest>=8.0",
  "ruff>=0.3",
  "mypy>=1.8",
]

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.mypy]
python_version = "3.10"
```

### 注意事项

- `[dependency-groups]` 是 PEP 735 的一部分，但 uv 对其支持良好
- 确保 `[project.scripts]` 在 `[dependency-groups]` 之前定义
- `--group` 参数是 uv 特有的，但已被广泛支持