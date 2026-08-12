"""
User model — login accounts for administrators.

Mirrors the `users` table in database/init.sql exactly (column names,
types, constraints). This file has ONE job: describe the table shape
to SQLAlchemy. No password hashing, no login logic — that belongs in
core/security.py and services/auth_service.py (Phase 5).
"""

from sqlalchemy import Column, String, TIMESTAMP, func

from app.database import Base, BigIntegerPK


class User(Base):
    __tablename__ = "users"

    id = Column(BigIntegerPK, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)

    # VARCHAR, not a DB enum — validity enforced by the app-level
    # UserRole Python Enum (Phase 5), consistent with the decision
    # documented in database/init.sql.
    role = Column(String(20), nullable=False, server_default="ADMIN")

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )
