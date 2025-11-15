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

# 创建数据目录 
mkdir ../data
./questdb.sh start -d ../data

JAVA: /Users/zhaoxin/.jenv/versions/17/bin/java

     ___                  _   ____  ____
    / _ \ _   _  ___  ___| |_|  _ \| __ )
   | | | | | | |/ _ \/ __| __| | | |  _ \
   | |_| | |_| |  __/\__ \ |_| |_| | |_) |
    \__\_\\__,_|\___||___/\__|____/|____/
                        www.questdb.io

    Web Console URL                 ILP Client Connection String

    http://192.168.31.96:9000       http::addr=192.168.31.96:9000;
    http://127.0.0.1:9000           http::addr=127.0.0.1:9000;
```

