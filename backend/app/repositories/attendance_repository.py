"""
Attendance repository — the only place that queries the `attendance`
table. Joins to Employee where needed (e.g. to return employee_name in
responses) but contains no business rules.
"""

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.attendance import Attendance
from app.models.employee import Employee


def get_by_id(db: Session, attendance_id: int) -> Attendance | None:
    return (
        db.query(Attendance)
        .options(joinedload(Attendance.employee))
        .filter(Attendance.id == attendance_id)
        .first()
    )


def get_by_employee_and_date(
    db: Session, employee_id: int, attendance_date: date
) -> Attendance | None:
    return (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == employee_id,
            Attendance.attendance_date == attendance_date,
        )
        .first()
    )


def create(db: Session, attendance: Attendance) -> Attendance:
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

def save(db: Session, attendance: Attendance) -> Attendance:
    """Persist changes to an already-loaded, already-modified Attendance instance."""
    db.commit()
    db.refresh(attendance)
    return attendance

def list_attendance(
    db: Session,
    employee_id: int | None,
    attendance_date: date | None,
    status: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Attendance], int]:
    query = db.query(Attendance).options(joinedload(Attendance.employee))

    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    if attendance_date:
        query = query.filter(Attendance.attendance_date == attendance_date)
    if status:
        query = query.filter(Attendance.status == status)

    total = query.count()
    query = query.order_by(Attendance.attendance_date.desc())
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return items, total


def list_by_employee(db: Session, employee_id: int) -> list[Attendance]:
    """Full attendance history for one employee, most recent first."""
    return (
        db.query(Attendance)
        .options(joinedload(Attendance.employee))
        .filter(Attendance.employee_id == employee_id)
        .order_by(Attendance.attendance_date.desc())
        .all()
    )

def list_for_export(
    db: Session,
    employee_id: int | None,
    attendance_date: date | None,
    status: str | None,
) -> list[Attendance]:
    """
    Same filters as list_attendance(), deliberately WITHOUT pagination —
    an export needs every matching row, not one page of them. Ordered
    chronologically (oldest first), which reads more naturally in a
    downloaded report than the "newest first" order used for on-screen
    browsing.
    """
    query = db.query(Attendance).options(joinedload(Attendance.employee))

    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    if attendance_date:
        query = query.filter(Attendance.attendance_date == attendance_date)
    if status:
        query = query.filter(Attendance.status == status)

    return query.order_by(Attendance.attendance_date.asc()).all()

def count_today_present(db: Session, today: date) -> int:
    return (
        db.query(func.count(Attendance.id))
        .filter(Attendance.attendance_date == today, Attendance.status == "PRESENT")
        .scalar()
    )


def summary_by_status(db: Session, start_date: date, end_date: date) -> dict:
    """
    One aggregation query: counts of each status within a date range.
    Returns a dict like {"PRESENT": 12, "ABSENT": 3, ...} — callers fill
    in zero for any status with no records rather than us padding here.
    """
    rows = (
        db.query(Attendance.status, func.count(Attendance.id))
        .filter(
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date,
        )
        .group_by(Attendance.status)
        .all()
    )
    return {status: count for status, count in rows}
