"""
Pydantic schemas for the attendance endpoints.

Field-level validation lives here (check-out >= check-in, valid date).
Cross-record rules that need a database lookup (employee exists and is
ACTIVE, no duplicate for the same date) belong in the service layer,
not here — a schema can only see the data in the request itself.
"""

from datetime import date, datetime, time

from pydantic import BaseModel, model_validator

from app.core.enums import AttendanceStatus


def _validate_check_in_out_against_status(status: AttendanceStatus, check_in, check_out) -> None:
    """
    Shared by both AttendanceCreate and AttendanceUpdate so the rule
    can never drift between "creating" and "editing" a record — one
    definition, used in two places, rather than two copies that could
    quietly diverge over time.

    Check-in/check-out requirements depend on the attendance status:

        PRESENT   -> check_in REQUIRED, check_out optional
                     (an employee may still be at work when marked;
                     check_out is typically added later via PUT once
                     they actually leave — see AttendanceUpdate)
        HALF_DAY  -> check_in REQUIRED, check_out optional
        ABSENT    -> check_in and check_out must both be EMPTY
        ON_LEAVE  -> check_in and check_out must both be EMPTY
    """
    requires_check_in = status in (AttendanceStatus.PRESENT, AttendanceStatus.HALF_DAY)
    forbids_times = status in (AttendanceStatus.ABSENT, AttendanceStatus.ON_LEAVE)

    if requires_check_in and check_in is None:
        raise ValueError(f"check_in is required when status is {status.value}")

    if forbids_times and (check_in is not None or check_out is not None):
        raise ValueError(f"check_in and check_out must not be provided when status is {status.value}")

    if check_in is not None and check_out is not None and check_out < check_in:
        raise ValueError("check_out cannot be earlier than check_in")


class AttendanceCreate(BaseModel):
    employee_id: int
    attendance_date: date
    check_in: time | None = None
    check_out: time | None = None
    status: AttendanceStatus

    @model_validator(mode="after")
    def validate_attendance_date_not_in_future(self):
        """
        Attendance records an event that already happened — an employee
        cannot have "attended" a date that hasn't occurred yet. Without
        this, the API would silently accept e.g. attendance_date in the
        year 2030, which makes no operational sense and would corrupt
        any date-range reporting (dashboard "present today," summary
        endpoint, exports).
        """
        if self.attendance_date > date.today():
            raise ValueError("attendance_date cannot be in the future")
        return self

    @model_validator(mode="after")
    def validate_check_in_out_against_status(self):
        """
        Client-side UI state (see MarkAttendance.jsx) is a convenience
        only — this is the real enforcement. The API rejects an invalid
        combination with 422 regardless of how the request arrives
        (form, Swagger, curl, another client).
        """
        _validate_check_in_out_against_status(self.status, self.check_in, self.check_out)
        return self


class AttendanceUpdate(BaseModel):
    """
    Used by PUT /api/attendance/{id} — lets an existing record be
    corrected or completed after the fact. The canonical use case this
    was added for: an employee is marked PRESENT with a check_in in the
    morning, and check_out is filled in later via this endpoint once
    they actually leave, rather than requiring check_out to be known at
    the moment of marking attendance.

    employee_id and attendance_date are intentionally NOT editable here
    — those identify WHICH record this is (and are protected by the
    UNIQUE(employee_id, attendance_date) constraint). Changing either
    would effectively mean "this is now a different record," which
    should be a delete-and-recreate, not an update. status, check_in,
    and check_out are the only fields that legitimately change after
    the fact.
    """

    check_in: time | None = None
    check_out: time | None = None
    status: AttendanceStatus

    @model_validator(mode="after")
    def validate_check_in_out_against_status(self):
        _validate_check_in_out_against_status(self.status, self.check_in, self.check_out)
        return self


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    employee_code: str
    employee_name: str
    attendance_date: date
    check_in: time | None
    check_out: time | None
    status: AttendanceStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttendanceListResponse(BaseModel):
    data: list[AttendanceResponse]
    total: int
    page: int
    page_size: int


class AttendanceSummaryResponse(BaseModel):
    """
    Overall counts by status for a date range (defaults to today if no
    range is given). Distinct from the per-employee history endpoint
    and from dashboard stats (which is today-only + employee counts).
    """

    start_date: date
    end_date: date
    total_records: int
    present: int
    absent: int
    half_day: int
    on_leave: int