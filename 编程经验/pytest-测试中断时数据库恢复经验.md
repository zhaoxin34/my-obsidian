### 背景

在使用 pytest + Playwright 进行 E2E 测试时，`conftest.py` 中的 `db_backup` fixture 会在测试开始前备份数据库，测试结束后恢复。但在测试执行过程中，如果用户使用 `Ctrl+C` 中断测试进程，数据库恢复可能不会执行，导致测试期间的数据修改被保留在数据库中，影响后续测试。

本经验基于 CDP 项目 e2e-test 的实际改进过程。

### 目标

1. 当收到 `Ctrl+C` 中断信号时，确保先执行数据库恢复再退出
2. 保证测试环境在任何情况下都能恢复到初始状态

### 方案

#### 1. 注册信号处理器

通过 `signal.signal()` 注册 `SIGINT` 处理函数，在收到中断信号时执行恢复逻辑：

```python
import signal

_backup_file_path: str | None = None

def restore_and_cleanup():
    """Restore database and cleanup on exit."""
    global _backup_file_path
    if _backup_file_path and Path(_backup_file_path).exists():
        print(f"\nRestoring database from: {_backup_file_path}")
        restore_database(_backup_file_path)
        Path(_backup_file_path).unlink(missing_ok=True)
        _backup_file_path = None

def signal_handler(signum, frame):
    """Handle Ctrl+C to restore database before exiting."""
    print("\n\nReceived interrupt signal. Restoring database...")
    restore_and_cleanup()
    # Re-raise the signal to allow normal exit
    signal.signal(signum, signal.SIG_DFL)
    raise KeyboardInterrupt()

# Register signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)
```

#### 2. 在 fixture 中使用全局变量存储备份文件路径

```python
@pytest.fixture(scope="session", autouse=True)
def db_backup():
    """Backup database before tests and restore after all tests complete."""
    global _backup_file_path

    backup_file = backup_database()
    _backup_file_path = backup_file
    print(f"\nDatabase backed up to: {backup_file}")

    yield

    # Normal cleanup
    restore_and_cleanup()
```

#### 3. 行为对比

| 操作 | 行为 |
|------|------|
| 正常结束 | 备份 → 测试 → 恢复 → 清理 |
| Ctrl+C 中断 | 备份 → 测试 → (Ctrl+C) → **恢复数据库** → 清理 → 退出 |

恢复过程会输出：
```
Received interrupt signal. Restoring database...
Restoring database from: /tmp/xxx.sql
Database restored and backup file cleaned up.
```

### 注意事项

1. **不要在信号处理器中调用 `sys.exit()`**：会阻止正常的中断流程，应重新抛出 `KeyboardInterrupt`
2. **全局变量存储备份路径**：信号处理器需要访问 fixture 中创建的备份文件路径
3. **cleanup_auth 不受影响**：`cleanup_auth` 是 function 级别的 autouse fixture，每个测试后都会清理，即使中断也会执行