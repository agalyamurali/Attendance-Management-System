"""Dashboard router — one endpoint, aggregated stats, computed server-side."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.schemas.dashboard import DashboardStatsResponse
from app.services import dashboard_service

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/stats", response_model=DashboardStatsResponse)
def dashboard_stats(db: Session = Depends(get_db)):
    """
    Aggregated counts for the dashboard: total/active employees,
    present/absent today, and department-wise active headcount.
    All computed via SQL aggregation in the repository layer — the
    frontend never fetches raw employee/attendance lists to compute
    these itself.
    """
    return dashboard_service.get_dashboard_stats(db)
