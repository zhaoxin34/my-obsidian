# 目标

* 测试大内存下创建大量小对象的gc性能
* 验证cms、g1、zgc垃圾回收的效率
* 对流程引擎未来使用哪种回收器提供数据支持

# 实现方案

使用同样的代码，在值更换gc方式的方式下，把gc日志输出，然后对比分析

# 实验代码的核心逻辑

代码见CMSFragmentationDemo.java

## 内存碎片生成

通过创建Fragment对象，创建小对象，小对象是32个字节的byte[]数组，然后创建虚对象，填满eden区，让Fragment的小对象晋升到old区
```java
class Fragment {
    public Fragment(long fragCount, int fragmentSize) {
        out.println("总碎片块: " + fragCount);
        fragments = new ArrayList<>((int) fragCount);
        for (long i = 0; i < fragCount; i++) {
            fragments.add(new byte[fragmentSize]);
            if (i % 100000 == 0) {
                out.println("新建了100k个碎片, 占用空间: " + i * fragmentSize / 1024 / 1024 + "M");
            }
        }

        // 创建新的对象让，fragments晋升到老年代
        createGarbage((long) fragCount * fragmentSize / 10);
    }
}
```

## 创建碎片

通过不断创建Fragment对象，让系统触发gc

```java
new Fragment(fragCount, FRAGMENT_SIZE);

```

# 启动脚本

## jdk1.8 cms

```bash
/workspace/software/jdk1.8.0_321/bin/java \
  -Xms60G -Xmx60G \
  -XX:+UseConcMarkSweepGC \
  -XX:+UseParNewGC \
  -XX:CMSInitiatingOccupancyFraction=75 \
  -XX:+UseCMSInitiatingOccupancyOnly \
  -XX:+PrintGCDetails \
  -XX:+PrintGCTimeStamps \
  -XX:MaxTenuringThreshold=5 \
  -Xloggc:out/gc.log \
  -classpath out \
  CMSFragmentationDemo 60000000000
```

## jdk1.8 g1

```bash
/workspace/software/jdk1.8.0_321/bin/java \
  -Xms60G -Xmx60G \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+UseG1GC -XX:G1ReservePercent=15 \
  -XX:+PrintGCDetails \
  -XX:+PrintGCTimeStamps \
  -XX:MaxTenuringThreshold=5 \
  -Xloggc:g1-jdk18.gc.log \
  -classpath out \
  CMSFragmentationDemo 60000000000
```

## jdk11 g1

```bash
/workspace/software/jdk-11.0.28/bin/java \
  -Xms60G -Xmx60G \
  -XX:+UseG1GC -XX:G1ReservePercent=15 \
  -XX:+PrintGCDetails \
  -XX:MaxTenuringThreshold=5 \
  -Xloggc:g1-jdk11-gc.log \
  -classpath out \
  CMSFragmentationDemo 60000000000
```

## jdk17 zgc

```bash
/workspace/software/jdk-17.0.16/bin/java \
  -Xms60G -Xmx60G \
  -XX:+UseZGC \
  -XX:+PrintGCDetails \
  -XX:MaxTenuringThreshold=5 \
  -Xloggc:out/zgc-jdk17-gc.log \
  -classpath out \
  CMSFragmentationDemo 60000000000
```

# 将gc日志发给gpt的分析结果

| 项目      | CMS (JDK 8) | G1 (JDK 8) | G1 (JDK 11) | **ZGC (JDK 17)** |
| ------- | ----------- | ---------- | ----------- | ---------------- |
| 平均停顿    | 1.8 s       | 0.85 s     | 0.35 s      | **0.0005 s**     |
| 标记耗时    | 100 s       | 22 s       | 3 s         | **0.006 s**      |
| Full GC | 1 次 (62 s)  | 1 次 (17 s) | 无           | **无**            |
| 吞吐      | 低           | 中          | 高           | **极高**           |
| 稳定性     | 差           | 中          | 高           | **极高**           |
| 调优复杂度   | 高           | 中          | 低           | **极低**           |
| 推荐场景    | 旧服务         | 一般服务       | 中低延迟        | **超低延迟/大堆系统**    |



# 操作方法
```bash
# 登录主机 root@ma-uat-arm-ncs01

# 登录pod
k exec -it -n dev-wolf wolf-campaign-mem-test-0 -- bash

# 进入/usr/local/src/java
# /usr/local/src/java
sh start-cms.sh
sh start-g1-jdk11.sh
sh start-g1-jdk18.sh
sh start-zgc.sh

# 日志生成到out目录下

```