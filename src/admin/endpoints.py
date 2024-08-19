"""Endpoints for admin-specific operations."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import Column, Table

from src.db import Base
from src.db.models import DB_User
from src.dependencies import RoleChecker, get_current_user
from src.roles import Roles
from src.tags import Tags

router = APIRouter(prefix="/admin", tags=[Tags.admin])


@router.get("/is_admin")
def check_if_admin(current_user: Annotated[DB_User, Depends(get_current_user)]) -> bool:
    """Check if the currently logged in user is an admin.

    Args:
    - **current_user**: An instance of the DB_User class, representing the currently logged in user.

    Returns:
        Boolean information about whether or not the currently logged in user is an admin.
    """
    return current_user.role == Roles.ADMIN.value
