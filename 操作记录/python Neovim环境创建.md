首先进行 [[python 环境初始化]]

pip install pynvim

使用pyright作为语言服务器，而不使用python-lsp-server，以下是对比

| 特性   | Pyright                 | python-lsp-server |
| ---- | ----------------------- | ----------------- |
| 开发者  | 微软                      | Python 社区         |
| 实现语言 | TypeScript (Node.js)    | Python            |
| 优势   | 快速、强大的类型推断和检查           | 插件生态灵活，Python 原生  |
| 缺点   | 不支持某些 Python-only 插件    | 性能不如 Pyright      |
| 推荐场景 | 现代 Python 项目，大型代码库，类型严格 |                   |
pyright需要node.js支持 [[Node.js环境初始化]]