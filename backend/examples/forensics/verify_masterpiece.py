import asyncio
import logging
from pathlib import Path
from side.intelligence.graph_kernel import GraphKernel
from side.intel.analyzers.universal import UniversalAnalyzer
from side.intel.memory.manager import MemoryManager
from side.intel.memory.persistence import MemoryPersistence
from side.llm.client import LLMClient
from side.finance.billing import FinanceEngine
from side.identity.simulation import IdentitySimulator

# Configure logging
logging.basicConfig(level=logging.INFO)

class MockLLM(LLMClient):
    async def complete_async(self, messages, **kwargs):
        content = messages[0]['content']
        if "Extract discrete facts" in content:
            return '[{"content": "Fraud threshold is set to 10000 based on Risk Board decision."}]'
        elif "Classify this fact" in content:
            return "business_logic"
        elif "Evolve Summaries" in content:
            return "Business Logic Updated."
        elif "Generate 10-20 search keywords" in content:
            return '["fraud", "billing"]'
        return "{}"

async def run_masterpiece():
    print("\n💎 STARTING MASTERPIECE E2E VERIFICATION (The Sequoia Standard) 💎")
    
    # 1. Initialize Sidelith Sovereign Stack
    DB_PATH = "masterpiece_fabric.sqlite"
    if Path(DB_PATH).exists(): Path(DB_PATH).unlink()
    
    graph = GraphKernel(storage_path=DB_PATH)
    analyzer = UniversalAnalyzer(graph=graph)
    persistence = MemoryPersistence("./masterpiece_memory")
    memory = MemoryManager(persistence, MockLLM(), graph=graph)
    
    # 2. Simulate Production Systems
    finance = FinanceEngine()
    identity = IdentitySimulator()
    
    # --- STEP A: INITIALIZE USER & CODE ---
    print("\n[Step A] User Creation & Code Analysis...")
    user = identity.create_user("erhan_engineer", "erhan@sequoiacap.com")
    token = identity.login("erhan_engineer")
    
    # Analyze the Finance Engine itself (Polyglot)
    billing_file = Path("/Users/erhanerdogan/Desktop/side/backend/src/side/finance/billing.py")
    await analyzer.analyze(Path("/Users/erhanerdogan/Desktop/side/backend/src/side"), [billing_file])
    
    # --- STEP B: HIGH-STAKES TRANSACTION ---
    print("\n[Step B] High-Stakes Financial Transaction...")
    # This triggers the fraud threshold logic
    txn = finance.process_payment(user.id, 15000.0, "tok_premium_sequoia")
    print(f"Transaction ID: {txn.id}, Status: {txn.status}")
    
    # --- STEP C: STRATEGIC INTENT CAPTURE ---
    print("\n[Step C] Capturing Strategic Intent (The 'Why' for the Fraud Logic)...")
    # We link this intent to the 'process_payment' method in the billing engine
    await memory.memorize(
        user_id=user.id,
        content=f"Decision: We use 10000 as the fraud limit for {user.username} to protect company liquidity.",
        meta={"focus_symbol": "finance/billing.py:process_payment"},
        rationale="Risk Board approved higher limits for premium Tier tokens."
    )
    
    # --- STEP D: SOVEREIGN FORENSIC QUERY ---
    print("\n[Step D] Forensic Data Fabric Audit...")
    # We query the logic graph for the 'process_payment' method
    cluster = graph.get_neighborhood("symbol:finance/billing.py:process_payment", depth=1)
    
    print(f"\nResults for 'process_payment' Logic Cluster (Size: {len(cluster)}):")
    for obj in cluster:
        print(f"🔹 [{obj.type}] {obj.uid}")
        if obj.type == "intent":
            content = obj.properties["content"]
            print(f"    -> Intent: {content}")
            
            # SCRIBE AUDIT: Check for PII Redaction
            if "erhan@sequoiacap.com" in content:
                print("    ❌ SECURITY LEAK: PII found in intent.")
            elif "[REDACTED_EMAIL]" in content or "erhan_engineer" not in content:
                 print("    ✅ SECURITY VERIFIED: PII Redacted.")
    
    # Verification Assertions
    has_code = any(o.type == 'symbol' for o in cluster)
    has_intent = any(o.type == 'intent' for o in cluster)
    
    if has_code and has_intent:
        print("\n✨ MASTERPIECE SUCCESS: Code, Finance, and Intent are Uniquely Linked. ✨")
    else:
        print("\n❌ MASTERPIECE FAILURE: Broken Logic Chain.")

    # Cleanup
    import shutil
    if Path("./masterpiece_memory").exists(): shutil.rmtree("./masterpiece_memory")

if __name__ == "__main__":
    asyncio.run(run_masterpiece())
