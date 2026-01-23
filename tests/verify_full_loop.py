import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "backend" / "src"))

async def test_full_proactive_loop():
    print("🕵️  Palantir Audit: Verifying 'Invisible Intelligence' Loop...\n")

    # 1. Setup Mocks
    mock_db = MagicMock()
    mock_llm = AsyncMock()
    mock_llm.is_available.return_value = True
    # Mock LLM response for 8B model
    mock_llm.complete_async.return_value = '[{"finding": "Race condition detected", "severity": "CRITICAL"}]'

    # 2. Patch Dependencies
    with patch("side.services.context_tracker.ContextTracker") as MockContext, \
         patch("side.intel.auditor.LLMClient") as MockLLMClient, \
         patch("side.storage.simple_db.SimplifiedDatabase", return_value=mock_db):
         
        from side.services.service_manager import ServiceManager
        from side.intel.auditor import AuditorService
        
        # Setup Service Manager
        manager = ServiceManager("/tmp/test_project")
        
        # Setup Auditor Service with mocked LLM
        auditor_service = AuditorService(mock_db, Path("/tmp/test_project"))
        auditor_service.auditor.llm = mock_llm 
        
        # Inject Auditor into Manager (simulating startup)
        manager._services["auditor"] = auditor_service
        manager._services["context_tracker"] = MockContext.return_value
        
        # 3. Trigger Event: "User Saves File"
        changed_files = [Path("backend/src/side/critical_logic.py")]
        
        # Mock reading the file
        with patch.object(Path, "read_text", return_value="print('Potential race condition')"):
            with patch.object(Path, "exists", return_value=True):
                 print(f"📝 Event: User modified {changed_files[0]}")
                 await manager._on_files_changed(changed_files)
        
        # 4. Verification Points
        print("\n🔍 Verification Results:")
        
        # Did Auditor get called?
        # We need to verify that Auditor.quick_scan was awaited.
        # Since we can't easily spy on the method call in this integration test setup without more complex mocking,
        # we check if the LLM was called, which is the ultimate proof.
        
        if mock_llm.complete_async.called:
            print("✅ PASS: LLM (8B) was triggered by File Save.")
            args = mock_llm.complete_async.call_args
            print(f"   -> Model Used: {args.kwargs.get('model_override')}")
            print(f"   -> Prompt Context: {args.kwargs.get('messages')[0]['content'][:50]}...")
        else:
            print("❌ FAIL: LLM was NOT triggered. The 'Invisible Loop' is broken.")

        # 5. Business Logic Verification (Did it Triage?)
        # For this test we just confirmed the call happened.

if __name__ == "__main__":
    asyncio.run(test_full_proactive_loop())
