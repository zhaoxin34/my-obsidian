# Wolf K8s 操作经验

> 源文件：[[../../raw/Wolf K8s操作经验.md]]

## 服务缩容

### 命令

```bash
kubectl patch -n ${NAMESPACE} sts ${app_name} -p '{"spec": {"replicas":${replicas}}}'
```

### 参数说明

| 参数 | 说明 |
|------|------|
| NAMESPACE | 命名空间 |
| app_name | 应用名称 |
| replicas | 目标副本数 |

## 使用场景

当需要减少 service 实例数量或进行服务缩容时使用此命令。
