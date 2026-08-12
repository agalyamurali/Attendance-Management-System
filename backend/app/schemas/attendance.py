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


class AttendanceCreate(BaseModel):
    employee_id: int
    attendance_date: date
    check_in: time | None = None
    check_out: time | None = None
    status: AttendanceStatus

    @model_validator(mode="after")
    def validate_check_in_out_against_status(self):
        """
        Check-in/check-out requirements depend on the attendance status:

            PRESENT   -> check_in REQUIRED, check_out optional
                         (an employee may still be at work when marked)
            HALF_DAY  -> check_in REQUIRED, check_out optional
                         (same reasoning as PRESENT — they did come in)
            ABSENT    -> check_in and check_out must both be EMPTY
            ON_LEAVE  -> check_in and check_out must both be EMPTY
                         (no physical attendance occurred, so a time
                         value would be meaningless/misleading data)

        This mirrors the frontend's field enabling/disabling, but is
        enforced here independently — client-side UI state is a
        convenience, never a substitute for server-side validation,
        since the API can be called directly (Swagger, curl, another
        client) without going through the form at all.
        """
        requires_check_in = self.status in (AttendanceStatus.PRESENT, AttendanceStatus.HALF_DAY)
        forbids_times = self.status in (AttendanceStatus.ABSENT, AttendanceStatus.ON_LEAVE)

        if requires_check_in and self.check_in is None:
            raise ValueError(f"check_in is required when status is {self.status.value}")

        if forbids_times and (self.check_in is not None or self.check_out is not None):
            raise ValueError(
                f"check_in and check_out must not be provided when status is {self.status.value}"
            )

        if self.check_in is not None and self.check_out is not None:
            if self.check_out < self.check_in:
                raise ValueError("check_out cannot be earlier than check_in")

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