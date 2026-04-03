import math
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.models import FinancialRecord
from app.schemas.schemas import RecordCreate, RecordUpdate, PaginatedRecords, RecordResponse


def create_record(db: Session, data: RecordCreate, user_id: int) -> FinancialRecord:
    record = FinancialRecord(**data.model_dump(), created_by=user_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_records(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    record_type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> PaginatedRecords:
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    # Apply filters
    filters = []
    if record_type:
        filters.append(FinancialRecord.type == record_type)
    if category:
        filters.append(FinancialRecord.category.ilike(f"%{category}%"))
    if date_from:
        filters.append(FinancialRecord.date >= date_from)
    if date_to:
        filters.append(FinancialRecord.date <= date_to)
    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    total_pages = max(1, math.ceil(total / page_size))

    if page > total_pages and total > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Page {page} does not exist. Total pages: {total_pages}",
        )

    items = (
        query.order_by(FinancialRecord.date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedRecords(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=[RecordResponse.model_validate(r) for r in items],
    )


def get_record_by_id(db: Session, record_id: int) -> FinancialRecord:
    record = (
        db.query(FinancialRecord)
        .filter(FinancialRecord.id == record_id, FinancialRecord.is_deleted == False)
        .first()
    )
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


def update_record(db: Session, record_id: int, data: RecordUpdate) -> FinancialRecord:
    record = get_record_by_id(db, record_id)
    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


def soft_delete_record(db: Session, record_id: int) -> None:
    record = get_record_by_id(db, record_id)
    record.is_deleted = True
    db.commit()
