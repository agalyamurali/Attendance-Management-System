"""
Employee repository — the only place that queries the `employees` table.

Contains query-building logic (search/filter/sort/paginate) but NO
business rules (no "is this email already taken" decision-making —
that's the service's job, this just executes whatever query it's asked
to run).
"""

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session

from app.models.employee import Employee

# Columns allowed as a sort key. Whitelisting like this (rather than
# accepting any string and passing it to getattr) prevents a client
# from requesting a sort on an arbitrary/nonexistent column.
_SORTABLE_COLUMNS = {
    "name": Employee.name,
    "employee_code": Employee.employee_code,
    "department": Employee.department,
    "designation": Employee.designation,
    "status": Employee.status,
    "created_at": Employee.created_at,
}


def get_by_id(db: Session, employee_id: int) -> Employee | None:
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_by_email(db: Session, email: str) -> Employee | None:
    return db.query(Employee).filter(Employee.email == email).first()


def get_by_employee_code(db: Session, employee_code: str) -> Employee | None:
    return db.query(Employee).filter(Employee.employee_code == employee_code).first()


def create(db: Session, employee: Employee) -> Employee:
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def save(db: Session, employee: Employee) -> Employee:
    """Persist changes to an already-loaded, already-modified Employee instance."""
    db.commit()
    db.refresh(employee)
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
    """
    Build one query, apply filters/search/sort, then run it twice:
    once for the total count (for pagination metadata), once for the
    actual page of results. Returns (items, total_count).
    """
    query = db.query(Employee)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Employee.name.ilike(pattern))
            | (Employee.email.ilike(pattern))
            | (Employee.employee_code.ilike(pattern))
        )

    if department:
        query = query.filter(Employee.department == department)

    if status:
        query = query.filter(Employee.status == status)

    total = query.count()

    sort_column = _SORTABLE_COLUMNS.get(sort_by, Employee.created_at)
    order_func = desc if sort_order.lower() == "desc" else asc
    query = query.order_by(order_func(sort_column))

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    return items, total


def count_all(db: Session) -> int:
    return db.query(func.count(Employee.id)).scalar()


def count_by_status(db: Session, status: str) -> int:
    return db.query(func.count(Employee.id)).filter(Employee.status == status).scalar()


def department_wise_active_counts(db: Session) -> list[tuple[str, int]]:
    """
    Active-employee headcount grouped by department. Restricted to
    ACTIVE employees deliberately — this is meant to answer "current
    workforce by department," not a historical total that includes
    deactivated employees.
    """
    return (
        db.query(Employee.department, func.count(Employee.id))
        .filter(Employee.status == "ACTIVE")
        .group_by(Employee.department)
        .all()
    )
