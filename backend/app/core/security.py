"""
Security primitives: password hashing and JWT create/decode.

Why this file exists:
    This is the ONLY file that touches bcrypt or JWT signing directly.
    Services call these functions without knowing HOW passwords are
    hashed or HOW tokens are signed — if either mechanism ever changed
    (e.g. bcrypt -> argon2), this is the only file that would change.

Two independent concerns live here, kept as separate functions:
    1. Password hashing  — hash_password() / verify_password()
    2. JWT tokens         — create_access_token() / decode_access_token()
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# --- Password hashing ---

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password for storage. Never store the plain password."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain-text password against a stored bcrypt hash."""
    return _pwd_context.verify(plain_password, password_hash)


# --- JWT ---


def create_access_token(subject: str, role: str) -> str:
    """
    Create a signed JWT for an authenticated user.

    `subject` is the username (stored in the standard "sub" claim).
    `role` is included so protected routes can check authorization
    (e.g. "is this user an ADMIN") without a second database lookup
    on every request.

    Expiry is read from settings (JWT_EXPIRE_MINUTES) — no refresh
    tokens, per the confirmed Phase 1 decision.
    """
    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "role": role, "exp": expire_at}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT.

    Raises jose.JWTError if the token is expired, malformed, or signed
    with a different secret. The caller (core/dependencies.py) is
    responsible for turning that into a clean 401 response — this
    function's only job is decode-or-raise.
    """
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
