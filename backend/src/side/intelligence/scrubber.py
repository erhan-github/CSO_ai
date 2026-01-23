import re
import logging
from typing import Any, Dict, List, Union
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SovereignScrubber:
    """
    The Security Gate for Sidelith.
    Ensures no PII or secrets enter the Engineering Data Fabric.
    """
    
    # Patterns for redaction
    PATTERNS = {
        "email": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        "ip": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        "bearer_token": r'Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*',
        "aws_key": r'AKIA[0-9A-Z]{12,20}',
        "generic_secret": r'(api_key|secret|password|token|auth_token)["\']?\s*[:=]\s*["\']?[A-Za-z0-9_\-]{12,}'
    }

    def __init__(self, audit_log_path: str = "security_audit.log"):
        self.audit_log_path = audit_log_path
        self._compiled_patterns = {name: re.compile(pat, re.IGNORECASE) for name, pat in self.PATTERNS.items()}

    def scrub_text(self, text: str) -> str:
        """Redacts sensitive info from text."""
        if not text:
            return ""
            
        scrubbed = text
        for name, pattern in self._compiled_patterns.items():
            matches = pattern.findall(scrubbed)
            if matches:
                self._log_redaction(name, len(matches))
                scrubbed = pattern.sub(f"[REDACTED_{name.upper()}]", scrubbed)
        
        return scrubbed

    def scrub_object(self, data: Any) -> Any:
        """Recursively scrubs a dictionary or list."""
        if isinstance(data, str):
            return self.scrub_text(data)
        elif isinstance(data, dict):
            return {k: self.scrub_object(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.scrub_object(v) for v in data]
        return data

    def _log_redaction(self, pattern_name: str, count: int):
        """Audit log for security compliance."""
        ts = datetime.now(timezone.utc).isoformat()
        log_entry = f"[{ts}] SECURITY_EVENT: Redacted {count} instances of {pattern_name}\n"
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"Failed to write security audit log: {e}")

    def validate_ingestion(self, uid: str, obj_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Final checkpoint before ingestion into the GraphKernel.
        Returns scrubbed properties.
        """
        scrubbed_props = self.scrub_object(properties)
        logger.debug(f"Sovereign Scrubber: Validated {uid} ({obj_type})")
        return scrubbed_props
