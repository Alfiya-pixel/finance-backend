from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.roles import Role
from app.middleware.dependencies import require_role, get_current_user
from app.models.models import User
from app.schemas.schemas import UserCreate, UserUpdate, UserResponse
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Create a new user [Admin only]",
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with a specified role. Admin access required."""
    return user_service.create_user(db, data)


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="List all users [Admin only]",
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def list_users(db: Session = Depends(get_db)):
    """Retrieve all users in the system. Admin access required."""
    return user_service.get_all_users(db)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get your own profile",
)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Returns the currently authenticated user's profile."""
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID [Admin only]",
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user_by_id(db, user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user role or status [Admin only]",
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    """Update a user's name, role, or active status. Admin access required."""
    return user_service.update_user(db, user_id, data)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete a user [Admin only]",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """Permanently delete a user. Cannot delete your own account."""
    user_service.delete_user(db, user_id, requesting_user_id=current_user.id)
