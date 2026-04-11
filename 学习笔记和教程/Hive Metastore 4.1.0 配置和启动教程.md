
本教程将帮助你快速配置并启动 Apache Hive Metastore 4.1.0，使用嵌入式 Derby 数据库作为开发/测试环境。

## 什么是 Hive Metastore

Hive Metastore 是 Apache Hive 的元数据存储服务，负责管理表、分区、列等元数据。它提供 Thrift API 供 Spark、Hive 等大数据组件访问元数据。

## 前提条件

在开始之前，确保你具备以下条件：

- **Java 17** 已安装（Metastore 4.1.0 需要 JDK 17+）
- **Hadoop 环境** 已配置（Hadoop 已安装或 HADOOP_HOME 已设置）
- 下载解压了 Hive Metastore 4.1.0

<Tip>
本教程使用嵌入式 Derby 数据库，适合开发测试环境。对于生产环境，建议使用 MySQL、PostgreSQL 等数据库。
</Tip>

## Step 1: 解压并进入目录

如果你还没有解压 Hive Metastore，先进行解压：

```bash
cd /Volumes/data/working/server
tar -xzf apache-hive-metastore-4.1.0-bin.tar.gz
cd apache-hive-metastore-4.1.0-bin
```

你应该看到以下目录结构：

```
apache-hive-metastore-4.1.0-bin/
├── bin/          # 启动脚本
├── conf/         # 配置文件
├── lib/          # JAR 包
├── scripts/      # 数据库脚本
└── licenses/
```

## Step 2: 配置 metastore-site.xml

Hive Metastore 的配置文件位于 `conf/metastore-site.xml`。创建一个适合开发环境的配置：

```bash
cat > conf/metastore-site.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <!-- Thrift 服务地址 -->
  <property>
    <name>metastore.thrift.uris</name>
    <value>thrift://localhost:9083</value>
    <description>Thrift URI for the remote metastore.</description>
  </property>

  <!-- 数据库连接配置 (嵌入式 Derby) -->
  <property>
    <name>javax.jdo.option.ConnectionURL</name>
    <value>jdbc:derby:/tmp/metastore_db;create=true</value>
    <description>JDBC connection URL for embedded Derby database</description>
  </property>

  <property>
    <name>javax.jdo.option.ConnectionDriverName</name>
    <value>org.apache.derby.jdbc.EmbeddedDriver</value>
  </property>

  <property>
    <name>javax.jdo.option.ConnectionUserName</name>
    <value>APP</value>
  </property>

  <property>
    <name>javax.jdo.option.ConnectionPassword</name>
    <value>mine</value>
  </property>

  <!-- Hive 仓库目录 -->
  <property>
    <name>metastore.warehouse.dir</name>
    <value>/tmp/hive/warehouse</value>
    <description>HDFS directory for Hive tables</description>
  </property>

  <!-- 关闭授权检查 (开发环境) -->
  <property>
    <name>metastore.security.authorization.enabled</name>
    <value>false</value>
  </property>

  <!-- 关闭 Schema 版本验证 -->
  <property>
    <name>hive.metastore.schema.verification</name>
    <value>false</value>
  </property>
</configuration>
EOF
```

保存文件。你应该看到 `metastore-site.xml` 已创建。

## Step 3: 创建必要的目录

```bash
mkdir -p /tmp/metastore_db /tmp/hive/warehouse
```

<Note>
Derby 数据库将数据存储在 `/tmp/metastore_db` 目录中。如果你希望数据持久化，可以将路径改为其他位置，如 `/Volumes/data/working/hive-metastore-db`。
</Note>

## Step 4: 设置环境变量并初始化数据库 Schema

在启动 Metastore 之前，需要先初始化数据库表结构。使用 `schematool` 工具：

```bash
export HADOOP_HOME=/Volumes/data/working/server/hadoop-3.4.3
cd /Volumes/data/working/server/apache-hive-metastore-4.1.0-bin
./bin/schematool -dbType derby -initSchema
```

你应该看到初始化过程：

```
Initializing the schema to: 4.1.0
Metastore connection URL:     jdbc:derby:/tmp/metastore_db;create=true
Metastore connection Driver :     org.apache.derby.jdbc.EmbeddedDriver
Starting metastore schema initialization to 4.1.0
Initialization script hive-schema-4.1.0.derby.sql
...
Initialization script completed
```

<Warning>
如果看到 "FUNCTION already exists" 错误，说明之前已经初始化过。需要先删除数据库目录再重新初始化：
```bash
mv /tmp/metastore_db /tmp/claude/.delete.metastore_db
./bin/schematool -dbType derby -initSchema
```
</Warning>

## Step 5: 启动 Hive Metastore

现在启动 Metastore 服务：

```bash
export HADOOP_HOME=/Volumes/data/working/server/hadoop-3.4.3
nohup ./bin/start-metastore > /tmp/metastore.log 2>&1 &
```

等待几秒钟让服务启动：

```bash
sleep 5
```

## Step 6: 验证 Metastore 是否成功启动

检查 Metastore 进程是否在运行：

```bash
ps aux | grep metastore | grep -v grep
```

你应该看到类似输出：

```
zhaoxin  30961   0.1  1.8 ... java -Dproc_metastore ... HiveMetaStore
```

检查端口 9083 是否正在监听：

```bash
lsof -i :9083
```

你应该看到：

```
COMMAND   PID    USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
java    30961 zhaoxin  661u  IPv6 0xff731c9...      0t0  TCP *:9083 (LISTEN)
```

恭喜！Metastore 已经在端口 9083 上运行了。

## 停止 Metastore

如果需要停止 Metastore，执行：

```bash
pkill -f "HiveMetaStore"
```

或者通过进程ID：

```bash
kill <PID>
```

## 常用命令汇总

```bash
# 设置环境变量
export HADOOP_HOME=/Volumes/data/working/server/hadoop-3.4.3
export METASTORE_HOME=/Volumes/data/working/server/apache-hive-metastore-4.1.0-bin

# 进入目录
cd $METASTORE_HOME

# 初始化数据库 (首次)
./bin/schematool -dbType derby -initSchema

# 启动 Metastore
./bin/start-metastore

# 查看 Schema 信息
./bin/schematool -dbType derby -info

# 查看日志
tail -f /tmp/metastore.log

# 停止 Metastore
pkill -f "HiveMetaStore"
```

## 常见问题

### Q: 启动时报 "Cannot find hadoop installation"

确保设置了 `HADOOP_HOME` 环境变量：

```bash
export HADOOP_HOME=/Volumes/data/working/server/hadoop-3.4.3
```

### Q: 端口 9083 被占用

先检查是哪个进程占用了端口：

```bash
lsof -i :9083
```

然后停止该进程或修改 `metastore-site.xml` 中的端口。

### Q: Derby 数据库损坏

删除数据库目录并重新初始化：

```bash
mv /tmp/metastore_db /tmp/claude/.delete.metastore_db
./bin/schematool -dbType derby -initSchema
```

## 下一步

现在 Metastore 已经运行，你可以：

- 使用 Spark 连接 Metastore：`spark.sql.warehouse.dir` 配置为 `/tmp/hive/warehouse`
- 使用 Hive CLI 连接：`hive --hiveconf hive.metastore.uris=thrift://localhost:9083`
- 将 Metastore 配置为 MySQL/PostgreSQL 用于生产环境

<Tip>
生产环境建议使用 MySQL 或 PostgreSQL 作为后端数据库，具体配置方法请参考 Hive 官方文档。
</Tip>
