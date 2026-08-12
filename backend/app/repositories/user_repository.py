"""
User repository — the only place that queries the `users` table.

Repositories are intentionally "dumb": they take/return SQLAlchemy
model instances or primitives, and contain no business rules. If we
ever needed to change HOW users are fetched (e.g. add caching), this
is the only file that would change.
"""

from sqlalchemy.orm import Session

from app.models.user import User


def get_by_username(db: Session, username: str) -> User | None:
    """Fetch a user by username, or None if no such user exists."""
    return db.query(User).filter(User.username == username).first()
