"""CRUD operations for the chat package."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.db.models import DB_Chat, DB_ChatMember, DB_Message, DB_User

from .models import ChatAdd


def create_chat_in_db(db: Session, chat_data: ChatAdd, creator_id: int) -> DB_Chat:
    """Create a new chat.

    The function creates a new chat based on the provided data as well as the first member
    (instance of the DB_ChatMember model). This first user is regarded as the creator of the chat.

    Args:
        - db: An instance of the sqlalchemy.orm.Session class, representing the current
                DB session.
        - chat_data: An instance of the ChatAdd model with the relevant data needed to
                    create a new chat.
        - creator_id: ID of the DB_User needed to instantiate the first DB_ChatMember object
                        related to the newly created Chat.

    Raises:
        HTTPException: Raised when the user with the provided 'creator_id' does not
                    exists in the db.

    Returns:
        A newly created instance of the DB_Chat model based on the provided data.
    """
    db_creator = db.query(DB_User).filter(DB_User.user_id == creator_id).first()
    if db_creator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with the given creator_id was not found in the DB.",
        )
    db_chat = DB_Chat(**chat_data.model_dump())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    create_chat_member_in_db(db=db, chat_id=db_chat.chat_id, user_id=creator_id, is_creator=True)
    return db_chat


def create_chat_member_in_db(
    db: Session, chat_id: int, user_id: int, is_creator: bool
) -> DB_ChatMember:
    """Add a member to the chat.

     Args:
        - db: An instance of the sqlalchemy.orm.Session class, representing the current
                DB session.
        - chat_id: ID of the chat that the user will be added to.
        - user_id: ID of the user that will be added to the given chat.
        - is_creator: Boolean value indicating whether or not the given user
                        is a creator of the chat, used as a value of the 'is_creator'
                        column for the given row.

    Raises:
        HTTPException: Raised when a chat or a user with given ID do not exist in the DB.

    Returns:
        An instance of the DB_ChatMember model, representing the newly added member.
    """
    db_chat = db.query(DB_Chat).filter(DB_Chat.chat_id == chat_id).first()
    if db_chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat with the given ID was not found in the DB.",
        )

    db_user = db.query(DB_User).filter(DB_User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with the given ID was not found in the DB.",
        )

    db_chat_member = DB_ChatMember(user_id=user_id, chat_id=chat_id, is_creator=is_creator)
    db.add(db_chat_member)
    db.commit()
    db.refresh(db_chat_member)
    return db_chat_member


def get_chat_members(db: Session, chat_id: int) -> list[DB_ChatMember]:
    """Return members of a given chat.

    Args:
        - db: An instance of the sqlalchemy.orm.Session class, representing the current
                DB session.
        - chat_id: ID of the chat whose members are meant to be fetched.

    Raises:
        HTTPException: Raised when a chat with given ID does not exist in the DB.
    """
    db_chat = db.query(DB_Chat).filter(DB_Chat.chat_id == chat_id).first()
    if db_chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat with the given ID was not found in the DB.",
        )
    return [
        chat_member
        for chat_member in db.query(DB_ChatMember).filter(DB_ChatMember.chat_id == chat_id).all()
    ]


def chat_exists(db: Session, chat_id: int) -> bool:
    """Check if the given chat exisits in DB.

    Args:
        - db: An instance of the sqlalchemy.orm.Session class, representing the current
                DB session.
        - chat_id: ID of the chat whose existence is to be verified.

    Returns:
        Boolean value indicating whether a chat with the given ID
        exists in the DB.
    """
    return False if db.query(DB_Chat).filter(DB_Chat.chat_id == chat_id).first() is None else True


def get_chat_member_from_db(db: Session, chat_id: int, user_id: int) -> DB_ChatMember | None:
    """Get chat member of a given chat with given user_id.

    Args:
        - db: An instance of the sqlalchemy.orm.Session class, representing the current
                DB session.
        - chat_id: ID of the chat to check.
        - user_id: ID of the user who allegadly is the given chat's member.

    Returns:
        Instance of the DB_ChatMember model representing the membership of the given
        user to the given chat is such instance exists, None otherwise.
    """
    return (
        db.query(DB_ChatMember)
        .filter(DB_ChatMember.chat_id == chat_id, DB_ChatMember.user_id == user_id)
        .first()
    )


def save_message_in_db(
    db: Session, chat_member: DB_ChatMember, text: str, reply_to: int | None
) -> DB_Message:
    """Save given message in the DB.

    Args:
        - db: An instance of the sqlalchemy.orm.Session class, representing the current
                DB session.
        - chat_member: An instance of the DB_ChatMember class, representing the sender
            in the given chat.
        - text: Text of the message.
        - reply_to: ID of the message that the currently saved message is a reply to.
    """
    db_message = DB_Message(chat_member_id=chat_member.chat_member_id, text=text, reply_to=reply_to)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
