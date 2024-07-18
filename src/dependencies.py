"""Dependencies for the app."""

from typing import Generator

from sqlalchemy.orm import Session

from src.db import SessionLocal


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
