from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import FinancialRecord
from app.schemas.schemas import (
    DashboardSummary,
    CategoryTotal,
    MonthlyTrend,
    RecordResponse,
)


def get_dashboard_summary(db: Session) -> DashboardSummary:
    base_query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    # ── Totals ──────────────────────────────────────────────────────────────
    income_result = (
        base_query.filter(FinancialRecord.type == "income")
        .with_entities(func.coalesce(func.sum(FinancialRecord.amount), 0.0))
        .scalar()
    )
    expense_result = (
        base_query.filter(FinancialRecord.type == "expense")
        .with_entities(func.coalesce(func.sum(FinancialRecord.amount), 0.0))
        .scalar()
    )
    total_income = float(income_result)
    total_expenses = float(expense_result)

    # ── Category Totals ─────────────────────────────────────────────────────
    category_rows = (
        base_query
        .with_entities(FinancialRecord.category, func.sum(FinancialRecord.amount))
        .group_by(FinancialRecord.category)
        .order_by(func.sum(FinancialRecord.amount).desc())
        .all()
    )
    category_totals = [
        CategoryTotal(category=row[0], total=round(float(row[1]), 2))
        for row in category_rows
    ]

    # ── Recent Activity (last 10 records) ────────────────────────────────────
    recent = (
        base_query
        .order_by(FinancialRecord.date.desc())
        .limit(10)
        .all()
    )

    # ── Monthly Trends (last 12 months) ─────────────────────────────────────
    all_records = base_query.order_by(FinancialRecord.date.asc()).all()
    monthly: dict = defaultdict(lambda: {"income": 0.0, "expense": 0.0})

    for r in all_records:
        key = (r.date.year, r.date.month)
        monthly[key][r.type] += r.amount

    # Sort and take last 12 months
    sorted_months = sorted(monthly.items())[-12:]
    monthly_trends = [
        MonthlyTrend(
            year=year,
            month=month,
            income=round(data["income"], 2),
            expense=round(data["expense"], 2),
            net=round(data["income"] - data["expense"], 2),
        )
        for (year, month), data in sorted_months
    ]

    return DashboardSummary(
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_balance=round(total_income - total_expenses, 2),
        total_records=base_query.count(),
        category_totals=category_totals,
        recent_activity=[RecordResponse.model_validate(r) for r in recent],
        monthly_trends=monthly_trends,
    )
