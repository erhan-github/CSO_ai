import asyncio
import os
import sqlite3
from pathlib import Path
from side.intelligence.graph_kernel import GraphKernel
from side.intel.analyzers.universal import UniversalAnalyzer
from side.intel.memory.manager import MemoryManager
from side.intel.memory.persistence import MemoryPersistence
from side.llm.client import LLMClient
from side.finance.billing import FinanceEngine
from side.identity.simulation import IdentitySimulator
from side.intelligence.graph_kernel import GraphKernel, GraphObject

# --- MOCKS ---
class MockLLM(LLMClient):
    async def complete_async(self, messages, **kwargs):
        content = messages[0]['content']
        if "Extract discrete facts" in content:
            return '[{"content": "Strategic Logic captured."}]'
        elif "Classify this fact" in content:
            return "business_rules"
        elif "Evolve Summaries" in content:
            return "Summary updated."
        elif "Generate 10-20 search keywords" in content:
            return '["logic", "test"]'
        return "{}"

# --- TEST SUITE ---
class ForensicStressTest:
    def __init__(self):
        self.DB_PATH = "stress_test.sqlite"
        if Path(self.DB_PATH).exists(): Path(self.DB_PATH).unlink()
        
        self.graph = GraphKernel(storage_path=self.DB_PATH)
        self.analyzer = UniversalAnalyzer(graph=self.graph)
        self.persistence = MemoryPersistence("./stress_memory")
        self.memory = MemoryManager(self.persistence, MockLLM(), graph=self.graph)
        
        self.results = {}

    async def run_all(self):
        print("🚀 STARTING 10-USE-CASE FORENSIC STRESS TEST 🚀")
        
        await self.case_1_hobby_python()
        await self.case_2_hobby_ts()
        await self.case_3_pro_go()
        await self.case_4_pro_rust()
        await self.case_5_pro_security()
        await self.case_6_pro_performance()
        await self.case_7_ent_identity()
        await self.case_8_ent_finance()
        await self.case_9_ent_scaling()
        await self.case_10_ent_sovereign()
        
        self.report()

    # --- HOBBY CASES ---
    async def case_1_hobby_python(self):
        print("\n[Case 1] Hobby: Python Script Analysis")
        f = Path("hobby_script.py")
        f.write_text("class Robot:\n    def beep(self):\n        pass")
        await self.analyzer.analyze(Path("."), [f])
        success = "symbol:hobby_script.py:Robot" in self.graph.objects
        self.results["hobby_python"] = success
        f.unlink()

    async def case_2_hobby_ts(self):
        print("[Case 2] Hobby: TS Component Analysis")
        f = Path("hobby_ui.ts")
        f.write_text("export class Button { constructor() {} render() {} }")
        await self.analyzer.analyze(Path("."), [f])
        success = "symbol:hobby_ui.ts:Button" in self.graph.objects
        self.results["hobby_ts"] = success
        f.unlink()

    # --- PRO CASES ---
    async def case_3_pro_go(self):
        print("[Case 3] Pro: Go Interface Analysis")
        f = Path("pro_service.go")
        f.write_text("package main\ntype Storage interface { Save(data string) error }")
        await self.analyzer.analyze(Path("."), [f])
        success = "symbol:pro_service.go:Storage" in self.graph.objects
        self.results["pro_go"] = success
        f.unlink()

    async def case_4_pro_rust(self):
        print("[Case 4] Pro: Rust Struct Analysis")
        f = Path("pro_lib.rs")
        f.write_text("struct Engine { power: u32 }\nimpl Engine { fn start(&self) {} }")
        await self.analyzer.analyze(Path("."), [f])
        success = "symbol:pro_lib.rs:Engine" in self.graph.objects
        self.results["pro_rust"] = success
        f.unlink()

    async def case_5_pro_security(self):
        print("[Case 5] Pro: Automated Security Audit")
        f = Path("unsecure.py")
        f.write_text("API_KEY = 'AKIAJSSECRETKEY123'\n# TODO: Fix this leak")
        await self.analyzer.analyze(Path("."), [f])
        findings = [o for o in self.graph.objects.values() if o.type == "finding"]
        success = any("SECRETS" in o.uid for o in findings) and any("TODO" in o.uid for o in findings)
        self.results["pro_security"] = success
        f.unlink()

    async def case_6_pro_performance(self):
        print("[Case 6] Pro: Performance Forensic Audit")
        f = Path("slow.py")
        f.write_text("def nested():\n    for i in range(10):\n        for j in range(10):\n            pass")
        await self.analyzer.analyze(Path("."), [f])
        findings = [o for o in self.graph.objects.values() if o.type == "finding"]
        success = any("PERFORMANCE" in o.uid for o in findings)
        self.results["pro_performance"] = success
        f.unlink()

    # --- ENTERPRISE CASES ---
    async def case_7_ent_identity(self):
        print("[Case 7] Ent: Multi-tenant Identity Flow")
        sim = IdentitySimulator()
        user = sim.create_user("corp_user", "user@corp.com")
        await self.memory.memorize(user.id, "User prefers dark mode.")
        success = any(o.type == "intent" for o in self.graph.objects.values())
        self.results["ent_identity"] = success

    async def case_8_ent_finance(self):
        print("[Case 8] Ent: High-Stakes Finance Logic Link")
        fin = FinanceEngine()
        txn = fin.process_payment("user_1", 15000.0, "tok_valid")
        # Ensure module exists
        self.graph.ingest_symbol("pro_lib.rs", "Engine", "struct", {})
        self.graph.ingest_intent("finance_decision", "Limit is 10k for risk reasons.", {"focus_symbol": "pro_lib.rs:Engine"}) 
        success = txn.status == "flagged_for_review" and "intent:finance_decision" in self.graph.objects
        self.results["ent_finance"] = success

    async def case_9_ent_scaling(self):
        print("[Case 9] Ent: Scaling & Graph Traversal")
        # Ensure module exists
        self.graph.upsert_object(GraphObject(uid="module:scale.py", type="module", properties={"name": "scale.py"}))
        # Ingest many nodes
        for i in range(50):
            self.graph.ingest_symbol("scale.py", f"Node_{i}", "function", {})
        cluster = self.graph.get_neighborhood("module:scale.py", depth=1)
        success = len(cluster) >= 50
        self.results["ent_scaling"] = success

    async def case_10_ent_sovereign(self):
        print("[Case 10] Ent: Sovereign Privacy Protection")
        self.graph.ingest_intent("pii_test", "Call 555-1234 or email john@doe.com", {})
        obj = self.graph.objects["intent:pii_test"]
        content = obj.properties["content"]
        success = "john@doe.com" not in content and "[REDACTED_EMAIL]" in content
        self.results["ent_sovereign"] = success

    def report(self):
        print("\n" + "="*40)
        print(" 📊 STRESS TEST FINAL REPORT 📊")
        print("="*40)
        passed = sum(1 for v in self.results.values() if v)
        print(f"OVERALL SCORE: {passed}/10")
        for k, v in self.results.items():
            status = "✅ PASSED" if v else "❌ FAILED"
            print(f"{k.replace('_', ' ').title():<25} {status}")
        print("="*40)

if __name__ == "__main__":
    test = ForensicStressTest()
    asyncio.run(test.run_all())
