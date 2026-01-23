# Side Architecture Rules
The "Sentinel" (ArchitectureProbe) enforces these high-level invariant rules.

## Core Pillars
1.  **Local-First / Zero Data Retention**:
    -   NEVER import cloud SDKs (boto3, google-cloud, supabase) in `simple_db.py` or `local_storage`.
    -   All sensitive data must stay in SQLite or the user's machines.

## Module Boundaries
2.  **Thin Routes**:
    -   `web/app/api` routes should NOT contain complex logic. They must delegate to `lib/` or `backend/`.
    
3.  **No Cyclic Dependencies (General)**:
    -   `utils` should never import from `core`.

## Specific Limits
4.  **Complexity Cap**:
    -   No single function should exceed 100 lines of code (except tests).
    -   Use `llm_client` for all AI calls, never raw `openai` or `anthropic` client instantiation.
