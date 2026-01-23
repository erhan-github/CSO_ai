import asyncio
import sqlite3
import json
from pathlib import Path
from side.intelligence.graph_kernel import GraphKernel
from side.intel.analyzers.universal import UniversalAnalyzer
from side.intel.memory.manager import MemoryManager
from side.intel.memory.persistence import MemoryPersistence
from side.llm.client import LLMClient

# 1. Setup
DB_PATH = "side_purified.sqlite"
if Path(DB_PATH).exists(): Path(DB_PATH).unlink()

graph = GraphKernel(storage_path=DB_PATH)
analyzer = UniversalAnalyzer(graph=graph)

class MockLLM(LLMClient):
    async def complete_async(self, messages, **kwargs):
        content = messages[0]['content']
        if "Extract discrete facts" in content:
            return '[{"content": "Auth logic is sensitive."}]'
        elif "Classify this fact" in content:
            return "security_rules"
        elif "Evolve Summaries" in content:
            return "Security Rules Updated."
        elif "Generate 10-20 search keywords" in content:
            return '["auth", "security"]'
        return "{}"

async def final_audit():
    print("💎 EXECUTING PALANTIR-LEVEL PURITY AUDIT 💎")
    
    # A. Ingest Polyglot (Rust)
    root = Path("/Users/erhanerdogan/Desktop/side/tests/polyglot")
    await analyzer.analyze(root, [root / "test.rs"])
    
    # B. Ingest Python (Mocking a python file)
    py_file = Path("audit_target.py")
    py_file.write_text("class Vault:\n    def open(self):\n        pass # TODO: Add auth")
    await analyzer.analyze(Path("."), [py_file])
    
    # C. Ingest Intent with PII (Testing Scrubber)
    print("--- Ingesting Intent with PII (Testing Scrubber) ---")
    graph.ingest_intent(
        "manual_pii_test",
        "Leaked info: erhan@example.com and AKIAJSSECRETKEY123.",
        {"focus_symbol": "audit_target.py:Vault"}
    )
    
    # D. Durability Check
    print("\n[Security Audit] Restarting Kernel and checking Redaction...")
    graph2 = GraphKernel(storage_path=DB_PATH)
    
    # E. Verify Redaction
    vault_cluster = graph2.get_neighborhood("symbol:audit_target.py:Vault", depth=1)
    intent_obj = [o for o in vault_cluster if o.uid == "intent:manual_pii_test"][0]
    content = intent_obj.properties["content"]
    
    print(f"🔹 Scrubbed Content: {content}")
    
    if "erhan@example.com" not in content and "AKIAJSSECRETKEY123" not in content:
        print("✅ SUCCESS: PII and Secrets were REDACTED.")
    else:
        print("❌ FAILURE: Sovereign Scrubber bypassed.")
        
    if "[REDACTED_EMAIL]" in content and "[REDACTED_AWS_KEY]" in content:
        print("✅ SUCCESS: Redaction tags are present.")

    has_code = any(o.uid == "symbol:audit_target.py:Vault" for o in vault_cluster)
    has_intent = any(o.type == "intent" for o in vault_cluster)
    
    if has_code and has_intent:
        print("\n✨ ARCHITECTURAL PURITY VERIFIED ✨")
        print("Everything is linked. Everything is persistent. The Fabric is alive.")
    else:
        print("\n❌ ARCHITECTURAL LEAK DETECTED.")
        if not has_intent: print("   Missing: Intent-to-Python-Symbol Link")

    # Cleanup
    if py_file.exists(): py_file.unlink()
    import shutil
    if Path("./test_audit_memory").exists(): shutil.rmtree("./test_audit_memory")

if __name__ == "__main__":
    asyncio.run(final_audit())
