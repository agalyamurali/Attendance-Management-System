"""
Employees router — HTTP layer for employee CRUD, search, filter, sort,
and pagination.

Every route here requires authentication (Depends(get_current_user)).
Query parameters map directly to what the service/repository expect —
this router does no filtering/sorting logic itself, it just parses the
request and hands off to the service.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services import employee_service

router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"],
    dependencies=[Depends(get_current_user)],  # every route in this router requires auth
)


@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    """Add a new employee. 409 if email or employee_code already exists."""
    return employee_service.create_employee(db, payload)


@router.get("", response_model=EmployeeListResponse)
def list_employees(
    db: Session = Depends(get_db),
    search: str | None = Query(None, description="Matches name, email, or employee_code"),
    department: str | None = Query(None),
    status: str | None = Query(None, description="ACTIVE or INACTIVE"),
    sort_by: str = Query("created_at", description="name, employee_code, department, designation, status, created_at"),
    sort_order: str = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """
    List employees with optional search/filter/sort, paginated.

    Example: /api/employees?search=John&department=IT&status=ACTIVE&page=1&page_size=10
    """
    items, total = employee_service.list_employees(
        db, search, department, status, sort_by, sort_order, page, page_size
    )
    return EmployeeListResponse(data=items, total=total, page=page, page_size=page_size)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Fetch a single employee by id. 404 if not found."""
    return employee_service.get_employee(db, employee_id)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    """Full update of an employee's editable fields. 404 if not found, 409 on duplicate email."""
    return employee_service.update_employee(db, employee_id, payload)


@router.delete("/{employee_id}", response_model=EmployeeResponse)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """
    "Delete" an employee — actually a soft delete (status -> INACTIVE).
    Attendance history is always preserved. See employee_service.delete_employee
    for the full reasoning.
    """
    return employee_service.delete_employee(db, employee_id)
