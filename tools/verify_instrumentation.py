
import asyncio
import sys
from pathlib import Path

# Mock sys.path to find backend
sys.path.append(str(Path.cwd() / "backend" / "src"))

from side.tools.planning import _generate_monolith_file
from side.storage.simple_db import SimplifiedDatabase

async def verify():
    print("🧭 Verifying Instrumentation UI...")
    db = SimplifiedDatabase()
    
    # 1. Trigger Monolith Generation
    await _generate_monolith_file(db)
    
    # 2. Inspect MONOLITH.md
    monolith_path = Path(".side/MONOLITH.md")
    if not monolith_path.exists():
        print("❌ MONOLITH.md not found.")
        return

    content = monolith_path.read_text()
    
    # 3. Check for Gamification Removal
    gamified_keywords = ["STREAK", "XP", "Level", "Badge", "Drip"]
    found_gamified = [kw for kw in gamified_keywords if kw in content and "Level" not in content[:500]] # Level might be in breadcrumbs?
    
    # 4. Check for Instrumentation Addition
    instrument_keywords = ["INSTRUMENTATION", "Operating Mode", "Leverage Factor"]
    missing_instrument = [kw for kw in instrument_keywords if kw not in content]
    
    print("\n--- MONOLITH CONTENT PREVIEW ---")
    print("\n".join(content.splitlines()[:20]))
    print("--------------------------------\n")
    
    if not found_gamified and not missing_instrument:
        print("✅ SUCCESS: Monolith is now a Quiet Instrumentation Dashboard.")
    else:
        if found_gamified:
            print(f"❌ FAILURE: Gamification traces found: {found_gamified}")
        if missing_instrument:
            print(f"❌ FAILURE: Instrumentation missing: {missing_instrument}")

if __name__ == "__main__":
    asyncio.run(verify())
