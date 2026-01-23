"""
Side Strategic Evaluator - The 10-Dimension Intelligence Engine.

Calculates Project Strategic IQ across 10 dimensions with a 400-point scale.
"""

from typing import Dict, Any, List
from pathlib import Path
import subprocess
import logging

logger = logging.getLogger(__name__)

class StrategicEvaluator:
    """Central evaluator for Project Strategic IQ and Grade (10 Dimensions)."""
    
    @staticmethod
    def calculate_iq(
        profile: Dict[str, Any], 
        active_plans: List[Dict[str, Any]], 
        audit_summary: Dict[str, int],
        project_root: Path = None,
        activities: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate unified Strategic IQ across 10 dimensions.
        
        Scale: 400 points max (10 dimensions × 40 each)
        Grades: A (90%+), B (80%+), C (70%+), D (60%+), F (<60%)
        """
        
        # Initialize 10 dimensions at baseline (25/40)
        dimensions = {
            "Architecture": 25,
            "Velocity": 25,
            "Security": 25,
            "Docs": 25,
            "Community": 25,
            "Resilience": 25,
            "MarketFit": 25,
            "Legal": 25,
            "Compliance": 25,
            "Investor": 25,
        }
        
        project_root = project_root or Path.cwd()
        activities = activities or []
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 1: ARCHITECTURE
        # ═══════════════════════════════════════════════════════════════════
        langs = profile.get("languages", {})
        if langs and len(langs) >= 2:
            dimensions["Architecture"] = 30
            
        # Monorepo Reward (Python + TS/JS)
        if langs:
            has_ts = any(ext in langs for ext in [".ts", ".tsx", ".js", ".jsx"])
            has_py = ".py" in langs
            if has_ts and has_py:
                dimensions["Architecture"] = min(40, dimensions["Architecture"] + 10)
        
        # Module separation check
        if (project_root / "src").exists() and (project_root / "tests").exists():
            dimensions["Architecture"] = min(40, dimensions["Architecture"] + 5)
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 2: VELOCITY
        # ═══════════════════════════════════════════════════════════════════
        if profile.get("domain"):
            dimensions["Velocity"] = 30
            
        if active_plans and len(active_plans) >= 2:
            dimensions["Velocity"] = min(40, dimensions["Velocity"] + 7)
        
        # Git velocity bonus
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "10", "--since=7 days ago"],
                capture_output=True, text=True, cwd=project_root, timeout=5
            )
            commit_count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            if commit_count >= 5:
                dimensions["Velocity"] = min(40, dimensions["Velocity"] + 5)
        except Exception:
            pass
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 3: SECURITY
        # ═══════════════════════════════════════════════════════════════════
        critical_count = audit_summary.get('CRITICAL', 0)
        high_count = audit_summary.get('HIGH', 0)
        warning_count = audit_summary.get('WARNING', 0) or audit_summary.get('MEDIUM', 0)
        
        if critical_count == 0 and high_count == 0:
            dimensions["Security"] = 35
        else:
            # Steep penalty for critical/high
            penalty = (critical_count * 8) + (high_count * 4)
            dimensions["Security"] = max(5, 35 - penalty)
            
        if warning_count == 0:
            dimensions["Security"] = min(40, dimensions["Security"] + 5)
        else:
            # Slight penalty for warnings/medium
            dimensions["Security"] = max(5, dimensions["Security"] - (warning_count * 2))
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 4: DOCS
        # ═══════════════════════════════════════════════════════════════════
        readme = project_root / "README.md"
        if readme.exists():
            dimensions["Docs"] = 30
            try:
                content = readme.read_text()
                if "## Installation" in content or "## Usage" in content:
                    dimensions["Docs"] = min(40, dimensions["Docs"] + 5)
                if "![" in content or "badge" in content.lower():
                    dimensions["Docs"] = min(40, dimensions["Docs"] + 5)
            except Exception:
                pass
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 5: COMMUNITY (Deprioritized - Local Git Only, No API)
        # ═══════════════════════════════════════════════════════════════════
        # We only use local git data, no GitHub API
        try:
            result = subprocess.run(
                ["git", "shortlog", "-sn", "--all"],
                capture_output=True, text=True, cwd=project_root, timeout=5
            )
            contributors = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            if contributors >= 2:
                dimensions["Community"] = 28
            if contributors >= 5:
                dimensions["Community"] = 32
        except Exception:
            pass
        
        # Local .github folder only (no API)
        if (project_root / ".github").exists():
            dimensions["Community"] = min(35, dimensions["Community"] + 3)
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 6: RESILIENCE
        # ═══════════════════════════════════════════════════════════════════
        if (project_root / "tests").exists():
            dimensions["Resilience"] = 30
            try:
                test_files = list((project_root / "tests").rglob("test_*.py"))
                if len(test_files) >= 5:
                    dimensions["Resilience"] = min(40, dimensions["Resilience"] + 5)
            except Exception:
                pass
        
        # CI/CD detection
        ci_files = [
            project_root / ".github" / "workflows",
            project_root / ".gitlab-ci.yml",
            project_root / "Jenkinsfile",
        ]
        if any(p.exists() for p in ci_files):
            dimensions["Resilience"] = min(40, dimensions["Resilience"] + 5)
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 7: MARKET FIT
        # ═══════════════════════════════════════════════════════════════════
        simulate_activities = [a for a in activities if a.get("tool") == "simulate"]
        if len(simulate_activities) >= 3:
            dimensions["MarketFit"] = 30
        if len(simulate_activities) >= 10:
            dimensions["MarketFit"] = min(40, dimensions["MarketFit"] + 10)
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 8: LEGAL
        # ═══════════════════════════════════════════════════════════════════
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt"]
        if any((project_root / f).exists() for f in license_files):
            dimensions["Legal"] = 30
            try:
                for f in license_files:
                    lf = project_root / f
                    if lf.exists():
                        content = lf.read_text().lower()
                        if "mit" in content or "apache" in content:
                            dimensions["Legal"] = 40
                        break
            except Exception:
                pass
        
        if (project_root / "PRIVACY.md").exists():
            dimensions["Legal"] = min(40, dimensions["Legal"] + 5)
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 9: COMPLIANCE
        # ═══════════════════════════════════════════════════════════════════
        if (project_root / "SECURITY.md").exists():
            dimensions["Compliance"] = 35
        
        # Audit trail check
        if len(activities) >= 50:
            dimensions["Compliance"] = min(40, dimensions["Compliance"] + 5)
        
        # ═══════════════════════════════════════════════════════════════════
        # DIMENSION 10: INVESTOR
        # ═══════════════════════════════════════════════════════════════════
        investor_files = ["VISION.md", "pitch.md", "ROADMAP.md"]
        if any((project_root / f).exists() for f in investor_files):
            dimensions["Investor"] = 35
        
        # Objectives in plans
        objectives = [p for p in active_plans if p.get("type") == "objective"]
        if objectives:
            dimensions["Investor"] = min(40, dimensions["Investor"] + 5)
        
        # ═══════════════════════════════════════════════════════════════════
        # FINAL CALCULATION: THE TWO PILLARS
        # ═══════════════════════════════════════════════════════════════════
        
        # 1. Forensic Pillar (Hard Tech Health)
        forensic_dims = ["Security", "Architecture", "Velocity", "Docs", "Resilience"]
        forensic_total = sum(dimensions[d] for d in forensic_dims)
        forensic_max = len(forensic_dims) * 40
        forensic_score = int((forensic_total / forensic_max) * 100)
        
        # 2. Strategic Pillar (Business Viability)
        strategic_dims = ["MarketFit", "Community", "Legal", "Compliance", "Investor"]
        strategic_total = sum(dimensions[d] for d in strategic_dims)
        strategic_max = len(strategic_dims) * 40
        strategic_score = int((strategic_total / strategic_max) * 100)
        
        # 3. Master Grade (50/50 Split)
        final_score = int((forensic_score + strategic_score) / 2)
        
        def get_grade(score):
            if score >= 90: return "A", "World Class"
            if score >= 80: return "B", "Solid"
            if score >= 70: return "C", "Functional"
            if score >= 60: return "D", "Risky"
            return "F", "Critical"

        grade, label = get_grade(final_score)
        f_grade, _ = get_grade(forensic_score)
        s_grade, _ = get_grade(strategic_score)
        
        # Restore Top Focus calculation
        min_dim = min(dimensions, key=dimensions.get)
        top_focus = f"{min_dim} enhancement required" if dimensions[min_dim] < 28 else "Sustaining excellence"
        
        raw_score = sum(dimensions.values())
        
        return {
            "score": final_score,         # 0-100
            "raw_score": raw_score,       # 0-400
            "grade": grade,               # A-F
            "label": label,               # Descriptor
            "forensic_score": forensic_score,
            "forensic_grade": f_grade,
            "strategic_score": strategic_score,
            "strategic_grade": s_grade,
            "dimensions": dimensions,
            "top_focus": top_focus
        }
