"""
Attendance service — business rules for marking, viewing, and
exporting attendance.

Rules enforced here (per the confirmed spec):
    1. Employee must exist                         -> NotFoundException
    2. Employee must be ACTIVE                      -> ValidationException
    3. No duplicate attendance for employee+date     -> ConflictException
       (checked here for a clean error message; the DB UNIQUE
       constraint in database/init.sql is the real race-condition-safe
       guarantee — see Phase 2 "defense in depth" reasoning)
    4. check_out >= check_in, and check-in/check-out requirements per
       status                                        -> enforced in the
       Pydantic schema (AttendanceCreate), not here, since it needs no
       database lookup — pure request-shape validation belongs there.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.attendance import Attendance
from app.repositories import attendance_repository, employee_repository
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceSummaryResponse,
)


def _to_response(attendance: Attendance) -> AttendanceResponse:
    """
    Build the response schema, pulling employee_code/name from the
    joined Employee row. Centralized here so every endpoint that
    returns attendance data shapes it identically.
    """
    return AttendanceResponse(
        id=attendance.id,
        employee_id=attendance.employee_id,
        employee_code=attendance.employee.employee_code,
        employee_name=attendance.employee.name,
        attendance_date=attendance.attendance_date,
        check_in=attendance.check_in,
        check_out=attendance.check_out,
        status=attendance.status,
        created_at=attendance.created_at,
        updated_at=attendance.updated_at,
    )


def mark_attendance(db: Session, payload: AttendanceCreate) -> AttendanceResponse:
    employee = employee_repository.get_by_id(db, payload.employee_id)
    if employee is None:
        raise NotFoundException(f"Employee with id {payload.employee_id} not found")

    if employee.status != "ACTIVE":
        raise ValidationException(
            f"Cannot mark attendance for employee '{employee.name}' — employee is INACTIVE"
        )

    existing = attendance_repository.get_by_employee_and_date(
        db, payload.employee_id, payload.attendance_date
    )
    if existing is not None:
        raise ConflictException(
            f"Attendance for employee {payload.employee_id} on "
            f"{payload.attendance_date} is already recorded"
        )

    attendance = Attendance(**payload.model_dump())
    saved = attendance_repository.create(db, attendance)
    # Reload with the employee relationship populated for the response
    saved = attendance_repository.get_by_id(db, saved.id)
    return _to_response(saved)


def get_attendance(db: Session, attendance_id: int) -> AttendanceResponse:
    attendance = attendance_repository.get_by_id(db, attendance_id)
    if attendance is None:
        raise NotFoundException(f"Attendance record with id {attendance_id} not found")
    return _to_response(attendance)


def list_attendance(
    db: Session,
    employee_id: int | None,
    attendance_date: date | None,
    status: str | None,
    page: int,
    page_size: int,
) -> tuple[list[AttendanceResponse], int]:
    items, total = attendance_repository.list_attendance(
        db, employee_id, attendance_date, status, page, page_size
    )
    return [_to_response(item) for item in items], total


def employee_attendance_history(db: Session, employee_id: int) -> list[AttendanceResponse]:
    employee = employee_repository.get_by_id(db, employee_id)
    if employee is None:
        raise NotFoundException(f"Employee with id {employee_id} not found")

    records = attendance_repository.list_by_employee(db, employee_id)
    return [_to_response(record) for record in records]


def attendance_summary(
    db: Session, start_date: date, end_date: date
) -> AttendanceSummaryResponse:
    counts = attendance_repository.summary_by_status(db, start_date, end_date)
    total = sum(counts.values())

    return AttendanceSummaryResponse(
        start_date=start_date,
        end_date=end_date,
        total_records=total,
        present=counts.get("PRESENT", 0),
        absent=counts.get("ABSENT", 0),
        half_day=counts.get("HALF_DAY", 0),
        on_leave=counts.get("ON_LEAVE", 0),
    )


def get_export_data(
    db: Session,
    employee_id: int | None,
    attendance_date: date | None,
    status: str | None,
) -> tuple[list[dict], str]:
    """
    Fetch the rows for an export and decide the filename.

    Returns (rows, filename_base) — rows are plain dicts (not
    AttendanceResponse objects) since export_service.py works with
    simple dicts, not knowing anything about our Pydantic schemas.

    filename_base has no extension yet — the router appends .csv or
    .xlsx depending on the requested format, so this function doesn't
    need to know about file formats at all.

    This doubles as "per-employee export" and "general export": when
    employee_id is provided, the filter narrows the same query down
    to one employee — there's no separate endpoint or code path for
    that case, just a different query parameter. Simpler to build,
    simpler to explain, and there's only one export implementation to
    keep correct.
    """
    if employee_id is not None:
        employee = employee_repository.get_by_id(db, employee_id)
        if employee is None:
            raise NotFoundException(f"Employee with id {employee_id} not found")
        filename_base = f"attendance_{employee.employee_code}"
    else:
        filename_base = f"attendance_export_{date.today().isoformat()}"

    records = attendance_repository.list_for_export(db, employee_id, attendance_date, status)

    rows = [
        {
            "employee_code": r.employee.employee_code,
            "employee_name": r.employee.name,
            "attendance_date": r.attendance_date.isoformat(),
            "check_in": r.check_in.strftime("%H:%M") if r.check_in else "",
            "check_out": r.check_out.strftime("%H:%M") if r.check_out else "",
            "status": r.status,
        }
        for r in records
    ]

    return rows, filename_base