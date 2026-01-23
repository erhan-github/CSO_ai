from side.intel.memory.persistence import MemoryPersistence
from side.llm.client import LLMClient
import time

class MemoryMaintenance:
    """
    Handles background maintenance tasks for the memory system.
    "Garbage collection" for knowledge.
    """

    def __init__(self, persistence: MemoryPersistence, llm_client: LLMClient):
        self.persistence = persistence
        self.llm = llm_client

    async def run_nightly_consolidation(self, user_id: str):
        """
        Review all categories and compress/clean them up.
        """
        categories = self.persistence.list_categories(user_id)
        
        for category in categories:
            content = self.persistence.load_category(user_id, category)
            if not content:
                continue

            # Re-summarize/clean
            prompt = f"""Review this memory profile for redundancy and clarity.
            Consolidate duplicate points.
            Remove temporal noise (e.g., "User said yesterday...").
            Keep it dense and factual.
            
            Profile:
            {content}
            
            Return ONLY the cleaned markdown profile.
            """
            cleaned = await self.llm.generate(prompt)
            self.persistence.save_category(user_id, category, cleaned)

    async def run_weekly_prune(self, user_id: str):
        """
        Future: Archive rarely used categories or items.
        For now, just a placeholder.
        """
        pass
