[官方部署文档](https://nacos.io/docs/v2.5/manual/admin/deployment/deployment-overview/?spm=5238cd80.1b6d9e68.0.0.2280568aeiMHBu)

## 集群模式的部署方式

 总目标
* 使用mysql
* 暴露promethues监控

官方推荐使用vip,实际可以用k8s sts的有头服务

默认参数
```bash
CUSTOM_NACOS_MEMORY:- -Xms2g -Xmx2g -Xmn1g -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=320m
```

创建nacos数据库
```sql
CREATE DATABASE IF NOT EXISTS nacos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

执行mysql-scehma.sql

application.properties
```
spring.sql.init.platform=mysql

### Count of DB:
db.num=1

### Connect URL of DB:
db.url.0=jdbc:mysql://mysql-svc.store.svc.cluster.local:3306/nacos?characterEncoding=utf8&connectTimeout=1000&socketTimeout=3000&autoReconnect=true&useUnicode=true&useSSL=false&serverTimezone=Asia/Shanghai
db.user.0=root
db.password.0=abc123

management.endpoints.web.exposure.include=prometheus,health



```