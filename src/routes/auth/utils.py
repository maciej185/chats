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
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
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
