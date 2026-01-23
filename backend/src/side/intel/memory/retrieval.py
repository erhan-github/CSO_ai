from typing import List, Dict
from side.intel.memory.persistence import MemoryPersistence
from side.llm.client import LLMClient

class MemoryRetrieval:
    """
    Handles the 'Read Path' of the memory system.
    Uses tiered retrieval to find relevant context without overloading the prompt.
    """

    def __init__(self, persistence: MemoryPersistence, llm_client: LLMClient):
        self.persistence = persistence
        self.llm = llm_client

    async def retrieve(self, query: str, user_id: str, limit: int = 5) -> str:
        """
        Main entry point. Find relevant memories for the query.
        Uses deterministic keyword matching via the memory index.
        """
        # 1. Load the Index
        index = self.persistence.load_index(user_id)
        if not index:
            # Fallback: If no index, maybe just return nothing or everything?
            # Let's be safe and return nothing to avoid context flooding,
            # unless the user has very few categories.
            all_cats = self.persistence.list_categories(user_id)
            if len(all_cats) <= 3:
                # If very few memories, just dump them all
                index = {c: [] for c in all_cats}
            else:
                return ""

        # 2. Tokenize Query (Simple set of lowercase words)
        query_tokens = set(query.lower().split())
        
        # 3. Score Categories
        scores = {}
        for category, keywords in index.items():
            # Match if category name is in query
            score = 0
            if category in query.lower():
                score += 5
            
            # Match keywords
            for token in query_tokens:
                if token in keywords:
                    score += 1
                # Partial match for longer keywords? 
                # Keep it simple and scalable for now.
            
            if score > 0:
                scores[category] = score
        
        # Always include 'critical' categories if they exist
        defaults = ["project_rules", "user_preferences", "tech_stack"]
        for d in defaults:
            if d in index:
                scores[d] = scores.get(d, 0) + 1  # Give them a nudge
        
        # 4. Select Top N
        # Sort by score descending
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_cats = [c for c, s in sorted_cats if s > 0][:limit] # Max 'limit' relevant files

        if not top_cats:
            return ""

        # 5. Load Content
        context_parts = []
        for cat in top_cats:
            content = self.persistence.load_category(user_id, cat)
            if content:
                # Filter out expired lines
                content = self._filter_expired(content)
                if content.strip():
                    context_parts.append(f"## Memory: {cat.replace('_', ' ').title()}\n{content}")
        
        return "\n\n".join(context_parts)

    def _filter_expired(self, content: str) -> str:
        """
        Parses markdown content and removes lines with expired timestamps.
        Format expected: "... [Expires: YYYY-MM-DD] ..."
        """
        import re
        from datetime import datetime

        lines = content.split('\n')
        active_lines = []
        now = datetime.now()

        for line in lines:
            # Check for [Expires: YYYY-MM-DD]
            match = re.search(r'\[Expires:\s*(\d{4}-\d{2}-\d{2})\]', line)
            if match:
                try:
                    expiry_date = datetime.strptime(match.group(1), "%Y-%m-%d")
                    if now > expiry_date:
                        continue # Skip expired line
                except ValueError:
                    pass # Invalid date format, keep line for safety
            
            active_lines.append(line)
        
        return '\n'.join(active_lines)
