
from passlib.context import CryptContext
from typing import Optional

# Safe password context using bcrypt
# We use bcrypt for its widespread support and resistance to GPU attacks
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """
    Securely hash a password using bcrypt.
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def is_safe_hash(hash_str: str) -> bool:
    """
    Check if a hash string looks like a bcrypt hash.
    """
    return hash_str.startswith("$2b$") or hash_str.startswith("$2a$")
