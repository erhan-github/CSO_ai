"""
Anonymous Telemetry Service for Side.

Sends non-PII health metrics to Supabase to enable product observability
while maintaining 100% user privacy.
"""

import asyncio
import logging
import os
import platform
import sys
from datetime import datetime, timezone
from typing import Dict, Any

from supabase import create_client, Client

logger = logging.getLogger(__name__)

class TelemetryService:
    """
    Handles anonymous heartbeat and error reporting to Supabase.
    """

    def __init__(self, project_hash: str):
        self.project_hash = project_hash
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        self.client: Client | None = None
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
            except Exception as e:
                logger.error(f"Telemetry client failed to init: {e}")
        
    async def run_forever(self, interval: int = 3600) -> None:
        """
        Sends an anonymous heartbeat every hour.
        """
        if not self.client:
            logger.debug("Telemetry disabled (no credentials).")
            return

        logger.info("Starting Anonymous Telemetry Heartbeat.")
        
        while True:
            try:
                await self.send_heartbeat()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Telemetry error: {e}")
                await asyncio.sleep(600) # Wait 10 mins on error

    async def send_heartbeat(self) -> None:
        """Send an anonymous pulse to Supabase & PostHog."""
        payload = {
            "project_hash": self.project_hash,
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": sys.version.split()[0],
            "app_version": "0.1.0", 
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # 1. Supabase (Legacy/Backup)
        if self.client:
            try:
                self.client.table("heartbeats").insert(payload).execute()
            except Exception as e:
                logger.debug(f"Supabase heartbeat failed: {e}")

        # 2. PostHog (Investor Metrics)
        await self._send_to_posthog("heartbeat", payload)
        logger.debug("Telemetry heartbeat sent.")

    async def report_error(self, error_type: str, context: str) -> None:
        """Report anonymous error."""
        import re
        scrubbed_context = re.sub(r'/[Uu]sers/[^/]+/', '/USER/', context)
        scrubbed_context = re.sub(r'(?i)(key|token|secret|password)[=" \']+[^\s]+', r'\1=[REDACTED]', scrubbed_context)

        payload = {
            "project_hash": self.project_hash,
            "error_type": error_type,
            "context": scrubbed_context[:1000],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # 1. Supabase
        if self.client:
            try:
                self.client.table("error_logs").insert(payload).execute()
            except Exception:
                pass 
        
        # 2. PostHog
        await self._send_to_posthog("error", payload)

    async def _send_to_posthog(self, event: str, properties: Dict[str, Any]) -> None:
        """Send event to PostHog via HTTP (No SDK dependency to keep binary small)."""
        ph_key = os.environ.get("POSTHOG_API_KEY")
        if not ph_key: return

        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    "https://app.posthog.com/capture/",
                    json={
                        "api_key": ph_key,
                        "event": event,
                        "distinct_id": self.project_hash,
                        "properties": properties,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    },
                    timeout=2
                )
        except Exception:
            pass # Fail silently

