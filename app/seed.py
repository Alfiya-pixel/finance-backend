"""
Seed script — run once to populate the database with:
  - 1 Admin user
  - 1 Analyst user
  - 1 Viewer user
  - 10 sample financial records
"""
from datetime import datetime, timezone, timedelta
import random

from app.database import SessionLocal, engine, Base
from app.models.models import User, FinancialRecord
from app.services.auth_service import hash_password
from app.core.roles import Role


SAMPLE_RECORDS = [
    ("income",  "Salary",        45000.00, "Monthly salary - March"),
    ("income",  "Freelance",      8500.00, "Web design project"),
    ("expense", "Rent",          15000.00, "Monthly rent"),
    ("expense", "Utilities",      2300.00, "Electricity + internet"),
    ("expense", "Groceries",      4800.00, "Weekly groceries"),
    ("income",  "Investments",    3200.00, "Dividend payout"),
    ("expense", "Transport",      1500.00, "Fuel and cab charges"),
    ("expense", "Entertainment",  2100.00, "Streaming + dining out"),
    ("income",  "Bonus",         10000.00, "Q1 performance bonus"),
    ("expense", "Healthcare",     3500.00, "Annual check-up and medicines"),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        # ── Create Users ─────────────────────────────────────────────────────
        admin = User(
            name="Admin User",
            email="admin@finance.dev",
            hashed_password=hash_password("admin123"),
            role=Role.ADMIN,
        )
        analyst = User(
            name="Analyst User",
            email="analyst@finance.dev",
            hashed_password=hash_password("analyst123"),
            role=Role.ANALYST,
        )
        viewer = User(
            name="Viewer User",
            email="viewer@finance.dev",
            hashed_password=hash_password("viewer123"),
            role=Role.VIEWER,
        )
        db.add_all([admin, analyst, viewer])
        db.commit()
        db.refresh(admin)

        # ── Create Financial Records ─────────────────────────────────────────
        base_date = datetime.now(timezone.utc)
        records = []
        for i, (rtype, category, amount, notes) in enumerate(SAMPLE_RECORDS):
            records.append(FinancialRecord(
                amount=amount,
                type=rtype,
                category=category,
                date=base_date - timedelta(days=i * 3),
                notes=notes,
                created_by=admin.id,
            ))
        db.add_all(records)
        db.commit()

        print("✅  Seed complete!")
        print("   admin@finance.dev    / admin123    (Admin)")
        print("   analyst@finance.dev  / analyst123  (Analyst)")
        print("   viewer@finance.dev   / viewer123   (Viewer)")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
