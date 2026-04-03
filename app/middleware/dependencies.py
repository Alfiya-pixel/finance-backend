from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user_payload
from app.core.roles import Role, has_minimum_role
from app.database import get_db
from app.models.models import User


def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
) -> User:
    """Resolve JWT payload → actual User DB object. Blocks inactive users."""
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    return user


def require_role(minimum_role: Role):
    """
    Factory that returns a FastAPI dependency enforcing a minimum role.

    Usage:
        @router.post("/", dependencies=[Depends(require_role(Role.ADMIN))])
    """
    def _check(current_user: User = Depends(get_current_user)):
        if not has_minimum_role(current_user.role, minimum_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {minimum_role.value}",
            )
        return current_user
    return _check
