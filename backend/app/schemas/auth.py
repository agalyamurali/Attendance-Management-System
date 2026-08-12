"""
Pydantic schemas for the auth endpoints.

Why schemas are separate from models:
    Employee/User/Attendance SQLAlchemy models describe DATABASE shape.
    These classes describe API CONTRACT shape — what the client sends
    and receives. They're not always the same (e.g. LoginResponse
    includes a token that has nothing to do with the users table).
    Keeping them separate means changing the API shape never risks
    accidentally changing the DB schema, and vice versa.
"""

from pydantic import BaseModel, Field

from app.core.enums import UserRole


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, examples=["admin"])
    password: str = Field(..., min_length=1, examples=["Admin@123"])


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    username: str
    role: UserRole


class CurrentUserResponse(BaseModel):
    username: str
    role: UserRole
