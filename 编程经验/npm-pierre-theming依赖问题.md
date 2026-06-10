# npm 依赖包被删除导致 update 失败的解决方案

## 使用场景

执行 `pi update` 或 `npm install` 时报错：

```
npm error 404 Not Found - GET https://registry.npmjs.org/@pierre%2ftheming - Not found
npm error 404  The requested resource '@pierre/theming@0.0.1' could not be found or you do not have permission to access it.
```

## 问题原因

某个 npm 包（这里是 `@pierre/diffs`）的传递依赖 `@pierre/theming@0.0.1` 已被作者删除或从未发布。

依赖链：
```
pi update
  └── @plannotator/pi-extension
        └── @pierre/diffs
              └── @pierre/theming@0.0.1  ← 已不存在
```

## 排查方法

1. **检查哪个包依赖问题包**：
```bash
# 查看当前 package.json
cat ~/.pi/agent/npm/package.json

# 逐个检查扩展包的依赖
npm view @plannotator/pi-extension dependencies
npm view @pierre/diffs@1.2.9 dependencies
```

2. **搜索 npm 上是否存在**：
```bash
npm search "@pierre/theming" 2>&1
npm view @pierre/theming 2>&1
```

## 解决方案

### 方案一：从 package.json 中移除问题包

如果 `package.json` 中包含有问题的包，直接删除：

```bash
cd ~/.pi/agent/npm
npm pkg delete dependencies.@plannotator/pi-extension
npm pkg delete dependencies.@juicesharp/rpiv-todo  # 可能也依赖问题包
rm -f package-lock.json
npm install --legacy-peer-deps
```

### 方案二：固定问题包到旧版本

如果必须使用某个包，可以固定到不依赖问题包的旧版本：

```bash
npm install @pierre/diffs@1.1.12 --save-exact
```

### 方案三：报告给包作者

这是上游问题，需要包作者修复依赖关系。

## 经验总结

1. **npm 包的传递依赖可能被悄悄删除**：即使 `package.json` 中没有直接依赖，问题包可能通过传递依赖被引入
2. **settings.json 和 package.json 是分开的**：pi 扩展可能在两个地方配置，需要同时检查
3. **删除 node_modules 后重新安装**：修改 package.json 后，删除 `package-lock.json` 并重新 `npm install` 可以清理残留的传递依赖