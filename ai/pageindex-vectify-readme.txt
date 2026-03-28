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
VectifyAI
/
PageIndex
Public
Notifications
Fork 1.9k
 Star 23.2k
Code
Issues
61
Pull requests
39
Discussions
Actions
Projects
Security
Insights
VectifyAI/PageIndex
 main
7 Branches
0 Tags
Code
Folders and files
Name	Last commit message	Last commit date

Latest commit
rejojer
Simplify agentic vectorless RAG demo (#191)
d50c293
 · 
History
266 Commits


.claude/commands
	
Simplify root directory
	


.github
	
Simplify root directory
	


cookbook
	
Merge pull request #118 from mooncos/patch-1
	


examples
	
Simplify agentic vectorless RAG demo (#191)
	


pageindex
	
Rename demo script and update README wording
	


.gitattributes
	
Ignore notebooks for language stats
	


.gitignore
	
Restructure examples directory and improve document storage (#189)
	


LICENSE
	
first commit
	


README.md
	
Rename demo script and update README wording
	


requirements.txt
	
Rename demo script and update README wording
	


run_pageindex.py
	
Integrate LiteLLM for multi-provider LLM support (#168)
	
Repository files navigation
README
MIT license




PageIndex: Vectorless, Reasoning-based RAG

Reasoning-based RAG  ◦  No Vector DB  ◦  No Chunking  ◦  Human-like Retrieval

🏠 Homepage  •   🖥️ Chat Platform  •   🔌 MCP  •   📚 Docs  •   💬 Discord  •   ✉️ Contact 
📢 Updates
🔥 Agentic Vectorless RAG: A simple agentic, vectorless RAG example with self-hosted PageIndex, using OpenAI Agents SDK.
PageIndex Chat: A Human-like document analysis agent platform for professional long documents. Also available via MCP or API.
PageIndex Framework: The PageIndex framework — an agentic, in-context tree index that enables LLMs to perform reasoning-based, human-like retrieval over long documents.
📑 Introduction to PageIndex

Are you frustrated with vector database retrieval accuracy for long professional documents? Traditional vector-based RAG relies on semantic similarity rather than true relevance. But similarity ≠ relevance — what we truly need in retrieval is relevance, and that requires reasoning. When working with professional documents that demand domain expertise and multi-step reasoning, similarity search often falls short.

Inspired by AlphaGo, we propose PageIndex — a vectorless, reasoning-based RAG system that builds a hierarchical tree index from long documents and uses LLMs to reason over that index for agentic, context-aware retrieval. It simulates how human experts navigate and extract knowledge from complex documents through tree search, enabling LLMs to think and reason their way to the most relevant document sections. PageIndex performs retrieval in two steps:

Generate a “Table-of-Contents” tree structure index of documents
Perform reasoning-based retrieval through tree search
🎯 Core Features

Compared to traditional vector-based RAG, PageIndex features:

No Vector DB: Uses document structure and LLM reasoning for retrieval, instead of vector similarity search.
No Chunking: Documents are organized into natural sections, not artificial chunks.
Human-like Retrieval: Simulates how human experts navigate and extract knowledge from complex documents.
Better Explainability and Traceability: Retrieval is based on reasoning — traceable and interpretable, with page and section references. No more opaque, approximate vector search (“vibe retrieval”).

PageIndex powers a reasoning-based RAG system that achieved state-of-the-art 98.7% accuracy on FinanceBench, demonstrating superior performance over vector-based RAG solutions in professional document analysis (see our blog post for details).

📍 Explore PageIndex

To learn more, please see a detailed introduction of the PageIndex framework. Check out this GitHub repo for open-source code, and the cookbooks, tutorials, and blog for additional usage guides and examples.

The PageIndex service is available as a ChatGPT-style chat platform, or can be integrated via MCP or API.

🛠️ Deployment Options
Self-host — run locally with this open-source repo.
Cloud Service — try instantly with our Chat Platform, or integrate with MCP or API.
Enterprise — private or on-prem deployment. Contact us or book a demo for more details.
🧪 Quick Hands-on
🔥 Agentic Vectorless RAG (latest) — a simple but complete agentic vectorless RAG example with self-hosted PageIndex, using OpenAI Agents SDK.
Try the Vectorless RAG notebook — a minimal, hands-on example of reasoning-based RAG using PageIndex.
Check out Vision-based Vectorless RAG — no OCR; a minimal, vision-based & reasoning-native RAG pipeline that works directly over page images.

    
🌲 PageIndex Tree Structure

PageIndex can transform lengthy PDF documents into a semantic tree structure, similar to a "table of contents" but optimized for use with Large Language Models (LLMs). It's ideal for: financial reports, regulatory filings, academic textbooks, legal or technical manuals, and any document that exceeds LLM context limits.

Below is an example PageIndex tree structure. Also see more example documents and generated tree structures.

...
{
  "title": "Financial Stability",
  "node_id": "0006",
  "start_index": 21,
  "end_index": 22,
  "summary": "The Federal Reserve ...",
  "nodes": [
    {
      "title": "Monitoring Financial Vulnerabilities",
      "node_id": "0007",
      "start_index": 22,
      "end_index": 28,
      "summary": "The Federal Reserve's monitoring ..."
    },
    {
      "title": "Domestic and International Cooperation and Coordination",
      "node_id": "0008",
      "start_index": 28,
      "end_index": 31,
      "summary": "In 2023, the Federal Reserve collaborated ..."
    }
  ]
}
...

You can generate the PageIndex tree structure with this open-source repo, or use our API.

⚙️ Package Usage

You can follow these steps to generate a PageIndex tree from a PDF document.

1. Install dependencies
pip3 install --upgrade -r requirements.txt
2. Set your LLM API key

Create a .env file in the root directory with your LLM API key, with multi-LLM support via LiteLLM:

OPENAI_API_KEY=your_openai_key_here
3. Generate PageIndex structure for your PDF
python3 run_pageindex.py --pdf_path /path/to/your/document.pdf
Optional parameters
Markdown support
Agentic Vectorless RAG Example

For a simple, end-to-end agentic vectorless RAG example using PageIndex (with OpenAI Agents SDK), see examples/agentic_vectorless_rag_demo.py.

# Install optional dependency
pip3 install openai-agents

# Run the demo
python3 examples/agentic_vectorless_rag_demo.py
📈 Case Study: PageIndex Leads Finance QA Benchmark

Mafin 2.5 is a reasoning-based RAG system for financial document analysis, powered by PageIndex. It achieved a state-of-the-art 98.7% accuracy on the FinanceBench benchmark, significantly outperforming traditional vector-based RAG systems.

PageIndex's hierarchical indexing and reasoning-driven retrieval enable precise navigation and extraction of relevant context from complex financial reports, such as SEC filings and earnings disclosures.

Explore the full benchmark results and our blog post for detailed comparisons and performance metrics.

🧭 Resources
🧪 Cookbooks: hands-on, runnable examples and advanced use cases.
📖 Tutorials: practical guides and strategies, including Document Search and Tree Search.
📝 Blog: technical articles, research insights, and product updates.
🔌 MCP setup & API docs: integration details and configuration options.
⭐ Support Us

Please cite this work as:

Mingtian Zhang, Yu Tang and PageIndex Team,
"PageIndex: Next-Generation Vectorless, Reasoning-based RAG",
PageIndex Blog, Sep 2025.

Or use the BibTeX citation.

Leave us a star 🌟 if you like our project. Thank you!

Connect with Us

      

© 2026 Vectify AI

About

📑 PageIndex: Document Index for Vectorless, Reasoning-based RAG

pageindex.ai
Topics
information-retrieval ai retrieval agents reasoning ai-agents rag vector-database llm retrieval-augmented-generation agentic-ai context-engineering
Resources
 Readme
License
 MIT license
 Activity
 Custom properties
Stars
 23.2k stars
Watchers
 107 watching
Forks
 1.9k forks
Report repository


Releases
No releases published


Packages
No packages published



Contributors
10


Languages
Python
100.0%
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
