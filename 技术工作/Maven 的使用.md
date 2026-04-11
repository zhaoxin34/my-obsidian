# 打包跳过测试

```bash
mvn package -U -Dmaven.test.skip=true
```

## 给spring-boot:run 加参数示例

```bash
mvn spring-boot:run -Dspring-boot.run.arguments="arg1 arg2 --property=value"
```

## 给java:run 加参数示例

```bash
export JAVA_PROGRAM_ARGS=`echo "$@"`
mvn exec:java -Dexec.mainClass="test.Main" -Dexec.args="$JAVA_PROGRAM_ARGS"
```