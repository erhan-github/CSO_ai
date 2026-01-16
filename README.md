# 🧠 CSO.ai

> **Your AI Chief Strategy Officer** - Strategic intelligence that understands your codebase, business, and market.

CSO.ai is an MCP server that acts as your personal Chief Strategy Officer. It deeply understands your codebase, infers your business context, tracks relevant market trends, and proactively surfaces insights.

## 🚀 Quick Start

### 1. Install

```bash
# From source
git clone https://github.com/your-org/cso-ai.git
cd cso-ai
uv venv && uv pip install -e .
```

### 2. Configure Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "cso-ai": {
      "command": "/path/to/cso-ai/.venv/bin/python",
      "args": ["-m", "cso_ai.server"]
    }
  }
}
```

### 3. Enable LLM (Recommended)

For smart article scoring and strategic advice, get a free Groq API key:

1. Go to https://console.groq.com/keys
2. Create a free account
3. Generate an API key
4. Add to your `.env`:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

Or export directly:
```bash
export GROQ_API_KEY=your_groq_api_key_here
```

### 4. Start Using

```
"CSO, analyze my codebase"
"What's new in tech?"
"Is this article worth reading?" + URL
```

---

## 📊 How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CSO.ai                              │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   LISTEN    │  │ UNDERSTAND  │  │  ANTICIPATE │         │
│  │             │  │             │  │             │         │
│  │ • Codebase  │  │ • Tech      │  │ • Risks     │         │
│  │ • Documents │─▶│ • Business  │─▶│ • Opps      │         │
│  │ • Git       │  │ • Market    │  │ • Advice    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                          │                                  │
│                          ▼                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    STORAGE                             │ │
│  │   ~/.cso-ai/data.db (SQLite)                          │ │
│  │   • Profiles • Articles • Insights                     │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Article Fetching

| Source | Articles/Request | Update Frequency |
|--------|------------------|------------------|
| Hacker News | ~30 top stories | On-demand |
| Lobste.rs | ~30 articles | On-demand |
| GitHub Trending | ~25 repos | On-demand |

**Total:** ~85 articles per `whats_new` or `refresh` call.

Articles are:
1. Fetched live from sources
2. Scored against YOUR profile (0-100)
3. Stored in local SQLite database
4. Available for future queries

### LLM Usage (January 2026 Models)

| Task | Model | Speed | Why |
|------|-------|-------|-----|
| Article Scoring | `llama-3.1-8b-instant` | 277 tok/s | Fast, cheap - high volume |
| URL Analysis | `llama-3.1-8b-instant` | 277 tok/s | Quick relevance checks |
| Strategic Advice | `llama-3.3-70b-versatile` | 218 tok/s | Best reasoning |
| Fallback | `gemma2-9b-it` | 814 tok/s | Ultra-cheap backup |

| Feature | With GROQ_API_KEY | Without API Key |
|---------|-------------------|-----------------|
| Article Scoring | LLM-powered (smart) | Keyword matching |
| URL Analysis | LLM-powered (smart) | Basic extraction |
| Strategic Advice | LLM-powered (full) | Stage-based tips |

**Provider:** Groq (fast LPU inference, free tier available)

---

## 🛠️ Available Tools

### Intelligence

| Tool | Trigger | What It Does |
|------|---------|--------------|
| `ping` | "hey CSO" | Check status |
| `analyze_codebase` | "analyze my codebase" | Deep analysis + insights |
| `show_profile` | "what do you know?" | Show saved profile |

### Market Intelligence

| Tool | Trigger | What It Does |
|------|---------|--------------|
| `whats_new` | "what's new?" | Scored articles from HN/Lobsters |
| `business_insights` | "business trends?" | Business-focused articles |
| `explore` | "tell me about X" | Deep-dive on topic |
| `analyze_url` | "is this worth reading?" | Evaluate any URL |
| `refresh` | "update your info" | Re-fetch all sources |

---

## 📁 What CSO.ai Detects

### Technical Intelligence

- **Languages** - File distribution by language
- **Frameworks** - React, FastAPI, SwiftUI, etc.
- **Dependencies** - npm, pip, cargo, etc.
- **Architecture** - Patterns and structure
- **Health** - README, tests, CI/CD, Docker, License
- **Git Activity** - Commits, contributors, frequency
- **Code Issues** - TODOs, FIXMEs, HACKs
- **Cursor Rules** - Your development preferences

### Business Intelligence

- **Product Type** - web_app, mobile_app, api, cli
- **Domain** - EdTech, FinTech, AI/ML, DevTools, etc.
- **Stage** - mvp, early, growth
- **Business Model** - B2B, B2C, E-commerce
- **Integrations** - Stripe, Supabase, Sentry, etc.

### Proactive Insights

- ⚠️ **Risks** - Missing tests, high tech debt
- 💡 **Opportunities** - Stage-specific guidance
- 📋 **Recommendations** - Add CI/CD, analytics, etc.

---

## 🔧 Configuration

### Environment Variables

```bash
# Required for LLM features (free at console.groq.com)
GROQ_API_KEY=your_groq_key_here
```

### Data Storage

All data is stored locally in `~/.cso-ai/data.db`:
- Intelligence profiles
- Fetched articles
- Relevance scores

---

## 📈 Future Enhancements

- [ ] Background article fetching (scheduled)
- [ ] Weekly digest emails
- [ ] Competitor tracking
- [ ] Custom RSS sources
- [ ] Team profiles

---

## 🤝 Philosophy

> "The best CSO doesn't wait to be asked. They see what's coming and prepare you for it."

CSO.ai embodies this philosophy. It's not a search engine - it's strategic intelligence that knows your business and helps you navigate what's ahead.

---

## 📄 License

MIT
