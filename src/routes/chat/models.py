"""Pydantic models for the chats package."""

from datetime import date

from pydantic import BaseModel

from src.routes.auth.models import UserInResponse


class ChatBase(BaseModel):
    """Base for Chat models."""

    name: str

    class Config:
        from_attributes = True


class ChatAdd(ChatBase):
    """Model for creating a new Chat."""


class ChatWithoutMembers(ChatBase):
    """Model with all relevant Chat info EXCEPT Members.

    To be used as a field in the ChatMember model
    and so the ChatMember had to be excluded to
    avoid recursion.
    """

    chat_id: int


class Chat(ChatWithoutMembers):
    """Model with all relevant Chat info."""

    members: list["ChatMember"]


class ChatMemberBase(BaseModel):
    """Base for ChatMember models."""

    user_id: int
    chat_id: int

    class Config:
        from_attributes = True


class ChatMemberAdd(ChatMemberBase):
    """Model for creating a new ChatMember."""


class ChatMemberWithoutChat(ChatMemberBase):
    """Model with all relevant ChatMember info EXCEPT Chat.

    To be used as a field in the Chat model
    and so Chat had to be excluded to avoid recursion.
    """

    user: UserInResponse


class ChatMember(ChatMemberWithoutChat):
    """Model with all relevant ChatMember info."""

    chat: ChatWithoutMembers


class MessageBase(BaseModel):
    """Base for Message models."""

    chat_member_id: int
    text: str
    reply_to: int | None = None
    time_sent: date

    class Config:
        from_attributes = True


class MessageAdd(MessageBase):
    """Model for creating a new Message."""


class MessageWithoutParentOrChild(MessageBase):
    """Model with all relevant Message info EXCEPT Message field representing parent or child message.

    The DB table implements self referencing foregin key, creating a recursive
    relationship that models replies. To have a field that refers to a related
    message without running into recursion a separate model has to be created.
    """

    message_id: int
    images: list["MessageImage"]


class Message(MessageWithoutParentOrChild):
    """Model with all relevant Message info."""

    parent_message: MessageWithoutParentOrChild | None
    child_message: MessageWithoutParentOrChild | None
    chat_member: ChatMemberWithoutChat


class MessageImageBase(MessageBase):
    """Base MessageImage models."""

    message_id: int
    image_path: str


class MessageImageAdd(MessageImageBase):
    """Model for creating a new MessageImage."""


class MessageImage(MessageImageBase):
    """Model with all relevant MessageImage info."""

    message_image_id: int
