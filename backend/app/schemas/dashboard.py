from pydantic import BaseModel


class DepartmentCount(BaseModel):
    department: str
    count: int


class DashboardStatsResponse(BaseModel):
    total_employees: int
    active_employees: int
    present_today: int
    absent_today: int
    department_wise_count: list[DepartmentCount]
