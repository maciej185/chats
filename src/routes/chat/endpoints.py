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
from fastapi.responses import FileResponse
from pydantic import FilePath
from sqlalchemy.orm import Session

from src.db.models import DB_Chat, DB_ChatMember, DB_Message, DB_User
from src.dependencies import (
    RoleChecker,
    check_if_user_is_chat_member,
    check_if_user_is_chat_member_with_message,
    get_current_user,
    get_current_user_ws,
    get_db,
    get_message,
)
from src.roles import Roles
from src.routes.auth.models import UserInResponse
from src.tags import Tags
from src.utils import FileStorageManager

from .connection_manager import ConnectionManager
from .crud import (
    chat_exists,
    create_chat_in_db,
    create_chat_member_in_db,
    get_chat_from_db,
    get_chat_member_from_db,
    get_chat_members,
    get_chats_from_db,
    get_messages_from_db,
    get_potential_chat_members_from_db,
    save_message_in_db,
)
from .models import Chat, ChatAdd, ChatMember, ChatMemberAdd, Message

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
            try:
                data = await ws.receive_json()
                db_message = await save_message_in_db(
                    db=db,
                    chat_member=db_chat_member,
                    text=data.get("message"),
                    reply_to=data.get("reply_to"),
                )
                await manager.broadcast(
                    Message.model_validate(db_message, from_attributes=True).model_dump(mode="json")
                )
            except KeyError:
                pass

            try:
                image = await ws.receive_bytes()
                image_path = await FileStorageManager.save_message_image(
                    user_id=user.user_id, chat_id=chat_id, image=image
                )
                db_message = await save_message_in_db(
                    db=db, chat_member=db_chat_member, text="", reply_to=None, image_path=image_path
                )
                await manager.broadcast(
                    Message.model_validate(db_message, from_attributes=True).model_dump(mode="json")
                )
            except KeyError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(ws)


@router.get(
    "/{chat_id}",
    response_model=Chat,
    dependencies=[Depends(RoleChecker(allowed_roles=[Roles.ADMIN.value, Roles.USER.value]))],
)
def get_chat(chat_id: Annotated[int, Path()], db: Annotated[Session, Depends(get_db)]) -> DB_Chat:
    """Return info about the chat with a given ID.

    Args:
    - **chat_id**: Info about chat with this ID will be fetched.
    - **db**: An instance of the sqlachemy.orm.Session class, representing the current DB session,
                returned from the annotated dependency function.

    Returns:
        An instance of the DB_Chat with the given ID.
    """
    return get_chat_from_db(db=db, chat_id=chat_id)


@router.get(
    "/get_potential_members/{chat_id}",
    response_model=list[UserInResponse],
    dependencies=[
        Depends(check_if_user_is_chat_member),
        Depends(RoleChecker(allowed_roles=[Roles.ADMIN.value, Roles.USER.value])),
    ],
)
def get_potential_members(
    chat_id: Annotated[int, Path()], db: Annotated[Session, Depends(get_db)]
) -> list[DB_User]:
    """Get potential new members for a given chat.

    Args:
    - **chat_id**: ID of the chat to fetch potential new users for.
    - **db**: An instance of the sqlachemy.orm.Session class, representing the current DB session,
                returned from the annotated dependency function.

    Returns:
        A list with with instances of the DB_User model,
        representing potential new chat members.
    """
    return get_potential_chat_members_from_db(db=db, chat_id=chat_id)


@router.get(
    "/messages/{chat_id}",
    response_model=list[Message],
    dependencies=[
        Depends(check_if_user_is_chat_member),
        Depends(RoleChecker(allowed_roles=[Roles.ADMIN.value, Roles.USER.value])),
    ],
)
def get_messages(
    chat_id: Annotated[int, Path()],
    index_from_the_top: Annotated[int, Query()],
    db: Annotated[Session, Depends(get_db)],
    no_of_messages_to_fetch: Annotated[int, Query()] = 10,
) -> list[Message]:
    """Returna given number of messages from a given chat.

    Args:
    - **chat_id**: ID of the chat from which the messages will be fetched.
    - **index_from_the_top**: An index specifying from which point the messages will be returned.
    = **no_of_messages_to_fetch**: Number of messages that will be fetched.
    - **db**: An instance of the sqlachemy.orm.Session class, representing the current DB session,
                returned from the annotated dependency function.

    Returns:
        An array of instances of the DB_Messages model, representing messages
        sent in a given chat.
    """
    db_messages = get_messages_from_db(
        db=db,
        chat_id=chat_id,
        index_from_the_top=index_from_the_top,
        no_of_messages_to_fetch=no_of_messages_to_fetch,
    )
    messages = []
    for db_message in db_messages:
        message = Message.model_validate(db_message, from_attributes=True)
        message.contains_image = True if not db_message.image_path is None else False
        messages.append(message)
    return messages


@router.get(
    "/image/{message_id}",
    dependencies=[
        Depends(check_if_user_is_chat_member_with_message),
        Depends(RoleChecker(allowed_roles=[Roles.ADMIN.value, Roles.USER.value])),
    ],
    response_class=FileResponse,
)
def get_image(message: Annotated[DB_Message, Depends(get_message)]) -> str:
    """Return image associated with a given message.

    Args:
    - **message**: Instance of the DB_Message model repesenting a message with that is
        associated with an image that will be asynchronously streamed as a response.

    Raises:
        HttpException: Raised when the given message is not associated with any
            image.

    Returns:
        Path to the image associated with the given image.
    """
    if message.image_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no picture associated with the given message.",
        )
    return message.image_path
