"""
CSO.ai Refined Tools - 3 perfect tools that deliver instant wow factor.

Philosophy: Zero setup, instant value, beautiful output.

Tools:
1. read - "What should I read?" (< 1 second)
2. analyze_url - "Is this worth my time?" (< 1 second)
3. strategy - "What should I focus on?" (< 2 seconds)
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from mcp.types import Tool

from cso_ai.intel.auto_intelligence import AutoIntelligence
from cso_ai.intel.market import MarketAnalyzer
from cso_ai.storage.simple_db import SimplifiedDatabase

# =============================================================================
# GLOBAL STATE
# =============================================================================

_auto_intel: AutoIntelligence | None = None
_database: SimplifiedDatabase | None = None
_market: MarketAnalyzer | None = None


def _get_auto_intel() -> AutoIntelligence:
    """Get or create auto-intelligence singleton."""
    global _auto_intel
    if _auto_intel is None:
        _auto_intel = AutoIntelligence()
    return _auto_intel


def _get_database() -> SimplifiedDatabase:
    """Get or create database singleton."""
    global _database
    if _database is None:
        _database = SimplifiedDatabase()
    return _database


def _get_market() -> MarketAnalyzer:
    """Get or create market analyzer singleton."""
    global _market
    if _market is None:
        _market = MarketAnalyzer()
    return _market


# =============================================================================
# TOOL DEFINITIONS - Only 3 Perfect Tools
# =============================================================================

TOOLS: list[Tool] = [
    Tool(
        name="read",
        description="""Show top 5 articles for YOUR stack. INSTANT.

Triggers:
- "what should I read?"
- "anything interesting?"
- "tech news for me"
- "relevant articles"

Returns: Personalized articles scored 0-100, cached 1 hour.
Speed: < 1 second (cached), < 3 seconds (fresh)""",
        inputSchema={
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "description": "Force refresh from sources (slower)",
                    "default": False,
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="analyze_url",
        description="""Evaluate if a URL is worth your time.

Triggers:
- "is this worth reading?" + URL
- "should I read this?"
- "evaluate this link"

Returns: Score 0-100, reasoning, key takeaways.
Speed: < 1 second""",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to analyze",
                },
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="strategy",
        description="""Get strategic advice based on your current work.

Triggers:
- "what should I focus on?"
- "strategic advice"
- "CSO, help me think"

Returns: Prioritized actions, relevant articles, reasoning.
Speed: < 2 seconds""",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {
                    "type": "string",
                    "description": "Optional context about what you're working on",
                },
            },
            "required": [],
        },
    ),
]


# =============================================================================
# TOOL HANDLERS
# =============================================================================


async def handle_tool_call(name: str, arguments: dict[str, Any]) -> str:
    """Route tool calls to appropriate handlers."""
    handlers = {
        "read": _handle_read,
        "analyze_url": _handle_analyze_url,
        "strategy": _handle_strategy,
    }

    handler = handlers.get(name)
    if handler is None:
        return f"❌ Unknown tool: {name}"

    try:
        return await handler(arguments)
    except Exception as e:
        return f"❌ Error: {str(e)}\n\nPlease try again or check your network connection."


# =============================================================================
# HANDLER IMPLEMENTATIONS
# =============================================================================


@handle_tool_errors
async def _handle_read(arguments: dict[str, Any]) -> str:
    """
    Show top 5 articles for user's stack.
    
    Target: < 100ms (query cache), < 1s (article cache), < 3s (fresh)
    """
    start_time = datetime.now(timezone.utc)
    force_refresh = arguments.get("refresh", False)

    # Get database
    db = _get_database()

    # Check query cache first (unless force refresh)
    if not force_refresh:
        cached_result = db.get_query_cache(
            query_type="read",
            query_params={"refresh": False},
        )
        if cached_result:
            # Add cache hit indicator
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"Query cache hit! Response in {elapsed*1000:.0f}ms")
            return cached_result + f"\n\n⚡ From query cache ({elapsed*1000:.0f}ms)"

    # Auto-detect stack (cached 24h)
    auto_intel = _get_auto_intel()
    profile = await auto_intel.get_or_create_profile()

    # Get work context for better relevance
    context = db.get_latest_work_context(str(Path.cwd()))
    focus_area = context["focus_area"] if context else None

    # Try article cache first (unless force refresh)
    articles = []
    cache_status = "fresh"
    
    if not force_refresh:
        articles = db.get_cached_articles(max_age_hours=1, limit=100)
        if articles:
            cache_status = "cached"

    # Fetch fresh if needed
    if not articles:
        market = _get_market()
        articles = await market.fetch_all_sources(days=7)
        
        # Save to cache
        for article in articles:
            db.save_article(article)
        
        cache_status = "fresh"

    # Score articles against profile + context
    profile_dict = profile.to_dict()
    if focus_area:
        profile_dict["current_focus"] = focus_area
    
    profile_hash = profile.get_hash()
    
    scored_articles = []
    for article in articles:
        # Check score cache
        cached_score = db.get_article_score(article.id, profile_hash)
        
        if cached_score:
            score = cached_score["score"]
            reason = cached_score["reason"]
        else:
            # Score with market analyzer (uses LLM or heuristics)
            market = _get_market()
            scored = await market.score_articles([article], profile_dict)
            if scored:
                score = scored[0].relevance_score or 0
                reason = scored[0].relevance_reason or "General tech content"
                
                # Cache the score
                db.save_article_score(article.id, profile_hash, score, reason)
            else:
                score = 0
                reason = "Could not score"
        
        article.relevance_score = score
        article.relevance_reason = reason
        scored_articles.append(article)

    # Sort by score and take top 5
    scored_articles.sort(key=lambda a: a.relevance_score or 0, reverse=True)
    top_articles = scored_articles[:5]

    # Calculate elapsed time
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

    # Format output beautifully
    output = _format_article_list(top_articles, profile, elapsed, cache_status, focus_area)
    
    # Cache the result (1 hour TTL)
    if not force_refresh:
        db.save_query_cache(
            query_type="read",
            query_params={"refresh": False},
            result=output,
            ttl_hours=1,
        )
    
    return output


@handle_tool_errors
async def _handle_analyze_url(arguments: dict[str, Any]) -> str:
    """
    Evaluate if a URL is worth reading.
    
    Target: < 1 second
    """
    start_time = datetime.now(timezone.utc)
    url = arguments.get("url")

    if not url:
        return "❌ Please provide a URL to analyze.\n\nExample: \"Is this worth reading? https://example.com/article\""

    # Validate and normalize URL
    try:
        url = validate_url(url)
    except ValueError as e:
        return f"❌ Invalid URL: {str(e)}\n\nPlease provide a valid URL."

    # Auto-detect stack
    auto_intel = _get_auto_intel()
    profile = await auto_intel.get_or_create_profile()

    # Analyze URL
    market = _get_market()
    profile_dict = profile.to_dict()
    
    try:
        result = await market.analyze_url(url, profile_dict)
    except Exception as e:
        return f"❌ Could not analyze URL: {str(e)}\n\nPlease check the URL and try again."

    # Calculate elapsed time
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

    # Format output
    output = _format_url_analysis(result, profile, elapsed)
    
    return output


@handle_tool_errors
async def _handle_strategy(arguments: dict[str, Any]) -> str:
    """
    Get strategic advice based on current work.
    
    Target: < 2 seconds
    """
    start_time = datetime.now(timezone.utc)
    context = arguments.get("context", "")

    # Auto-detect stack + recent work
    auto_intel = _get_auto_intel()
    profile = await auto_intel.get_or_create_profile()

    # Get relevant articles
    db = _get_database()
    articles = db.get_cached_articles(max_age_hours=24, limit=10)

    # Generate strategy
    from cso_ai.intel.strategist import Strategist
    
    strategist = Strategist()
    profile_dict = profile.to_dict()
    
    question = f"What should I focus on? {context}".strip()
    
    if strategist.is_available():
        # Use LLM for smart strategy
        article_dicts = [
            {"title": a.title, "url": a.url, "description": a.description}
            for a in articles[:5]
        ]
        strategy = await strategist.get_strategy(
            question=question,
            profile=profile_dict,
            articles=article_dicts,
        )
    else:
        # Fallback strategy
        strategy = await strategist._fallback_strategy(question, profile_dict)

    # Calculate elapsed time
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

    # Format output
    output = _format_strategy(strategy, profile, articles[:3], elapsed)
    
    return output


# =============================================================================
# OUTPUT FORMATTING - Beautiful, Scannable, Actionable
# =============================================================================


def _format_article_list(
    articles: list[Any],
    profile: Any,
    elapsed: float,
    cache_status: str,
    focus_area: str | None = None,
) -> str:
    """Format article list beautifully."""
    
    # Header
    stack_summary = _get_stack_summary(profile)
    output = f"📰 Top Articles for Your Stack ({stack_summary})\n"
    
    # Show focus area if detected
    if focus_area:
        output += f"🎯 Current Focus: {focus_area.title()}\n"
    
    output += "\n"

    if not articles:
        output += "⚠️ No articles found. Try refreshing with `refresh: true`\n"
        return output

    # Articles
    for i, article in enumerate(articles, 1):
        score = article.relevance_score or 0
        score_bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
        
        # Title (truncate if too long)
        title = article.title
        if len(title) > 60:
            title = title[:57] + "..."
        
        output += f"{i}. [{score:.0f}] {score_bar} {title}\n"
        output += f"   💡 {article.relevance_reason or 'Relevant to your stack'}\n"
        output += f"   🔗 {article.url}\n"
        
        # Estimate read time (rough: 200 words/min, avg article 1000 words)
        read_time = 5  # Default 5 min
        output += f"   ⏱️ ~{read_time} min read\n\n"

    # Footer with timing
    cache_emoji = "⚡" if cache_status == "cached" else "🔄"
    output += f"{cache_emoji} Analyzed in {elapsed:.1f}s"
    
    if cache_status == "cached":
        output += " | From cache"
    else:
        output += " | Next refresh in 60 min"
    
    output += "\n"
    
    return output


def _format_url_analysis(
    result: dict[str, Any],
    profile: Any,
    elapsed: float,
) -> str:
    """Format URL analysis beautifully."""
    
    score = result.get("score", 0)
    reasoning = result.get("reasoning", "No analysis available")
    
    # Header
    output = f"🎯 Relevance Score: {score}/100\n\n"
    
    # Verdict
    if score >= 80:
        output += "✅ HIGHLY RECOMMENDED\n\n"
    elif score >= 60:
        output += "👍 WORTH YOUR TIME\n\n"
    elif score >= 40:
        output += "🤔 MAYBE USEFUL\n\n"
    else:
        output += "⏭️ SKIP THIS ONE\n\n"
    
    # Reasoning
    output += f"Why: {reasoning}\n\n"
    
    # Key takeaways (if available)
    takeaways = result.get("takeaways", [])
    if takeaways:
        output += "Key Takeaways:\n"
        for takeaway in takeaways[:3]:
            output += f"• {takeaway}\n"
        output += "\n"
    
    # Timing
    output += f"⚡ Analyzed in {elapsed:.1f}s\n"
    
    return output


def _format_strategy(
    strategy: str,
    profile: Any,
    articles: list[Any],
    elapsed: float,
) -> str:
    """Format strategic advice beautifully."""
    
    stack_summary = _get_stack_summary(profile)
    
    output = f"🎯 Strategic Focus ({stack_summary})\n\n"
    
    # Recent activity context
    if profile.recent_commits > 0:
        output += f"📊 Recent Activity: {profile.recent_commits} commits in last 7 days\n"
        if profile.focus_areas:
            output += f"🔍 Working on: {', '.join(profile.focus_areas)}\n"
        output += "\n"
    
    # Strategy from LLM or fallback
    output += strategy
    output += "\n\n"
    
    # Relevant reading
    if articles:
        output += "📚 Relevant Reading:\n"
        for article in articles[:3]:
            output += f"• \"{article.title}\" ({article.source})\n"
            output += f"  {article.url}\n"
        output += "\n"
    
    # Timing
    output += f"⚡ Generated in {elapsed:.1f}s\n"
    
    return output


def _get_stack_summary(profile: Any) -> str:
    """Get concise stack summary."""
    parts = []
    
    if profile.primary_language:
        parts.append(profile.primary_language)
    
    if profile.frameworks:
        parts.extend(profile.frameworks[:2])  # Top 2 frameworks
    
    if not parts:
        return "Unknown stack"
    
    return " + ".join(parts)
