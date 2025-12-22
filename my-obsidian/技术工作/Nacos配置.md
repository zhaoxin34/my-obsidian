[官方部署文档](!https://nacos.io/docs/v2.5/manual/admin/deployment/deployment-overview/?spm=5238cd80.1b6d9e68.0.0.2280568aeiMHBu)

## 集群模式的部署方式

 总目标
* 使用mysql
* 暴露promethues监控

官方推荐使用vip,实际可以用k8s sts的有头服务

默认参数
```bash
CUSTOM_NACOS_MEMORY:- -Xms2g -Xmx2g -Xmn1g -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=320m
```

