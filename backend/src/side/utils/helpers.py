from typing import Any, Dict, TypeVar, Optional

T = TypeVar("T")

def safe_get(data: Dict[str, Any], key: str, default: Optional[T] = None) -> T:
    """Safe dictionary retrieval helper."""
    if not data or not isinstance(data, dict):
        return default
    return data.get(key, default)

def parse_int_safe(value: Any, default: int = 0) -> int:
    """Safely parse integer from string/float."""
    try:
        if value is None: 
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default
