"""
CSO.ai Simplified Database - Fast, focused storage with auto-cleanup.

Simplified from 5 tables to 4 tables:
1. profiles - Lightweight auto-detected profiles
2. articles - Articles with embedded score cache
3. work_context - What user is working on (7-day retention)
4. query_cache - Pre-computed results (1-hour retention)

Philosophy: Keep it simple, keep it fast, auto-cleanup old data.
"""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Generator

from cso_ai.intel.market import Article


class SimplifiedDatabase:
    """
    Simplified SQLite storage for CSO.ai with auto-cleanup.

    Design goals:
    - 4 tables (profiles, articles, work_context, query_cache)
    - Smart caching (articles 1hr, scores forever, queries 1hr)
    - Auto-cleanup (7-day retention for context/index)
    - Fast queries with proper indexes
    - Minimal overhead
    """

    def __init__(self, db_path: str | Path | None = None):
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.cso-ai/local.db
        """
        if db_path is None:
            db_path = Path.home() / ".cso-ai" / "local.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize simplified database schema."""
        with self._connection() as conn:
            # Profiles table (lightweight, auto-detected)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    path TEXT PRIMARY KEY,
                    languages JSON NOT NULL,
                    primary_language TEXT,
                    frameworks JSON,
                    recent_commits INTEGER DEFAULT 0,
                    recent_files JSON,
                    focus_areas JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_profiles_updated 
                ON profiles(updated_at DESC)
            """)

            # Articles table (with embedded score cache)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    description TEXT,
                    author TEXT,
                    score INTEGER,
                    published_at TIMESTAMP,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags JSON,
                    scores JSON
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_fetched 
                ON articles(fetched_at DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_source 
                ON articles(source, fetched_at DESC)
            """)

            # Work context table (what user is working on)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS work_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    focus_area TEXT,
                    recent_files JSON,
                    recent_commits JSON,
                    current_branch TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    confidence FLOAT DEFAULT 0.0
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_work_context_path 
                ON work_context(project_path, detected_at DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_work_context_expires 
                ON work_context(expires_at)
            """)

            # Query cache table (pre-computed results)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_cache (
                    query_hash TEXT PRIMARY KEY,
                    query_type TEXT NOT NULL,
                    result JSON NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_cache_expires 
                ON query_cache(expires_at)
            """)

            conn.commit()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # =========================================================================
    # Profile Operations
    # =========================================================================

    def save_profile(
        self,
        path: str,
        languages: dict[str, int],
        primary_language: str | None = None,
        frameworks: list[str] | None = None,
        recent_commits: int = 0,
        recent_files: list[str] | None = None,
        focus_areas: list[str] | None = None,
    ) -> None:
        """Save or update a profile."""
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO profiles (
                    path, languages, primary_language, frameworks,
                    recent_commits, recent_files, focus_areas, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    languages = excluded.languages,
                    primary_language = excluded.primary_language,
                    frameworks = excluded.frameworks,
                    recent_commits = excluded.recent_commits,
                    recent_files = excluded.recent_files,
                    focus_areas = excluded.focus_areas,
                    updated_at = excluded.updated_at
                """,
                (
                    path,
                    json.dumps(languages),
                    primary_language,
                    json.dumps(frameworks or []),
                    recent_commits,
                    json.dumps(recent_files or []),
                    json.dumps(focus_areas or []),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()

    def get_profile(self, path: str) -> dict[str, Any] | None:
        """Get a profile by path."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE path = ?",
                (path,),
            ).fetchone()

            if row is None:
                return None

            return {
                "path": row["path"],
                "languages": json.loads(row["languages"]),
                "primary_language": row["primary_language"],
                "frameworks": json.loads(row["frameworks"]) if row["frameworks"] else [],
                "recent_commits": row["recent_commits"],
                "recent_files": json.loads(row["recent_files"]) if row["recent_files"] else [],
                "focus_areas": json.loads(row["focus_areas"]) if row["focus_areas"] else [],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }

    def get_latest_profile(self) -> dict[str, Any] | None:
        """Get most recently updated profile."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM profiles ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()

            if row is None:
                return None

            return {
                "path": row["path"],
                "languages": json.loads(row["languages"]),
                "primary_language": row["primary_language"],
                "frameworks": json.loads(row["frameworks"]) if row["frameworks"] else [],
                "recent_commits": row["recent_commits"],
                "recent_files": json.loads(row["recent_files"]) if row["recent_files"] else [],
                "focus_areas": json.loads(row["focus_areas"]) if row["focus_areas"] else [],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }

    # =========================================================================
    # Article Operations (with score caching)
    # =========================================================================

    def save_article(self, article: Article) -> None:
        """Save or update an article."""
        with self._connection() as conn:
            # Get existing scores if article exists
            existing = conn.execute(
                "SELECT scores FROM articles WHERE id = ?",
                (article.id,),
            ).fetchone()

            existing_scores = {}
            if existing and existing["scores"]:
                existing_scores = json.loads(existing["scores"])

            conn.execute(
                """
                INSERT INTO articles (
                    id, title, url, source, description, author,
                    score, published_at, fetched_at, tags, scores
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description,
                    fetched_at = excluded.fetched_at,
                    scores = excluded.scores
                """,
                (
                    article.id,
                    article.title,
                    article.url,
                    article.source,
                    article.description,
                    article.author,
                    article.score,
                    article.published_at.isoformat() if article.published_at else None,
                    article.fetched_at.isoformat(),
                    json.dumps(article.tags),
                    json.dumps(existing_scores),
                ),
            )
            conn.commit()

    def get_cached_articles(self, max_age_hours: int = 1, limit: int = 100) -> list[Article]:
        """
        Get cached articles if fresh enough.

        Args:
            max_age_hours: Maximum age in hours (default 1 hour)
            limit: Maximum number of articles to return

        Returns:
            List of cached articles, or empty list if cache is stale
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM articles 
                WHERE fetched_at > ?
                ORDER BY fetched_at DESC
                LIMIT ?
                """,
                (cutoff.isoformat(), limit),
            ).fetchall()

            articles = []
            for row in rows:
                article = Article(
                    id=row["id"],
                    title=row["title"],
                    url=row["url"],
                    source=row["source"],
                    description=row["description"],
                    author=row["author"],
                    score=row["score"],
                    published_at=datetime.fromisoformat(row["published_at"]) if row["published_at"] else None,
                    fetched_at=datetime.fromisoformat(row["fetched_at"]),
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                )
                articles.append(article)

            return articles

    def save_article_score(
        self,
        article_id: str,
        profile_hash: str,
        score: float,
        reason: str,
    ) -> None:
        """
        Cache article score for a specific profile.

        Args:
            article_id: Article ID
            profile_hash: Hash of the profile (for cache key)
            score: Relevance score (0-100)
            reason: Reasoning for the score
        """
        with self._connection() as conn:
            # Get existing scores
            row = conn.execute(
                "SELECT scores FROM articles WHERE id = ?",
                (article_id,),
            ).fetchone()

            scores = {}
            if row and row["scores"]:
                scores = json.loads(row["scores"])

            # Add new score
            scores[profile_hash] = {
                "score": score,
                "reason": reason,
                "cached_at": datetime.now(timezone.utc).isoformat(),
            }

            # Update article
            conn.execute(
                "UPDATE articles SET scores = ? WHERE id = ?",
                (json.dumps(scores), article_id),
            )
            conn.commit()

    def get_article_score(
        self,
        article_id: str,
        profile_hash: str,
    ) -> dict[str, Any] | None:
        """
        Get cached score for article + profile combo.

        Args:
            article_id: Article ID
            profile_hash: Hash of the profile

        Returns:
            Cached score dict or None if not found
        """
        with self._connection() as conn:
            row = conn.execute(
                "SELECT scores FROM articles WHERE id = ?",
                (article_id,),
            ).fetchone()

            if not row or not row["scores"]:
                return None

            scores = json.loads(row["scores"])
            return scores.get(profile_hash)

    def get_article_count(self) -> int:
        """Get total article count."""
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM articles").fetchone()
            return row["count"] if row else 0

    def get_profile_count(self) -> int:
        """Get total profile count."""
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM profiles").fetchone()
            return row["count"] if row else 0

    # =========================================================================
    # Work Context Operations (7-day retention)
    # =========================================================================

    def save_work_context(
        self,
        project_path: str,
        focus_area: str,
        recent_files: list[str],
        recent_commits: list[dict[str, Any]],
        current_branch: str | None = None,
        confidence: float = 0.8,
    ) -> None:
        """
        Save current work context.

        Args:
            project_path: Path to project
            focus_area: Detected focus area (e.g., "authentication", "api")
            recent_files: Recently edited files
            recent_commits: Recent commits
            current_branch: Current git branch
            confidence: Confidence in focus area detection (0-1)
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO work_context (
                    project_path, focus_area, recent_files, recent_commits,
                    current_branch, expires_at, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_path,
                    focus_area,
                    json.dumps(recent_files),
                    json.dumps(recent_commits),
                    current_branch,
                    expires_at.isoformat(),
                    confidence,
                ),
            )
            conn.commit()

    def get_latest_work_context(self, project_path: str) -> dict[str, Any] | None:
        """Get most recent work context for project."""
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM work_context 
                WHERE project_path = ? AND expires_at > ?
                ORDER BY detected_at DESC 
                LIMIT 1
                """,
                (project_path, datetime.now(timezone.utc).isoformat()),
            ).fetchone()

            if row is None:
                return None

            return {
                "focus_area": row["focus_area"],
                "recent_files": json.loads(row["recent_files"]) if row["recent_files"] else [],
                "recent_commits": json.loads(row["recent_commits"]) if row["recent_commits"] else [],
                "current_branch": row["current_branch"],
                "detected_at": row["detected_at"],
                "confidence": row["confidence"],
            }

    # =========================================================================
    # Query Cache Operations (1-hour retention)
    # =========================================================================

    def save_query_cache(
        self,
        query_type: str,
        query_params: dict[str, Any],
        result: Any,
        ttl_hours: int = 1,
    ) -> None:
        """
        Cache query result.

        Args:
            query_type: Type of query (e.g., "read", "analyze_url")
            query_params: Query parameters (for hash)
            result: Result to cache
            ttl_hours: Time to live in hours
        """
        # Generate hash from query type + params
        query_str = f"{query_type}:{json.dumps(query_params, sort_keys=True)}"
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]

        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO query_cache (query_hash, query_type, result, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(query_hash) DO UPDATE SET
                    result = excluded.result,
                    cached_at = CURRENT_TIMESTAMP,
                    expires_at = excluded.expires_at
                """,
                (query_hash, query_type, json.dumps(result), expires_at.isoformat()),
            )
            conn.commit()

    def get_query_cache(
        self,
        query_type: str,
        query_params: dict[str, Any],
    ) -> Any | None:
        """
        Get cached query result.

        Args:
            query_type: Type of query
            query_params: Query parameters

        Returns:
            Cached result or None if not found/expired
        """
        # Generate hash
        query_str = f"{query_type}:{json.dumps(query_params, sort_keys=True)}"
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT result FROM query_cache 
                WHERE query_hash = ? AND expires_at > ?
                """,
                (query_hash, datetime.now(timezone.utc).isoformat()),
            ).fetchone()

            if row is None:
                return None

            return json.loads(row["result"])

    def invalidate_query_cache(self, query_type: str | None = None) -> int:
        """
        Invalidate query cache.

        Args:
            query_type: Specific query type to invalidate, or None for all

        Returns:
            Number of entries deleted
        """
        with self._connection() as conn:
            if query_type:
                cursor = conn.execute(
                    "DELETE FROM query_cache WHERE query_type = ?",
                    (query_type,),
                )
            else:
                cursor = conn.execute("DELETE FROM query_cache")

            conn.commit()
            return cursor.rowcount

    # =========================================================================
    # Auto-Cleanup Operations
    # =========================================================================

    def cleanup_expired_data(self) -> dict[str, int]:
        """
        Clean up expired data (7-day retention for context, 1-hour for cache).

        Returns:
            Dict with counts of deleted records per table
        """
        now = datetime.now(timezone.utc).isoformat()
        deleted = {}

        with self._connection() as conn:
            # Clean up expired work context
            cursor = conn.execute(
                "DELETE FROM work_context WHERE expires_at < ?",
                (now,),
            )
            deleted["work_context"] = cursor.rowcount

            # Clean up expired query cache
            cursor = conn.execute(
                "DELETE FROM query_cache WHERE expires_at < ?",
                (now,),
            )
            deleted["query_cache"] = cursor.rowcount

            # Clean up old articles (> 7 days)
            cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            cursor = conn.execute(
                "DELETE FROM articles WHERE fetched_at < ?",
                (cutoff,),
            )
            deleted["articles"] = cursor.rowcount

            conn.commit()

        return deleted

    def get_database_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        with self._connection() as conn:
            stats = {}

            # Table counts
            for table in ["profiles", "articles", "work_context", "query_cache"]:
                row = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                stats[f"{table}_count"] = row["count"] if row else 0

            # Database size
            stats["db_size_bytes"] = self.db_path.stat().st_size if self.db_path.exists() else 0
            stats["db_size_mb"] = stats["db_size_bytes"] / (1024 * 1024)

            return stats
