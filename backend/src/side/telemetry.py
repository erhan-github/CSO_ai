import os
import time
import functools
from typing import Any, Callable
from side.logging_config import get_logger

logger = get_logger(__name__)

# Mock Posthog if not configured
class MockPosthog:
    def capture(self, *args, **kwargs):
        pass
    def identify(self, *args, **kwargs):
        pass

ph_client = MockPosthog()

# Initialize Posthog if credentials exist
try:
    from posthog import Posthog
    api_key = os.getenv("POSTHOG_API_KEY")
    host = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
    if api_key:
        ph_client = Posthog(api_key, host=host)
        logger.info("PostHog initialized")
except ImportError:
    pass


def telemetry(event_name: str):
    """Decorator to track tool execution time and success/failure."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            # Try to extract project_id or user_id for context
            context_id = os.getenv("SIDE_PROJECT_ID", "anonymous")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                ph_client.capture(
                    context_id,
                    f"tool_{event_name}_success",
                    {
                        "duration_sec": duration,
                        "tool": func.__name__,
                        "status": "success"
                    }
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                ph_client.capture(
                    context_id,
                    f"tool_{event_name}_failure",
                    {
                        "duration_sec": duration,
                        "tool": func.__name__,
                        "status": "failure",
                        "error": str(e)
                    }
                )
                raise e
        return wrapper
    return decorator
