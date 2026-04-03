from enum import Enum


class Role(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


# Role hierarchy: higher index = more permissions
ROLE_HIERARCHY = [Role.VIEWER, Role.ANALYST, Role.ADMIN]


def has_minimum_role(user_role: str, required_role: Role) -> bool:
    """Check if user_role meets or exceeds the required_role."""
    try:
        user_index = ROLE_HIERARCHY.index(Role(user_role))
        required_index = ROLE_HIERARCHY.index(required_role)
        return user_index >= required_index
    except ValueError:
        return False
