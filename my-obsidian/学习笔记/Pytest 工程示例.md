## 项目结构

```
pytest-demo/
├── pyproject.toml          # 项目配置和依赖管理
├── README.md               # 项目说明
├── src/                    # 源代码目录
│   └── demo/               # 示例模块
│       ├── __init__.py
│       └── calculator.py   # 示例代码
└── tests/                  # 测试目录
    ├── __init__.py
    └── test_calculator.py  # 测试文件
```

*pyproject.toml*

```toml
[project]
name = "pytest-demo"
version = "0.1.0"
description = "A pytest demo project using uv"
readme = "README.md"
requires-python = ">=3.9"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/demo"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

*test_calculator.py*
```python

import pytest
from demo.calculator import Calculator


class TestCalculator:
    """Calculator 类的测试套件。"""

    def test_add_positive_numbers(self, calculator):
        """测试正数加法。"""
        assert calculator.add(5, 3) == 8

    def test_divide_by_zero_raises_error(self, calculator):
        """测试除以零应该抛出异常。"""
        with pytest.raises(ValueError, match="除数不能为0"):
            calculator.divide(10, 0)
```

## 安装依赖

使用 uv 安装开发依赖：

```bash
uv sync --extra dev
```

## 运行测试

运行所有测试：

```bash
uv run pytest
```

运行测试并生成覆盖率报告：

```bash
uv run pytest --cov=src --cov-report=html
```

运行特定测试文件：

```bash
uv run pytest tests/test_calculator.py
```

运行特定测试函数：

```bash
uv run pytest tests/test_calculator.py::test_add
```

