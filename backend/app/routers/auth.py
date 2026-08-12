"""
Auth router — HTTP layer for authentication.

Thin by design: parses the request via LoginRequest, calls
auth_service.login(), returns whatever it gets back. All the actual
decision-making (is this password correct, what goes in the token)
lives in the service layer, not here.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.auth import CurrentUserResponse, LoginRequest, LoginResponse
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with username/password and receive a JWT.

    On success: 200 with access_token, token_type, expiry, and user info.
    On failure: 401 with a generic "Invalid username or password" message
    (see auth_service.login for why the message is intentionally generic).
    """
    return auth_service.login(db, payload.username, payload.password)


@router.get("/me", response_model=CurrentUserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user.

    Exists mainly as a simple way to prove the JWT + protected-route
    flow works end-to-end — useful for testing and for demonstrating
    the "protected API" requirement during the review without needing
    a real business endpoint.
    """
    return current_user
