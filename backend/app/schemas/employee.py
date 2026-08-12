"""
Pydantic schemas for the employee endpoints.

Three request shapes, one response shape:
    EmployeeCreate — everything needed to add a new employee
    EmployeeUpdate — everything editable on an existing employee
                     (employee_code is intentionally excluded — see note below)
    EmployeeResponse — what the API returns for a single employee
    EmployeeListResponse — the paginated envelope for GET /api/employees
"""

import re

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

from app.core.enums import EmployeeStatus

# Simple, explainable mobile number rule: 10 to 15 digits, optionally
# with a leading "+". Not a full international-format validator (that
# would need a library like `phonenumbers`), which would be
# over-engineering for this assessment's scope.
_MOBILE_PATTERN = re.compile(r"^\+?\d{10,15}$")


class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Asha Rao"])
    email: EmailStr = Field(..., examples=["asha.rao@example.com"])
    mobile: str = Field(..., examples=["9876543210"])
    department: str = Field(..., min_length=1, max_length=50, examples=["IT"])
    designation: str = Field(..., min_length=1, max_length=50, examples=["Software Engineer"])

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value: str) -> str:
        if not _MOBILE_PATTERN.match(value):
            raise ValueError("Mobile number must be 10–15 digits, optionally starting with +")
        return value


class EmployeeCreate(EmployeeBase):
    employee_code: str = Field(..., min_length=1, max_length=20, examples=["EMP001"])
    status: EmployeeStatus = EmployeeStatus.ACTIVE


class EmployeeUpdate(EmployeeBase):
    """
    Full-update schema for PUT /api/employees/{id}.

    employee_code is deliberately NOT editable here — it's treated as
    an immutable natural identifier once assigned (like a username).
    Changing it would silently break anything that referenced the
    employee by code. If the business ever needs to correct a wrongly
    entered code, that's a deliberate one-off admin action, not a
    routine edit — easy to add later as a separate endpoint if needed.
    """

    status: EmployeeStatus


class EmployeeResponse(EmployeeBase):
    id: int
    employee_code: str
    status: EmployeeStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # allows creating this schema directly from a SQLAlchemy model


class EmployeeListResponse(BaseModel):
    data: list[EmployeeResponse]
    total: int
    page: int
    page_size: int
