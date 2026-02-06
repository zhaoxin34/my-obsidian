## 使用compose方法启动

```yaml
services:
  starrocks:
	name: starrocks
    image: starrocks/allin1-ubuntu:latest
    ports:
      - '8030:8030'
      - '8040:8040'
      - '9030:9030'
```

```bash
docker compose up starrocks

docker exec -it starrocks \  
mysql -P 9030 -h 127.0.0.1 -u root --prompt="StarRocks > "
```

## docker 命令

docker ps -a 可以看所有docker container，包括没启动成功的
docker logs container_id就可以看失败原因