import os
import json
import time
from typing import List, Dict, Optional, Any
from pathlib import Path

MEMORY_INDEX_FILENAME = "memory_index.json"

class MemoryPersistence:
    """
    Handles the low-level file I/O for the File-Based Memory System.
    Stores data in a human-readable 3-layer structure:
    1. Resources (Raw Logs)
    2. Items (Atomic Facts)
    3. Categories (Evolving Summaries)
    """

    def __init__(self, base_path: str):
        """
        Initialize persistence with a base directory.
        Args:
            base_path: Absolute path to the root memory directory
                       (e.g. /Users/user/.side/memory)
        """
        self.base_path = Path(base_path)
        self.resources_path = self.base_path / "resources"
        self.items_path = self.base_path / "items"
        self.categories_path = self.base_path / "categories"
        
        # Ensure directories exist
        self.resources_path.mkdir(parents=True, exist_ok=True)
        self.items_path.mkdir(parents=True, exist_ok=True)
        self.categories_path.mkdir(parents=True, exist_ok=True)

    def save_resource(self, user_id: str, content: str, meta: Dict[str, Any] = None) -> str:
        """
        Save a raw resource (conversation log, document, etc.).
        Returns the resource_id.
        """
        timestamp = int(time.time())
        resource_id = f"{timestamp}_{hash(content) & 0xFFFFFF}"
        file_path = self.resources_path / f"{user_id}_{resource_id}.md"
        
        data = {
            "id": resource_id,
            "timestamp": timestamp,
            "meta": meta or {},
            "content": content
        }
        
        # We store as JSON-frontmatter markdown or just simple blocks
        # For simplicity and readability, we'll write a header + content
        file_content = f"""---
id: {resource_id}
timestamp: {timestamp}
meta: {json.dumps(meta or {})}
---

{content}
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)
            
        return resource_id

    def save_item(self, user_id: str, category: str, item_content: str, source_resource_id: str, 
                  rationale: Optional[str] = None, valid_until: Optional[str] = None) -> str:
        """
        Save an atomic item (fact).
        Items are appended to a daily items file for the user to avoid too many small files,
        or essentially kept in a simplistic DB format if needed. 
        For this implementation: We append to a 'items_inbox.jsonl' for processing.
        """
        timestamp = int(time.time())
        item_id = f"item_{timestamp}_{hash(item_content) & 0xFFFF}"
        
        item_data = {
            "id": item_id,
            "timestamp": timestamp,
            "category": category,
            "content": item_content,
            "source_id": source_resource_id,
            "rationale": rationale,
            "valid_until": valid_until
        }
        
        # Append to a JSONL file for that user
        inbox_file = self.items_path / f"{user_id}_inbox.jsonl"
        with open(inbox_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(item_data) + "\n")
            
        return item_id

    def load_category(self, user_id: str, category: str) -> str:
        """
        Load the current summary for a specific category.
        Returns empty string if not exists.
        """
        file_path = self.categories_path / f"{user_id}_{category}.md"
        if not file_path.exists():
            return ""
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def save_category(self, user_id: str, category: str, content: str):
        """
        Overwrite the category summary with new content.
        """
        file_path = self.categories_path / f"{user_id}_{category}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def list_categories(self, user_id: str) -> List[str]:
        """
        List all category names for a user.
        """
        prefix = f"{user_id}_"
        categories = []
        for file in self.categories_path.glob(f"{prefix}*.md"):
            # filename is user_id_category.md
            # remove prefix and suffix
            cat_name = file.stem[len(prefix):]
            categories.append(cat_name)
        return categories

    def load_index(self, user_id: str) -> Dict[str, List[str]]:
        """
        Load the keyword index for the user.
        start_format: {category: [keywords...]}
        """
        file_path = self.base_path / f"{user_id}_{MEMORY_INDEX_FILENAME}"
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_index(self, user_id: str, index_data: Dict[str, List[str]]):
        """
        Save the keyword index.
        """
        file_path = self.base_path / f"{user_id}_{MEMORY_INDEX_FILENAME}"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
