"""Endpoints for the chat package."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from src.db.models import DB_Chat, DB_User
from src.dependencies import get_db
from src.roles import Roles
from src.routes.auth.utils import RoleChecker, get_current_user
from src.tags import Tags

from .crud import create_chat_in_db
from .models import Chat, ChatAdd

router = APIRouter(prefix="/chat", tags=[Tags.chat.value])


@router.post(
    "/add",
    response_model=Chat,
    dependencies=[Depends(RoleChecker(allowed_roles=[Roles.ADMIN.value, Roles.USER.value]))],
    status_code=status.HTTP_201_CREATED,
)
def create_chat(
    chat_data: Annotated[ChatAdd, Body()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[DB_User, Depends(get_current_user)],
) -> DB_Chat:
    """Create and return new Chat.

    Together with the chat a first member (creator) is instantiated which is the
    authenticated user making the request.

    Args:
    - **chat_data**: An instance of the ChatAdd pydantic model with the information needed to
                    create a new Chat in the DB.
    - **db**: An instance of the sqlachemy.orm.Session class, representing the current DB session,
                returned from the annotated dependency function.
    - **current_user**: An instance of the DB_User class, representing the currently logged in user.

    Returns:
        An instance of the DB_Chat model, representing the newly created Chat object.
    """
    return create_chat_in_db(db=db, chat_data=chat_data, creator_id=current_user.user_id)
