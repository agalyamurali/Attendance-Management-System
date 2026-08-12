"""
Dashboard service — assembles the aggregated stats shown on the
dashboard. Pure orchestration: calls repository aggregation queries
and shapes the result. No business rules of its own.

Definitions used here (documented since they're judgment calls not
spelled out field-by-field in the spec):
    present_today = employees with a PRESENT attendance record today
    absent_today  = active_employees - present_today
                    (anyone not marked present today, including
                    employees not yet marked at all, counts as absent
                    for this headline number — a simple, defensible
                    definition worth stating explicitly if asked)
    department_wise_count = ACTIVE employees grouped by department
"""

from datetime import date

from sqlalchemy.orm import Session

from app.repositories import attendance_repository, employee_repository
from app.schemas.dashboard import DashboardStatsResponse, DepartmentCount


def get_dashboard_stats(db: Session) -> DashboardStatsResponse:
    total_employees = employee_repository.count_all(db)
    active_employees = employee_repository.count_by_status(db, "ACTIVE")

    today = date.today()
    present_today = attendance_repository.count_today_present(db, today)
    absent_today = max(active_employees - present_today, 0)

    department_rows = employee_repository.department_wise_active_counts(db)
    department_wise_count = [
        DepartmentCount(department=dept, count=count) for dept, count in department_rows
    ]

    return DashboardStatsResponse(
        total_employees=total_employees,
        active_employees=active_employees,
        present_today=present_today,
        absent_today=absent_today,
        department_wise_count=department_wise_count,
    )
