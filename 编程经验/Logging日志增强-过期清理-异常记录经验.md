# Logging 改进经验

## 背景

基于 [LoggingMiddleware 异常日志记录经验](Python-LoggingMiddleware异常日志记录经验.md) 的方案，对 neo/backend 项目进行了日志系统增强。

目标是：
1. 日志同时输出到 console 和 ./logs 目录
2. 异常日志记录包含堆栈跟踪
3. 日志文件有过期自动清理功能

## 实现方案

### 1. LoggingMiddleware 异常捕获

在 middleware 层捕获请求处理中的异常，使用 `logger.exception()` 记录堆栈信息：

```python
async def dispatch(self, request: Request, call_next: Callable) -> Response:
    try:
        response = await call_next(request)
    except Exception:
        # Log exception with stack trace
        logger.exception(
            f"{request.method} {request.url.path} - Request failed",
            extra={"event": "http_request", "request_id": request_id},
        )
        raise  # 必须重新抛出，让框架处理
```

**关键点**：
- `logger.exception()` 自动包含 `exc_info=True`
- 捕获后必须 `raise`，否则破坏异常传播

### 2. 日志过期自动清理

在 `logging.py` 中实现清理函数：

```python
def cleanup_old_logs(log_dir: str, log_file: str, retention_days: int) -> None:
    """Clean up log files older than retention_days."""
    if retention_days <= 0:
        return

    cutoff_time = datetime.now(timezone.utc) - timedelta(days=retention_days)
    
    for rotated_file in glob.glob(os.path.join(log_dir, f"{log_file}.*")):
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(rotated_file), tz=timezone.utc)
            if mtime < cutoff_time:
                os.remove(rotated_file)
        except Exception as e:
            logger.warning(f"Failed to clean up log file {rotated_file}: {e}")
```

在 `setup_logging()` 启动时调用清理。

### 3. 配置项

在 `config.py` 中添加配置：

```python
# Logging
LOG_RETENTION_DAYS: int = 7  # Auto-delete logs older than this many days
```

### 4. 输出格式

使用 `PlainFormatter` 输出可读的日志：

```
2026-05-26 10:49:44.597 | INFO     | http                        | [6a79a1bb] | [None] | GET /health - 200 - 0.001s
```

当有异常时，自动附加堆栈跟踪。

## 注意事项

1. **异常必须抛出**：`logger.exception()` 后要 `raise`，否则上层框架无法感知错误
2. **使用 getattr 访问 record 属性**：避免类型检查错误（如 `getattr(record, "event", None)`）
3. **日志路径计算**：使用 `os.path.abspath(__file__)` 避免工作目录影响
4. **清理时机**：在 `setup_logging()` 时调用，而非每次请求时
5. **UTC 时区**：使用 `datetime.now(timezone.utc)` 确保时间一致性

## 相关文件

- `src/app/core/logging.py` - 日志配置和清理逻辑
- `src/app/middleware/logging_middleware.py` - 异常捕获
- `src/app/config.py` - 配置项 `LOG_RETENTION_DAYS`