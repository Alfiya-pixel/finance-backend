from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.roles import Role
from app.middleware.dependencies import require_role
from app.schemas.schemas import RecordCreate, RecordUpdate, RecordResponse, PaginatedRecords
from app.services import record_service

router = APIRouter(prefix="/api/records", tags=["Financial Records"])


@router.post(
    "/",
    response_model=RecordResponse,
    status_code=201,
    summary="Create a financial record [Analyst/Admin]",
)
def create_record(
    data: RecordCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(Role.ANALYST)),
):
    """Create a new income or expense record. Analyst and Admin access required."""
    return record_service.create_record(db, data, user_id=current_user.id)


@router.get(
    "/",
    response_model=PaginatedRecords,
    summary="List records with filters & pagination [All roles]",
)
def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None, pattern="^(income|expense)$"),
    category: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_role(Role.VIEWER)),
):
    """
    Retrieve paginated financial records.
    Optional filters: type, category, date_from, date_to.
    """
    return record_service.get_records(
        db,
        page=page,
        page_size=page_size,
        record_type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Get a single record [All roles]",
)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role(Role.VIEWER)),
):
    return record_service.get_record_by_id(db, record_id)


@router.patch(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Update a record [Analyst/Admin]",
)
def update_record(
    record_id: int,
    data: RecordUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role(Role.ANALYST)),
):
    """Partially update an existing record. Analyst and Admin access required."""
    return record_service.update_record(db, record_id, data)


@router.delete(
    "/{record_id}",
    status_code=204,
    summary="Soft-delete a record [Admin only]",
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """
    Soft-deletes a record (sets is_deleted=True). Admin access required.
    The record is hidden from all queries but preserved in the database.
    """
    record_service.soft_delete_record(db, record_id)
