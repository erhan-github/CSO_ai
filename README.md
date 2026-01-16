# CSO.ai - Your AI Chief Strategy Officer

> **Open Cursor. Ask "what should I read?". Get 5 perfect articles in < 1 second.**

CSO.ai is an intelligent MCP (Model Context Protocol) server that acts as your personal Chief Strategy Officer, delivering hyper-relevant tech articles and strategic insights tailored to your codebase.

[![Tests](https://img.shields.io/badge/tests-53%20passing-brightgreen)]() [![Code Size](https://img.shields.io/badge/code-5.1k%20lines-blue)]() [![License](https://img.shields.io/badge/license-MIT-green)]()

---

## ✨ The Magic

```
You: "What should I read?"

CSO: 📰 Top Articles for Your Stack (Python + FastAPI)
     🎯 Current Focus: Authentication

     1. [95] ██████████ FastAPI Auth Best Practices
        💡 Directly relevant to your API architecture
        🔗 https://...
        ⏱️ ~8 min read

     ⚡ Analyzed in 80ms | From cache
```

**Zero setup.** **Instant value.** **Always relevant.**

---

## 🚀 Quick Start (< 2 minutes)

### 1. Install

```bash
# Clone the repository
git clone https://github.com/yourusername/cso-ai.git
cd cso-ai

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### 2. Configure Cursor

Add to your Cursor MCP settings (`~/.cursor/config.json` or via Settings → MCP):

```json
{
  "mcpServers": {
    "cso-ai": {
      "command": "python",
      "args": ["-m", "cso_ai.server"]
    }
  }
}
```

### 3. Use It!

Open Cursor and try:
- "What should I read?"
- "Is this article worth reading? https://..."
- "What should I focus on?"

**That's it!** CSO.ai auto-detects your stack and starts delivering value immediately.

---

## 🎯 Core Features

### 1. **Smart Article Recommendations** (`read`)
- **Auto-detects your stack** (Python, FastAPI, React, etc.)
- **Fetches from 3 sources** (Hacker News, Lobsters, GitHub Trending)
- **Scores 0-100** for relevance to YOUR codebase
- **Context-aware** (knows what you're working on)
- **Sub-100ms responses** (query cache)

### 2. **URL Analysis** (`analyze_url`)
- **Instant evaluation** of any article/link
- **Relevance scoring** against your stack
- **Key takeaways** extraction
- **Read/skip recommendations**

### 3. **Strategic Advice** (`strategy`)
- **Analyzes your recent commits** and work patterns
- **Prioritized actions** (critical → important → opportunity)
- **Relevant reading** based on current focus
- **LLM-powered insights** (with Groq API)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  MCP Server (Local, Per User)          │
│  - 3 core tools (read, analyze, strategy)
│  - Auto-intelligence (zero setup)      │
│  - Query cache (< 100ms responses)     │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Background Services (Always On)        │
│  - FileWatcher (monitors code changes)  │
│  - ContextTracker (detects focus)       │
│  - CacheWarmer (30-min article refresh) │
│  - CleanupScheduler (daily at 3 AM)     │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Local Database (~/.cso-ai/local.db)    │
│  - profiles (your stack, forever)       │
│  - articles (7-day retention)           │
│  - work_context (7-day retention)       │
│  - query_cache (1-hour TTL)             │
│  Size: < 50MB                           │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  External Sources (Resilient)           │
│  - Hacker News (with retry logic)       │
│  - Lobsters (with retry logic)          │
│  - GitHub Trending (with retry logic)   │
└─────────────────────────────────────────┘
```

**Key Design Principles**:
- **Local-first**: Fast, private, works offline
- **Auto-everything**: Zero config, auto-cleanup, auto-context
- **Production-ready**: Retry logic, error handling, 53 tests

---

## 📊 Performance

| Metric | Target | Actual |
|--------|--------|--------|
| **Query Response** | < 100ms | 80ms (cached) |
| **Article Cache** | < 1s | 800ms |
| **Fresh Query** | < 3s | 2.5s |
| **Database Size** | < 50MB | ~10MB (typical) |
| **Memory Usage** | < 100MB | ~50MB |

**Caching Strategy**:
- **Query Cache**: 1-hour TTL (instant responses)
- **Article Cache**: 1-hour TTL (fresh content)
- **Profile Cache**: 24-hour TTL (stable detection)
- **Score Cache**: Permanent (per profile)

---

## 🛠️ Configuration

### Optional: Groq API (for smart scoring)

```bash
# Get API key from https://console.groq.com
export GROQ_API_KEY=your_key_here

# Or create .env file
echo "GROQ_API_KEY=your_key_here" > .env
```

**Without Groq**: Falls back to heuristic scoring (still works great!)

### Optional: Debug Mode

```bash
export CSO_AI_DEBUG=1
```

---

## 🧪 Development

### Run Tests

```bash
# All tests (53 tests, 100% passing)
pytest tests/ -v

# Specific test file
pytest tests/test_auto_intelligence.py -v

# With coverage
pytest tests/ --cov=cso_ai --cov-report=html
```

### Code Quality

```bash
# Linting
ruff check src/

# Formatting
ruff format src/

# Type checking
mypy src/
```

### Project Structure

```
cso-ai/
├── src/cso_ai/
│   ├── server.py              # MCP server entry point
│   ├── tools_refined.py       # 3 core tools (512 lines)
│   ├── intel/
│   │   ├── auto_intelligence.py  # Zero-setup stack detection
│   │   ├── market.py             # Article fetching & scoring
│   │   ├── strategist.py         # LLM-powered advice
│   │   └── technical.py          # Codebase analysis
│   ├── storage/
│   │   └── simple_db.py          # Local SQLite (4 tables)
│   ├── services/
│   │   ├── file_watcher.py       # File change monitoring
│   │   ├── context_tracker.py    # Work focus detection
│   │   ├── service_manager.py    # Service lifecycle
│   │   └── cleanup_scheduler.py  # Auto-cleanup (3 AM daily)
│   ├── sources/
│   │   ├── hackernews.py         # HN API integration
│   │   ├── lobsters.py           # Lobsters RSS
│   │   └── github.py             # GitHub Trending scraper
│   └── utils/
│       ├── retry.py              # Exponential backoff
│       ├── errors.py             # User-friendly errors
│       ├── performance.py        # Metrics tracking
│       └── cache_warmer.py       # Background refresh
├── tests/                     # 53 tests, 100% passing
└── docs/                      # Documentation
```

---

## 📚 Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design & data flow
- **[API Reference](docs/API.md)** - Tool specifications & examples
- **[Contributing](docs/CONTRIBUTING.md)** - Development guide
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues & solutions
- **[Product Roadmap](docs/ROADMAP.md)** - Future features & vision

---

## 🎯 Use Cases

### For Individual Developers
- **Stay current** without drowning in HN/Reddit
- **Discover relevant articles** for your stack
- **Get strategic advice** on what to focus on
- **Save 10+ hours/week** on research

### For Teams
- **Shared knowledge** across team members
- **Onboard new developers** faster
- **Track team focus areas** automatically
- **Collaborative article ratings**

### For Tech Leaders
- **Monitor tech trends** relevant to your stack
- **Identify opportunities** and threats
- **Make informed decisions** on tech adoption
- **Keep team aligned** on priorities

---

## 🚀 Roadmap

### ✅ Phase 1: Core (Complete)
- 3 perfect tools (read, analyze, strategy)
- Auto-intelligence (zero setup)
- Smart caching (sub-100ms)
- Production hardening (retry, errors, tests)

### 🔄 Phase 2: Proactive Intelligence (In Progress)
- Morning briefings (daily intelligence)
- Contextual nudges (proactive suggestions)
- Predictive recommendations (AI learns your patterns)

### 📅 Phase 3: Team Features (Planned)
- Team profiles & shared knowledge
- Collaborative filtering
- Onboarding automation
- Team analytics

### 🔮 Phase 4: Deep Integration (Future)
- Inline code suggestions
- Code review assistant
- Breaking change alerts
- Custom sources (RSS, Slack, etc.)

**See [Product Roadmap](docs/ROADMAP.md) for details.**

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

**Quick Start**:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Submit a PR

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Hacker News** - For the amazing community & API
- **Lobsters** - For quality tech discussions
- **GitHub** - For trending repositories
- **Groq** - For lightning-fast LLM inference
- **Model Context Protocol** - For the MCP standard

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/cso-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/cso-ai/discussions)
- **Twitter**: [@cso_ai](https://twitter.com/cso_ai)

---

## ⭐ Star History

If CSO.ai saves you time, give it a star! ⭐

---

**Built with ❤️ for developers who want to stay current without the overwhelm.**

*CSO.ai - Your AI Chief Strategy Officer*
