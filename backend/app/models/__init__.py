"""
Importing every model here ensures they're all registered on
Base.metadata as soon as `app.models` is imported anywhere — needed
for SQLAlchemy relationship resolution and for any future tooling
(e.g. Alembic) that inspects Base.metadata.tables.
"""

from app.models.user import User
from app.models.employee import Employee
from app.models.attendance import Attendance

__all__ = ["User", "Employee", "Attendance"]
