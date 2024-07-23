"""Endpoints for the chat package."""

from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.orm import Session

from src.db.models import DB_Chat, DB_ChatMember, DB_User
from src.dependencies import get_db
from src.roles import Roles
from src.routes.auth.utils import RoleChecker, get_current_user, get_current_user_ws
from src.tags import Tags

from .connection_manager import ConnectionManager
from .crud import (
    chat_exists,
    create_chat_in_db,
    create_chat_member_in_db,
    get_chat_member_from_db,
    get_chat_members,
    get_chats_from_db,
    save_message_in_db,
)
from .models import Chat, ChatAdd, ChatMember, ChatMemberAdd

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
    - An instance of the DB_Chat model, representing the newly created row in the DB.
    """
    return create_chat_in_db(db=db, chat_data=chat_data, creator_id=current_user.user_id)


@router.post(
    "/add_member",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(allowed_roles=[Roles.ADMIN.value, Roles.USER.value]))],
    response_model=ChatMember,
)
def add_member(
    chat_member_data: Annotated[ChatMemberAdd, Body()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[DB_User, Depends(get_current_user)],
) -> DB_ChatMember:
    """Endpoint for adding member to a given chat.

    Args:
    - **chat_member_data**: Instance of the ChatMemberAdd pydantic model with
        all the relevant info for creating a new chat member.
    - **db**: An instance of the sqlachemy.orm.Session class, representing the current DB session,
                returned from the annotated dependency function.
    - **current_user**: An instance of the DB_User class, representing the currently logged in user.

    Raises:
    - **HTTPException**: Raised when:
        - the current user's ID is the same as the ID of the user that is meant to be added to a given chat.
        - the current user is not a member of the chat.
        - the user that is meant to be added is already a member of the given chat.

    Returns:
    - An instance of DB_ChatMember model, representing a newly created row in the DB.
    """
    chat_members = get_chat_members(db=db, chat_id=chat_member_data.chat_id)
    if not current_user in [chat_member.user for chat_member in chat_members]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Currently authorized user is not a member of the chat. Only chat members can add new members.",
        )
    if chat_member_data.user_id in [chat_member.user.user_id for chat_member in chat_members]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is already a member of the given chat.",
        )
    return create_chat_member_in_db(
        db=db, chat_id=chat_member_data.chat_id, user_id=chat_member_data.user_id, is_creator=False
    )


@router.get("/list", response_model=list[Chat])
def get_chats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[DB_User, Depends(get_current_user)],
) -> list[DB_Chat]:
    """Get chats that the current user is a member of.

    Args:
    - **db**: An instance of the sqlachemy.orm.Session class, representing the current DB session,
                returned from the annotated dependency function.
    - **current_user**: An instance of the DB_User class, representing the currently logged in user.

    Returns:
        A list of the chats that the currently authorized user is a member of.
    """
    return get_chats_from_db(db=db, user_id=current_user.user_id)


manager = ConnectionManager()


@router.websocket(
    "/{chat_id}",
)
async def chat(
    ws: WebSocket,
    chat_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Query()],
) -> None:
    """Send/receive messages in the given chat.

    Args:
    - **ws**: An instance of the fastapi.WebSocket class, representing
            the current connection.
    - **chat_id**: ID of the chat to which the messages are being sent to
                and from which they are received.
    - **db**: An instance of the sqlachemy.orm.Session class, representing the current DB session,
                returned from the annotated dependency function.
    - **current_user**: An instance of the DB_User class, representing the currently logged in user.
    """
    user = get_current_user_ws(db=db, token=token)
    if user is None:
        await ws.send_denial_response(
            Response("Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)
        )
        return
    if not chat_exists(db=db, chat_id=chat_id):
        await ws.send_denial_response(
            Response("Chat does not exist", status_code=status.HTTP_404_NOT_FOUND)
        )
        return
    db_chat_member = get_chat_member_from_db(db=db, chat_id=chat_id, user_id=user.user_id)
    if db_chat_member is None:
        await ws.send_denial_response(
            Response("User is not member of the chat", status_code=status.HTTP_404_NOT_FOUND)
        )
        return
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            save_message_in_db(
                db=db,
                chat_member=db_chat_member,
                text=data.get("message"),
                reply_to=data.get("reply_to"),
            )
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(ws)
