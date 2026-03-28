Skip to content
Navigation Menu
Platform
Solutions
Resources
Open Source
Enterprise
Pricing
Sign in
Sign up
HKUDS
/
LightRAG
Public
Notifications
Fork 4.4k
 Star 30.9k
Code
Issues
179
Pull requests
17
Discussions
Actions
Projects
Security
Insights
HKUDS/LightRAG
 main
2 Branches
81 Tags
Code
Folders and files
Name	Last commit message	Last commit date

Latest commit
danielaskdd
Merge branch 'fix/cwe89-memgraph-impl-cypher-58d4'
16a2d74
 · 
History
6,782 Commits


.clinerules
	
Add testing workflow guidelines to basic development rules
	


.github
	
Refac: Centralizes version management in dedicated module
	


README.assets
	
Add chinese version of README
	


assets
	
Add litewrite link
	


docs
	
docs: rewrite InteractiveSetup.md for clarity and usability
	


examples
	
Merge branch 'main' into fix/cypher-injection-workspace-label
	


k8s-deploy
	
Refactor Helm template to handle optional envFrom values safely
	


lightrag
	
fix: sanitize entity_type in Memgraph upsert_node to prevent Cypher i…
	


lightrag_webui
	
Merge pull request #2842 from HKUDS/dependabot/bun/lightrag_webui/con…
	


reproduce
	
Remove manual initialize_pipeline_status() calls across codebase
	


scripts
	
Prefer single quotes in env files for Docker Compose compatibility
	


tests
	
💄 style(utils): update prompt text casing for consistency
	


.dockerignore
	
Add offline Docker build support with embedded models and cache
	


.gitattributes
	
Update .gitattributes for webui files
	


.gitignore
	
🐛 fix(utils): restore C1 control char preservation and fix replacemen…
	


.pre-commit-config.yaml
	
Exclude lightrag/api/webui from pre-commit hooks.
	


AGENTS.md
	
📝 docs(AGENTS): add upstream PR target guidance
	


CLAUDE.md
	
Add comprehensive CLAUDE.md developer guide for team sharing
	


Dockerfile
	
📦 build(docker): use native build platform for frontend stage
	


Dockerfile.lite
	
📦 build(docker): use native build platform for frontend stage
	


LICENSE
	
Update LICENSE
	


MANIFEST.in
	
Include static files in package distribution
	


Makefile
	
📝 docs(makefile): update make env references to make base
	


README-zh.md
	
docs(contributing): add CONTRIBUTING.md and improve linting CI feedback
	


README.md
	
docs(contributing): add CONTRIBUTING.md and improve linting CI feedback
	


SECURITY.md
	
Fix linting
	


config.ini.example
	
Fix pre-commit ruff-format CI failures in Milvus test file (#11)
	


docker-build-push.sh
	
Improve Docker build workflow with automated multi-arch script and docs
	


docker-compose-full.yml
	
📝 docs(makefile): update make env references to make base
	


docker-compose.yml
	
refactor: improve Docker restart policy and compose healthcheck config
	


env.example
	
Prefer single quotes in env files for Docker Compose compatibility
	


lightrag.service.example
	
Refactor systemd service config to use environment variables
	


pyproject.toml
	
Refac: Centralizes version management in dedicated module
	


requirements-offline-llm.txt
	
Bump llama-index to 0.14.0 for OpenAI 2.x compatibility
	


requirements-offline-storage.txt
	
Fix linting
	


requirements-offline.txt
	
🛡️ Sentinel: Fix linting and formatting in password hashing implement…
	


setup.py
	
Refactor setup.py to utilize pyproject.toml for project installat…
	


uv.lock
	
refactor(opensearch): replace get() with mget() for not-found handling
	
Repository files navigation
README
Contributing
MIT license
Security
🚀 LightRAG: Simple and Fast Retrieval-Augmented Generation

  

 

 

 

	
🎉 News
[2026.03]🎯[New Feature]: Integrated OpenSearch as a unified storage backend, providing comprehensive support for all four LightRAG storage.
[2026.03]🎯[New Feature]: Introduced a setup wizard. Support for local deployment of embedding, reranking, and storage backends via Docker.
[2025.11]🎯[New Feature]: Integrated RAGAS for Evaluation and Langfuse for Tracing. Updated the API to return retrieved contexts alongside query results to support context precision metrics.
[2025.10]🎯[Scalability Enhancement]: Eliminated processing bottlenecks to support Large-Scale Datasets Efficiently.
[2025.09]🎯[New Feature] Enhances knowledge graph extraction accuracy for Open-Sourced LLMs such as Qwen3-30B-A3B.
[2025.08]🎯[New Feature] Reranker is now supported, significantly boosting performance for mixed queries (set as default query mode).
[2025.08]🎯[New Feature] Added Document Deletion with automatic KG regeneration to ensure optimal query performance.
[2025.06]🎯[New Release] Our team has released RAG-Anything — an All-in-One Multimodal RAG system for seamless processing of text, images, tables, and equations.
[2025.06]🎯[New Feature] LightRAG now supports comprehensive multimodal data handling through RAG-Anything integration, enabling seamless document parsing and RAG capabilities across diverse formats including PDFs, images, Office documents, tables, and formulas. Please refer to the new multimodal section for details.
[2025.03]🎯[New Feature] LightRAG now supports citation functionality, enabling proper source attribution and enhanced document traceability.
[2025.02]🎯[New Feature] You can now use MongoDB as an all-in-one storage solution for unified data management.
[2025.02]🎯[New Release] Our team has released VideoRAG-a RAG system for understanding extremely long-context videos
[2025.01]🎯[New Release] Our team has released MiniRAG making RAG simpler with small models.
[2025.01]🎯You can now use PostgreSQL as an all-in-one storage solution for data management.
[2024.11]🎯[New Resource] A comprehensive guide to LightRAG is now available on LearnOpenCV. — explore in-depth tutorials and best practices. Many thanks to the blog author for this excellent contribution!
[2024.11]🎯[New Feature] Introducing the LightRAG WebUI — an interface that allows you to insert, query, and visualize LightRAG knowledge through an intuitive web-based dashboard.
[2024.11]🎯[New Feature] You can now use Neo4J for Storage-enabling graph database support.
[2024.10]🎯[New Feature] We've added a link to a LightRAG Introduction Video. — a walkthrough of LightRAG's capabilities. Thanks to the author for this excellent contribution!
[2024.10]🎯[New Channel] We have created a Discord channel!💬 Welcome to join our community for sharing, discussions, and collaboration! 🎉🎉
Algorithm Flowchart
Installation

💡 Using uv for Package Management: This project uses uv for fast and reliable Python package management. Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh (Unix/macOS) or powershell -c "irm https://astral.sh/uv/install.ps1 | iex" (Windows)

Note: You can also use pip if you prefer, but uv is recommended for better performance and more reliable dependency management.

📦 Offline Deployment: For offline or air-gapped environments, see the Offline Deployment Guide for instructions on pre-installing all dependencies and cache files.

Install LightRAG Server

The LightRAG Server is designed to provide Web UI and API support. The Web UI facilitates document indexing, knowledge graph exploration, and a simple RAG query interface. LightRAG Server also provide an Ollama compatible interfaces, aiming to emulate LightRAG as an Ollama chat model. This allows AI chat bot, such as Open WebUI, to access LightRAG easily.

Install from PyPI
### Install LightRAG Server as tool using uv (recommended)
uv tool install "lightrag-hku[api]"

### Or using pip
# python -m venv .venv
# source .venv/bin/activate  # Windows: .venv\Scripts\activate
# pip install "lightrag-hku[api]"

### Build front-end artifacts
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..

# Setup env file
# Obtain the env.example file by downloading it from the GitHub repository root
# or by copying it from a local source checkout.
cp env.example .env  # Update the .env with your LLM and embedding configurations
# Launch the server
lightrag-server
Installation from Source
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG

# Using uv (recommended)
# Note: uv sync automatically creates a virtual environment in .venv/
uv sync --extra api
source .venv/bin/activate  # Activate the virtual environment (Linux/macOS)
# Or on Windows: .venv\Scripts\activate

### Or using pip with virtual environment
# python -m venv .venv
# source .venv/bin/activate  # Windows: .venv\Scripts\activate
# pip install -e ".[api]"

# Build front-end artifacts
cd lightrag_webui
bun install --frozen-lockfile
bun run build
cd ..

# setup env file
cp env.example .env  # Update the .env with your LLM and embedding configurations
# Launch API-WebUI server
lightrag-server
Launching the LightRAG Server with Docker Compose
git clone https://github.com/HKUDS/LightRAG.git
cd LightRAG
cp env.example .env  # Update the .env with your LLM and embedding configurations
# modify LLM and Embedding settings in .env
docker compose up

Historical versions of LightRAG docker images can be found here: LightRAG Docker Images

Create .env File With Setup Tool

Instead of editing env.example by hand, use the interactive setup wizard to generate a configured .env and, when needed, docker-compose.final.yml:

make env-base           # Required first step: LLM, embedding, reranker
make env-storage        # Optional: storage backends and database services
make env-server         # Optional: server port, auth, and SSL
make env-base-rewrite   # Optional: force-regenerate wizard-managed compose services
make env-storage-rewrite # Optional: force-regenerate wizard-managed compose services
make env-security-check # Optional: audit the current .env for security risks

For full description of every target see docs/InteractiveSetup.md. The setup wizards update configuration only; run make env-security-check separately to audit the current .env for security risks before deployment. By default, rerunning the setup preserves unchanged wizard-managed compose service blocks; use a *-rewrite target only when you need to rebuild those managed blocks from the bundled templates.

Install LightRAG Core
Install from source (Recommended)
cd LightRAG
# Note: uv sync automatically creates a virtual environment in .venv/
uv sync
source .venv/bin/activate  # Activate the virtual environment (Linux/macOS)
# Or on Windows: .venv\Scripts\activate

# Or: pip install -e .
Install from PyPI
uv pip install lightrag-hku
# Or: pip install lightrag-hku
Quick Start
LLM and Technology Stack Requirements for LightRAG

LightRAG's demands on the capabilities of Large Language Models (LLMs) are significantly higher than those of traditional RAG, as it requires the LLM to perform entity-relationship extraction tasks from documents. Configuring appropriate Embedding and Reranker models is also crucial for improving query performance.

LLM Selection:
It is recommended to use an LLM with at least 32 billion parameters.
The context length should be at least 32KB, with 64KB being recommended.
It is not recommended to choose reasoning models during the document indexing stage.
During the query stage, it is recommended to choose models with stronger capabilities than those used in the indexing stage to achieve better query results.
Embedding Model:
A high-performance Embedding model is essential for RAG.
We recommend using mainstream multilingual Embedding models, such as: BAAI/bge-m3 and text-embedding-3-large.
Important Note: The Embedding model must be determined before document indexing, and the same model must be used during the document query phase. For certain storage solutions (e.g., PostgreSQL), the vector dimension must be defined upon initial table creation. Therefore, when changing embedding models, it is necessary to delete the existing vector-related tables and allow LightRAG to recreate them with the new dimensions.
Reranker Model Configuration:
Configuring a Reranker model can significantly enhance LightRAG's retrieval performance.
When a Reranker model is enabled, it is recommended to set the "mix mode" as the default query mode.
We recommend using mainstream Reranker models, such as: BAAI/bge-reranker-v2-m3 or models provided by services like Jina.
Quick Start for LightRAG Server
For more information about LightRAG Server, please refer to LightRAG Server.
Quick Start for LightRAG core

To get started with LightRAG core, refer to the sample codes available in the examples folder. Additionally, a video demo demonstration is provided to guide you through the local setup process. If you already possess an OpenAI API key, you can run the demo right away:

### you should run the demo code with project folder
cd LightRAG
### provide your API-KEY for OpenAI
export OPENAI_API_KEY="sk-...your_opeai_key..."
### download the demo document of "A Christmas Carol" by Charles Dickens
curl https://raw.githubusercontent.com/gusye1234/nano-graphrag/main/tests/mock_data.txt > ./book.txt
### run the demo code
python examples/lightrag_openai_demo.py

For a streaming response implementation example, please see examples/lightrag_openai_compatible_demo.py. Prior to execution, ensure you modify the sample code's LLM and embedding configurations accordingly.

Note 1: When running the demo program, please be aware that different test scripts may use different embedding models. If you switch to a different embedding model, you must clear the data directory (./dickens); otherwise, the program may encounter errors. If you wish to retain the LLM cache, you can preserve the kv_store_llm_response_cache.json file while clearing the data directory.

Note 2: Only lightrag_openai_demo.py and lightrag_openai_compatible_demo.py are officially supported sample codes. Other sample files are community contributions that haven't undergone full testing and optimization.

Programming with LightRAG Core

⚠️ If you would like to integrate LightRAG into your project, we recommend utilizing the REST API provided by the LightRAG Server. LightRAG Core is typically intended for embedded applications or for researchers who wish to conduct studies and evaluations.

⚠️ Important: Initialization Requirements

LightRAG requires explicit initialization before use. You must call await rag.initialize_storages() after creating a LightRAG instance, otherwise you will encounter errors.

A Simple Program

Use the below Python snippet to initialize LightRAG, insert text to it, and perform queries:

import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed
from lightrag.utils import setup_logger

setup_logger("lightrag", level="INFO")

WORKING_DIR = "./rag_storage"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    # IMPORTANT: Both initialization calls are required!
    await rag.initialize_storages()  # Initialize storage backends
    return rag

async def main():
    try:
        # Initialize RAG instance
        rag = await initialize_rag()
        await rag.ainsert("Your text")

        # Perform hybrid search
        mode = "hybrid"
        print(
          await rag.aquery(
              "What are the top themes in this story?",
              param=QueryParam(mode=mode)
          )
        )

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if rag:
            await rag.finalize_storages()

if __name__ == "__main__":
    asyncio.run(main())

Important notes for the above snippet:

Export your OPENAI_API_KEY environment variable before running the script.
This program uses the default storage settings for LightRAG, so all data will be persisted to WORKING_DIR/rag_storage.
This program demonstrates only the simplest way to initialize a LightRAG object: Injecting the embedding and LLM functions, and initializing storage and pipeline status after creating the LightRAG object.
LightRAG init parameters

A full list of LightRAG init parameters:

Parameters
Query Param

Use QueryParam to control the behavior your query:

class QueryParam:
    """Configuration parameters for query execution in LightRAG."""

    mode: Literal["local", "global", "hybrid", "naive", "mix", "bypass"] = "global"
    """Specifies the retrieval mode:
    - "local": Focuses on context-dependent information.
    - "global": Utilizes global knowledge.
    - "hybrid": Combines local and global retrieval methods.
    - "naive": Performs a basic search without advanced techniques.
    - "mix": Integrates knowledge graph and vector retrieval.
    """

    only_need_context: bool = False
    """If True, only returns the retrieved context without generating a response."""

    only_need_prompt: bool = False
    """If True, only returns the generated prompt without producing a response."""

    response_type: str = "Multiple Paragraphs"
    """Defines the response format. Examples: 'Multiple Paragraphs', 'Single Paragraph', 'Bullet Points'."""

    stream: bool = False
    """If True, enables streaming output for real-time responses."""

    top_k: int = int(os.getenv("TOP_K", "60"))
    """Number of top items to retrieve. Represents entities in 'local' mode and relationships in 'global' mode."""

    chunk_top_k: int = int(os.getenv("CHUNK_TOP_K", "20"))
    """Number of text chunks to retrieve initially from vector search and keep after reranking.
    If None, defaults to top_k value.
    """

    max_entity_tokens: int = int(os.getenv("MAX_ENTITY_TOKENS", "6000"))
    """Maximum number of tokens allocated for entity context in unified token control system."""

    max_relation_tokens: int = int(os.getenv("MAX_RELATION_TOKENS", "8000"))
    """Maximum number of tokens allocated for relationship context in unified token control system."""

    max_total_tokens: int = int(os.getenv("MAX_TOTAL_TOKENS", "30000"))
    """Maximum total tokens budget for the entire query context (entities + relations + chunks + system prompt)."""

    # History messages are only sent to LLM for context, not used for retrieval
    conversation_history: list[dict[str, str]] = field(default_factory=list)
    """Stores past conversation history to maintain context.
    Format: [{"role": "user/assistant", "content": "message"}].
    """

    # Deprecated (ids filter lead to potential hallucination effects)
    ids: list[str] | None = None
    """List of ids to filter the results."""

    model_func: Callable[..., object] | None = None
    """Optional override for the LLM model function to use for this specific query.
    If provided, this will be used instead of the global model function.
    This allows using different models for different query modes.
    """

    user_prompt: str | None = None
    """User-provided prompt for the query.
    Addition instructions for LLM. If provided, this will be inject into the prompt template.
    It's purpose is the let user customize the way LLM generate the response.
    """

    enable_rerank: bool = True
    """Enable reranking for retrieved text chunks. If True but no rerank model is configured, a warning will be issued.
    Default is True to enable reranking when rerank model is available.
    """

default value of Top_k can be change by environment variables TOP_K.

LLM and Embedding Injection

LightRAG requires the utilization of LLM and Embedding models to accomplish document indexing and querying tasks. During the initialization phase, it is necessary to inject the invocation methods of the relevant models into LightRAG：

Using Open AI-like APIs
Using Hugging Face Models
Using Ollama Models
LlamaIndex
Using Azure OpenAI Models
Using Google Gemini Models
Rerank Function Injection

To enhance retrieval quality, documents can be re-ranked based on a more effective relevance scoring model. The rerank.py file provides three Reranker provider driver functions:

Cohere / vLLM: cohere_rerank
Jina AI: jina_rerank
Aliyun: ali_rerank

You can inject one of these functions into the rerank_model_func attribute of the LightRAG object. This will enable LightRAG's query function to re-order retrieved text blocks using the injected function. For detailed usage, please refer to the examples/rerank_example.py file.

User Prompt vs. Query

When using LightRAG for content queries, avoid combining the search process with unrelated output processing, as this significantly impacts query effectiveness. The user_prompt parameter in Query Param is specifically designed to address this issue — it does not participate in the RAG retrieval phase, but rather guides the LLM on how to process the retrieved results after the query is completed. Here's how to use it:

# Create query parameters
query_param = QueryParam(
    mode = "hybrid",  # Other modes：local, global, hybrid, mix, naive
    user_prompt = "For diagrams, use mermaid format with English/Pinyin node names and Chinese display labels",
)

# Query and process
response_default = rag.query(
    "Please draw a character relationship diagram for Scrooge",
    param=query_param
)
print(response_default)
Insert
Basic Insert
Batch Insert
Insert with ID
Insert using Pipeline
Insert Multi-file Type Support
Citation Functionality
Storage

LightRAG uses 4 types of storage for different purposes:

KV_STORAGE: llm response cache, text chunks, document information
VECTOR_STORAGE: entities vectors, relation vectors, chunks vectors
GRAPH_STORAGE: entity relation graph
DOC_STATUS_STORAGE: document indexing status

Each storage type has several implementations:

KV_STORAGE supported implementations:
JsonKVStorage        JsonFile (default)
PGKVStorage          Postgres
RedisKVStorage       Redis
MongoKVStorage       MongoDB
OpenSearchKVStorage  OpenSearch

GRAPH_STORAGE supported implementations:
NetworkXStorage          NetworkX (default)
Neo4JStorage             Neo4J
PGGraphStorage           PostgreSQL with AGE plugin
MemgraphStorage          Memgraph
OpenSearchGraphStorage   OpenSearch


Testing has shown that Neo4J delivers superior performance in production environments compared to PostgreSQL with AGE plugin.

VECTOR_STORAGE supported implementations:
NanoVectorDBStorage         NanoVector (default)
PGVectorStorage             Postgres
MilvusVectorDBStorage       Milvus
FaissVectorDBStorage        Faiss
QdrantVectorDBStorage       Qdrant
MongoVectorDBStorage        MongoDB
OpenSearchVectorDBStorage   OpenSearch

DOC_STATUS_STORAGE: supported implementations:
JsonDocStatusStorage        JsonFile (default)
PGDocStatusStorage          Postgres
MongoDocStatusStorage       MongoDB
OpenSearchDocStatusStorage  OpenSearch


Example connection configurations for each storage type can be found in the repository's env.example file. The database instance in the connection string needs to be created by you on the database server beforehand. LightRAG is only responsible for creating tables within the database instance, not for creating the database instance itself. If using Redis as storage, remember to configure automatic data persistence rules for Redis, otherwise data will be lost after the Redis service restarts. If using PostgreSQL, it is recommended to use version 16.6 or above.

Using Neo4J Storage
Using PostgreSQL Storage
Using Faiss Storage
Using Memgraph for Storage
Using Milvus for Vector Storage
Using MongoDB Storage
Using Redis Storage
Using OpenSearch Storage
Data Isolation Between LightRAG Instances

The workspace parameter ensures data isolation between different LightRAG instances. Once initialized, the workspace is immutable and cannot be changed. Here is how workspaces are implemented for different types of storage:

For local file-based databases, data isolation is achieved through workspace subdirectories: JsonKVStorage, JsonDocStatusStorage, NetworkXStorage, NanoVectorDBStorage, FaissVectorDBStorage.
For databases that store data in collections, it's done by adding a workspace prefix to the collection name: RedisKVStorage, RedisDocStatusStorage, MilvusVectorDBStorage, MongoKVStorage, MongoDocStatusStorage, MongoVectorDBStorage, MongoGraphStorage, PGGraphStorage.
For Qdrant vector database, data isolation is achieved through payload-based partitioning (Qdrant's recommended multitenancy approach): QdrantVectorDBStorage uses shared collections with payload filtering for unlimited workspace scalability.
For relational databases, data isolation is achieved by adding a workspace field to the tables for logical data separation: PGKVStorage, PGVectorStorage, PGDocStatusStorage.
For the Neo4j graph database, logical data isolation is achieved through labels: Neo4JStorage
For OpenSearch, data isolation is achieved through index name prefixes: OpenSearchKVStorage, OpenSearchDocStatusStorage, OpenSearchGraphStorage, OpenSearchVectorDBStorage

To maintain compatibility with legacy data, the default workspace for PostgreSQL non-graph storage is default and, for PostgreSQL AGE graph storage is null, for Neo4j graph storage is base when no workspace is configured. For all external storages, the system provides dedicated workspace environment variables to override the common WORKSPACE environment variable configuration. These storage-specific workspace environment variables are: REDIS_WORKSPACE, MILVUS_WORKSPACE, QDRANT_WORKSPACE, MONGODB_WORKSPACE, POSTGRES_WORKSPACE, NEO4J_WORKSPACE, OPENSEARCH_WORKSPACE.

Usage Example: For a practical demonstration of managing multiple isolated knowledge bases (e.g., separating "Book" content from "HR Policies") within a single application, refer to the Workspace Demo.

AGENTS.md -- Guiding Coding Agents

AGENTS.md is a simple, open format for guiding coding agents (https://agents.md/). It is a dedicated, predictable place to provide the context and instructions to help AI coding agents work on LightRAG project. Different AI coders should not maintain separate guidance files individually. If any AI coder cannot automatically recognize AGENTS.md, symbolic links can be used as a solution. After establishing symbolic links, you can prevent them from being committed to the Git repository by configuring your local .gitignore_global.

Edit Entities and Relations

LightRAG now supports comprehensive knowledge graph management capabilities, allowing you to create, edit, and delete entities and relationships within your knowledge graph.

Create Entities and Relations
Edit Entities and Relations
Insert Custom KG
Other Entity and Relation Operations
Delete Functions

LightRAG provides comprehensive deletion capabilities, allowing you to delete documents, entities, and relationships.

Delete Entities
Delete Relations
Delete by Document ID

Important Reminders:

Irreversible Operations: All deletion operations are irreversible, please use with caution
Performance Considerations: Deleting large amounts of data may take some time, especially deletion by document ID
Data Consistency: Deletion operations automatically maintain consistency between the knowledge graph and vector database
Backup Recommendations: Consider backing up data before performing important deletion operations

Batch Deletion Recommendations:

For batch deletion operations, consider using asynchronous methods for better performance
For large-scale deletions, consider processing in batches to avoid excessive system load
Entity Merging
Merge Entities and Their Relationships
Multimodal Document Processing (RAG-Anything Integration)

LightRAG now seamlessly integrates with RAG-Anything, a comprehensive All-in-One Multimodal Document Processing RAG system built specifically for LightRAG. RAG-Anything enables advanced parsing and retrieval-augmented generation (RAG) capabilities, allowing you to handle multimodal documents seamlessly and extract structured content—including text, images, tables, and formulas—from various document formats for integration into your RAG pipeline.

Key Features:

End-to-End Multimodal Pipeline: Complete workflow from document ingestion and parsing to intelligent multimodal query answering
Universal Document Support: Seamless processing of PDFs, Office documents (DOC/DOCX/PPT/PPTX/XLS/XLSX), images, and diverse file formats
Specialized Content Analysis: Dedicated processors for images, tables, mathematical equations, and heterogeneous content types
Multimodal Knowledge Graph: Automatic entity extraction and cross-modal relationship discovery for enhanced understanding
Hybrid Intelligent Retrieval: Advanced search capabilities spanning textual and multimodal content with contextual understanding

Quick Start:

Install RAG-Anything:

pip install raganything

Process multimodal documents:

RAGAnything Usage Example

For detailed documentation and advanced usage, please refer to the RAG-Anything repository.

Token Usage Tracking
Overview and Usage
Data Export Functions
Overview

LightRAG allows you to export your knowledge graph data in various formats for analysis, sharing, and backup purposes. The system supports exporting entities, relations, and relationship data.

Export Functions
Basic Usage
Different File Formats supported
Additional Options
Data Included in Export

All exports include:

Entity information (names, IDs, metadata)
Relation data (connections between entities)
Relationship information from vector database
Cache
Clear Cache
Troubleshooting
Common Initialization Errors

If you encounter these errors when using LightRAG:

AttributeError: __aenter__

Cause: Storage backends not initialized
Solution: Call await rag.initialize_storages() after creating the LightRAG instance

KeyError: 'history_messages'

Cause: Pipeline status not initialized
Solution: Call await rag.initialize_storages() after creating the LightRAG instance

Both errors in sequence

Cause: Neither initialization method was called
Solution: Always follow this pattern:
rag = LightRAG(...)
await rag.initialize_storages()
Model Switching Issues

When switching between different embedding models, you must clear the data directory to avoid errors. The only file you may want to preserve is kv_store_llm_response_cache.json if you wish to retain the LLM cache.

LightRAG API

The LightRAG Server is designed to provide Web UI and API support. For more information about LightRAG Server, please refer to LightRAG Server.

Graph Visualization

The LightRAG Server offers a comprehensive knowledge graph visualization feature. It supports various gravity layouts, node queries, subgraph filtering, and more. For more information about LightRAG Server, please refer to LightRAG Server.

Langfuse observability integration

Langfuse provides a drop-in replacement for the OpenAI client that automatically tracks all LLM interactions, enabling developers to monitor, debug, and optimize their RAG systems without code changes.

Installation with Langfuse option
pip install lightrag-hku
pip install lightrag-hku[observability]

# Or install from source code with debug mode enabled
pip install -e .
pip install -e ".[observability]"

Config Langfuse env vars

modify .env file:

## Langfuse Observability (Optional)
# LLM observability and tracing platform
# Install with: pip install lightrag-hku[observability]
# Sign up at: https://cloud.langfuse.com or self-host
LANGFUSE_SECRET_KEY=""
LANGFUSE_PUBLIC_KEY=""
LANGFUSE_HOST="https://cloud.langfuse.com"  # or your self-hosted instance
LANGFUSE_ENABLE_TRACE=true

Langfuse Usage

Once installed and configured, Langfuse automatically traces all OpenAI LLM calls. Langfuse dashboard features include:

Tracing: View complete LLM call chains
Analytics: Token usage, latency, cost metrics
Debugging: Inspect prompts and responses
Evaluation: Compare model outputs
Monitoring: Real-time alerting
Important Notice

Note: LightRAG currently only integrates OpenAI-compatible API calls with Langfuse. APIs such as Ollama, Azure, and AWS Bedrock are not yet supported for Langfuse observability.

RAGAS-based Evaluation

RAGAS (Retrieval Augmented Generation Assessment) is a framework for reference-free evaluation of RAG systems using LLMs. There is an evaluation script based on RAGAS. For detailed information, please refer to RAGAS-based Evaluation Framework.

Evaluation
Dataset

The dataset used in LightRAG can be downloaded from TommyChien/UltraDomain.

Generate Query

LightRAG uses the following prompt to generate high-level queries, with the corresponding code in examples/generate_query.py.

Prompt
Batch Eval

To evaluate the performance of two RAG systems on high-level queries, LightRAG uses the following prompt, with the specific code available in reproduce/batch_eval.py.

Prompt
Overall Performance Table
	Agriculture		CS		Legal		Mix	
	NaiveRAG	LightRAG	NaiveRAG	LightRAG	NaiveRAG	LightRAG	NaiveRAG	LightRAG
Comprehensiveness	32.4%	67.6%	38.4%	61.6%	16.4%	83.6%	38.8%	61.2%
Diversity	23.6%	76.4%	38.0%	62.0%	13.6%	86.4%	32.4%	67.6%
Empowerment	32.4%	67.6%	38.8%	61.2%	16.4%	83.6%	42.8%	57.2%
Overall	32.4%	67.6%	38.8%	61.2%	15.2%	84.8%	40.0%	60.0%
	RQ-RAG	LightRAG	RQ-RAG	LightRAG	RQ-RAG	LightRAG	RQ-RAG	LightRAG
Comprehensiveness	31.6%	68.4%	38.8%	61.2%	15.2%	84.8%	39.2%	60.8%
Diversity	29.2%	70.8%	39.2%	60.8%	11.6%	88.4%	30.8%	69.2%
Empowerment	31.6%	68.4%	36.4%	63.6%	15.2%	84.8%	42.4%	57.6%
Overall	32.4%	67.6%	38.0%	62.0%	14.4%	85.6%	40.0%	60.0%
	HyDE	LightRAG	HyDE	LightRAG	HyDE	LightRAG	HyDE	LightRAG
Comprehensiveness	26.0%	74.0%	41.6%	58.4%	26.8%	73.2%	40.4%	59.6%
Diversity	24.0%	76.0%	38.8%	61.2%	20.0%	80.0%	32.4%	67.6%
Empowerment	25.2%	74.8%	40.8%	59.2%	26.0%	74.0%	46.0%	54.0%
Overall	24.8%	75.2%	41.6%	58.4%	26.4%	73.6%	42.4%	57.6%
	GraphRAG	LightRAG	GraphRAG	LightRAG	GraphRAG	LightRAG	GraphRAG	LightRAG
Comprehensiveness	45.6%	54.4%	48.4%	51.6%	48.4%	51.6%	50.4%	49.6%
Diversity	22.8%	77.2%	40.8%	59.2%	26.4%	73.6%	36.0%	64.0%
Empowerment	41.2%	58.8%	45.2%	54.8%	43.6%	56.4%	50.8%	49.2%
Overall	45.2%	54.8%	48.0%	52.0%	47.2%	52.8%	50.4%	49.6%
Reproduce

All the code can be found in the ./reproduce directory.

Step-0 Extract Unique Contexts

First, we need to extract unique contexts in the datasets.

Code
Step-1 Insert Contexts

For the extracted contexts, we insert them into the LightRAG system.

Code
Step-2 Generate Queries

We extract tokens from the first and the second half of each context in the dataset, then combine them as dataset descriptions to generate queries.

Code
Step-3 Query

For the queries generated in Step-2, we will extract them and query LightRAG.

Code
🔗 Related Projects

Ecosystem & Extensions

📸
RAG-Anything
Multimodal RAG
	
🎥
VideoRAG
Extreme Long-Context Video RAG
	
✨
MiniRAG
Extremely Simple RAG
⭐ Star History

🤝 Contribution
We welcome contributions of all kinds — bug fixes, new features, documentation improvements, and more.
Please read our Contributing Guide before submitting a pull request.


We thank all our contributors for their valuable contributions.
📖 Citation
@article{guo2024lightrag,
title={LightRAG: Simple and Fast Retrieval-Augmented Generation},
author={Zirui Guo and Lianghao Xia and Yanhua Yu and Tu Ao and Chao Huang},
year={2024},
eprint={2410.05779},
archivePrefix={arXiv},
primaryClass={cs.IR}
}
  
⭐ Thank you for visiting LightRAG! ⭐
About

[EMNLP2025] "LightRAG: Simple and Fast Retrieval-Augmented Generation"

arxiv.org/abs/2410.05779
Topics
knowledge-graph gpt rag gpt-4 large-language-models llm genai retrieval-augmented-generation graphrag
Resources
 Readme
License
 MIT license
Contributing
 Contributing
Security policy
 Security policy
 Activity
 Custom properties
Stars
 30.9k stars
Watchers
 188 watching
Forks
 4.4k forks
Report repository


Releases 67
v1.4.12
Latest
+ 66 releases


Packages
1
lightrag


Contributors
236
+ 222 contributors


Languages
Python
80.7%
 
TypeScript
13.4%
 
Shell
5.4%
 
JavaScript
0.2%
 
CSS
0.1%
 
Dockerfile
0.1%
 
Other
0.1%
Footer
© 2026 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Community
Docs
Contact
Manage cookies
Do not share my personal information
