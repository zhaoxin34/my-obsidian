一个生产级的个人知识库系统，支持语义搜索和基于 LLM 的问答功能。

## 项目信息
* github地址：https://github.com/zhaoxin34/memory
## 功能特性
- **仓库隔离**: 使用仓库（Repository）组织和隔离不同项目或主题的文档
- **语义搜索**: 使用向量相似度查找相关信息，支持仓库范围搜索
- **LLM 问答**: 提出问题并获得带有来源引用的 AI 生成答案
- **模块化架构**: 可灵活切换嵌入模型、LLM 和向量数据库
- **多种文档类型**: 支持 Markdown、PDF、HTML 和纯文本
- **配置驱动**: 所有行为通过 TOML 配置文件控制
- **类型安全**: 完整的类型提示和 Pydantic 验证
- **生产就绪**: 结构化日志、错误处理和可观测

## 相关文档
* [[Split markdown - text splitter integration 一个markdown切分工具]]
* [[Docling 文档处理 - 可以用于embedding]]