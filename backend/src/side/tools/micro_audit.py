"""
Micro Audit Tool.
Designed for Agent/MCP use.
Runs a specific audit probe on a specific file instantly.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[3]))

from side.forensic_audit.runner import ForensicAuditRunner

async def main():
    if len(sys.argv) < 3:
        print("Usage: python3 micro_audit.py <probe_id> <file_path>")
        return

    probe_id = sys.argv[1]
    file_path = sys.argv[2]
    
    # Project root assumption: 3 levels up from tools/
    project_root = Path(__file__).parents[3]
    
    runner = ForensicAuditRunner(str(project_root))
    
    # Force loading of keys if needed? 
    # Runner handles LLMClient init which handles .env
    
    result = await runner.run_single_probe(probe_id, file_path)
    print(result)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Execution Error: {e}")
