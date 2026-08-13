"""
Attendance router — HTTP layer for marking, viewing, updating, and
exporting attendance. All routes require authentication.
"""

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceListResponse,
    AttendanceResponse,
    AttendanceSummaryResponse,
    AttendanceUpdate,
)
from app.services import attendance_service, export_service

router = APIRouter(
    prefix="/api/attendance",
    tags=["Attendance"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=AttendanceResponse, status_code=201)
def mark_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    """
    Mark attendance for an employee on a given date.

    Validation, in order: employee must exist (404), employee must be
    ACTIVE (422), no duplicate for that employee+date (409), and
    check-in/check-out requirements depend on status, plus
    attendance_date cannot be in the future (422, both enforced by the
    request schema — see AttendanceCreate in app/schemas/attendance.py).

    To add or correct a check-out time (or anything else) on a record
    that already exists, use PUT /api/attendance/{id} instead of
    calling this again — a second POST for the same employee/date will
    correctly be rejected as a duplicate (409).
    """
    return attendance_service.mark_attendance(db, payload)


@router.get("", response_model=AttendanceListResponse)
def list_attendance(
    db: Session = Depends(get_db),
    employee_id: int | None = Query(None),
    attendance_date: date | None = Query(None),
    status: str | None = Query(None, description="PRESENT, ABSENT, HALF_DAY, or ON_LEAVE"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """List attendance records, optionally filtered by employee, date, or status."""
    items, total = attendance_service.list_attendance(
        db, employee_id, attendance_date, status, page, page_size
    )
    return AttendanceListResponse(data=items, total=total, page=page, page_size=page_size)


@router.get("/summary", response_model=AttendanceSummaryResponse)
def attendance_summary(
    db: Session = Depends(get_db),
    start_date: date | None = Query(None, description="Defaults to today if omitted"),
    end_date: date | None = Query(None, description="Defaults to today if omitted"),
):
    """Aggregated attendance counts by status for a date range (default: today)."""
    today = date.today()
    return attendance_service.attendance_summary(
        db, start_date or today, end_date or today
    )


@router.get("/export")
def export_attendance(
    db: Session = Depends(get_db),
    format: Literal["csv", "xlsx"] = Query("csv"),
    employee_id: int | None = Query(
        None, description="If given, exports only this employee's history (per-employee export)"
    ),
    attendance_date: date | None = Query(None),
    status: str | None = Query(None, description="PRESENT, ABSENT, HALF_DAY, or ON_LEAVE"),
):
    """
    Export attendance records as a downloadable CSV or XLSX file.

    Same filters as GET /api/attendance, minus pagination — an export
    returns every matching row. Passing employee_id narrows this to a
    single employee's full history, which is how both the general
    "Export" button (no employee_id) and the per-employee "Export
    History" button (employee_id set) are served by one endpoint.

    404 if employee_id is given but doesn't exist.
    """
    rows, filename_base = attendance_service.get_export_data(
        db, employee_id, attendance_date, status
    )

    if format == "xlsx":
        content = export_service.to_xlsx_bytes(rows)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{filename_base}.xlsx"
    else:
        content = export_service.to_csv_bytes(rows)
        media_type = "text/csv"
        filename = f"{filename_base}.csv"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/employee/{employee_id}", response_model=list[AttendanceResponse])
def employee_attendance_history(employee_id: int, db: Session = Depends(get_db)):
    """Full attendance history for one employee, most recent first. 404 if employee doesn't exist."""
    return attendance_service.employee_attendance_history(db, employee_id)


# NOTE: this generic /{attendance_id} route is registered LAST, after
# every other more specific literal path (/summary, /export,
# /employee/{employee_id}). FastAPI matches routes in registration
# order — if this were declared earlier, a request to /export would
# incorrectly match here first, with "export" parsed as attendance_id.


@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """Fetch a single attendance record by id. 404 if not found."""
    return attendance_service.get_attendance(db, attendance_id)


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id: int, payload: AttendanceUpdate, db: Session = Depends(get_db)):
    """
    Update an existing attendance record — status, check_in, and/or
    check_out. This is how a check_out time gets added after the fact:
    mark PRESENT with just check_in in the morning (POST), then call
    this endpoint later in the day with check_out filled in.

    employee_id and attendance_date cannot be changed here (see
    AttendanceUpdate). 404 if the record doesn't exist; 422 if the
    check-in/check-out values don't match the requested status.
    """
    return attendance_service.update_attendance(db, attendance_id, payload)