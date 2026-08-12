"""
Employee model — the people whose attendance is tracked.

Mirrors the `employees` table in database/init.sql. The `attendance`
relationship below is the ORM-level expression of "one employee has
many attendance records" — it does not create any SQL by itself, it
just lets Python code write `employee.attendance` to get the list,
instead of writing a manual query every time.
"""

from sqlalchemy import Column, String, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.database import Base, BigIntegerPK


class Employee(Base):
    __tablename__ = "employees"

    id = Column(BigIntegerPK, primary_key=True, autoincrement=True)
    employee_code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    mobile = Column(String(10), nullable=False)
    department = Column(String(50), nullable=False)
    designation = Column(String(50), nullable=False)

    # VARCHAR, app-level EmployeeStatus Enum (ACTIVE / INACTIVE).
    # "Delete Employee" sets this to INACTIVE — see Phase 2 soft-delete
    # decision. Never physically removed while attendance history exists.
    status = Column(String(10), nullable=False, server_default="ACTIVE")

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # One employee -> many attendance records.
    # Deliberately NO delete/delete-orphan cascade here. If Python code
    # ever calls db.delete(employee) directly (bypassing the service
    # layer's soft-delete rule), we want that to FAIL LOUDLY — the
    # database's ON DELETE RESTRICT constraint (init.sql) will raise an
    # IntegrityError rather than silently deleting attendance history.
    # An ORM-level delete-orphan cascade would defeat that safety net by
    # deleting the child attendance rows before the FK constraint is
    # ever checked. The default cascade ("save-update, merge") is fine
    # for normal read/relate use — e.g. employee.attendance_records.
    attendance_records = relationship(
        "Attendance",
        back_populates="employee",
    )
