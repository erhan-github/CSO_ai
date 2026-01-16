"""
CSO.ai Market Intelligence.

Gathers and analyzes market information:
- Tech trends and news
- Competitor signals
- Industry developments
- Opportunity detection
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx


@dataclass
class Article:
    """Represents a piece of content from any source."""

    id: str
    title: str
    url: str
    source: str  # hackernews, lobsters, github, etc.
    description: str | None = None
    author: str | None = None
    score: int | None = None  # Source-specific score (HN points, stars, etc.)
    published_at: datetime | None = None
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    tags: list[str] = field(default_factory=list)

    # Relevance scoring (added later)
    relevance_score: float | None = None
    relevance_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize article."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "description": self.description,
            "author": self.author,
            "score": self.score,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "fetched_at": self.fetched_at.isoformat(),
            "tags": self.tags,
            "relevance_score": self.relevance_score,
            "relevance_reason": self.relevance_reason,
        }


class MarketAnalyzer:
    """
    Analyzes market trends and gathers intelligence.

    Uses Groq (Llama 3.3 70B) for smart article scoring.

    Responsibilities:
    - Fetch content from multiple sources
    - Score relevance against profile
    - Identify trends and patterns
    - Surface actionable opportunities
    """

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self._articles: list[Article] = []
        self._strategist = None

    def _get_strategist(self):
        """Lazy load the strategist."""
        if self._strategist is None:
            from cso_ai.intel.strategist import Strategist
            self._strategist = Strategist()
        return self._strategist

    async def fetch_all_sources(self, days: int = 7) -> list[Article]:
        """
        Fetch articles from all sources.

        Args:
            days: Number of days to look back

        Returns:
            List of fetched articles
        """
        from cso_ai.sources import HackerNewsSource, LobstersSource, GitHubSource

        all_articles = []

        # Fetch from each source
        sources = [
            ("HackerNews", HackerNewsSource()),
            ("Lobsters", LobstersSource()),
            ("GitHub", GitHubSource()),
        ]

        for name, source in sources:
            try:
                articles = await source.fetch(days=days, limit=30)
                all_articles.extend(articles)
                await source.close()
            except Exception as e:
                # Log but continue with other sources
                print(f"Error fetching from {name}: {e}")
                continue

        self._articles = all_articles
        return all_articles

    async def score_articles(
        self,
        articles: list[Article],
        profile: dict[str, Any],
    ) -> list[Article]:
        """
        Score articles for relevance against a profile.

        Uses Groq LLM if available, otherwise falls back to heuristics.

        Args:
            articles: Articles to score
            profile: Intelligence profile

        Returns:
            Articles with relevance scores, sorted by relevance
        """
        strategist = self._get_strategist()

        for article in articles:
            score, reason = await strategist.score_article(
                title=article.title,
                url=article.url,
                description=article.description,
                profile=profile,
            )
            article.relevance_score = score
            article.relevance_reason = reason

        # Sort by relevance
        articles.sort(key=lambda a: a.relevance_score or 0, reverse=True)
        return articles

    def _format_profile(self, profile: dict[str, Any]) -> str:
        """Format profile for scoring prompt."""
        lines = []

        tech = profile.get("technical", {})
        if tech.get("primary_language"):
            lines.append(f"Language: {tech['primary_language']}")
        if tech.get("frameworks"):
            lines.append(f"Frameworks: {', '.join(tech['frameworks'])}")

        biz = profile.get("business", {})
        if biz.get("domain"):
            lines.append(f"Domain: {biz['domain']}")
        if biz.get("product_type"):
            lines.append(f"Product: {biz['product_type']}")
        if biz.get("integrations"):
            lines.append(f"Uses: {', '.join(biz['integrations'])}")

        return "\n".join(lines) if lines else "General software project"

    async def get_tech_articles(
        self,
        profile: dict[str, Any],
        days: int = 7,
        limit: int = 10,
    ) -> list[Article]:
        """Get tech-focused articles scored for the profile."""
        articles = await self.fetch_all_sources(days)
        scored = await self.score_articles(articles, profile)
        return scored[:limit]

    async def get_business_articles(
        self,
        profile: dict[str, Any],
        days: int = 7,
        limit: int = 10,
    ) -> list[Article]:
        """Get business-focused articles."""
        # For now, same as tech but could filter differently
        articles = await self.fetch_all_sources(days)
        scored = await self.score_articles(articles, profile)

        # Prefer business-related content
        business_keywords = ["startup", "funding", "business", "market", "growth", "revenue"]
        for article in scored:
            text = f"{article.title} {article.description or ''}".lower()
            if any(kw in text for kw in business_keywords):
                article.relevance_score = (article.relevance_score or 0) + 10

        scored.sort(key=lambda a: a.relevance_score or 0, reverse=True)
        return scored[:limit]

    async def explore_topic(
        self,
        topic: str,
        profile: dict[str, Any],
        limit: int = 10,
    ) -> list[Article]:
        """Get articles about a specific topic."""
        articles = await self.fetch_all_sources(days=14)

        # Filter by topic
        topic_lower = topic.lower()
        relevant = []
        for article in articles:
            text = f"{article.title} {article.description or ''} {' '.join(article.tags)}".lower()
            if topic_lower in text:
                relevant.append(article)

        # Score remaining
        scored = await self.score_articles(relevant, profile)
        return scored[:limit]

    async def analyze_url(
        self,
        url: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze a specific URL for relevance."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Extract title from HTML
                html = response.text
                title_match = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
                title = title_match.group(1) if title_match else url

                # Extract description
                desc_match = re.search(
                    r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
                    html,
                    re.IGNORECASE,
                )
                description = desc_match.group(1) if desc_match else None

        except Exception:
            title = url
            description = None

        # Score using strategist
        strategist = self._get_strategist()
        score, reason = await strategist.score_article(
            title=title,
            url=url,
            description=description,
            profile=profile,
        )

        return {
            "url": url,
            "title": title,
            "description": description,
            "relevance_score": score,
            "relevance_reason": reason,
            "worth_reading": score >= 50,
            "recommendation": (
                "Highly relevant - read this!" if score >= 70 else
                "Somewhat relevant - skim it" if score >= 50 else
                "Low relevance - skip unless curious"
            ),
        }
