# Pre-Launch Audit Template

**Project:** ____________________  
**Target Launch Date:** ____________________  
**Audit Owner:** ____________________  
**Last Updated:** ____________________

---

## How to Use This Template

1. Copy this template for each project
2. Go through each section systematically
3. Mark items as: ✅ Pass | ⚠️ Needs Work | ❌ Fail | N/A
4. Fix all ❌ items before launch
5. Document exceptions for any ⚠️ items you accept

---

## 1. Security Audit

### 1.1 Authentication & Authorization

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1.1.1 | All endpoints require authentication (unless intentionally public) | ☐ | |
| 1.1.2 | JWT tokens have appropriate expiration (<24h for access, <7d for refresh) | ☐ | |
| 1.1.3 | Password requirements meet minimum standards (8+ chars, complexity) | ☐ | |
| 1.1.4 | Leaked password protection enabled (HaveIBeenPwned or similar) | ☐ | |
| 1.1.5 | OTP/magic link expiry is reasonable (<1 hour) | ☐ | |
| 1.1.6 | Failed login attempts are rate-limited | ☐ | |
| 1.1.7 | Session invalidation works on logout | ☐ | |
| 1.1.8 | OAuth callback URLs are properly configured (no localhost in prod) | ☐ | |
| 1.1.9 | OAuth state parameter is validated to prevent CSRF | ☐ | |
| 1.1.10 | Admin endpoints have additional authorization checks | ☐ | |

### 1.2 Data Access Control

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1.2.1 | Row Level Security (RLS) enabled on all user data tables | ☐ | |
| 1.2.2 | RLS policies correctly isolate user data (user can only see own data) | ☐ | |
| 1.2.3 | No overly permissive policies (`USING (true)` for write operations) | ☐ | |
| 1.2.4 | Service role key only used in backend, never exposed to clients | ☐ | |
| 1.2.5 | Public/anon access is intentional and documented for each table | ☐ | |
| 1.2.6 | Views don't use `SECURITY DEFINER` (or it's intentional with documentation) | ☐ | |
| 1.2.7 | Functions have explicit `search_path` set | ☐ | |
| 1.2.8 | API endpoints verify user ownership before returning/modifying data | ☐ | |

### 1.3 Secrets Management

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1.3.1 | No secrets in source code (API keys, passwords, tokens) | ☐ | |
| 1.3.2 | No secrets in git history (check with `git log -p | grep -i secret`) | ☐ | |
| 1.3.3 | Environment variables used for all configuration | ☐ | |
| 1.3.4 | Production secrets are different from development | ☐ | |
| 1.3.5 | Secrets are rotatable without code changes | ☐ | |
| 1.3.6 | `.env` files are in `.gitignore` | ☐ | |
| 1.3.7 | No secrets logged (check log statements for sensitive data) | ☐ | |

### 1.4 Input Validation & Injection Prevention

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1.4.1 | All user inputs are validated (type, length, format) | ☐ | |
| 1.4.2 | Parameterized queries used (no string concatenation for SQL) | ☐ | |
| 1.4.3 | No `eval()`, `exec()`, or dynamic code execution with user input | ☐ | |
| 1.4.4 | File uploads are validated (type, size, content) | ☐ | |
| 1.4.5 | URLs/redirects are validated against allowlist | ☐ | |
| 1.4.6 | JSON/XML parsing has depth limits | ☐ | |
| 1.4.7 | HTML output is escaped to prevent XSS | ☐ | |

### 1.5 Transport Security

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1.5.1 | HTTPS enforced for all endpoints | ☐ | |
| 1.5.2 | HSTS header configured | ☐ | |
| 1.5.3 | TLS 1.2+ required (no legacy protocols) | ☐ | |
| 1.5.4 | CORS configured correctly (not `*` in production for sensitive APIs) | ☐ | |
| 1.5.5 | Secure cookies (HttpOnly, Secure, SameSite flags) | ☐ | |

---

## 2. Infrastructure Audit

### 2.1 Database

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 2.1.1 | Database is on latest stable version with security patches | ☐ | |
| 2.1.2 | Connection pooling configured appropriately | ☐ | |
| 2.1.3 | Database backups enabled (daily minimum) | ☐ | |
| 2.1.4 | Point-in-time recovery (PITR) enabled if available | ☐ | |
| 2.1.5 | Backup restoration tested | ☐ | |
| 2.1.6 | Database credentials are not default | ☐ | |
| 2.1.7 | Database not publicly accessible (only via app/VPN) | ☐ | |

### 2.2 Hosting & Deployment

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 2.2.1 | Production environment is separate from staging/dev | ☐ | |
| 2.2.2 | Deployment process is automated (CI/CD) | ☐ | |
| 2.2.3 | Rollback procedure exists and is tested | ☐ | |
| 2.2.4 | Health check endpoints exist | ☐ | |
| 2.2.5 | Auto-scaling configured (if applicable) | ☐ | |
| 2.2.6 | Resource limits set (memory, CPU) | ☐ | |
| 2.2.7 | Container images are from trusted sources | ☐ | |

### 2.3 DNS & Networking

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 2.3.1 | Custom domain configured | ☐ | |
| 2.3.2 | SSL certificate valid and auto-renewing | ☐ | |
| 2.3.3 | DNS TTL appropriate for failover | ☐ | |
| 2.3.4 | CDN configured for static assets (if applicable) | ☐ | |

---

## 3. Performance Audit

### 3.1 Database Performance

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 3.1.1 | Indexes exist for all foreign keys | ☐ | |
| 3.1.2 | Indexes exist for commonly queried columns | ☐ | |
| 3.1.3 | No N+1 query patterns | ☐ | |
| 3.1.4 | Large queries are paginated | ☐ | |
| 3.1.5 | Unused indexes identified and removed | ☐ | |
| 3.1.6 | Query execution plans reviewed for slow queries | ☐ | |
| 3.1.7 | RLS policies optimized (auth functions wrapped in SELECT) | ☐ | |

### 3.2 API Performance

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 3.2.1 | Response times acceptable (<500ms P95 for reads) | ☐ | |
| 3.2.2 | Rate limiting configured | ☐ | |
| 3.2.3 | Caching implemented where appropriate | ☐ | |
| 3.2.4 | Large payloads are compressed | ☐ | |
| 3.2.5 | Async operations used for long-running tasks | ☐ | |
| 3.2.6 | Connection pooling for external services | ☐ | |

### 3.3 Frontend Performance

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 3.3.1 | Assets are minified and compressed | ☐ | |
| 3.3.2 | Images are optimized (WebP, lazy loading) | ☐ | |
| 3.3.3 | Code splitting implemented | ☐ | |
| 3.3.4 | First Contentful Paint <2s | ☐ | |
| 3.3.5 | Largest Contentful Paint <4s | ☐ | |
| 3.3.6 | No memory leaks (check with DevTools) | ☐ | |

---

## 4. Reliability Audit

### 4.1 Error Handling

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 4.1.1 | All async functions have try/catch | ☐ | |
| 4.1.2 | Errors are logged with context (user, request ID, stack trace) | ☐ | |
| 4.1.3 | User-facing errors are generic (no stack traces exposed) | ☐ | |
| 4.1.4 | Exception chaining preserves original error context | ☐ | |
| 4.1.5 | Graceful degradation for non-critical failures | ☐ | |
| 4.1.6 | Retry logic for transient failures (with backoff) | ☐ | |

### 4.2 Monitoring & Alerting

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 4.2.1 | Error tracking configured (Sentry, etc.) | ☐ | |
| 4.2.2 | Uptime monitoring configured | ☐ | |
| 4.2.3 | Alerts configured for error rate spikes | ☐ | |
| 4.2.4 | Alerts configured for latency spikes | ☐ | |
| 4.2.5 | On-call/escalation process defined | ☐ | |
| 4.2.6 | Runbooks exist for common issues | ☐ | |

### 4.3 Logging

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 4.3.1 | Structured logging implemented (JSON) | ☐ | |
| 4.3.2 | Log levels used appropriately (DEBUG, INFO, WARN, ERROR) | ☐ | |
| 4.3.3 | Request IDs for tracing | ☐ | |
| 4.3.4 | Sensitive data not logged (passwords, tokens, PII) | ☐ | |
| 4.3.5 | Log retention policy defined | ☐ | |

---

## 5. Code Quality Audit

### 5.1 Code Health

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 5.1.1 | No linter errors | ☐ | |
| 5.1.2 | Type hints/annotations on all functions | ☐ | |
| 5.1.3 | No hardcoded values (use constants/config) | ☐ | |
| 5.1.4 | No dead code or unused imports | ☐ | |
| 5.1.5 | No TODO/FIXME items that block launch | ☐ | |
| 5.1.6 | Functions are <50 lines | ☐ | |
| 5.1.7 | Files are <500 lines | ☐ | |

### 5.2 Testing

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 5.2.1 | Critical paths have test coverage | ☐ | |
| 5.2.2 | Auth flows are tested | ☐ | |
| 5.2.3 | Payment flows are tested (if applicable) | ☐ | |
| 5.2.4 | Edge cases are handled | ☐ | |
| 5.2.5 | Tests pass in CI | ☐ | |

### 5.3 Dependencies

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 5.3.1 | Dependencies are up to date | ☐ | |
| 5.3.2 | No known vulnerabilities (npm audit, pip-audit) | ☐ | |
| 5.3.3 | Lock files committed (package-lock.json, etc.) | ☐ | |
| 5.3.4 | Dependency versions are pinned | ☐ | |

---

## 6. User Experience Audit

### 6.1 Functionality

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 6.1.1 | All user flows work end-to-end | ☐ | |
| 6.1.2 | Onboarding/signup flow is smooth | ☐ | |
| 6.1.3 | Core features work on all target platforms | ☐ | |
| 6.1.4 | Offline behavior is handled gracefully | ☐ | |
| 6.1.5 | Deep links work correctly | ☐ | |

### 6.2 Error States

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 6.2.1 | Loading states for all async operations | ☐ | |
| 6.2.2 | Error messages are user-friendly | ☐ | |
| 6.2.3 | Empty states are handled | ☐ | |
| 6.2.4 | Network errors show retry option | ☐ | |
| 6.2.5 | 404 pages exist and are helpful | ☐ | |

### 6.3 Accessibility

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 6.3.1 | Color contrast meets WCAG AA | ☐ | |
| 6.3.2 | All interactive elements are keyboard accessible | ☐ | |
| 6.3.3 | Screen reader labels on icons/images | ☐ | |
| 6.3.4 | Focus indicators are visible | ☐ | |
| 6.3.5 | Text is resizable without breaking layout | ☐ | |

---

## 7. Legal & Compliance Audit

### 7.1 Privacy

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 7.1.1 | Privacy policy exists and is linked | ☐ | |
| 7.1.2 | Terms of service exists and is linked | ☐ | |
| 7.1.3 | Cookie consent implemented (if required by region) | ☐ | |
| 7.1.4 | Data deletion/export capability (GDPR if applicable) | ☐ | |
| 7.1.5 | Only necessary data is collected | ☐ | |

### 7.2 Third-Party Services

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 7.2.1 | Analytics configured with privacy settings | ☐ | |
| 7.2.2 | Third-party SDKs are from trusted sources | ☐ | |
| 7.2.3 | Data processing agreements in place (if required) | ☐ | |

### 7.3 App Store Requirements (Mobile)

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 7.3.1 | App store descriptions are accurate | ☐ | |
| 7.3.2 | Screenshots reflect actual UI | ☐ | |
| 7.3.3 | Age rating is appropriate | ☐ | |
| 7.3.4 | In-app purchases are properly configured | ☐ | |
| 7.3.5 | Required permissions are justified | ☐ | |

---

## 8. Business Continuity Audit

### 8.1 Disaster Recovery

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 8.1.1 | Data backups are in different region | ☐ | |
| 8.1.2 | Recovery time objective (RTO) defined | ☐ | |
| 8.1.3 | Recovery point objective (RPO) defined | ☐ | |
| 8.1.4 | Disaster recovery procedure documented | ☐ | |
| 8.1.5 | DR procedure tested | ☐ | |

### 8.2 Vendor Dependencies

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 8.2.1 | Critical vendor SLAs reviewed | ☐ | |
| 8.2.2 | Fallback plan for vendor outages | ☐ | |
| 8.2.3 | Vendor costs projected for scale | ☐ | |

---

## Summary

### Audit Results

| Category | Pass | Needs Work | Fail | N/A |
|----------|------|------------|------|-----|
| 1. Security | /25 | /25 | /25 | /25 |
| 2. Infrastructure | /14 | /14 | /14 | /14 |
| 3. Performance | /18 | /18 | /18 | /18 |
| 4. Reliability | /17 | /17 | /17 | /17 |
| 5. Code Quality | /15 | /15 | /15 | /15 |
| 6. User Experience | /15 | /15 | /15 | /15 |
| 7. Legal & Compliance | /11 | /11 | /11 | /11 |
| 8. Business Continuity | /8 | /8 | /8 | /8 |
| **TOTAL** | /123 | /123 | /123 | /123 |

### Launch Decision

| Criteria | Threshold | Status |
|----------|-----------|--------|
| Security fails | 0 | ☐ |
| Infrastructure fails | 0 | ☐ |
| Reliability fails | 0 | ☐ |
| Total fails | <5 | ☐ |
| Total needs work | <15 | ☐ |

**Launch Approved:** ☐ Yes / ☐ No

**Approved By:** ____________________  
**Date:** ____________________

---

## Appendix: Quick Commands

### Security Scans
```bash
# Check for secrets in code
git log -p | grep -iE "(password|secret|api_key|token)" | head -50

# Check for eval/exec (Python)
grep -r "eval\|exec\|os.system" --include="*.py"

# Check for SQL injection patterns
grep -r "f\".*SELECT\|f\".*INSERT\|f\".*UPDATE" --include="*.py"
```

### Dependency Audits
```bash
# Node.js
npm audit

# Python
pip-audit

# Go
go list -m all | nancy sleuth
```

### Database Checks (PostgreSQL/Supabase)
```sql
-- Tables without RLS
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename NOT IN (
  SELECT tablename FROM pg_policies WHERE schemaname = 'public'
);

-- Overly permissive policies
SELECT tablename, policyname, qual, with_check
FROM pg_policies 
WHERE qual = 'true' OR with_check = 'true';

-- Missing indexes on foreign keys
SELECT conrelid::regclass AS table_name,
       conname AS constraint_name
FROM pg_constraint
WHERE contype = 'f'
AND NOT EXISTS (
  SELECT 1 FROM pg_index
  WHERE indrelid = conrelid
  AND conkey <@ indkey
);
```

### Performance Baseline
```bash
# API response times
curl -w "@curl-format.txt" -o /dev/null -s "https://api.example.com/health"

# Load test
ab -n 1000 -c 10 https://api.example.com/health
```

---

*Template Version: 1.0*  
*Created: January 2026*
