# LightRAG 使用教程 — 轻量级检索增强生成系统

> LightRAG 由香港大学（HKU）开发，已被 EMNLP 2025 录用。它通过基于图的索引策略和双模式检索（局部+全局）实现了高效且具有上下文关联的 RAG 能力。
>
> **项目地址**: https://github.com/HKUDS/LightRAG

## 目录

- [核心特性](#核心特性)
- [系统架构](#系统架构)
- [安装方式](#安装方式)
- [快速入门（Python API）](#快速入门python-api)
- [LightRAG Server 部署](#lightrag-server-部署)
- [多种存储后端配置](#多种存储后端配置)
- [查询模式详解](#查询模式详解)
- [高级功能](#高级功能)
- [LLM 配置要求](#llm-配置要求)

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **图索引增强** | 将文档中的实体和关系抽取为知识图谱，支持多跳推理 |
| **双模式检索** | 局部检索（local）利用实体邻居，全局检索（global）通过图遍历 |
| **流式输出** | 支持 LLM 流式响应，降低感知延迟 |
| **多存储后端** | 默认使用 JSON/NetworkX，也支持 Neo4j、Milvus、MongoDB、Redis、OpenSearch 等 |
| **多模态扩展** | 通过 RAG-Anything 集成支持 PDF、Office、图片、表格等多格式文档 |
| **并行查询优化** | 有效缩短查询耗时 |
| **Token 用量追踪** | 支持统计每次 LLM 调用的 token 消耗 |
| **数据导出** | 可将知识图谱导出为 CSV 文件 |

---

## 系统架构

### 索引流程（Indexing Flow）

```
文档 → 文本分块（Chunking）
     → LLM 实体/关系抽取（Entity Extraction）
     → 构建知识图谱（Entity + Relation）
     → 向量化存储（Embedding）
     → 四类存储（KV / Vector / Graph / DocStatus）
```

### 查询流程（Querying Flow）

```
用户查询 → 向量化查询向量
        → 同时执行：
        │  ├─ 局部模式（Local）：向量检索 → 找到实体邻居节点
        │  └─ 全局模式（Global）：图遍历 → 基于关系图谱聚合信息
        → 合并两路结果 → LLM 生成最终答案
```

LightRAG 的关键创新在于：**将实体级别的局部感知与图结构级别的全局感知相结合**，避免了一般向量 RAG 容易忽略跨文档关联信息的缺点。

---

## 安装方式

### 方式一：通过 uv 安装（推荐）

```bash
# 安装 LightRAG 核心库
uv tool install "lightrag-hku"

# 安装含 API Server 的完整版
uv tool install "lightrag-hku[api]"

# 或使用 pip
pip install "lightrag-hku[api]"
```

### 方式二：从源码安装

```bash
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG

# 推荐的开发环境安装（含 API + 存储后端 + 测试工具链）
make dev
source .venv/bin/activate

# 等价的手动步骤（uv）
uv sync --extra api --extra offline
source .venv/bin/activate

# 仅安装 API 支持
uv sync --extra api
```

### 方式三：Docker 部署（Server）

```bash
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG

# 创建并编辑环境变量文件
cp env.example .env
# 修改 .env 中的 LLM 和 Embedding 配置

# 启动
docker compose up
```

### 离线/内网环境部署

参考 `docs/OfflineDeployment.md`，需要预先下载所有依赖和模型文件。

---

## 快速入门（Python API）

### 1. 准备代码

LightRAG 提供了与 OpenAI API 兼容的示例代码，最简单的方式是修改示例运行：

```python
# examples/lightrag_openai_compatible_demo.py
import os
import asyncio
import inspect
import logging
from functools import partial

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.llm.ollama import ollama_embed
from lightrag.utils import EmbeddingFunc
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=False)
WORKING_DIR = "./dickens"

# ========== 1. 定义 LLM 和 Embedding 函数 ==========

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        os.getenv("LLM_MODEL", "deepseek-chat"),
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("LLM_BINDING_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("LLM_BINDING_HOST", ""),
        **kwargs,
    )

# Embedding 函数（使用 Ollama）
embedding_func = ollama_embed(model="bge-m3")

# ========== 2. 初始化 LightRAG ==========

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=llm_model_func,
    embedding_func=embedding_func,
)

# ========== 3. 插入文档 ==========

with open("./book.txt", "r", encoding="utf-8") as f:
    await rag.ainsert(f.read())

# ========== 4. 执行查询 ==========

# 局部搜索 —— 适合关于特定实体的问题
print("\n===== Local Mode =====")
resp = await rag.aquery(
    "What are the top themes in this story?",
    param=QueryParam(mode="local", stream=True),
)
if inspect.isasyncgen(resp):
    async for chunk in resp:
        print(chunk, end="", flush=True)
else:
    print(resp)

# 全局搜索 —— 适合需要综合多方面信息的问题
print("\n===== Global Mode =====")
resp = await rag.aquery(
    "What are the top themes in this story?",
    param=QueryParam(mode="global", stream=True),
)
# ...
```

### 2. 配置 .env 文件

```bash
# .env 示例（使用 OpenAI）
LLM_BINDING=openai
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=3072
OPENAI_API_KEY=your-api-key
```

或使用 Ollama 本地模型：

```bash
LLM_BINDING=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-chat
EMBEDDING_BINDING=ollama
OLLAMA_EMBED_MODEL=bge-m3
```

### 3. 运行

```bash
# 确保 book.txt 存在
mkdir -p ./dickens
echo "Once upon a time..." > ./dickens/book.txt

python examples/lightrag_openai_compatible_demo.py
```

### 4. QueryParam 详解

```python
from lightrag import QueryParam

param = QueryParam(
    mode="mix",           # 检索模式：naive / local / global / mix
    stream=False,         # 是否流式返回
    top_k=60,             # 向量检索返回的 Top-K 结果
    max_entity_collect=100,  # 最大实体收集数量
    max_graph_collect=300,    # 图检索最大收集节点数
    history_turns=3,         # 对话历史轮次
)
```

| mode | 说明 |
|------|------|
| `naive` | 纯向量检索（传统 RAG） |
| `local` | 基于实体邻居的局部检索 |
| `global` | 基于图遍历的全局检索 |
| `mix` | 混合局部+全局（推荐默认选项） |

---

## LightRAG Server 部署

LightRAG Server 提供 Web UI + REST API，适合不想直接操作 Python 代码的用户。

### 前置条件

- 已安装 LightRAG（见上方安装步骤）
- Node.js + Bun（构建前端）

### 启动步骤

```bash
# 1. 安装前端依赖并构建
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..

# 2. 配置环境变量
cp env.example .env
# 编辑 .env，填入 LLM 和 Embedding 的 API Key / URL

# 3. 启动服务
lightrag-server
```

启动后，Web UI 通常在 `http://localhost:9720`，API 在 `http://localhost:9720/api`。

### Web UI 功能

- **文档索引**：上传文件，触发知识图谱构建
- **知识图谱可视化**：支持多种布局、节点查询、子图过滤
- **RAG 查询**：直接输入自然语言查询
- **Ollama 兼容接口**：LightRAG Server 模拟 Ollama API，可被 Open WebUI 等工具直接调用

### Docker Compose 启动（推荐用于生产）

```bash
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG
cp env.example .env
# 修改 .env

docker compose up
```

---

## 多种存储后端配置

LightRAG 默认使用本地 JSON 文件存储，适合小规模使用。生产环境建议使用专用数据库。

### 四类存储说明

| 存储类型 | 用途 | 默认实现 |
|----------|------|----------|
| `KV_STORAGE` | LLM 响应缓存、文本块、文档信息 | JsonKVStorage |
| `VECTOR_STORAGE` | 实体/关系/文本块的向量 | NanoVectorDBStorage |
| `GRAPH_STORAGE` | 实体-关系图结构 | NetworkXStorage |
| `DOC_STATUS_STORAGE` | 文档索引状态 | JsonDocStatusStorage |

### Neo4j 图数据库

```bash
# 启动 Neo4j
docker run -d -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

```python
import os
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "password"

rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=llm_model_func,
    embedding_func=embedding_func,
    graph_storage="Neo4jStorage",
)
```

### Milvus 向量数据库

```bash
# 通过环境变量配置
MILVUS_URI=http://localhost:19530
MILVUS_DB_NAME=lightrag
LIGHTRAG_VECTOR_STORAGE=MilvusVectorDBStorage
```

```python
rag = LightRAG(
    working_dir="./rag_storage",
    llm_model_func=llm_model_func,
    embedding_func=embedding_func,
    vector_storage="MilvusVectorDBStorage",
    vector_db_storage_cls_kwargs={
        "milvus_uri": "http://localhost:19530",
        "milvus_db_name": "lightrag",
        "cosine_better_than_threshold": 0.2,
    },
)
```

Milvus 支持多种索引类型（HNSW、IVF、DISKANN 等），详见 `docs/MilvusConfigurationGuide.md`。

### MongoDB 存储

MongoDB 提供 KV + Vector + Graph 的一体化存储方案：

```python
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=llm_model_func,
    embedding_func=embedding_func,
    kv_storage="MongoKVStorage",
    vector_storage="MongoVectorDBStorage",
    graph_storage="MongoGraphStorage",
)
```

> 注意：`MongoVectorDBStorage` 需要 MongoDB Atlas（带 Vector Search 插件），本地 Docker MongoDB 不支持此功能。

### Redis 存储

```python
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=llm_model_func,
    embedding_func=embedding_func,
    kv_storage="RedisKVStorage",
)
```

### OpenSearch 统一存储

OpenSearch 可以同时承担 KV + Vector + Graph + DocStatus 四种存储角色：

```bash
# 启动 OpenSearch（含 k-NN 插件）
docker run -d -p 9200:9200 -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=StrongPassword" \
  opensearchproject/opensearch:latest
```

```python
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=llm_model_func,
    embedding_func=embedding_func,
    kv_storage="OpenSearchKVStorage",
    doc_status_storage="OpenSearchDocStatusStorage",
    graph_storage="OpenSearchGraphStorage",
    vector_storage="OpenSearchVectorDBStorage",
)
```

### 数据隔离（多租户）

通过 `workspace` 参数实现不同实例间的数据隔离：

```python
rag_instance_a = LightRAG(working_dir="./storage_a", workspace="tenant_a")
rag_instance_b = LightRAG(working_dir="./storage_b", workspace="tenant_b")
```

---

## 查询模式详解

LightRAG 提供四种查询模式，通过 `QueryParam(mode="...")` 指定：

### 1. naive（基础模式）

```
查询向量 → 向量数据库检索 → 返回最相似的文本块
```

等价于传统向量 RAG，不利用知识图谱结构。适合作为对比基准。

### 2. local（局部模式）

```
查询向量 → 识别实体 → 找到实体的邻居节点 → 聚合邻居文本块 → LLM 生成
```

适合问及**特定实体**的问题，如"《双城记》中卡顿先生的人物关系"。

### 3. global（全局模式）

```
查询 → 识别核心实体 → 在图谱中广度优先遍历 → 收集所有相关子图 → 聚合 → LLM 生成
```

适合需要**综合大量关联信息**的问题，如"比较《双城记》和《傲慢与偏见》中的社会阶层描写"。

### 4. mix（混合模式，推荐默认）

```
局部检索结果 + 全局检索结果 → 合并去重 → LLM 生成
```

综合了局部精确性和全局完整性，是大多数场景下的最佳选择。

---

## 高级功能

### Token 用量追踪

```python
from lightrag import LightRAG
from lightrag.utils import TokenTracker

with TokenTracker() as tracker:
    await rag.ainsert(document)
    result = await rag.aquery("your question")

print("Token usage:", tracker.get_usage())
```

### 知识图谱数据导出

```python
# 导出为 CSV（包含实体和关系）
rag.export_data("knowledge_graph.csv")
```

### LLM 缓存管理

LightRAG 内置 LLM 响应缓存，相同 chunk 的重复查询可直接命中缓存，提升速度并降低成本。

### RAGAS 评估

支持使用 RAGAS 框架评估 RAG 系统性能：

```python
# 详见 docs/AdvancedFeatures.md
```

### 多模态文档处理（RAG-Anything 集成）

支持 PDF、Office 文档、图片、表格、数学公式等多种格式：

```bash
pip install raganything
```

```python
import asyncio
from raganything import RAGAnything
from lightrag import LightRAG

rag_anything = RAGAnything(lightrag_instance=rag)

await rag_anything.process_document_complete(
    file_path="path/to/document.pdf",
    output_dir="./output"
)

result = await rag.query_with_multimodal(
    "What data has been processed?",
    mode="hybrid"
)
```

### Langfuse 可观测性集成

支持对接 Langfuse 进行 RAG 系统的链路追踪和监控。

---

## LLM 配置要求

> LightRAG 对 LLM 的能力要求比传统 RAG 系统更高，因为它需要 LLM 执行实体-关系抽取任务。

### 模型选择建议

| 阶段 | 建议 |
|------|------|
| **文档索引阶段** | 至少 32B 参数，上下文窗口 ≥ 32KB（推荐 64KB），不建议使用推理模型（Reasoning Model） |
| **查询阶段** | 建议使用比索引阶段更强的模型，以获得更好的查询效果 |

### Embedding 模型推荐

- `BAAI/bge-m3`（开源推荐）
- `text-embedding-3-large`（OpenAI）

### Reranker 模型推荐

- `BAAI/bge-reranker-v2-m3`

配置适当的 Embedding 和 Reranker 模型对提升查询性能至关重要。

---

## 参考链接

- GitHub: https://github.com/HKUDS/LightRAG
- 论文: LightRAG: Simple and Fast Retrieval-Augmented Generation (EMNLP 2025)
- RAG-Anything 多模态扩展: https://github.com/RAG-Anything/RAG-Anything
- 官方文档: `docs/ProgramingWithCore.md`、`docs/AdvancedFeatures.md`

---

*最后更新: 2026-04-13*
