import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from unittest.mock import MagicMock, patch
from side.strategic_engine import StrategicDecisionEngine, StrategicContext

def test_hybrid_router():
    print("🧪 Verifying Hybrid Router Logic...")
    
    # Mock Context
    context = StrategicContext(
        tech_stack=["Python"], team_size=1, team_skills=["SQL"],
        stage="pmf", users=0, revenue=0, runway_months=12,
        focus_area="backend", recent_commits=0, open_issues=0
    )
    
    # Initialize Engine
    engine = StrategicDecisionEngine()
    
    # Mock the LLM Client instance attached to the engine
    engine.llm = MagicMock()
    engine.llm.complete.return_value = '{"recommendation": "PostGIS", "reasoning": ["Maps need PostGIS"]}'
    
    # TEST 1: Heuristic (Fast Path)
    print("\n[Test 1] 'Postgres vs Mongo' (Standard)")
    engine.analyze_tech_stack_decision("Should I use Postgres or Mongo?", context)
    
    if engine.llm.complete.called:
        print("❌ FAIL: Heuristic path called LLM! (Expensive)")
    else:
        print("✅ PASS: Heuristic path bypassed LLM (Free/Fast)")
        
    # TEST 2: Expert (Smart Path)
    print("\n[Test 2] 'Geospatial Data' (Nuanced)")
    engine.analyze_tech_stack_decision("I need to store geospatial data", context)
    
    if engine.llm.complete.called:
        print("✅ PASS: Complex path called LLM (Smart)")
    else:
        print("❌ FAIL: Complex path blocked LLM (Dumb)")

if __name__ == "__main__":
    test_hybrid_router()
