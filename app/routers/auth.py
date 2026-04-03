from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user, build_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, summary="Login and get JWT token")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email + password. Returns a JWT Bearer token.
    Include this token as `Authorization: Bearer <token>` on all protected routes.
    """
    user = authenticate_user(db, data.email, data.password)
    return build_token(user)
