# Documentation Discipline Plan
> Palantir-Level Documentation Standards for Side Intelligence

---

## I. DOCUMENTATION STRUCTURE

### Current Structure

```
side/backend/src/side/intel/
├── README.md                          # Main intelligence overview
├── query_analyzer/
│   └── README.md                      # Query analysis docs
├── feeds/
│   └── README.md                      # Feed registry docs
├── trending/
│   └── README.md                      # Trending APIs docs
├── api/
│   └── README.md                      # Unified API docs
└── rss/
    └── README.md                      # RSS fetcher docs (TODO)
```

### Documentation Hierarchy

```
Level 1: Main README (side/intel/README.md)
    ↓
Level 2: Feature READMEs (query_analyzer/, feeds/, etc.)
    ↓
Level 3: Code docstrings (inline documentation)
```

---

## II. README STANDARDS

### Required Sections

Every README must have:

1. **Title + Tagline**
   ```markdown
   # Feature Name
   > One-line description of purpose
   ```

2. **Purpose**
   - What problem does this solve?
   - Why does it exist?

3. **Usage**
   - Quick start code example
   - Most common use case

4. **Examples**
   - 3-5 real-world examples
   - Input → Output format

5. **API Reference**
   - Function signatures
   - Parameters
   - Return values

6. **Testing**
   - How to run tests
   - Expected output

7. **Performance** (if applicable)
   - Speed metrics
   - Success rates
   - Cost

### Optional Sections

- **Advanced Usage**: For power users
- **Error Handling**: How failures are handled
- **Dependencies**: What it relies on
- **See Also**: Links to related docs

---

## III. CONTENT GUIDELINES

### Writing Style

✅ **DO**:
- Use active voice
- Be concise and direct
- Include code examples
- Show real output
- Use tables for comparisons
- Link to related docs

❌ **DON'T**:
- Use passive voice
- Be verbose or redundant
- Include outdated strategies
- Show hypothetical examples
- Duplicate content across READMEs

### Code Examples

All code examples must:
- ✅ Be runnable (copy-paste works)
- ✅ Show actual output
- ✅ Use realistic data
- ✅ Include imports

```python
# ✅ GOOD
from side.intel.api import IntelligenceAPI

api = IntelligenceAPI()
signals = await api.get_signals("What's trending?")
# Returns: [{'title': '...', 'source': 'github'}, ...]

# ❌ BAD
api.get_signals(query)  # No imports, no output
```

---

## IV. DEPRECATED DOCUMENTATION

### Files to Archive

Move to `docs/archive/`:

1. **Old Strategy Docs**:
   - `INTELLIGENCE_CURATION_PLAN.md` (superseded by zero-storage)
   - `MVP_INTELLIGENCE_STRATEGY.md` (superseded by unified API)
   - `INTELLIGENCE_IMPLEMENTATION.md` (superseded by READMEs)

2. **Redundant Docs**:
   - Any doc that duplicates README content
   - Old implementation plans
   - Superseded walkthroughs

### Archive Structure

```
docs/archive/
├── 2026-01-18/
│   ├── INTELLIGENCE_CURATION_PLAN.md
│   ├── MVP_INTELLIGENCE_STRATEGY.md
│   └── INTELLIGENCE_IMPLEMENTATION.md
└── README.md  # Index of archived docs
```

---

## V. MAINTENANCE PROCEDURES

### Weekly Review

Every week:
1. Check all code examples still work
2. Update performance metrics
3. Fix broken links
4. Update feed counts

### Monthly Audit

Every month:
1. Review for outdated content
2. Archive superseded docs
3. Update API references
4. Add new examples

### On Feature Changes

When code changes:
1. Update affected READMEs immediately
2. Update code examples
3. Update performance metrics
4. Add migration guide if breaking

---

## VI. DOCUMENTATION CHECKLIST

### For New Features

- [ ] Create feature README in appropriate directory
- [ ] Add to main intelligence README
- [ ] Include 3+ code examples
- [ ] Add testing instructions
- [ ] Document performance metrics
- [ ] Link from related READMEs

### For Feature Updates

- [ ] Update feature README
- [ ] Update code examples
- [ ] Update performance metrics
- [ ] Add changelog entry
- [ ] Archive old docs if superseded

### For Deprecations

- [ ] Mark as deprecated in README
- [ ] Add migration guide
- [ ] Set removal date
- [ ] Archive after removal

---

## VII. CURRENT DOCUMENTATION STATUS

### ✅ Complete

- [x] Main intelligence README
- [x] Query analyzer README
- [x] Feed registry README
- [x] Trending APIs README
- [x] Unified API README

### 🚧 In Progress

- [ ] RSS fetcher README
- [ ] Text analysis README
- [ ] Strategic filtering README

### 📦 To Archive

- [ ] `INTELLIGENCE_CURATION_PLAN.md`
- [ ] `MVP_INTELLIGENCE_STRATEGY.md`
- [ ] `INTELLIGENCE_IMPLEMENTATION.md`
- [ ] `EXTERNAL_INTEL_RESEARCH.md` (keep as reference)

---

## VIII. DOCUMENTATION METRICS

### Quality Metrics

| Metric | Target | Current |
| :--- | :---: | :---: |
| **Code examples** | 3+ per README | ✅ 3-5 |
| **Broken links** | 0 | ✅ 0 |
| **Outdated content** | <10% | ✅ 0% |
| **Missing READMEs** | 0 | 🚧 2 |

### Coverage Metrics

| Component | Has README | Has Examples | Has Tests |
| :--- | :---: | :---: | :---: |
| Query Analyzer | ✅ | ✅ | ✅ |
| Feed Registry | ✅ | ✅ | ✅ |
| Trending APIs | ✅ | ✅ | ✅ |
| Unified API | ✅ | ✅ | ✅ |
| RSS Fetcher | ❌ | ✅ | ✅ |
| Text Analysis | ❌ | ✅ | ✅ |

---

## IX. PALANTIR-LEVEL STANDARDS

### Principles

1. **Clarity Over Cleverness**
   - Simple, direct language
   - No jargon unless necessary
   - Explain acronyms

2. **Examples Over Explanations**
   - Show, don't tell
   - Real code, real output
   - Copy-paste ready

3. **Maintenance Over Creation**
   - Keep docs updated
   - Archive old content
   - Review regularly

4. **Discoverability Over Completeness**
   - Clear hierarchy
   - Good navigation
   - Cross-references

### Quality Bar

Every README must:
- ✅ Be readable in <5 minutes
- ✅ Have runnable examples
- ✅ Show actual output
- ✅ Link to related docs
- ✅ Include testing instructions

---

## X. IMPLEMENTATION TIMELINE

### Week 1 (Current)
- [x] Create main intelligence README
- [x] Create query analyzer README
- [x] Create feed registry README
- [x] Create trending APIs README
- [x] Create unified API README

### Week 2
- [ ] Create RSS fetcher README
- [ ] Create text analysis README
- [ ] Archive old strategy docs
- [ ] Add migration guides

### Week 3
- [ ] Review all READMEs
- [ ] Fix broken examples
- [ ] Update performance metrics
- [ ] Add advanced usage sections

---

## XI. SUCCESS CRITERIA

Documentation is successful when:

1. **New developers** can use the system in <30 minutes
2. **Code examples** all work without modification
3. **Performance metrics** are up-to-date
4. **No redundant** content across docs
5. **Archive** contains all old strategies

---

**End of Documentation Discipline Plan // Side Alpha-0**
