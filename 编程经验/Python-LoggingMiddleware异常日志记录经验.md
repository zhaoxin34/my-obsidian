### 背景

在使用 FastAPI/Starlette 构建 Web 应用时，需要统一记录请求/响应的日志，特别是在生产环境中，当请求处理出现未捕获的异常时，需要能够将异常信息和堆栈跟踪写入日志文件，而不是只输出到 stderr/stdout。

本经验基于 CDP 后端项目的 `LoggingMiddleware` 实际修复过程。

### 目标

1. 在 Middleware 层统一捕获请求处理中的异常
2. 将异常信息（包括堆栈跟踪）写入日志文件
3. 确保日志路径正确（相对于应用工作目录）
4. 格式化器能够输出可读的堆栈信息

### 方案

#### 1. 在 Middleware 中捕获异常

使用 `try/except` 包裹 `call_next(request)` 调用，捕获异步处理中的异常：

```python
async def dispatch(self, request: Request, call_next: Callable) -> Response:
    try:
        response = await call_next(request)
    except Exception as exc:
        # 记录异常日志后再重新抛出
        self.logger.exception(f"HTTP request failed | error={exc}")
        raise
```

**关键点**：
- 使用 `logger.exception()` 而不是 `logger.error()`，前者会自动包含 `exc_info=True`
- 捕获后必须 `raise`，否则会破坏正常的异常传播流程

#### 2. 自定义 Formatter 输出堆栈信息

Starlette 默认的日志格式化器可能不包含堆栈信息，需要在自定义格式化器中处理：

```python
class PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()

        # 当有异常信息时，附加堆栈跟踪
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            return f"{msg}\n{exc_text}"

        return msg
```

**关键点**：
- `record.exc_info` 是一个三元组 `(type, value, traceback)`
- `self.formatException(record.exc_info)` 将异常信息格式化为字符串

#### 3. 正确处理日志路径

避免使用 `__file__` 的相对路径计算，可能因为工作目录不同导致日志位置错误：

```python
# 错误示例：会受到工作目录影响
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

# 正确示例：使用绝对路径
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
log_dir = os.path.join(backend_dir, settings.LOG_DIR)
```

**关键点**：
- `os.path.abspath(__file__)` 获取文件的绝对路径
- 从文件位置向上找到应用根目录，再拼接相对路径

#### 4. 进程监听端口检查

当发现日志没有按预期写入时，检查是否有多个进程在监听同一端口：

```bash
lsof -i :8001 | grep LISTEN
```

这可以发现重复启动的服务导致的混乱。

### 注意事项

1. **异常重新抛出**：Middleware 捕获异常后必须 `raise`，否则上层框架无法感知错误
2. **日志格式化器**：默认 formatter 可能不输出堆栈信息，需要自定义
3. **路径计算**：使用 `__file__` 的相对路径时要小心工作目录的影响
4. **多进程问题**：开发时 `--reload` 可能产生多个进程，确认只有一个主进程在监听端口
