---
title: mise + JDK 多版本管理实战 - Spring Boot 项目场景
tags: [mise, jdk, java, spring-boot, 工具链]
---

# mise + JDK 多版本管理实战 - Spring Boot 项目场景

> 适用场景：你维护一堆 Spring Boot 工程，老项目用 JDK 8/11，新项目用 JDK 17/21，每个项目还有自己固定的 Maven 版本。不想再用 `JAVA_HOME` 切来切去。

## 1. 核心心智模型（一句话版）

**mise.toml = 项目级 `.nvmrc` 升级版。** 它声明"进入这个目录后，应该用什么版本的 JDK / Maven / Node"。你 `cd` 进去，shell 提示符一刷，版本就自动切好。**不要手工 source、不要写 bash 脚本。**

三层配置，**就近覆盖**：

| 范围 | 文件 | 谁会用 |
|---|---|---|
| 当前项目 | `./mise.toml` | 团队成员，CI |
| 用户全局 | `~/.config/mise/config.toml` | 你的所有项目 |
| 系统兜底 | `MISE_*` 环境变量 | 临时覆盖 |

项目级 `./mise.toml` **优先**于全局。**所以你的 Spring Boot 工程根目录必须各放一个 `mise.toml`**，这是关键。

## 2. 第一个 `mise.toml`

Spring Boot + JDK 17 + Maven 3.9 的典型项目根目录：

```toml
[env]
# 让 mvn / gradle 等工具能感知 JAVA_HOME
JAVA_HOME = "{{env.JDK17_HOME}}"  # 写法见下，更推荐用 _java 别名

[tools]
java = "17.0.11"
maven = "3.9.9"
```

**注意**：上面 `{{env.JDK17_HOME}}` 只是示意。mise 处理 JDK 时会**自动把当前激活的 java 暴露成 `JAVA_HOME` 环境变量**，根本不用你自己写 `[env]`。所以最小可用版其实只有两行：

```toml
[tools]
java = "17.0.11"
maven = "3.9.9"
```

需要 Maven 用阿里云镜像？继续加：

```toml
[env]
# 注意：mise 的 [env] 在 shell 启动时 export，mvn 能直接读到
MAVEN_OPTS = "-Xmx2g"
_.source = ".maven-settings.env"   # 想拆文件也行，参考文档

[tools]
java = "17.0.11"
maven = "3.9.9"
```

## 3. JDK 关键命令（记住这几个就够用）

```bash
# 列出当前系统可用的 JDK（mise 已安装 + 候选）
mise ls java              # 已安装
mise ls-remote java       # 所有可下载的版本

# 安装指定版本（手动安装，没写进 mise.toml）
mise install java@21.0.4
mise install              # 读取当前目录 mise.toml，一次性装齐

# 看当前目录激活的是什么
mise current              # 一次性看 java/maven/... 当前版本
mise current java         # 单看 java

# 临时切换（不写进文件，仅当前 shell）
mise use java@21          # 仅当前 shell
mise use --env java=21    # 写进 mise.toml 的 [env]，非交互

# 验证 JDK 真的切了
which java
java -version
echo $JAVA_HOME
```

> ⚠️ `mise use java@21` 会**自动写入**当前目录的 `mise.toml`，如果是 `[tools]` 段没写就会新建。**这个行为是 mise 的核心**，别怕它改文件。

## 4. 多项目实战：JDK 版本不一的 Spring Boot 工程

### 4.1 项目根布局示意

```text
~/work/
├── legacy-erp/                 # JDK 8 老古董
│   ├── mise.toml               # java = "8.0.412"
│   ├── pom.xml
│   └── src/
├── order-service/              # JDK 17 主力
│   ├── mise.toml               # java = "17.0.11"
│   └── pom.xml
└── ai-platform/                # JDK 21 新项目
    ├── mise.toml               # java = "21.0.4"
    └── pom.xml
```

### 4.2 每个项目自己的 `mise.toml`

**`~/work/legacy-erp/mise.toml`**

```toml
[tools]
java = "8.0.412"          # Temurin 8，最后一个免费商用版本
maven = "3.6.3"           # 老项目别用太新的 mvn，插件会炸
```

**`~/work/order-service/mise.toml`**

```toml
[tools]
java = "17.0.11"
maven = "3.9.9"
```

**`~/work/ai-platform/mise.toml`**

```toml
[tools]
java = "21.0.4"
maven = "3.9.9"
```

### 4.3 工作流

```bash
cd ~/work/legacy-erp
mise current               # 输出 java 8.0.412  maven 3.6.3
mvn clean package          # 用 JDK 8 编译

cd ~/work/ai-platform
mise current               # 输出 java 21.0.4  maven 3.9.9
mvn spring-boot:run        # 用 JDK 21 起服务
```

**没有 `export JAVA_HOME`，没有 `sdk use java`，没有任何脚本。** 切目录就完事。

### 4.4 全局兜底配置（可选）

如果 90% 项目都是 JDK 17，把 17 设为全局默认，进入没有 `mise.toml` 的目录也不会报错：

```toml
# ~/.config/mise/config.toml
[tools]
java = "17.0.11"
```

## 5. JDK 选型的几个坑

### 5.1 版本号写法的含义

```toml
[tools]
java = "17"           # 任意 17.x.y
java = "17.0.11"      # 精确锁版本（推荐，团队一致）
java = "17.0.11+tem"  # 锁到 Temurin 发行版
java = "openjdk-17"   # 用通用 openjdk
```

**团队项目必须写精确版本**，否则 A 同学装了 17.0.10，B 同学是 17.0.11，maven 编译产物可能不一致。CI 也读这个文件，**确保 CI 装的是同一个 mise**，就能复现。

### 5.2 JDK 发行版选择

mise 的 java 后端支持多发行版，常见几个：

| 写法 | 发行版 | 适用 |
|---|---|---|
| `17.0.11` / `temurin-17.0.11` | Eclipse Temurin (Adoptium) | 主流，**推荐** |
| `corretto-17.0.11` | AWS Corretto | AWS 生态 |
| `zulu-17.0.11` | Azul Zulu | 有 Azul 商业支持需求 |
| `graalvm-17.0.11` | GraalVM | 用 native-image 必选 |

切发行版：

```toml
[tools]
java = "21.0.4-graal"   # 末尾加 -graal 即 GraalVM JDK 21
```

### 5.3 mise 装的 JDK 在哪？

```bash
mise where java          # 输出当前激活的 JDK 绝对路径
ls $(mise where java)    # 真实安装位置 ~/.local/share/mise/installs/java/
```

**别再去 `/Library/Java/JavaVirtualMachines/` 找了**，macOS 系统自带的 JDK 和 mise 装的不冲突，**以 PATH 为准**。

### 5.4 Maven 调用的 JDK 不是预期的？

写一个测试验证：

```bash
cd ~/work/order-service
mise exec -- mvn -version
```

`mise exec` 会**强制**用 mise.toml 声明的环境执行，看到的 java 版本就是团队约定的。如果 `mvn -version` 报错的 JDK 版本不对，**说明你的 shell hook 没装好**：

```bash
mise doctor               # 自检
mise activate zsh >> ~/.zshrc   # 没生效就重新跑一次
```

## 6. CI 里怎么用

GitHub Actions 例子：

```yaml
- uses: jdx/mise-action@v2
- run: mvn -version
- run: mvn verify
```

**不用再写 `actions/setup-java@v4` + `distribution: temurin` + `java-version: 17` 一堆配置**，因为 `mise.toml` 已经声明了。

## 7. 配合 IntelliJ IDEA

IDEA 读 `mise.toml`：

1. `Settings → Build, Execution, Deployment → Build Tools → Maven → JDK for importer`
2. 选 **"Detect from MISE"**（2024.2+ 支持），或在 `Project SDK` 下拉里选 mise 装的 JDK
3. `Settings → Project → Project SDK` 同样指定

或者更简单：把 mise 的 JDK 路径加进 `Project Structure → SDKs → +`，**手动选一次**，IDEA 会记住。

## 8. 速查表

| 需求 | 命令 / 配置 |
|---|---|
| 在当前目录声明使用 JDK 17 | `mise use java@17` |
| 在当前目录声明使用 JDK 17 + Maven 3.9 | `mise use java@17 maven@3.9` |
| 一次性装齐项目所有工具 | `mise install` |
| 看远程可装的 JDK | `mise ls-remote java` |
| 查当前激活的工具路径 | `mise where java` |
| 用项目约定的环境跑命令 | `mise exec -- mvn clean package` |
| 全局默认 JDK 17 | `~/.config/mise/config.toml` 写 `[tools] java = "17"` |
| 团队新人 clone 项目后 | `cd 进去 && mise install` |
| CI 集成 | `jdx/mise-action@v2` |

## 9. 一句话总结

**给每个 Spring Boot 项目根目录丢一个 `mise.toml` 写 `java = "精确版本"`，从此 `cd` 即切版本。** 其他事情都交给 mise 和 shell hook。
