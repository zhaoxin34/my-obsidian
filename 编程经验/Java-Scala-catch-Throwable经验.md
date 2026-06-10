# Java/Scala 捕获 Throwable 而非 Exception 的经验

## 背景

在调试 wolf-campaign-streaming 项目时，HiveMetastoreClient 调用卡住，jstack 找不到阻塞线程，日志也没有打印错误。最终发现是 `java.lang.NoSuchMethodError`——这是一个 `Error` 而不是 `Exception`。

## 问题场景

### 错误日志

```
java.lang.NoSuchMethodError: 'void org.apache.hadoop.hive.metastore.HiveMetaStoreClient.<init>(org.apache.hadoop.conf.Configuration)'
```

### 原代码问题

```scala
// 只捕获 Exception，不会捕获 Error！
try {
    hiveClient = new HiveMetaStoreClient(hiveConf)
    Success(fun(hiveClient))
} catch {
    case e: Exception => Failure(e)  // ❌ Error 不会被捕获
}
```

### 修改后

```scala
// 捕获 Throwable，可以捕获所有异常类型
try {
    hiveClient = new HiveMetaStoreClient(hiveConf)
    Success(fun(hiveClient))
} catch {
    case e: Throwable =>  // ✅ 捕获 Error、Exception、RuntimeException
        logger.error(s"捕获异常: ${e.getClass.getName}, message=${e.getMessage}", e)
        Failure(e)
}
```

## Java 异常继承关系

```
Throwable
├── Error (非检查型，不需要捕获或声明)
│   ├── NoSuchMethodError
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── ...
└── Exception
    ├── RuntimeException (非检查型)
    │   ├── NullPointerException
    │   ├── IllegalArgumentException
    │   └── ...
    └── IOException, SQLException 等 (检查型)
```

## 使用场景

当遇到以下情况时，考虑使用 `catch Throwable`：
1. **依赖库内部卡住**：jstack 显示线程在执行某方法，但无响应
2. **NoSuchMethodError / NoClassDefFoundError**：类版本不兼容
3. **OutOfMemoryError**：内存溢出
4. **第三方库抛出非标准异常**

## 注意事项

1. **日志要打印异常**：使用 `logger.error(..., e)` 记录完整堆栈
2. **finally 关闭资源**：确保资源被正确释放
3. **区分处理**：可以在 catch 中区分 Error 和 Exception 做不同处理
4. **不要 catch Throwable 后静默处理**：Error 通常表示严重问题，至少要记录日志

```scala
catch {
    case e: Throwable =>
        e match {
            case _: Error =>
                logger.error(s"严重错误: ${e.getClass.getName}", e)
            case _: Exception =>
                logger.warn(s"普通异常: ${e.getMessage}", e)
        }
        Failure(e)
}
```

## Scala 示例

```scala
import scala.util.{Failure, Success, Try}

def execute[T](block: => T): Try[T] = {
    try {
        Success(block)
    } catch {
        case e: Throwable =>
            logger.error(s"执行失败: ${e.getClass.getName}", e)
            Failure(e)
    } finally {
        // 清理资源
    }
}
```

## 经验总结

| 场景 | 推荐捕获 |
|------|---------|
| 普通业务逻辑 | `catch Exception` |
| 库调用/底层代码 | `catch Throwable` |
| 必须捕获的资源错误 | `catch Throwable` |

**核心教训**：当 jstack 找不到阻塞原因，日志也没有错误时，很可能是 `Error` 被静默抛出而非 `Exception`。
