"""
Application-level enums — the single source of truth for every
"controlled set of values" column in the system (role, employee status,
attendance status).

Why these live in Python, not as a MySQL ENUM type:
    Documented in database/init.sql — columns are VARCHAR, validity is
    enforced here instead. This is the ONE place that knows what a
    valid role/status is. Pydantic schemas use these directly (so bad
    values are rejected at the API boundary, before touching the DB),
    and services can import them instead of comparing raw strings.

Inheriting from `str, Enum` means these behave as normal strings in
JSON responses (e.g. "ADMIN", not an enum repr), while still giving
type safety and autocomplete in code.
"""

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"


class EmployeeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    ON_LEAVE = "ON_LEAVE"
