from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.roles import Role
from app.middleware.dependencies import require_role
from app.schemas.schemas import DashboardSummary
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Get dashboard summary [Analyst/Admin]",
)
def get_summary(
    db: Session = Depends(get_db),
    _=Depends(require_role(Role.ANALYST)),
):
    """
    Returns aggregated financial data including:
    - Total income, expenses, and net balance
    - Category-wise totals
    - Recent activity (last 10 records)
    - Monthly trends (last 12 months)

    Analyst and Admin access required.
    """
    return dashboard_service.get_dashboard_summary(db)
