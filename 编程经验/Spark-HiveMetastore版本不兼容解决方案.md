# Spark 访问 Hive Metastore 版本不兼容解决方案

## 背景

在 wolf-campaign-streaming 项目中，使用 `HiveMetaStoreClient` 直接连接 Hive Metastore 时遇到 `NoSuchMethodError`：

```
java.lang.NoSuchMethodError: 'void org.apache.hadoop.hive.metastore.HiveMetaStoreClient.<init>(org.apache.hadoop.conf.Configuration)'
```

**根因**：编译时依赖的 Hive 版本与运行时 Spark 打包的 Hive 版本不一致。

## 问题分析

### 依赖配置

```scala
// project/Dep.scala
val versionHiveMetastore = "4.1.0"
val versionSpark = "4.1.1"

val depsSparkProvided = Seq(
    sparkHive % Provided,  // Spark 4.1.1 内置 Hive
    "org.apache.hive" % "hive-metastore" % versionHiveMetastore % Provided,  // 4.1.0
)
```

**问题**：
- 编译时用 `hive-metastore 4.1.0` 创建 `HiveMetaStoreClient`
- 运行时 Spark 4.1.1 打包了不同版本的 Hive Metastore
- `HiveMetaStoreClient` 构造函数签名在两个版本间不兼容

### 错误代码

```scala
// ❌ 直接 new HiveMetaStoreClient，依赖编译时的 Hive 版本
def execute[T](sparkConf: SparkConf)(fun: HiveMetaStoreClient => T): Try[T] = {
    try {
        val hiveConf = new HiveConf()
        hiveConf.set("hive.metastore.uris", sparkConf.get("hive.metastore.uris"))
        hiveClient = new HiveMetaStoreClient(hiveConf)  // ❌ 版本冲突
        Success(fun(hiveClient))
    } catch {
        case e: Throwable => Failure(e)
    }
}
```

## 解决方案

### 推荐方案：使用 SparkSession.catalog

使用 Spark 自带的 API，Spark 会自动处理 Hive 版本兼容性问题：

```scala
import org.apache.spark.sql.SparkSession

object HiveClient {
    
    def tableExists(spark: SparkSession)(database: String, tableName: String): Try[Boolean] = {
        Try {
            spark.catalog.tableExists(database, tableName)
        }
    }
    
    def listTables(spark: SparkSession)(database: String): Try[Seq[String]] = {
        Try {
            spark.catalog.listTables(database).collect().map(_.name)
        }
    }
    
    def getTablePartitions(spark: SparkSession)
                          (database: String, tableName: String): Try[Seq[String]] = {
        Try {
            val df = spark.sql(s"SHOW PARTITIONS $database.$tableName")
            df.collect().map(_.getString(0))
        }
    }
}
```

### 调用方式

```scala
// 原来
HiveClient.execute(spark.sparkContext.getConf)(_.tableExists(database, tableName))

// 现在
HiveClient.tableExists(spark)(database, tableName)
```

## SparkSession.catalog API 列表

| API | 用途 |
|-----|------|
| `catalog.tableExists(database, tableName)` | 检查表是否存在 |
| `catalog.listTables(database)` | 列出数据库中的表 |
| `catalog.listDatabases()` | 列出所有数据库 |
| `catalog.tableExists(tableName)` | 检查当前数据库中的表 |
| `spark.sql("SHOW PARTITIONS ...")` | 获取分区列表 |
| `spark.sql("DESCRIBE TABLE ...")` | 获取表结构 |

## 使用场景

1. **Spark 应用中访问 Hive 表**：使用 SparkSession.catalog
2. **需要 SparkSession 的场景**：必须通过 Spark 访问 Hive
3. **版本不确定的生产环境**：避免直接依赖 Hive Metastore 客户端 JAR

## 不适用场景

如果必须使用原始的 Hive Metastore API（如 `HiveMetaStoreClient` 的高级功能），可以考虑：

1. **统一依赖版本**：确保编译和运行的 Hive 版本完全一致
2. **shade jar**：将 Hive 依赖打包进 uber-jar
3. **分离服务**：单独的 Hive Metastore 客户端进程

## 经验总结

| 方案 | 优点 | 缺点 |
|------|------|------|
| SparkSession.catalog | 版本兼容、无额外依赖 | API 有限 |
| HiveMetaStoreClient | 功能完整 | 版本兼容性问题 |
| 统一依赖版本 | 完全控制 | 部署复杂 |

**核心教训**：在 Spark 应用中，优先使用 Spark 自带的 DataFrame/SQL API，而非直接使用底层 Hive 客户端。Spark 会自动处理版本兼容性问题。
