# Graph Report - .  (2026-04-11)

## Corpus Check
- Corpus is ~46,316 words - fits in a single context window. You may not need a graph.

## Summary
- 216 nodes · 189 edges · 50 communities detected
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.72)
- Token cost: 25,228 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `AntAgent` - 8 edges
2. `Full Marketing Automation System` - 8 edges
3. `运营产品` - 7 edges
4. `anteam Slack Chat System` - 7 edges
5. `React` - 6 edges
6. `LLM架构层` - 6 edges
7. `Neovim` - 6 edges
8. `OmniWM` - 6 edges
9. `CMS Garbage Collector` - 6 edges
10. `Service Avalanche (服务雪崩)` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Obsidian知识库` --semantically_similar_to--> `运营产品`  [INFERRED] [semantically similar]
  CLAUDE.md → 曾用过的提示词/运营产品提示词.md
- `Memory Semantic Search` --semantically_similar_to--> `LangChain Embedding Model`  [INFERRED] [semantically similar]
  我的项目/memory/Memory 个人知识库系统.md → 学习笔记和教程/lang-chain-graph/LangChain学习笔记.md
- `AntAgent` --semantically_similar_to--> `Aurasell AI CRM`  [INFERRED] [semantically similar]
  我的项目/antagent/方案.md → 我的项目/全自动营销产品/Aurasell与Salesforce_SFA对比研究报告.md
- `anteam Slack Chat System` --semantically_similar_to--> `Memory Personal Knowledge System`  [INFERRED] [semantically similar]
  我的项目/anteam/Slack 风格聊天系统 - 技术产品设计文档.md → 我的项目/memory/Memory 个人知识库系统.md
- `anteam Bot (AI Agent)` --semantically_similar_to--> `Aurasell AI CRM`  [INFERRED] [semantically similar]
  我的项目/anteam/Slack 风格聊天系统 - 技术产品设计文档.md → 我的项目/全自动营销产品/Aurasell与Salesforce_SFA对比研究报告.md

## Hyperedges (group relationships)
- **前端技术栈** — React, Vite, TypeScript, pnpm, Ant_Design [EXTRACTED 1.00]
- **后端技术栈** — FastAPI, Python, uv, MySQL, SQLAlchemy [EXTRACTED 1.00]
- **LLM基础设施层** — llm_base, llm_types, llm_registry, llm_providers, MockLLM, PlaceholderLLM [EXTRACTED 1.00]
- **Neovim Language Server Configuration** — neovim, pyright, python_lsp_server, metals, copilot_language_server [EXTRACTED 0.85]
- **前端技术栈** — React, Vite, TypeScript, pnpm, Ant_Design [EXTRACTED 1.00]
- **后端技术栈** — FastAPI, Python, uv, MySQL, SQLAlchemy [EXTRACTED 1.00]
- **LLM基础设施层** — llm_base, llm_types, llm_registry, llm_providers, MockLLM, PlaceholderLLM [EXTRACTED 1.00]
- **Neovim Language Server Configuration** — neovim, pyright, python_lsp_server, metals, copilot_language_server [EXTRACTED 0.85]
- **CMS GC Failure Chain** — CMS_garbage_collector, Promotion_Failure, Concurrent_Mode_Failure, Full_GC, STW, memory_fragmentation [EXTRACTED 0.90]
- **Service Avalanche Prevention Mechanisms** — Circuit_Breaker, Service_Degradation, Rate_Limiting, Bulkhead_Pattern, Timeout_Mechanism, Load_Balancing [EXTRACTED 0.90]
- **GC Performance Metrics Comparison** — CMS_GC, G1_GC, ZGC, GC_performance_comparison [EXTRACTED 0.85]
- **LangChain RAG Pipeline** — langchain_embedding_model, langchain_vectorstore_chroma, langchain_retrieval_qa, langchain_llm [EXTRACTED 0.90]
- **Aurasell vs Salesforce CRM Architecture Comparison** — aurasell, salesforce_sales_cloud, ai_native_crm, ai_enhanced_crm, einstein_ai, agentforce [EXTRACTED 0.85]
- **Full Marketing Automation System Architecture** — customer_data_center, decision_system_marketing, reach_system, analysis_system, prediction_system, profile_system, content_system, feedback_loop [EXTRACTED 0.90]

## Communities

### Community 0 - "CRM AI Architecture"
Cohesion: 0.11
Nodes (18): Salesforce Agentforce, AI-Enhanced CRM Architecture, AI-Native CRM Architecture, anteam Slack Chat System, anteam API Gateway, anteam Bot (AI Agent), anteam Channel, anteam Message (+10 more)

### Community 1 - "Frontend Stack"
Cohesion: 0.14
Nodes (14): Ant Design, FastAPI, Obsidian知识库, Python, React, TypeScript, Vite, pnpm (+6 more)

### Community 2 - "AntAgent Core"
Cohesion: 0.18
Nodes (14): AntAgent, AntAgent Agent Loop, AntAgent Channel Adapter, AntAgent Claude Provider, AntAgent LLM Provider Interface, AntAgent Memory System, AntAgent Message Bus, AntAgent Skill System (+6 more)

### Community 3 - "LLM Integration Layer"
Cohesion: 0.17
Nodes (12): LLM架构层, MockLLM, OpenAI SDK, PlaceholderLLM, Prompt资产独立性, document_edit.py Prompt, llm/base.py, llm/providers目录 (+4 more)

### Community 4 - "Neovim Plugins"
Cohesion: 0.17
Nodes (12): blink.cmp, Copilot Language Server, copilot.lua, Coursier, Karabiner-Elements, Metals, Neovim, Node.js (+4 more)

### Community 5 - "GC Performance"
Cohesion: 0.31
Nodes (10): CMS GC, CMS Garbage Collector, Concurrent Mode Failure, G1 GC, GC Performance Comparison, JVM Parameter Tuning, Promotion Failure, Stop-the-World (STW) (+2 more)

### Community 6 - "Tiling WM"
Cohesion: 0.22
Nodes (9): Dwindle Layout, Niri Layout, OmniWM, Quake Terminal, brew services, Homebrew, Sketchybar, Tiling Window Manager (+1 more)

### Community 7 - "Node.js Dev Env"
Cohesion: 0.25
Nodes (9): Node.js 20, nvm, .nvmrc, Oh My Zsh, Poetry, pyenv, venv, zsh-autoswitch-virtualenv (+1 more)

### Community 8 - "LangChain RAG"
Cohesion: 0.25
Nodes (9): LangChain Chain, LangChain Embedding Model, RetrievalQA Chain, LangChain Sequential Chain, Chroma Vector Store, FAISS Vector Store, Memory Repository, Memory Semantic Search (+1 more)

### Community 9 - "Marketing Automation"
Cohesion: 0.39
Nodes (9): Marketing Analysis System, Marketing Content System, Customer Data Center, Marketing Decision System, Marketing Feedback Loop, Full Marketing Automation System, Marketing Prediction System, Marketing Profile System (+1 more)

### Community 10 - "LangChain Agent"
Cohesion: 0.25
Nodes (8): LangChain Agent, LangChain Chat Model, LangChain LLM, LangChain Memory, LangChain Prompt Template, ReAct Agent, LangChain Tools, LangGraph Agents

### Community 11 - "Service Resilience"
Cohesion: 0.29
Nodes (7): Bulkhead Pattern (Thread Pool Isolation), Circuit Breaker, Load Balancing, Rate Limiting, Service Degradation, Timeout Mechanism, Service Avalanche (服务雪崩)

### Community 12 - "Frontend Components"
Cohesion: 0.47
Nodes (6): ChatPanel组件, MarkdownEditor组件, VersionPanel组件, axios, 前后端联调, 前端API封装层

### Community 13 - "Marketing Strategy"
Cohesion: 0.33
Nodes (6): ABC Customer Stratification, Algorithmic Opportunity Finding, Data-Rich Industry Strategy, Foreign Trade Industry, Sales Process Automation, Smart Decision Brain

### Community 14 - "Android Automation"
Cohesion: 0.5
Nodes (4): HTTP Protocol, Python Client, UiAutomator, uiautomator2

### Community 15 - "Chrome DevTools MCP"
Cohesion: 0.67
Nodes (4): Chrome DevTools, Model Context Protocol (MCP), WebMCP, chrome-devtools-mcp

### Community 16 - "StarRocks OLAP"
Cohesion: 0.5
Nodes (4): MySQL Commands, StarRocks Database, StarRocks Docker Installation, Docker Compose

### Community 17 - "Data Export"
Cohesion: 0.5
Nodes (4): HDFS, MinIO, Parquet Format, StarRocks Data Export

### Community 18 - "Database Config"
Cohesion: 0.67
Nodes (3): MySQL, SQLAlchemy, StarRocks数据生成

### Community 19 - "Claude Code & Ollama"
Cohesion: 0.67
Nodes (3): Claude Code, MCP服务器, Ollama

### Community 20 - "macOS Window Mgmt"
Cohesion: 0.67
Nodes (3): launchd Service, skhd, yabai

### Community 21 - "Java/JDK Env"
Cohesion: 0.67
Nodes (3): JDK, jEnv, QuestDB

### Community 22 - "WezTerm SSH"
Cohesion: 0.67
Nodes (3): WezTerm, SSH Domain, SSH Multiplexing

### Community 23 - "NanoBot Agent"
Cohesion: 0.67
Nodes (3): NanoBot, Ollama, uv tool

### Community 24 - "Doc Chunking"
Cohesion: 0.67
Nodes (3): MarkdownHeaderTextSplitter, Document Chunking, langchain-text-splitters

### Community 25 - "Jenkins CI"
Cohesion: 0.67
Nodes (3): JDK 21, Jenkins 2.541, Jenkins Plugin Mirror

### Community 26 - "Document Models"
Cohesion: 1.0
Nodes (2): DocumentVersion模型, Document模型

### Community 27 - "LLM APIs China"
Cohesion: 1.0
Nodes (2): 文本转语音, 智谱大模型API

### Community 28 - "Git Workflow"
Cohesion: 1.0
Nodes (2): Git, Git Hooks

### Community 29 - "Android Dev"
Cohesion: 1.0
Nodes (2): Android Studio, Android Debug Bridge (adb)

### Community 30 - "Keyboard Remapping"
Cohesion: 1.0
Nodes (2): Via Keyboard Customization, Key Remapping

### Community 31 - "GC Types"
Cohesion: 1.0
Nodes (2): Full GC, Minor GC

### Community 32 - "ZooKeeper ACL"
Cohesion: 1.0
Nodes (2): ZooKeeper ACL, zkCli

### Community 33 - "Bash Scripting"
Cohesion: 1.0
Nodes (2): Bash $(cat) substitution, Bash read command

### Community 34 - "AI Reflection"
Cohesion: 1.0
Nodes (2): AI Code Modification Workflow, AI Knowledge Extraction

### Community 35 - "LangChain Learning"
Cohesion: 1.0
Nodes (1): LangChain/LangGraph学习工程

### Community 36 - "OpenVPN"
Cohesion: 1.0
Nodes (1): OpenVPN

### Community 37 - "Enterprise Email"
Cohesion: 1.0
Nodes (1): 阿里云企业邮箱

### Community 38 - "Learning List"
Cohesion: 1.0
Nodes (1): 待学习列表

### Community 39 - "OpenSpec"
Cohesion: 1.0
Nodes (1): OpenSpec

### Community 40 - "LazyVim"
Cohesion: 1.0
Nodes (1): LazyVim

### Community 41 - "Zellij"
Cohesion: 1.0
Nodes (1): Zellij

### Community 42 - "InfluxDB"
Cohesion: 1.0
Nodes (1): InfluxDB

### Community 43 - "MySQL"
Cohesion: 1.0
Nodes (1): MySQL

### Community 44 - "Rime Input"
Cohesion: 1.0
Nodes (1): Rime

### Community 45 - "Powerlevel10k"
Cohesion: 1.0
Nodes (1): Powerlevel10k

### Community 46 - "llmfit"
Cohesion: 1.0
Nodes (1): llmfit

### Community 47 - "Ruby"
Cohesion: 1.0
Nodes (1): Ruby

### Community 48 - "Alibaba Cloud Bailian"
Cohesion: 1.0
Nodes (1): Alibaba Cloud Bailian (阿里云百炼)

### Community 49 - "Aurasell CEO"
Cohesion: 1.0
Nodes (1): Jason Eubanks (Aurasell CEO)

## Knowledge Gaps
- **127 isolated node(s):** `对话编辑系统`, `文档版本管理`, `Vite`, `TypeScript`, `pnpm` (+122 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Document Models`** (2 nodes): `DocumentVersion模型`, `Document模型`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `LLM APIs China`** (2 nodes): `文本转语音`, `智谱大模型API`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Git Workflow`** (2 nodes): `Git`, `Git Hooks`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Android Dev`** (2 nodes): `Android Studio`, `Android Debug Bridge (adb)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Keyboard Remapping`** (2 nodes): `Via Keyboard Customization`, `Key Remapping`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `GC Types`** (2 nodes): `Full GC`, `Minor GC`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ZooKeeper ACL`** (2 nodes): `ZooKeeper ACL`, `zkCli`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Bash Scripting`** (2 nodes): `Bash $(cat) substitution`, `Bash read command`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `AI Reflection`** (2 nodes): `AI Code Modification Workflow`, `AI Knowledge Extraction`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `LangChain Learning`** (1 nodes): `LangChain/LangGraph学习工程`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `OpenVPN`** (1 nodes): `OpenVPN`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Enterprise Email`** (1 nodes): `阿里云企业邮箱`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Learning List`** (1 nodes): `待学习列表`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `OpenSpec`** (1 nodes): `OpenSpec`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `LazyVim`** (1 nodes): `LazyVim`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Zellij`** (1 nodes): `Zellij`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `InfluxDB`** (1 nodes): `InfluxDB`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `MySQL`** (1 nodes): `MySQL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Rime Input`** (1 nodes): `Rime`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Powerlevel10k`** (1 nodes): `Powerlevel10k`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `llmfit`** (1 nodes): `llmfit`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ruby`** (1 nodes): `Ruby`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Alibaba Cloud Bailian`** (1 nodes): `Alibaba Cloud Bailian (阿里云百炼)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Aurasell CEO`** (1 nodes): `Jason Eubanks (Aurasell CEO)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Aurasell AI CRM` connect `CRM AI Architecture` to `AntAgent Core`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `anteam Slack Chat System` connect `CRM AI Architecture` to `LangChain RAG`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `AntAgent` connect `AntAgent Core` to `CRM AI Architecture`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `对话编辑系统`, `文档版本管理`, `Vite` to the rest of the system?**
  _127 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CRM AI Architecture` be split into smaller, more focused modules?**
  _Cohesion score 0.11 - nodes in this community are weakly interconnected._
- **Should `Frontend Stack` be split into smaller, more focused modules?**
  _Cohesion score 0.14 - nodes in this community are weakly interconnected._