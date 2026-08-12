"""
Attendance model — one row per employee per date.

Mirrors the `attendance` table in database/init.sql, including the two
constraints that carry real business meaning:
    - UNIQUE(employee_id, attendance_date): no duplicate attendance,
      enforced at the DB level (race-condition safe).
    - ondelete="RESTRICT" on the FK: the database refuses to delete an
      employee that still has attendance rows (see Phase 2 decision —
      attendance history is preserved, "delete" is really a soft
      deactivation at the service layer).
"""

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    ForeignKey,
    String,
    TIMESTAMP,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base, BigIntegerPK


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(BigIntegerPK, primary_key=True, autoincrement=True)

    employee_id = Column(
        BigInteger,
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
    )

    attendance_date = Column(Date, nullable=False)
    check_in = Column(Time, nullable=True)   # nullable: ABSENT has no check-in
    check_out = Column(Time, nullable=True)

    # VARCHAR, app-level AttendanceStatus Enum (PRESENT / ABSENT /
    # HALF_DAY / ON_LEAVE) — see documented trade-off in init.sql.
    status = Column(String(15), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    employee = relationship("Employee", back_populates="attendance_records")

    __table_args__ = (
        UniqueConstraint(
            "employee_id", "attendance_date", name="uq_attendance_employee_date"
        ),
    )
