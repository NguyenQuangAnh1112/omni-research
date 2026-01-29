# 🔬 Omni Research

> Multi-Agent AI system for automated topic research and report generation

A hierarchical multi-agent system built with **LangGraph** that automates the research and writing process. Simply input a topic, and the agents will research, write, and produce a polished Markdown report — with you as the final reviewer.

## ✨ Features

- 🔍 **Automated Research** — Uses Tavily API to search and gather information
- ✍️ **AI Writing Agent** — Synthesizes research into a structured report  
- 👤 **Human-in-the-Loop** — Review and approve before publishing
- 📝 **Markdown Output** — Clean reports saved in `reports/`

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Tavily API key ([get one here](https://tavily.com/))
- Ollama running locally (for LLM)

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/omni-research.git
cd omni-research

# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env and add your TAVILY_API_KEY
```

### Usage

```bash
python main.py
```

Then enter a topic when prompted:

```
Nhập chủ đề: Future of AI Agents
   Using Node: supervisor...
   Using Node: researcher...
   Using Node: writer...

📄 BẢN NHÁP ĐỀ XUẤT TỪ WRITER:
==================================================
...
==================================================

REVIEW: Bạn có duyệt bài này không? (yes/no): yes
>> Đã duyệt! Đang tiến hành lưu file...

Quy trình hoàn tất! File đã được lưu.
```

## 🏗️ Architecture

```
User Input → Supervisor → Researcher → Writer → Human Review → Publish
                ↑                         ↓
                └──── Revision loop ──────┘
```

| Agent | Role |
|-------|------|
| **Supervisor** | Orchestrates workflow and routing |
| **Researcher** | Searches and collects information |
| **Writer** | Synthesizes data into reports |
| **Human** | Reviews and approves final output |

## 📁 Project Structure

```
omni-research/
├── main.py                 # Entry point
├── src/
│   ├── agents/
│   │   ├── supervisor.py   # Main graph + routing
│   │   ├── researcher.py   # Research subgraph
│   │   └── writer.py       # Writer subgraph
│   ├── tools/
│   │   ├── search_tools.py # Tavily integration
│   │   └── file_tools.py   # Report saving
│   ├── utils/
│   │   ├── logger.py       # Logging setup
│   │   └── exception.py    # Error handling
│   └── state.py            # State definitions
├── reports/                # Generated reports
├── logs/                   # Application logs
└── test/                   # Test files
```

## 🔧 Configuration

| Variable | Description |
|----------|-------------|
| `TAVILY_API_KEY` | Your Tavily API key for web search |

## 📦 Dependencies

- [LangGraph](https://langchain-ai.github.io/langgraph/) — Agent orchestration
- [LangChain](https://python.langchain.com/) — LLM framework
- [Tavily](https://tavily.com/) — Web search API
- [Ollama](https://ollama.ai/) — Local LLM

## 📄 License

MIT

---

<p align="center">Built with ❤️ and LangGraph</p>
