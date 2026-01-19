# Side Strategic Intelligence Curation Plan
> *Top 10 Strategy // Palantir-Level Quality*

---

## I. THE TOP 10 PHILOSOPHY

**Core Principle**: Quality over quantity. Only surface the absolute best signals.

### Curation Strategy by Source

| Source | Fetch Volume | Filter Criteria | Keep Top |
| :--- | :---: | :--- | :---: |
| **ArXiv AI** | 50/day | LLM score + citation potential | 10 |
| **ArXiv LLM** | 30/day | Keyword: "reasoning", "GPT", "benchmark" | 5 |
| **HackerNews** | 50/day | Score > 100 points | 10 |
| **Lobsters** | 30/day | Tags: "ai", "programming", "practices" | 10 |
| **GitHub Trending** | 25/day | Stars > 500, updated this week | 10 |
| **Substack (Tech)** | 20/week | From curated list of 5 authors | All |
| **Dev.to** | 50/day | Reactions > 50 | 10 |

**Total daily storage**: ~65 articles/day = **2KB/day**

---

## II. LLM SCORING PIPELINE

### Phase 1: Fetch (Cheap)
```python
# Free API calls, no cost
articles = await fetch_arxiv(limit=50)
articles += await fetch_hackernews(limit=50)
```

### Phase 2: Score (Groq - Fast & Cheap)
```python
# Batch scoring: 50 articles in ONE LLM call
# Cost: ~5K tokens = $0.0005 (half a cent)

prompt = f"""
Score these 50 articles for a {user_domain} developer:
[List of titles + abstracts]

Return JSON: [{{"url": "...", "score": 85, "reason": "..."}}]
"""

scores = await groq_llm.score_batch(prompt)
```

### Phase 3: Filter (Free)
```python
# Keep top 10 by score
top_10 = sorted(scores, key=lambda x: x['score'], reverse=True)[:10]
```

**Total cost per day**: ~$0.01 (one cent)

---

## III. QUALITY FILTERS (Palantir-Level)

### ArXiv Papers

**Tier 1 Signals** (Auto-include):
- Authors from: OpenAI, DeepMind, Anthropic, Meta AI
- Cited by > 10 papers already (via Semantic Scholar API)
- Keywords: "state-of-the-art", "SOTA", "benchmark"

**Tier 2 Signals** (LLM score):
- Novel architectures
- Practical applications
- Survey papers

**Reject**:
- Incremental improvements (<2% gain)
- Narrow domain-specific (unless user's domain)

### HackerNews

**Tier 1 Signals**:
- Score > 200 points
- Comments > 50
- Domain: github.com, arxiv.org, blog.* (not news sites)

**Tier 2 Signals**:
- "Ask HN" with > 100 comments
- "Show HN" with working demo

**Reject**:
- Political content
- Crypto hype
- Clickbait titles

### GitHub Trending

**Tier 1 Signals**:
- Stars gained today > 100
- README quality score > 8/10 (has: demo, install, usage)
- Active maintainers (commit in last 7 days)

**Tier 2 Signals**:
- Forks > Stars/10 (high utility)
- Issues closed > Issues opened (responsive)

**Reject**:
- Awesome lists
- Tutorial repos
- Forks without original work

---

## IV. STORAGE ECONOMICS

### Current State (Wasteful)
```
Fetch 200 articles/day → Store all → Delete after 7 days
Storage: 200 × 7 = 1,400 articles in DB
```

### Proposed State (Strategic)
```
Fetch 200 articles/day → Score → Keep top 65 → Store for 30 days
Storage: 65 × 30 = 1,950 articles in DB
```

**Why this is better:**
- Higher quality (only top signals)
- Longer retention (30 days for trend detection)
- Similar storage footprint

### Storage Schema (Optimized)

```sql
CREATE TABLE intelligence_signals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    source TEXT,  -- 'arxiv', 'hn', 'github'
    domain TEXT,  -- 'ai', 'devtool', 'saas'
    score INTEGER,  -- LLM relevance score 0-100
    keywords JSON,  -- ['reasoning', 'llm', 'benchmark']
    published_at TIMESTAMP,
    fetched_at TIMESTAMP,
    expires_at TIMESTAMP  -- Auto-delete after 30 days
);

CREATE INDEX idx_signals_score ON intelligence_signals(score DESC);
CREATE INDEX idx_signals_keywords ON intelligence_signals(keywords);
```

---

## V. WHO READS IT? THE CONSUMPTION FLOW

### Scenario 1: User Asks a Question

```
User: "Side, what's the best way to handle auth in 2026?"

Flow:
1. Retrieve: Top 10 articles with keywords "auth", "authentication"
2. Context: Feed to LLM as RAG context
3. LLM: "Based on recent HN discussions and an ArXiv paper from last week..."
```

### Scenario 2: Daily Digest (Future)

```
Every morning:
1. Retrieve: Top 5 signals from yesterday
2. Filter: Match user's project domain
3. Notify: "Side found 3 relevant updates for you"
```

### Scenario 3: Proactive Suggestions (Future)

```
User is working on auth code:
1. Detect: User editing auth.py
2. Retrieve: Recent auth-related signals
3. Suggest: "FYI: Passkeys are trending. Consider this library..."
```

---

## VI. IMPLEMENTATION PRIORITY

### Week 1: Foundation
- [x] ArXiv RSS feeds added
- [ ] Implement LLM batch scoring
- [ ] Create `intelligence_signals` table
- [ ] Add Top 10 filter logic

### Week 2: Quality
- [ ] Add Tier 1 auto-include filters
- [ ] Implement keyword extraction
- [ ] Add 30-day retention policy

### Week 3: Consumption
- [ ] Build RAG retrieval for user questions
- [ ] Test: "Side, what's new in X?" queries
- [ ] Measure: LLM answer quality

---

## VII. COST ANALYSIS (Palantir-Level Efficiency)

| Operation | Volume | Cost |
| :--- | :--- | :--- |
| RSS fetching | 200 calls/day | **Free** |
| LLM scoring | 200 articles/day | $0.01/day |
| Storage | 1,950 articles | **Free** (SQLite) |
| RAG retrieval | 10 queries/day | $0.02/day |

**Total monthly cost**: ~$1.00

**Value delivered**: Real-time intelligence for strategic decisions

---

## VIII. SUCCESS METRICS

| Metric | Target | Measurement |
| :--- | :--- | :--- |
| Signal quality | >80% user-rated "useful" | User feedback |
| Freshness | <24 hours old | Timestamp delta |
| Relevance | >70 LLM score | Automated |
| Diversity | 5+ sources per day | Source count |

---

**End of Curation Plan // Side Alpha-0**
