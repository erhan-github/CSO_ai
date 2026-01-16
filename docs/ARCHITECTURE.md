# CSO.ai Scalable Architecture - 10M+ Users

## 🎯 Critical Constraints

**Target**: 10M+ Cursor/Claude users
**Use Case**: MCP tool (not a web service)
**Key Challenge**: Each user has their own local instance
**Storage**: Supabase (shared) + Local SQLite (per-user)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    10M+ Users (Cursor/Claude)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │         MCP Server (Per User)           │
        │  - Runs locally in user's environment   │
        │  - Lightweight, fast, isolated          │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │      Hybrid Storage Architecture        │
        ├─────────────────────────────────────────┤
        │                                         │
        │  LOCAL (SQLite)          SHARED (Cloud) │
        │  ├─ User profile         ├─ Articles   │
        │  ├─ Work context         ├─ Scores     │
        │  ├─ Code index           ├─ Insights   │
        │  └─ Cache (7 days)       └─ Analytics  │
        │                                         │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │         Shared Intelligence Layer       │
        │  - Supabase (PostgreSQL + Edge Funcs)  │
        │  - Global article cache                 │
        │  - Collaborative filtering              │
        │  - Usage analytics                      │
        └─────────────────────────────────────────┘
```

---

## 📊 Data Architecture

### 1. **Local Storage (Per User - SQLite)**

**Purpose**: Fast, private, user-specific data
**Retention**: 7 days rolling window
**Size**: ~10-50MB per user

```sql
-- User's local database (~/.cso-ai/local.db)

-- Profile (updated on code changes)
profiles (
    project_path TEXT PRIMARY KEY,
    languages JSON,
    frameworks JSON,
    last_updated TIMESTAMP,
    -- NO article data here!
)

-- Work context (what user is doing NOW)
work_context (
    id INTEGER PRIMARY KEY,
    focus_area TEXT,
    recent_files JSON,
    detected_at TIMESTAMP,
    expires_at TIMESTAMP  -- Auto-delete after 7 days
)

-- Code index (for fast search)
code_index (
    file_path TEXT,
    symbol_name TEXT,
    indexed_at TIMESTAMP,
    expires_at TIMESTAMP  -- Auto-delete after 7 days
)

-- Query cache (pre-computed results)
query_cache (
    query_hash TEXT PRIMARY KEY,
    result JSON,
    cached_at TIMESTAMP,
    expires_at TIMESTAMP  -- Auto-delete after 1 hour
)
```

**Auto-Cleanup**: Daily job deletes expired data

---

### 2. **Shared Storage (Global - Supabase)**

**Purpose**: Shared intelligence, collaborative filtering
**Retention**: Smart retention based on popularity
**Size**: Optimized for billions of records

```sql
-- Supabase schema (shared across all users)

-- Articles (global cache, deduplicated)
articles (
    id UUID PRIMARY KEY,
    url TEXT UNIQUE,
    title TEXT,
    source TEXT,
    content_hash TEXT,  -- Dedupe
    fetched_at TIMESTAMP,
    popularity_score FLOAT,  -- How many users read this
    expires_at TIMESTAMP,  -- Smart expiration
    INDEX (source, fetched_at),
    INDEX (popularity_score DESC)
)

-- Article scores (collaborative filtering)
article_scores (
    article_id UUID,
    stack_hash TEXT,  -- Hash of tech stack (Python+FastAPI)
    avg_score FLOAT,  -- Average score for this stack
    score_count INTEGER,  -- How many users scored this
    last_updated TIMESTAMP,
    PRIMARY KEY (article_id, stack_hash),
    INDEX (stack_hash, avg_score DESC)
)

-- User analytics (anonymous, aggregated)
user_analytics (
    user_hash TEXT,  -- Anonymous hash
    stack_hash TEXT,
    query_count INTEGER,
    last_active TIMESTAMP,
    -- NO personal data!
)
```

**Smart Retention**:
- Popular articles (score_count > 100): Keep 30 days
- Medium popularity (10-100): Keep 7 days
- Low popularity (< 10): Keep 24 hours
- Auto-cleanup runs hourly

---

## 🔄 Data Flow

### Query Flow (Optimized for Speed)

```
User Query: "What should I read?"
    ↓
┌─────────────────────────────────────┐
│ 1. Local Cache Check (< 10ms)      │
│    - Check query_cache table        │
│    - If hit: Return immediately     │
└─────────────────────────────────────┘
    ↓ (cache miss)
┌─────────────────────────────────────┐
│ 2. Get User Context (< 50ms)       │
│    - Read work_context (local)      │
│    - Get stack_hash from profile    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Fetch Pre-Scored Articles       │
│    (< 100ms)                        │
│    - Query Supabase:                │
│      SELECT * FROM article_scores   │
│      WHERE stack_hash = ?           │
│      ORDER BY avg_score DESC        │
│      LIMIT 5                        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. Cache Result Locally (< 10ms)   │
│    - Store in query_cache           │
│    - Set 1-hour expiration          │
└─────────────────────────────────────┘
    ↓
Return to user (Total: ~160ms)
```

**Key Optimization**: Pre-scored articles in Supabase = No LLM calls needed!

---

### Background Sync Flow

```
File Change Detected
    ↓
┌─────────────────────────────────────┐
│ 1. Update Local Context (< 1s)     │
│    - Update work_context            │
│    - Update code_index              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Invalidate Cache (< 10ms)       │
│    - Clear query_cache              │
│    - Force fresh query next time    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Async Sync to Supabase          │
│    (Optional, batched)              │
│    - Update user_analytics          │
│    - Contribute to collaborative    │
│      filtering                      │
└─────────────────────────────────────┘
```

---

## 📈 Scaling Strategy

### Phase 1: 0-100K Users (Current)
**Storage**: SQLite (local) + Supabase Free Tier
**Cost**: $0-25/month
**Architecture**: Simple, single-region

### Phase 2: 100K-1M Users
**Storage**: SQLite (local) + Supabase Pro
**Cost**: ~$500/month
**Optimizations**:
- Add Supabase connection pooling
- Implement CDN for article content
- Add read replicas

### Phase 3: 1M-10M Users
**Storage**: SQLite (local) + Supabase Enterprise + Redis
**Cost**: ~$5K/month
**Optimizations**:
- Multi-region Supabase
- Redis for hot article cache
- Horizontal scaling with Edge Functions
- Implement rate limiting

### Phase 4: 10M+ Users
**Storage**: SQLite (local) + Distributed Database
**Cost**: ~$50K/month
**Architecture**:
- Move to distributed database (CockroachDB/PlanetScale)
- Global CDN for articles
- Dedicated article fetching service
- ML-based collaborative filtering

---

## 🎯 Data Retention Strategy

### Local (Per User)
```
Profile:        Forever (tiny, ~1KB)
Work Context:   7 days (auto-delete)
Code Index:     7 days (auto-delete)
Query Cache:    1 hour (auto-delete)
```

**Why 7 days?**
- Covers typical sprint cycle
- Keeps database small (< 50MB)
- Old data is irrelevant

### Shared (Supabase)
```
Articles:
  - Popular (100+ users):   30 days
  - Medium (10-100 users):  7 days
  - Unpopular (< 10 users): 24 hours

Article Scores:
  - Active stacks:          90 days
  - Inactive stacks:        30 days

User Analytics:
  - Aggregated only:        Forever
  - Individual records:     90 days
```

**Auto-Cleanup Jobs**:
- Hourly: Delete expired articles
- Daily: Aggregate analytics
- Weekly: Vacuum database

---

## 🔐 Privacy & Security

### Local Data
- ✅ Stored locally (~/.cso-ai/)
- ✅ Never leaves user's machine
- ✅ User has full control

### Shared Data
- ✅ Anonymous (user_hash, no PII)
- ✅ Aggregated (collaborative filtering)
- ✅ Opt-out available
- ✅ GDPR compliant

---

## 💰 Cost Analysis (10M Users)

### Storage Costs
```
Local (per user):  50MB × 10M = 500TB
  → User's disk, $0 for us

Supabase:
  Articles:        ~100GB (deduplicated)
  Scores:          ~500GB (collaborative)
  Analytics:       ~50GB (aggregated)
  Total:           ~650GB
  Cost:            ~$5K/month
```

### Compute Costs
```
Article Fetching:  ~$1K/month (scheduled jobs)
Edge Functions:    ~$2K/month (query processing)
Redis Cache:       ~$1K/month (hot data)
Total:             ~$4K/month
```

### Total: ~$9K/month for 10M users = $0.0009/user/month

**Revenue Model**: Freemium
- Free tier: 100 queries/day
- Pro tier: $5/month, unlimited
- Enterprise: Custom pricing

---

## 🚀 Implementation Priority

### Phase 1: Foundation (Week 1-2) ✅
- [x] Local SQLite with auto-cleanup
- [x] Basic Supabase integration
- [x] File watcher
- [x] Service manager

### Phase 2: Shared Intelligence (Week 3-4)
- [ ] Supabase schema setup
- [ ] Collaborative filtering
- [ ] Pre-scoring pipeline
- [ ] Auto-cleanup jobs

### Phase 3: Optimization (Week 5-6)
- [ ] Query cache optimization
- [ ] Connection pooling
- [ ] Rate limiting
- [ ] Monitoring dashboard

### Phase 4: Scale Testing (Week 7-8)
- [ ] Load testing (1M queries/day)
- [ ] Cost optimization
- [ ] Performance tuning
- [ ] Documentation

---

## 📊 System Diagrams

### Architecture Layers
```
┌─────────────────────────────────────────────────────────┐
│                  User Layer (10M users)                 │
│  Each user runs MCP server locally in Cursor/Claude    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Local Intelligence Layer                   │
│  - SQLite database (~/.cso-ai/local.db)                │
│  - File watcher (monitors code changes)                │
│  - Context tracker (what user is working on)           │
│  - Query cache (1-hour TTL)                            │
│  Size: ~50MB per user                                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│            Shared Intelligence Layer (Cloud)            │
│  - Supabase PostgreSQL (articles, scores)              │
│  - Redis (hot cache for popular articles)              │
│  - Edge Functions (query processing)                   │
│  - Background jobs (article fetching, cleanup)         │
│  Size: ~650GB total (deduplicated)                     │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              External Data Sources                      │
│  - Hacker News API                                     │
│  - Lobsters RSS                                        │
│  - GitHub Trending                                     │
│  - (Future: Reddit, Dev.to, etc.)                      │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Diagram
```
┌──────────┐
│   User   │
└────┬─────┘
     │ "What should I read?"
     ↓
┌────────────────┐
│ Local Cache?   │ ← Check query_cache (10ms)
└────┬───────────┘
     │ Miss
     ↓
┌────────────────┐
│ Get Context    │ ← Read work_context (50ms)
│ (stack_hash)   │
└────┬───────────┘
     │
     ↓
┌────────────────┐
│ Query Supabase │ ← Pre-scored articles (100ms)
│ article_scores │   WHERE stack_hash = ?
└────┬───────────┘   ORDER BY avg_score DESC
     │               LIMIT 5
     ↓
┌────────────────┐
│ Cache Result   │ ← Store in query_cache (10ms)
└────┬───────────┘
     │
     ↓
┌────────────────┐
│ Return to User │ ← Total: ~170ms
└────────────────┘
```

---

## 🎯 Key Decisions

### ✅ What We Store Locally
- User profile (tiny, ~1KB)
- Work context (7 days)
- Code index (7 days)
- Query cache (1 hour)

### ✅ What We Store in Cloud
- Articles (deduplicated, smart retention)
- Pre-computed scores (collaborative filtering)
- Anonymous analytics

### ❌ What We DON'T Store
- User code (privacy!)
- Personal information
- Long-term history (> 90 days)
- Unpopular articles (< 10 users, > 24h)

---

## 🚀 Next Steps

1. **Implement Supabase schema** (this week)
2. **Build collaborative filtering** (next week)
3. **Add auto-cleanup jobs** (next week)
4. **Load testing** (week 3)
5. **Cost optimization** (ongoing)

This architecture scales to 10M+ users while keeping costs reasonable and performance excellent! 🎉
