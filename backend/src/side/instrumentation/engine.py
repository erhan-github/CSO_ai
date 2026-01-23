"""
Instrumentation Engine - Observability for Human-Machine Leverage.
"""

from typing import Dict, Any, Optional
import json
from datetime import datetime, timezone
from ..storage.simple_db import SimplifiedDatabase

class InstrumentationEngine:
    """
    Quietly measures and reports human leverage.
    Replaces the previous Gamification philosophy.
    """

    OPERATING_MODES = {
        1: "Manual Execution",
        2: "Assisted Completion",
        3: "Intent-Level Editing",
        4: "Multi-File Orchestration",
        5: "Autonomous Delegation"
    }

    def __init__(self, db: SimplifiedDatabase):
        self.db = db

    def record_outcome(self, project_id: str, outcome_type: str, leverage_signal: float = 1.0) -> Dict[str, Any]:
        """
        Records a successful outcome to measure leverage over time.
        No XP is awarded. No celebrations triggered.
        """
        with self.db._connection() as conn:
            # 1. Log the outcome for instrumentation
            conn.execute(
                "INSERT INTO outcomes_ledger (project_id, outcome_type, leverage_value) VALUES (?, ?, ?)",
                (project_id, outcome_type, leverage_signal)
            )
            
            # 2. Update stats (Quietly)
            stats = conn.execute(
                "SELECT * FROM user_stats WHERE project_id = ?", (project_id,)
            ).fetchone()
            
            now_utc = datetime.now(timezone.utc).isoformat()
            
            if not stats:
                conn.execute(
                    "INSERT INTO user_stats (project_id, last_action_at) VALUES (?, ?)",
                    (project_id, now_utc)
                )
            else:
                conn.execute(
                    "UPDATE user_stats SET last_action_at = ? WHERE project_id = ?",
                    (now_utc, project_id)
                )
            
            conn.commit()

        return {"status": "recorded", "outcome": outcome_type}

    def get_status(self, project_id: str) -> Dict[str, Any]:
        """
        Returns factual observability data.
        """
        with self.db._connection() as conn:
            # 1. Calculate Leverage Factor
            # Leverage = Outcomes / Total Activity Log entries (approx)
            outcomes_count = conn.execute(
                "SELECT COUNT(*) as count FROM outcomes_ledger WHERE project_id = ?", (project_id,)
            ).fetchone()["count"]
            
            activity_count = conn.execute(
                "SELECT COUNT(*) as count FROM activities WHERE project_id = ?", (project_id,)
            ).fetchone()["count"]
            
            leverage_factor = round(outcomes_count / max(activity_count, 1), 2)
            
            # 2. Determine Operating Mode based on Delegation Depth
            # For now, we anchor to plan complexity or recent tool usage.
            mode_id = 1
            if outcomes_count > 50: mode_id = 4
            elif outcomes_count > 20: mode_id = 3
            elif outcomes_count > 5: mode_id = 2
            
            # 3. Get Recent Outcomes
            outcomes = conn.execute(
                "SELECT outcome_type, created_at FROM outcomes_ledger WHERE project_id = ? ORDER BY created_at DESC LIMIT 5",
                (project_id,)
            ).fetchall()

        return {
            "operating_mode": self.OPERATING_MODES.get(mode_id, "Unknown"),
            "leverage_factor": leverage_factor,
            "outcomes_count": outcomes_count,
            "recent_outcomes": [o["outcome_type"] for o in outcomes]
        }
