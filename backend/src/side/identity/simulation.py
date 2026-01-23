import logging
import time
import secrets
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)

@dataclass
class User:
    id: str
    username: str
    email: str
    tier: str = "free"

class IdentitySimulator:
    """
    Simulates a User Management and Auth system.
    Provides 'Real tokens' and session state for E2E verification.
    """
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.active_tokens: Dict[str, str] = {} # token -> user_id
        
    def create_user(self, username: str, email: str) -> User:
        user_id = f"user_{secrets.token_hex(4)}"
        user = User(id=user_id, username=username, email=email)
        self.users[user_id] = user
        logger.info(f"IdentitySimulator: Created user {username} ({user_id})")
        return user

    def login(self, username: str) -> str:
        """Simulate login and return a token."""
        for user in self.users.values():
            if user.username == username:
                token = f"sk_live_{secrets.token_urlsafe(16)}"
                self.active_tokens[token] = user.id
                logger.info(f"IdentitySimulator: User {username} logged in with token.")
                return token
        raise ValueError("User not found")

    def get_user_from_token(self, token: str) -> Optional[User]:
        user_id = self.active_tokens.get(token)
        if user_id:
            return self.users.get(user_id)
        return None
