"""Endpoints for admin-specific operations."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Body

from src.db import Base
from src.db.models import DB_User
from src.dependencies import RoleChecker, get_current_user, get_db
from src.roles import Roles
from src.tags import Tags

from sqlalchemy.orm import Session
from .assets.sqlalchemy_type_2_html_input import sqlalchemy_to_html_mapping
from .types import ColumnDict
from .models import PasswordChangeData
from .crud import update_password

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


@router.get("/tables", dependencies=[Depends(RoleChecker(allowed_roles=[Roles.ADMIN.value]))])
def get_tables() -> dict[str, dict[str, ColumnDict]]:
    """Get info about all tables in the DB.

    Returns:
        A dictionay with table names as keys and dictionaries describing columns as the values.
        The dictionaries then are made up of column names and specific column's metadata like
        type and info about whether or not it's a primary or foreign key.
    """
    tables = {}
    for table in Base.metadata.tables.keys():
        columns = {}
        for column in Base.metadata.tables[table].c:
            column_dict = {
                "type": column.type.__class__.__name__,
                "html": sqlalchemy_to_html_mapping[column.type.__class__.__name__],
                "primary_key": column.primary_key,
                "foreign_key": (
                    None
                    if len(column.foreign_keys) == 0
                    else [
                        {"table": fk.column.table.name, "column": fk.column.name}
                        for fk in column.foreign_keys
                    ]
                ),
            }
            columns.update({column.description: column_dict})
        tables.update({table: columns})
    return tables

@router.post("/change_password", dependencies=[Depends(RoleChecker(allowed_roles=[Roles.ADMIN.value]))])
def change_password(password_change_data: Annotated[PasswordChangeData, Body()], current_user: Annotated[DB_User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)],) -> None:
    """Change password of the currently logged in admin.
    
    ## Args:
    - **password_change_data**: Instance of the PasswordChangeData model containing the new password.
    - **current_user**: An instance of the DB_User class, representing the currently logged in user.
    - **db**: Instance of the sqlalchemy.orm.Session class, representing the
            current DB session returned from the annotated dependency.
    """
    update_password(db=db, user=current_user, password_change_data=password_change_data)

