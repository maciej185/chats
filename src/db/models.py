from sqlalchemy.orm import declarative_base

Base = declarative_base()

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

from src.roles import Roles
from src.utils import ConfigManager

config = ConfigManager.get_config()


class DB_User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(150), nullable=False)
    create_date = Column(Date, default=datetime.now())
    role = Column(Integer, default=Roles.USER.value)

    profile = relationship("DB_Profile", back_populates="user")
    as_chat_member_in = relationship("DB_ChatMember", back_populates="user")


class DB_Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    profile_pic_path = Column(String(300), default=str(config.default_profile_pic_path))
    date_of_birth = Column(Date, default=datetime.now())

    user = relationship("DB_User", back_populates="profile")


class DB_Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    create_date = Column(Date, default=datetime.now(), nullable=False)

    members = relationship("DB_ChatMember", back_populates="chat")


class DB_ChatMember(Base):
    __tablename__ = "chat_members"

    chat_member_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    chat_id = Column(Integer, ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False)
    date_when_added = Column(Date, default=datetime.now(), nullable=False)
    is_creator = Column(Boolean, default=True, nullable=False)

    chat = relationship("DB_Chat", back_populates="members")
    user = relationship("DB_User", back_populates="as_chat_member_in")
    messages = relationship("DB_Message", back_populates="chat_member")


class DB_Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True)
    chat_member_id = Column(
        Integer, ForeignKey("chat_members.chat_member_id", ondelete="SET NULL"), nullable=True
    )
    text = Column(Text, nullable=False)
    time_sent = Column(DateTime, default=datetime.now(), nullable=False)
    reply_to = Column(Integer, ForeignKey("messages.message_id"), nullable=True)
    image_path = Column(String(400), nullable=True, default=None)

    chat_member = relationship("DB_ChatMember", back_populates="messages")
    parent_message = relationship(
        "DB_Message", back_populates="child_message", uselist=False, remote_side=reply_to
    )
    child_message = relationship(
        "DB_Message", back_populates="parent_message", uselist=False, remote_side=message_id
    )
