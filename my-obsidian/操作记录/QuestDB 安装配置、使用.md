## 安装

### tar包下载安装

```bash
cd ~/working/server/questdb
wget https://github.com/questdb/questdb/releases/download/9.2.0/questdb-9.2.0-no-jre-bin.tar.gz
tar xzvf questdb-9.2.0-no-jre-bin.tar.gz
```

### 使用jdk17启动 [参考文档](https://questdb.com/docs/quick-start/)

确保主机上安装有jdk17 `jenv versions`

```bash
cd ~/working/server/questdb/questdb-9.2.0-no-jre-bin
jenv local 17
./questdb.sh start
```