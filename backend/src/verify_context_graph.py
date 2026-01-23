
import asyncio
import os
import shutil
import time
from pathlib import Path
from side.intel.memory import MemoryPersistence, MemoryManager, MemoryRetrieval
from side.llm.client import LLMClient

# Mock LLM Client to avoid actual API calls and costs
class MockLLMClient(LLMClient):
    async def complete_async(self, messages, system_prompt=None, **kwargs):
        # Determine behavior based on prompt content
        content = messages[0]['content']
        if "Extract discrete facts" in content:
            return '[{"content": "Project uses Python"}, {"content": "Server port is 8000"}]'
        elif "Classify this fact" in content:
            return "project_specs"
        elif "Evolve Summaries" in content:
            return "## Project Specs\n- Project uses Python\n- Server port is 8000"
        elif "Generate 10-20 search keywords" in content:
            return '["python", "port", "specs"]'
        elif "Memory Synchronization" in content:
             return messages[0]['content'].split("## New Memory Items to Integrate")[1].strip()
        return "mock_response"

async def test_decision_traces(persistence, manager):
    print("--- Testing Decision Traces ---")
    user_id = "test_user_traces"
    rationale = "Because Python is great for AI."
    
    await manager.memorize(
        user_id=user_id,
        content="We decided to use Python.",
        rationale=rationale
    )
    
    # Verify directly in file
    inbox_file = persistence.items_path / f"{user_id}_inbox.jsonl"
    assert inbox_file.exists()
    with open(inbox_file, "r") as f:
        data = f.read()
        assert rationale in data
        print("✅ Rationale successfully saved to inbox.")

async def test_temporal_validity(persistence, retrieval):
    print("\n--- Testing Temporal Validity ---")
    user_id = "test_user_time"
    category = "time_sensitive"
    
    # 1. Save an expired memory
    # We manually create a category file with an expired tag since the manager logic 
    # for resolving dates into the summary text is complex/LLM-dependent.
    # We are testing the VALIDITY ENFORCEMENT (Retrieval), not the extraction.
    expired_content = "This fact is old. [Expires: 1999-01-01]\nThis fact is forever."
    persistence.save_category(user_id, category, expired_content)
    
    # 2. Fake an index entry so retrieval finds it
    persistence.save_index(user_id, {category: ["fact"]})
    
    # 3. Retrieve
    result = await retrieval.retrieve("fact", user_id)
    
    assert "This fact is old" not in result
    assert "This fact is forever" in result
    print("✅ Expired content successfully filtered out.")

async def test_smart_context_budget(persistence, retrieval):
    print("\n--- Testing Smart Context Budget ---")
    user_id = "test_user_budget"
    
    # Create 5 categories
    for i in range(5):
        cat = f"cat_{i}"
        persistence.save_category(user_id, cat, f"Content for {cat}")
        
    # Create index matching all of them
    index = {f"cat_{i}": ["budget"] for i in range(5)}
    persistence.save_index(user_id, index)
    
    # Retrieve with limit 2
    result = await retrieval.retrieve("budget", user_id, limit=2)
    
    # Count how many headers we got
    count = result.count("## Memory:")
    assert count == 2
    print(f"✅ Budget enforcement worked. Requested 2, got {count}.")

async def main():
    base_path = Path("./test_memory_context_graph")
    if base_path.exists():
        shutil.rmtree(base_path)
    base_path.mkdir()
    
    persistence = MemoryPersistence(str(base_path))
    llm = MockLLMClient()
    manager = MemoryManager(persistence, llm)
    retrieval = MemoryRetrieval(persistence, llm)
    
    try:
        await test_decision_traces(persistence, manager)
        await test_temporal_validity(persistence, retrieval)
        await test_smart_context_budget(persistence, retrieval)
        print("\n🎉 All Context Graph features verified!")
    finally:
        if base_path.exists():
            shutil.rmtree(base_path)

if __name__ == "__main__":
    asyncio.run(main())
