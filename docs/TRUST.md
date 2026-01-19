# Side Security & Trust

> **One Simple Rule: We never see, read, or store your code.**

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR MACHINE                            │
│  ┌──────────────┐                                          │
│  │ Side MCP     │ ← Reads your local files                 │
│  │ (local)      │ ← Stores history in .side/               │
│  └──────────────┘                                          │
│         │                                                   │
└─────────│───────────────────────────────────────────────────┘
          │ Code snippets (for analysis only)
          ▼
┌─────────────────────────────────────────────────────────────┐
│                     SIDE API                                │
│                                                             │
│  • Stateless proxy                                         │
│  • Zero retention                                          │
│  • No logging of code                                      │
│  • We don't care who you are                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                     LLM PROVIDER                            │
│                                                             │
│  • Groq (default)                                          │
│  • Analysis only                                           │
│  • No training on your code                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## What We Store

| ❌ Never Stored | ✅ Stored |
|-----------------|-----------|
| Your source code | Your email |
| File paths | Token usage |
| Git history | Account created date |
| Secrets/credentials | |
| Project names | |

## Security Measures

| Layer | Protection |
|-------|------------|
| **Transport** | TLS 1.3 encryption |
| **Storage** | AES-256 (Supabase) |
| **Auth** | Bearer tokens, rate limiting |
| **API** | Stateless, zero retention |

## Compliance

| Standard | Status |
|----------|--------|
| GDPR | ✅ Compliant |
| Privacy Policy | ✅ Published |
| Vulnerability Disclosure | ✅ Active |
| SOC 2 Type II | 🎯 Post-funding |
| ISO 27001 | 🎯 Post-funding |

## Report a Vulnerability

Email: **security@side.ai**

We respond within 24 hours. See [SECURITY.md](/SECURITY.md) for details.

## Why This Matters

We're an intelligence layer, not a surveillance layer.

Your code is your competitive advantage. We help you improve it without ever seeing it ourselves.

---

**Questions?** Email security@side.ai
