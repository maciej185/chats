from sqlalchemy.orm import declarative_base

Base = declarative_base()

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
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


class DB_Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    profile_pic_path = Column(String(300), default=str(config.default_profile_pic_path))
    date_of_birth = Column(Date, default=datetime.now())

    user = relationship("DB_User", back_populates="profile")
