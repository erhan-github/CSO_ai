"""
CSO.ai Auto-Intelligence - Zero-setup magic.

Automatically detects your stack on first query with minimal overhead.
Caches profile for 24 hours to ensure instant subsequent queries.

Philosophy: No explicit "analyze_codebase" needed. Just ask and it works.
"""

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cso_ai.intel.technical import TechnicalAnalyzer


@dataclass
class QuickProfile:
    """Lightweight profile for instant queries."""

    path: str
    languages: dict[str, int] = field(default_factory=dict)
    primary_language: str | None = None
    frameworks: list[str] = field(default_factory=list)
    recent_commits: int = 0
    recent_files: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "path": self.path,
            "languages": self.languages,
            "primary_language": self.primary_language,
            "frameworks": self.frameworks,
            "recent_commits": self.recent_commits,
            "recent_files": self.recent_files,
            "focus_areas": self.focus_areas,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuickProfile":
        """Deserialize from dict."""
        return cls(
            path=data["path"],
            languages=data.get("languages", {}),
            primary_language=data.get("primary_language"),
            frameworks=data.get("frameworks", []),
            recent_commits=data.get("recent_commits", 0),
            recent_files=data.get("recent_files", []),
            focus_areas=data.get("focus_areas", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )

    def is_expired(self) -> bool:
        """Check if profile has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def get_hash(self) -> str:
        """Get hash for cache key."""
        key_data = {
            "languages": self.languages,
            "frameworks": self.frameworks,
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()


class AutoIntelligence:
    """
    Auto-detects project intelligence with zero setup.

    Design goals:
    - < 500ms for quick analysis
    - 24-hour cache (balance freshness vs speed)
    - Minimal memory footprint
    - No user intervention required
    """

    def __init__(self):
        """Initialize auto-intelligence."""
        self._cache: dict[str, QuickProfile] = {}
        self._tech_analyzer = TechnicalAnalyzer()

    async def get_or_create_profile(self, path: str | None = None) -> QuickProfile:
        """
        Get cached profile or create new one.

        Args:
            path: Project path. Defaults to current working directory.

        Returns:
            QuickProfile with stack information
        """
        if path is None:
            path = os.getcwd()

        path = str(Path(path).resolve())

        # Check cache
        if path in self._cache:
            profile = self._cache[path]
            if not profile.is_expired():
                return profile

        # Create new profile
        profile = await self._quick_analyze(path)
        self._cache[path] = profile
        return profile

    async def _quick_analyze(self, path: str) -> QuickProfile:
        """
        Quick analysis focusing on essentials.

        Target: < 500ms total
        - Language detection: ~100ms
        - Framework detection: ~100ms
        - Git activity: ~200ms
        """
        root = Path(path)

        if not root.exists() or not root.is_dir():
            # Return empty profile for invalid paths
            return QuickProfile(path=path)

        # Detect languages (fast file counting)
        languages = await self._detect_languages_fast(root)
        primary_language = self._get_primary_language(languages)

        # Detect frameworks from dependencies (fast file reading)
        frameworks = await self._detect_frameworks_fast(root)

        # Get recent git activity (if git repo)
        recent_commits, recent_files, focus_areas = await self._get_git_activity(root)

        return QuickProfile(
            path=path,
            languages=languages,
            primary_language=primary_language,
            frameworks=frameworks,
            recent_commits=recent_commits,
            recent_files=recent_files,
            focus_areas=focus_areas,
        )

    async def _detect_languages_fast(self, root: Path) -> dict[str, int]:
        """Fast language detection (top 5 only)."""
        # Use existing TechnicalAnalyzer but limit scope
        languages = await self._tech_analyzer._detect_languages(root)

        # Return top 5 languages only
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_langs[:5])

    def _get_primary_language(self, languages: dict[str, int]) -> str | None:
        """Get primary language."""
        if not languages:
            return None
        return max(languages.items(), key=lambda x: x[1])[0]

    async def _detect_frameworks_fast(self, root: Path) -> list[str]:
        """Fast framework detection from dependency files."""
        frameworks = []

        # Check package.json
        package_json = root / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    # Common frameworks
                    if "react" in deps:
                        frameworks.append("React")
                    if "vue" in deps:
                        frameworks.append("Vue")
                    if "next" in deps:
                        frameworks.append("Next.js")
                    if "@angular/core" in deps:
                        frameworks.append("Angular")
            except Exception:
                pass

        # Check pyproject.toml / requirements.txt
        pyproject = root / "pyproject.toml"
        requirements = root / "requirements.txt"

        if pyproject.exists():
            try:
                content = pyproject.read_text()
                if "fastapi" in content.lower():
                    frameworks.append("FastAPI")
                if "django" in content.lower():
                    frameworks.append("Django")
                if "flask" in content.lower():
                    frameworks.append("Flask")
            except Exception:
                pass
        elif requirements.exists():
            try:
                content = requirements.read_text().lower()
                if "fastapi" in content:
                    frameworks.append("FastAPI")
                if "django" in content:
                    frameworks.append("Django")
                if "flask" in content:
                    frameworks.append("Flask")
            except Exception:
                pass

        return frameworks[:5]  # Top 5 only

    async def _get_git_activity(self, root: Path) -> tuple[int, list[str], list[str]]:
        """Get recent git activity (last 7 days)."""
        import subprocess

        if not (root / ".git").exists():
            return 0, [], []

        try:
            # Get commit count (last 7 days)
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=7.days.ago"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=2,
            )
            commits = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

            # Get changed files (last 7 days)
            result = subprocess.run(
                ["git", "log", "--name-only", "--pretty=format:", "--since=7.days.ago"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=2,
            )
            files = [f for f in result.stdout.strip().split("\n") if f]
            unique_files = list(set(files))[:10]  # Top 10 unique files

            # Infer focus areas from file paths
            focus_areas = self._infer_focus_from_files(unique_files)

            return commits, unique_files, focus_areas

        except Exception:
            return 0, [], []

    def _infer_focus_from_files(self, files: list[str]) -> list[str]:
        """Infer what developer is working on from changed files."""
        focus = set()

        for file in files:
            path_lower = file.lower()

            # API/Backend
            if any(x in path_lower for x in ["api", "endpoint", "route", "controller"]):
                focus.add("API development")

            # Frontend
            if any(x in path_lower for x in ["component", "page", "view", "ui"]):
                focus.add("Frontend")

            # Auth
            if any(x in path_lower for x in ["auth", "login", "user", "session"]):
                focus.add("Authentication")

            # Database
            if any(x in path_lower for x in ["model", "schema", "migration", "db"]):
                focus.add("Database")

            # Testing
            if any(x in path_lower for x in ["test", "spec"]):
                focus.add("Testing")

            # Config/Infrastructure
            if any(x in path_lower for x in ["config", "docker", "deploy", ".yml", ".yaml"]):
                focus.add("Infrastructure")

        return list(focus)[:3]  # Top 3 focus areas
