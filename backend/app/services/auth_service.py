"""
Auth service — business logic for authentication.

This is the ONLY place that decides "are these credentials valid."
The router calls this and gets back either a token or an exception —
it never touches password verification or the user repository itself.
"""

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.config import settings
from app.exceptions import UnauthorizedException
from app.repositories import user_repository
from app.schemas.auth import LoginResponse


def login(db: Session, username: str, password: str) -> LoginResponse:
    """
    Verify username/password and return a signed JWT on success.

    Deliberately uses the SAME error message ("Invalid username or
    password") whether the username doesn't exist or the password is
    wrong. This is a small but real security detail worth mentioning
    in the interview: revealing "username not found" vs "wrong
    password" tells an attacker which usernames are valid — a form of
    user enumeration. One generic message avoids that.
    """
    user = user_repository.get_by_username(db, username)

    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedException("Invalid username or password")

    token = create_access_token(subject=user.username, role=user.role)

    return LoginResponse(
        access_token=token,
        expires_in_minutes=settings.JWT_EXPIRE_MINUTES,
        username=user.username,
        role=user.role,
    )
