"""
Billing Service - Manages Strategic Units (SUs) and Access Control.
"""
from enum import Enum
from typing import Optional, Dict, Any
import logging
from side.storage.simple_db import SimplifiedDatabase, InsufficientTokensError

logger = logging.getLogger(__name__)

class SystemAction(Enum):
    SCAN_QUICK = "scan_quick"
    SCAN_DEEP = "scan_deep"
    FIX_AGENT = "fix_agent"
    STRATEGY_CHAT = "strategy_chat"
    NUDGE = "nudge"
    MONOLITH_UPDATE = "monolith_update"

# Capacity Table (Strategic Units - SUs)
# SUs represent the risk envelope and compute budget allocated to the user.
COSTS = {
    SystemAction.SCAN_QUICK: 1,      # Conservative check
    SystemAction.SCAN_DEEP: 1,       # High-compute audit
    SystemAction.FIX_AGENT: 1,       # Deep orchestration
    SystemAction.STRATEGY_CHAT: 1,   # Contextual reasoning
    SystemAction.NUDGE: 1,           # Proactive check
    SystemAction.MONOLITH_UPDATE: 0  # State synchronization (FREE)
}

class BillingService:
    def __init__(self, db: SimplifiedDatabase):
        self.db = db

    def claim_trial(self, project_path: str) -> bool:
        """
        Anti-Abuse Logic: 'The Repository Lock'.
        
        1. Hash 'git remote origin' + Machine ID.
        2. Check against Cloud Ledger (Stubbed).
        3. If claimed -> Grant 0.
        4. If new -> Grant 2000.
        
        Returns: True if trial granted (50 SUs), False if already claimed (0 SUs).
        """
        import hashlib
        import subprocess
        
        # 1. Get Repo Hash
        repo_hash = "local_only"
        try:
            # Try to get git remote
            remote_url = subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"], 
                cwd=project_path, 
                stderr=subprocess.DEVNULL
            ).decode().strip()
            repo_hash = hashlib.sha256(remote_url.encode()).hexdigest()
        except Exception:
            # Fallback: Path Hash (weak, but better than nothing)
            repo_hash = hashlib.sha256(str(project_path).encode()).hexdigest()

        # 2. Check Cloud (Palantir-Level Verification)
        from side.auth.supabase_auth import verify_trial_claim_cloud
        
        # Machine ID (Stub for now, usually getnode())
        import uuid
        machine_id = str(uuid.getnode())
        
        result = verify_trial_claim_cloud(repo_hash, machine_id)
        
        if not result.get("granted"):
            # Update to 0
            grant_amount = 0
            # logger.warning(f"Trial Denied: {result.get('reason')}")
        else:
            grant_amount = result.get("amount", 50)
        
        # Update DB
        project_id = self.db.get_project_id(project_path)
        with self.db._connection() as conn:
             # Force set
             conn.execute(
                 "UPDATE profile SET token_balance = ? WHERE id = ?",
                 (grant_amount, project_id)
             )
             
        return result.get("granted", False)

    # Daily Drips removed. Capacity is adjusted based on demonstrated outcome leverage.

    def get_cost(self, action: SystemAction) -> int:
        return COSTS.get(action, 0)

    def can_afford(self, project_id: str, action: SystemAction) -> bool:
        """Check if project has enough capacity for action."""
        
        cost = self.get_cost(action)
        if cost == 0:
            return True
            
        try:
            balance_info = self.db.get_token_balance(project_id)
            return balance_info["balance"] >= cost
        except Exception:
            return False

    def charge(self, project_id: str, action: SystemAction, tool_name: str, payload: Dict[str, Any] = None) -> int:
        """
        Deduct SUs for an action.
        
        Args:
            project_id: The project ID
            action: The system action being performed
            tool_name: The tool causing the charge (for audit log)
            payload: Optional metadata
            
        Returns:
            int: New balance
            
        Raises:
            InsufficientTokensError: If balance is too low
        """
        cost = self.get_cost(action)
        
        # If free, just log and return
        if cost == 0:
            self.db.log_activity(project_id, tool_name, action.value, 0, "unknown", payload)
            # Need to fetch balance just to return it
            # Or return -1? No, best to return actual.
            info = self.db.get_token_balance(project_id)
            return info["balance"]
            
        # Deduct
        try:
            # 1. Try to deduct locally
            new_balance = self.db.update_token_balance(project_id, -cost)
            
            # 2. Log successful transaction
            info = self.db.get_token_balance(project_id)
            self.db.log_activity(project_id, tool_name, action.value, cost, info["tier"], payload)
            
            return new_balance
            
        except InsufficientTokensError:
            # [Instant Gratification Protocol]
            # If funds are low, check Cloud Ledger IMMEDIATELY before failing.
            # The user might have just paid on the web.
            logger.info(f"Funds low for {action.value}. Attempting Cloud Sync...")
            
            if self.sync_credits(project_id):
                # Retry deduction with new balance
                try:
                    new_balance = self.db.update_token_balance(project_id, -cost)
                    info = self.db.get_token_balance(project_id)
                    self.db.log_activity(project_id, tool_name, action.value, cost, info["tier"], payload)
                    logger.info("✅ Payment detected! Transaction succeeded.")
                    return new_balance
                except InsufficientTokensError:
                    pass # Still broke after sync
                    
            logger.warning(f"Project {project_id} attempted {action.value} without funds.")
            raise

    def sync_credits(self, project_id: str) -> bool:
        """
        Check Cloud Ledger for recent Top-Ups.
        Returns True if balance increased.
        """
        # 1. Get API Key from Env
        import os
        from side.auth.supabase_auth import get_cloud_balance
        
        api_key = os.getenv("SIDE_API_KEY")
        if not api_key:
            return False
            
        # 2. Query Cloud
        cloud_balance = get_cloud_balance(api_key)
        if cloud_balance is None:
            return False
            
        # 3. Compare with Local
        try:
            local_info = self.db.get_token_balance(project_id)
            local_balance = local_info["balance"]
            
            # 4. Sync Strategy: Trust the Higher Number (or strictly Cloud?)
            # Usually Cloud is Truth. But if Local is higher (maybe offline usage?),
            # we should update Cloud. But here we assume Web Purchase -> Cloud High -> Local Low.
            if cloud_balance > local_balance:
                delta = cloud_balance - local_balance
                self.top_up(project_id, delta, "cloud_sync")
                return True
                
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            
        return False

    def top_up(self, project_id: str, amount: int, source: str) -> int:
        """
        Adjust Capacity for project.
        """
        new_balance = self.db.update_token_balance(project_id, amount)
        
        info = self.db.get_token_balance(project_id)
        self.db.log_activity(
            project_id, 
            "billing", 
            "capacity_adjustment", 
            amount, 
            info["tier"], 
            {"source": source}
        )
        return new_balance
