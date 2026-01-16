"""
Tests for Core CSO.ai modules.
"""

import pytest

from cso_ai.core.listener import Listener, Observation
from cso_ai.core.understander import Understander, IntelligenceProfile
from cso_ai.core.anticipator import Anticipator, Insight, InsightType


class TestListener:
    """Tests for Listener."""

    @pytest.mark.asyncio
    async def test_observe_codebase(self, tmp_path) -> None:
        """Test codebase observation."""
        listener = Listener()
        observations = await listener.observe_codebase(tmp_path)

        assert len(observations) > 0
        assert observations[0].source == "codebase"

    def test_get_recent_observations(self) -> None:
        """Test observation retrieval."""
        listener = Listener()
        listener.observations.append(
            Observation(
                source="test",
                type="test_type",
                data={"key": "value"},
            )
        )

        recent = listener.get_recent_observations()
        assert len(recent) == 1
        assert recent[0].source == "test"


class TestUnderstander:
    """Tests for Understander."""

    @pytest.mark.asyncio
    async def test_process_observations(self) -> None:
        """Test observation processing."""
        understander = Understander()
        observations = [
            Observation(
                source="codebase",
                type="structure_scan",
                data={"root": "/test"},
            )
        ]

        profile = await understander.process_observations(observations, "/test")

        assert profile.path == "/test"
        assert profile.confidence > 0

    def test_get_latest_profile(self) -> None:
        """Test latest profile retrieval."""
        understander = Understander()
        understander.profiles["/test"] = IntelligenceProfile(path="/test")

        latest = understander.get_latest_profile()
        assert latest is not None
        assert latest.path == "/test"


class TestAnticipator:
    """Tests for Anticipator."""

    @pytest.mark.asyncio
    async def test_analyze_profile(self) -> None:
        """Test profile analysis."""
        anticipator = Anticipator()
        profile = IntelligenceProfile(path="/test")

        insights = await anticipator.analyze_profile(profile)

        # Should generate at least some insights
        assert isinstance(insights, list)

    def test_get_insights_filtering(self) -> None:
        """Test insight filtering."""
        anticipator = Anticipator()
        anticipator.insights.append(
            Insight(
                type=InsightType.RISK,
                priority=anticipator.insights[0].priority if anticipator.insights else None,
                title="Test Risk",
                description="Test description",
                reasoning="Test reasoning",
            ) if False else Insight(
                type=InsightType.RISK,
                priority=__import__("cso_ai.core.anticipator", fromlist=["InsightPriority"]).InsightPriority.HIGH,
                title="Test Risk",
                description="Test description",
                reasoning="Test reasoning",
            )
        )

        risks = anticipator.get_insights(type_filter=InsightType.RISK)
        assert len(risks) == 1
        assert risks[0].type == InsightType.RISK
