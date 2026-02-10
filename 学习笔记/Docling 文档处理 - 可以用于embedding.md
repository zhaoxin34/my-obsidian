> 用于文档转 Markdown/JSON，适合 RAG 和 embedding 预处理

## 概述

**Docling** 是由 IBM Research Zurich 团队开发的开源文档处理工具，托管在 **LF AI & Data Foundation** 下。它简化了文档处理流程，支持解析多种格式并进行高级 PDF 理解。

- **GitHub**: https://github.com/docling-project/docling
- **文档**: https://docling-project.github.io/docling/
- **技术报告**: [arXiv 2408.09869](https://arxiv.org/abs/2408.09869)

---

## 核心特性

| 功能 | 说明 |
|------|------|
| **多格式解析** | PDF, DOCX, PPTX, XLSX, HTML, WAV, MP3, VTT, 图片(PNG, TIFF, JPEG等) |
| **高级 PDF 理解** | 页面布局、阅读顺序、表格结构、代码、公式识别、图片分类 |
| **统一表示格式** | DoclingDocument 统一的文档表示格式 |
| **多种导出格式** | Markdown, HTML, DocTags, JSON |
| **本地执行** | 支持敏感数据和气隙环境 |
| **OCR 支持** | 对扫描件和图片进行文字识别 |
| **VLM 支持** | 支持 GraniteDocling 等视觉语言模型 |
| **音频 ASR** | 自动语音识别 |
| **MCP 服务器** | 可连接任意 Agent |

### 集成生态

- LangChain
- LlamaIndex
- Crew AI
- Haystack

---

## 安装

```bash
pip install docling
```

> **注意**: Python 3.9 支持已在 2.70.0 版本移除，需使用 Python 3.10+

---

## 使用方法

### Python API

```python
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # 支持本地路径或 URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # 输出 Markdown
```

### CLI 命令

```bash
docling https://arxiv.org/pdf/2206.01062
```

### 使用 VLM 模型

```bash
docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062
```

---

## 适用场景

- 文档转 Markdown/HTML
- RAG 系统的文档预处理
- 企业文档数字化
- 构建知识库
- 多种格式统一转为结构化 JSON

---

## 参考

- 详细文档: https://docling-project.github.io/docling/
- 示例代码: https://docling-project.github.io/docling/examples/
- Extractions: https://docling-project.github.io/docling/examples/extraction/
