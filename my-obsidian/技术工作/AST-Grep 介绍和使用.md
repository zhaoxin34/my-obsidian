## 简介

可以认为ast-grep就是高级版本的grep、lint, 下面是个简单示例

```
ast-grep --pattern 'var code = $PAT' --rewrite 'let code = $PAT' --lang js
```

## 入门操作

*安装*

```bash
brew install ast-grep

sg --help
```

 