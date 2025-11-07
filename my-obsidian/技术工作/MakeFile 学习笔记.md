 [官网](https://makefiletutorial.com/)

# 简单示例

* 创建变量
* 如何利用@隐藏
```bash
# 简单示例1：直接写命令
hello:
	echo hello

# 简单示例2：使用变量
message = hello world
say:
	echo $(message)

# 简单示例3：多个步骤
all:
	@echo 第一步
	@echo 第二步
	@echo 完成

# 简单示例4：两个独立的目标
target1:
	echo 这是目标1

target2:
	echo 这是目标2

```

# 复杂案例


```bash
# 进阶示例1：依赖关系
# 先编译，再运行
build: compile
	@echo "=== 构建完成 ==="

compile: hello.o
	@echo "正在链接目标文件..."

hello.o: hello.c
	@echo "正在编译 hello.c..."

# 进阶示例2：模式规则
# 自动编译所有.c文件为.o文件
%.o: %.c
	@echo "编译: $< -> $@"

# 进阶示例3：自动变量
# $@ = 目标名, $< = 第一个依赖, $^ = 所有依赖
show-info: info.c
	@echo "目标文件: $@"
	@echo "第一个依赖: $<"
	@echo "所有依赖: $^"

# 进阶示例4：条件判断
# 根据条件执行不同命令
check-debug:
	@if [ -f "debug.mode" ]; then \
		echo "调试模式已开启"; \
	else \
		echo "调试模式未开启"; \
	fi

# 进阶示例5：函数使用
# 使用通配符和字符串替换
SOURCES = $(wildcard *.c)
OBJECTS = $(SOURCES:.c=.o)

show-files:
	@echo "所有源文件: $(SOURCES)"
	@echo "所有目标文件: $(OBJECTS)"

# 进阶示例6：多个依赖
# 一个目标依赖于多个其他目标
final: prepare build check
	@echo "=== 所有步骤完成 ==="

prepare:
	@echo "准备阶段..."

build:
	@echo "构建阶段..."

check:
	@echo "检查阶段..."

# 进阶示例7：带参数的目标
# 使用shell参数
greet:
	@echo "你好, $(USER)!"

show-date:
	@echo "当前日期: $(shell date)"
```


*进阶功能解析

  1️⃣ 依赖关系
  * build: compile        # build依赖compile
  * compile: hello.o      # compile依赖hello.o
  * hello.o: hello.c      # hello.o依赖hello.c

  2️⃣ 模式规则
  * %.o: %.c
        @echo "编译: $< -> $@"
  - %.o: %.c 匹配所有 .c 文件自动编译成 .o
  - 比如有 main.c 和 test.c，会自动编译成 main.o 和 test.o

  3️⃣ 自动变量
  - $@ = 目标文件名（如 hello.o）
  - $< = 第一个依赖名（如 hello.c）
  - $^ = 所有依赖列表

  4️⃣ 条件判断
  @if [ -f "debug.mode" ]; then \
        echo "调试模式已开启"; \
  else \
        echo "调试模式未开启"; \
  fi
  - 检查文件是否存在，做不同处理

  5️⃣ 函数使用
  SOURCES = $(wildcard *.c)      # 查找所有.c文件
  OBJECTS = $(SOURCES:.c=.o)     # 把.c替换成.o
  - $(wildcard *.c) 列出所有.c文件
  - $(SOURCES:.c=.o) 字符串替换

  6️⃣ 多个依赖
  final: prepare build check
  - final 依赖三个目标，会依次执行prepare→build→check

  7️⃣ Shell函数
  show-date:
        @echo "当前日期: $(shell date)"
  - 可以直接调用shell命令