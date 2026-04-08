##  服务缩容或减少service实例数量

```bash
kubectl patch -n ${NAMESPACE} sts ${app_name} -p '{"spec": {"replicas":${replicas}}}
```
