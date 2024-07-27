"""Dependencies for the app."""

from typing import Annotated, Generator

import jwt
from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.db import SessionLocal
from src.db.models import DB_ChatMember, DB_User
from src.utils import ConfigManager

config = ConfigManager.get_config()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db() -> Generator[Session, None, None]:
    """Get DB session and close it after the response was delivered.

    The function is used as a dependency in path operation functions
    which means that any code before the 'yield' will be executed before
    sending the response and the code after is executed afterwards which
    means it can be used to perform clean-up actions, as it is used in this
    case for closing the DB session.

    Yields:
        An instance of the sqlalchemy.orm.Session class, representing the current DB
        session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]
) -> DB_User:
    """Get authenticated user.

    The function is used as a dependency in path operations.
    The idenetity of the user is determined based on the 'Authorization'
    header containing the header that is fetched by the 'oauth2_scheme'
    dependency. It is then decoded and validated.

    Args:
        - db: An instance of the sqlalchemy.orm.Session class representing
                the current DB session, returned from the annotated dependency
                function.
        - token: A token fetched from the 'Authorization' request header,
                    returned by the annotated dependency function.

    Raises:
        HTTPException: Raised when the credentials could not be validated.

    Returns:
        An instance of the DB_User model, representing the user
        that matched the authorization header.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.token_signing_key, algorithms=[config.token_signing_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = db.query(DB_User).filter(DB_User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_user_ws(db: Session, token: str) -> DB_User | None:
    """Get authenticated user in a WebSocket

    Args:
        - db: An instance of the sqlalchemy.orm.Session class representing
                the current DB session.
        - token: An authorization token.

    Returns:
        An instance of the DB_User model, representing the user
        that matched the authorization token if there were no
        errors, None otherwise.
    """
    try:
        payload = jwt.decode(
            token, config.token_signing_key, algorithms=[config.token_signing_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
    except jwt.InvalidTokenError:
        return None
    user = db.query(DB_User).filter(DB_User.username == username).first()
    if user is None:
        return None
    return user


class RoleChecker:
    """DEpendency for checking the permissions of the currently logged in user."""

    def __init__(self, allowed_roles: list[int]) -> None:
        """Initizalize the class's instance.

        Args:
            allowed_roles: A list of allowed rolles represented by integers.
        """
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[DB_User, Depends(get_current_user)]) -> None:
        """Check if the current user's role is allowed.

        The method gets called when the class is used as a dependency
        in a path operation function and determines if the current users
        role is included in the list of allowed roles.

        Args:
            user: An instance of the DB_User model representing the currently
                    logged in (authenticated based on headers sent in the request)
                    user, returned from the annotated dependency function.

        Raises:
            HTTPException: Raised when current user's role is not present in the
                        list of allowed roles.
        """
        if user.role in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You don't have enough permissions"
        )


def check_if_user_is_chat_member(
    chat_id: Annotated[int, Path()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[DB_User, Depends(get_current_user)],
) -> None:
    """Check if the currently logged in user is the given chat's member.

    Raises:
        HTTPException: Raised when the current user is not a member of a given chat.
    """
    chat_members = db.query(DB_ChatMember).filter(DB_ChatMember.chat_id == chat_id).all()
    if current_user.user_id not in [chat_member.user_id for chat_member in chat_members]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Currently authorized user is not a member of the chat. Only chat members can add new members.",
        )
