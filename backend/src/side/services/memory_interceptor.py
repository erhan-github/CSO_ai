import logging
import asyncio
from typing import Dict, Any
from side.intel.memory import MemoryManager, MemoryPersistence
from side.llm.client import LLMClient

logger = logging.getLogger("side-memory")

class MemoryInterceptor:
    """
    Intercepts tool calls and explicitly saves relevant context to the 
    File-Based Memory System. 
    """

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    async def intercept(self, tool_name: str, arguments: Dict[str, Any], project_id: str, result: Any = None):
        """
        Fire-and-forget memory interception.
        We don't want to block the user's request, so this should be spawned as a background task.
        """
        # We only care about tools that contain "strategic context"
        INTERESTING_TOOLS = ["strategy", "consult", "brief", "architectural_decision", "audit_deep"]
        
        if tool_name not in INTERESTING_TOOLS:
            return

        try:
            # Construct a narrative based on the tool
            content = ""
            rationale = None

            if tool_name == "strategy":
                ctx = arguments.get("context", "")
                if ctx:
                    content = f"User asked for strategic advice on: {ctx}"
                # If result is provided (usually a plan string), use specific parts as rationale
                if isinstance(result, str):
                    rationale = result[:500] + "..." if len(result) > 500 else result

            elif tool_name == "consult":
                question = arguments.get("question", "")
                content = f"User consulted on decision: {question}"
                if isinstance(result, str):
                    rationale = result

            if content:
                logger.info(f"🧠 Memorizing interaction: {content[:50]}...")
                # We save with specific metadata
                await self.memory.memorize(
                    user_id=project_id, 
                    content=content, 
                    meta={"source": "tool_interceptor", "tool": tool_name},
                    rationale=rationale
                )
        except Exception as e:
            logger.error(f"Failed to memorize interaction: {e}")
            
        # LIVE WIRE: Trigger Monolith Update
        try:
            from side.storage.simple_db import SimplifiedDatabase
            from side.services.monolith import generate_monolith
            
            # Initialize with default path
            # Since this is a distinct service, we instantiate a fresh DB accessor
            # which connects to the same SQLite file.
            db = SimplifiedDatabase()
            
            await generate_monolith(db)
            logger.info("🏛️ Monolith Updated (Live Wire)")
        except Exception as e:
            logger.warning(f"Live Wire update failed: {e}")

