# Log4j 2.x 日志级别配置不生效的解决方案

## 使用场景

当使用 Log4j 2.x 时，代码中通过 `Configurator.setRootLevel()` 或 `LogManager.getRootLogger().setLevel()` 设置日志级别，但运行时日志仍然不输出或级别被覆盖。

### 典型症状

1. 代码中调用了 `logger.info()` 但控制台没有输出
2. `Configurator.setRootLevel(Level.INFO)` 后仍然看不到 INFO 日志
3. 只有 WARN 或 ERROR 级别的日志输出

### 错误关键字

```
LogManager.getRootLogger.setLevel
Configurator.setRootLevel
log4j.rootCategory=WARN
log4j.rootLogger
value setLevel is not a member of org.apache.logging.log4j.Logger
```

## 根本原因

Log4j 2.x 的日志级别由**配置文件**决定，运行时代码设置只是临时覆盖。如果配置文件中的设置优先级更高，日志级别仍会被配置覆盖。

常见冲突场景：

1. **Spark 应用**：Spark 默认使用 `log4j.properties` 配置，设置为 `WARN`
2. **Spring Boot 应用**：使用 `log4j2.xml` 或 `log4j2-spring.xml`
3. **依赖冲突**：同时引入 `log4j-1.2-api`（桥接层）和 `log4j-core`（实际实现）

## 解决方案

### 方案一：修改配置文件（推荐）

将 Log4j 1.x 格式改为 Log4j 2.x 格式，或调整日志级别：

```properties
# Log4j 2.x 格式
rootLogger.level=INFO
rootLogger.appenderRef.stdout.ref=console

# 或针对特定包设置
logger.name=com.datatist.wolf
logger.level=INFO
```

### 方案二：删除冲突配置

如果应用启动时自动加载了 `log4j.properties`（Log4j 1.x 格式），删除或禁用该文件：

```bash
rm /path/to/log4j.properties
# 或在代码中禁用自动配置
System.setProperty("log4j.configurationFile", "")
```

### 方案三：完全禁用 Log4j 1.x 桥接

如果同时使用 Log4j 1.x 和 2.x，确保只使用 2.x：

```xml
<!-- 排除 log4j-1.2-api -->
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-1.2-api</artifactId>
    <exclusions>
        <exclusion>
            <groupId>log4j</groupId>
            <artifactId>log4j</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

### 方案四：在 JVM 参数中指定配置文件

```bash
-Dlog4j.configurationFile=/path/to/log4j2.xml
```

## Spark 应用特殊处理

Spark 使用特殊的日志配置机制，需要注意：

```bash
# 复制 log4j2.properties 到 Spark 配置目录
cp log4j2.properties $SPARK_HOME/conf/

# 或通过 spark-submit 指定
--conf spark.driver.extraJavaOptions="-Dlog4j.configurationFile=file:/path/to/log4j2.properties"
```

Spark 的默认日志配置（`log4j2.properties.template`）：
```properties
rootLogger.level = info
rootLogger.appenderRef.stdout.ref = console
appender.console.target = SYSTEM_ERR
```

## 验证方法

1. 检查日志输出的时间戳格式：
   - Log4j 1.x: `2026/06/04 10:38:14`
   - Log4j 2.x: `2026-06-04T10:38:14.123Z`

2. 检查日志前缀：
   - Log4j 1.x: `INFO MasterNode:`
   - Log4j 2.x: `[INFO] [MasterNode] [2026-06-04T10:38:14]`

3. 在代码中添加测试日志：
```scala
println(s"Current log level: ${LogManager.getRootLogger.getLevel}")
Configurator.setRootLevel(Level.DEBUG)
println(s"New log level: ${LogManager.getRootLogger.getLevel}")
```

## 相关链接

- [Log4j 2.x Configuration](https://logging.apache.org/log4j/2.x/manual/configuration.html)
- [Log4j 1.x to 2.x Migration](https://logging.apache.org/log4j/2.x/manual/migration.html)