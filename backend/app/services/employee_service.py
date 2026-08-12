"""
Employee service — business rules for employee management.

Everything a router needs to know is "call this function, get back a
result or a clean exception." Duplicate-checking, not-found handling,
and the soft-delete rule all live here — the router and repository
don't know these rules exist.
"""

from sqlalchemy.orm import Session

from app.core.enums import EmployeeStatus
from app.exceptions import ConflictException, NotFoundException
from app.models.employee import Employee
from app.repositories import employee_repository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, payload: EmployeeCreate) -> Employee:
    if employee_repository.get_by_email(db, payload.email):
        raise ConflictException(f"An employee with email '{payload.email}' already exists")

    if employee_repository.get_by_employee_code(db, payload.employee_code):
        raise ConflictException(
            f"An employee with employee_code '{payload.employee_code}' already exists"
        )

    employee = Employee(**payload.model_dump())
    return employee_repository.create(db, employee)


def get_employee(db: Session, employee_id: int) -> Employee:
    employee = employee_repository.get_by_id(db, employee_id)
    if employee is None:
        raise NotFoundException(f"Employee with id {employee_id} not found")
    return employee


def list_employees(
    db: Session,
    search: str | None,
    department: str | None,
    status: str | None,
    sort_by: str,
    sort_order: str,
    page: int,
    page_size: int,
) -> tuple[list[Employee], int]:
    return employee_repository.list_employees(
        db, search, department, status, sort_by, sort_order, page, page_size
    )


def update_employee(db: Session, employee_id: int, payload: EmployeeUpdate) -> Employee:
    employee = get_employee(db, employee_id)  # raises NotFoundException if missing

    # Only re-check email uniqueness if it's actually changing — avoids
    # a false "duplicate" conflict against the employee's own current row.
    if payload.email != employee.email:
        existing = employee_repository.get_by_email(db, payload.email)
        if existing is not None:
            raise ConflictException(f"An employee with email '{payload.email}' already exists")

    employee.name = payload.name
    employee.email = payload.email
    employee.mobile = payload.mobile
    employee.department = payload.department
    employee.designation = payload.designation
    employee.status = payload.status

    return employee_repository.save(db, employee)


def delete_employee(db: Session, employee_id: int) -> Employee:
    """
    "Delete" an employee — always a soft delete (status -> INACTIVE),
    never a physical row removal, regardless of whether attendance
    history exists.

    Why always, not conditionally on "does attendance history exist":
    a single, consistent rule is simpler to explain, simpler to test,
    and avoids a confusing edge case where the exact same DELETE
    request would behave differently depending on unrelated data. The
    database's ON DELETE RESTRICT constraint (see database/init.sql)
    remains as a safety net in case any future code path ever attempts
    an actual hard delete.
    """
    employee = get_employee(db, employee_id)  # raises NotFoundException if missing
    employee.status = EmployeeStatus.INACTIVE
    return employee_repository.save(db, employee)
