"""Utils for the auth package."""

from typing import Annotated, Literal, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.db.models import DB_User
from src.dependencies import get_db
from src.utils import ConfigManager

config = ConfigManager.get_config()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the provided password matches the hash.

    Args:
        - plain_password: Plain version of the password.
        - hashed_password: Hashed version of the password.

    Returns:
        Boolean information whether the passwords match,
        determined using the verify method from the 'pwd_context'
        library.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a hash for the given password.

    Args:
        - password: Plain version of the password.

    Returns:
        Hashed version of the password, generated using the
        'hash' function from the 'pwd_context'.
    """
    return pwd_context.hash(password)


def get_user(db: Session, username: str) -> Optional[DB_User]:
    """Get user from the DB.

    Args:
        - db: An instance of the sqlalchemy.orm.Session, representing
            the current DB session.
        - username: Username of the User that is meant to be fetched from
            the DB.
    Returns:
        An instance of the DB_User model representing the fetched user
        if it was found in the DB, None otherwise.
    """
    return db.query(DB_User).filter(DB_User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Literal[False] | DB_User:
    """Authenticate the user based on the given username and password.

    Args:
        - db: An instance of the sqlalchemy.orm.Session, representing
            the current DB session.
        - username: Username of the User that is meant to be authenticated.
        - password: plain text version of the password.

    Returns:
        - Instance if the DB_User that matched the given credentials if
        the authentication was successful, False otherwise.
    """
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict) -> str:
    """Create JWT based on the provided JSON.

    Args:
        - data: Dictionary representing the JSON data
                that is meant to be encoded into a token.

    Returns:
        A string that is an encoded JSON and can be used as an authentication
        token.
    """
    to_encode = data.copy()
    encoded_jwt = jwt.encode(
        to_encode, config.token_signing_key, algorithm=config.token_signing_algorithm
    )
    return encoded_jwt
