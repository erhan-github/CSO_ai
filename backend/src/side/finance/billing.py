import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

@dataclass
class Transaction:
    id: str
    user_id: str
    amount: float
    currency: str
    status: str
    timestamp: str

class FinanceEngine:
    """
    A simulated billing engine for E2E architectural verification.
    Handles 'Real-World' high-stakes logic: Subscriptions, Tokens, and Cards.
    """
    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self.subscriptions: Dict[str, str] = {} # user_id -> tier
        
    def process_payment(self, user_id: str, amount: float, card_token: str) -> Transaction:
        """
        Simulates a credit card transaction.
        In a real world, this would hit Lemon Squeezy.
        """
        # Logic Gate: Fraud check simulation
        if amount > 10000:
            status = "flagged_for_review"
        elif card_token == "tok_fraud":
            status = "declined"
        else:
            status = "successful"
            
        txn_id = f"txn_{uuid.uuid4().hex[:8]}"
        txn = Transaction(
            id=txn_id,
            user_id=user_id,
            amount=amount,
            currency="USD",
            status=status,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self.transactions[txn_id] = txn
        logger.info(f"FinanceEngine: Processed {txn_id} for {user_id} - {status}")
        return txn

    def upgrade_subscription(self, user_id: str, tier: str):
        """High-stakes logic: State mutation based on billing."""
        self.subscriptions[user_id] = tier
        logger.info(f"FinanceEngine: User {user_id} upgraded to {tier}")
