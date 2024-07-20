"""Database utilities for tests."""

from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # using
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db() -> Generator[Session, Any, Any]:
    """Get DB session and close it after the response was delivered.

    Used to override the original 'get_db' dependency to ensure that any
    DB connection created during tests uses the previously instantiated
    in-memory database instead of the normal DB.

    Docstring of the original dependency:
        The function is used as a dependency in path operation functions
        which means that any code before the 'yield' will be executed before
        sending the response and the code after is executed afterwards which
        means it can be used to perform clean-up actions, as it is used in this
        case for closing the DB session.

    Yields:
        An instance of the sqlalchemy.orm.Session class, representing the current DB
        session.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
